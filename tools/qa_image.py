"""AI-vision QA for generated assets — catches hallucinations BEFORE paid Kling jobs.

QA gate of the asset-generation SOP (see workflows/generate_assets.md, gates A-D).
Sends the candidate image (or a clip's first+last frames) to Gemini multimodal with a
per-shot-type rubric (qa/rubrics.json) and optional reference anchors (persona base
image, phone prop, app UI), and returns a structured verdict:

    {"verdict": "pass|warn|fail", "defects": [{code, severity, description, region}],
     "regenerate_hint": "...", "guardrail_candidates": [...]}

Defect codes map 1:1 to guardrail categories — pipe failures into the ledger with:
    tools/guardrails.py add --from-verdict <verdict.json>

The tool JUDGES; the agent DECIDES (regenerate vs escalate) per the workflow's
max-2-regenerate rule. QA checks defects only — creative taste stays human.

Usage:
    .venv\\Scripts\\python.exe tools\\qa_image.py --input ai-images\\img-3.png --shot-type extract ^
        --persona assets\\_shared\\personas\\retiree-female-poc\\base-character.png ^
        --context "chunk 3: seated on the sofa, no phone in this shot" ^
        --out .tmp\\qa\\img-3.verdict.json --log generation-log.json --label img-3
    .venv\\Scripts\\python.exe tools\\qa_image.py --input "ai-videos\\Clip 2.mp4" --shot-type aroll-clip ...
    .venv\\Scripts\\python.exe tools\\qa_image.py --batch ai-images --persona <base.png> --out-dir .tmp\\qa

Cost: ~258 tokens per image on gemini-2.5-flash — a full video's QA (~45 checks) costs
well under $0.10. Exit codes: 0 = pass, 2 = warn, 1 = fail (worst across batch).
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import requests

import _research_lib as rl

GEMINI_BASE = "https://generativelanguage.googleapis.com"
DEFAULT_MODEL = "gemini-2.5-flash"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RUBRIC = PROJECT_ROOT / "qa" / "rubrics.json"
IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp")
VID_EXTS = (".mp4", ".mov", ".webm")

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["pass", "warn", "fail"]},
        "score": {"type": "number", "description": "0-1 overall quality confidence (1 = flawless)."},
        "defects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "One of the rubric defect codes, verbatim."},
                    "severity": {"type": "string", "enum": ["warn", "fail"]},
                    "description": {"type": "string"},
                    "region": {"type": "string", "description": "Where in frame (e.g. 'left hand', 'grid row 2 col 3')."},
                },
                "required": ["code", "severity", "description"],
            },
        },
        "regenerate_hint": {
            "type": "string",
            "description": "POSITIVELY-phrased prompt guidance to avoid the worst defect on regeneration (empty if pass).",
        },
        "guardrail_candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "shot_type": {"type": "string"},
                    "defect": {"type": "string", "description": "The rubric defect code."},
                    "rule": {"type": "string", "description": "A reusable, positively-phrased prompt rule (<=2 lines)."},
                },
                "required": ["shot_type", "defect", "rule"],
            },
        },
    },
    "required": ["verdict", "score", "defects", "regenerate_hint"],
}

# shot-type inference for --batch mode, by filename pattern
_BATCH_PATTERNS: list[tuple[str, str]] = [
    (r"^base-character", "persona"),
    (r"^environment", "environment"),
    (r"^grid-\d+", "grid"),
    (r"^img-\d+", "extract"),
    (r"^phone-ui", "phone-shot"),
    (r"^broll-phone", "phone-shot"),
    (r"_b-roll\.(mp4|mov|webm)$", "broll-clip"),
    (r"_b-roll", "broll-still"),
    (r"^broll-", "broll-still"),
    (r"^Clip \d+", "aroll-clip"),
]


def infer_shot_type(path: Path) -> str | None:
    for pat, st in _BATCH_PATTERNS:
        if re.search(pat, path.name, re.IGNORECASE):
            return st
    return None


def ffprobe_duration(path: Path) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True,
        )
        return float(r.stdout.strip())
    except Exception:  # noqa: BLE001
        return 0.0


def extract_frames(video: Path, workdir: Path) -> list[tuple[str, Path]]:
    """Extract first + last frames of a clip -> [(tag, png_path), ...]."""
    workdir.mkdir(parents=True, exist_ok=True)
    dur = ffprobe_duration(video)
    frames: list[tuple[str, Path]] = []
    plan = [("first", 0.0)]
    if dur > 0.6:
        plan.append(("last", max(0.0, dur - 0.3)))
    for tag, ts in plan:
        out = workdir / f"{video.stem}-{tag}.png"
        r = subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-ss", f"{ts:.3f}", "-i", str(video),
             "-frames:v", "1", str(out)],
            capture_output=True, text=True,
        )
        if r.returncode == 0 and out.exists():
            frames.append((tag, out))
        else:
            print(f"[qa] frame extract failed ({tag}): {r.stderr.strip()[:200]}")
    return frames


def image_part(path: Path) -> dict:
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(path.suffix.lower().lstrip("."), "image/png")
    return {"inlineData": {"mimeType": mime, "data": base64.b64encode(path.read_bytes()).decode()}}


def build_prompt(shot_type: str, rubric: dict, context: str,
                 has_persona: bool, has_props: bool, has_app_ui: bool) -> str:
    st = rubric["shot_types"].get(shot_type)
    if not st:
        sys.exit(f"unknown --shot-type '{shot_type}' — rubric has: {', '.join(rubric['shot_types'])}")
    defects = rubric["defects"]
    lines = [
        "You are a strict visual QA inspector for AI-generated UGC video assets. "
        "Inspect IMAGE 1 (the CANDIDATE) for the defects listed below — and ONLY those "
        "defects. Do not judge creative taste, composition, or beauty. Report every "
        "defect you find with its code verbatim, a severity, a one-line description, "
        "and where in the frame it is. If the candidate is clean, return verdict 'pass' "
        "with an empty defects list.",
        "",
        f"SHOT TYPE: {shot_type}. {st['instructions']}",
    ]
    if context:
        lines += ["", f"SHOT CONTEXT (what SHOULD be in frame): {context}"]
    refs = []
    n = 2
    if has_persona:
        refs.append(f"IMAGE {n} is the PERSONA REFERENCE (the character's canonical face + wardrobe)."); n += 1
    if has_props:
        refs.append(f"IMAGE {n} is the PHONE PROP REFERENCE (the exact device that must appear)."); n += 1
    if has_app_ui:
        refs.append(f"IMAGE {n} is the APP UI REFERENCE (what a visible phone screen must show)."); n += 1
    if refs:
        lines += [""] + refs
    lines += ["", "DEFECT CODES TO CHECK (use codes verbatim):"]
    for code in st["codes"]:
        d = defects[code]
        lines.append(f"- {code} (default severity {d['severity']}): {d['check']}")
    lines += [
        "",
        "Verdict rules: any 'fail' defect => verdict 'fail'; only 'warn' defects => "
        "'warn'; none => 'pass'. score is your 0-1 confidence the asset is production-clean.",
        "regenerate_hint: if failing, write POSITIVELY-phrased prompt guidance that "
        "would avoid the worst defect (state what SHOULD be in frame — never 'no X'/'avoid X').",
        "guardrail_candidates: only for defects likely to recur systematically, propose "
        "a reusable <=2-line positively-phrased prompt rule.",
    ]
    return "\n".join(lines)


def gemini_qa(candidate: Path, prompt: str, refs: list[Path], model: str, key: str,
              timeout: int = 120, retries: int = 2) -> dict:
    parts = [{"text": prompt}, image_part(candidate)]
    for r in refs:
        parts.append(image_part(r))
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "responseSchema": VERDICT_SCHEMA},
    }
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = requests.post(
                f"{GEMINI_BASE}/v1beta/models/{model}:generateContent",
                params={"key": key}, json=body, timeout=timeout,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Gemini HTTP {resp.status_code}: {resp.text[:300]}")
            data = resp.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text)
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < retries:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"Gemini QA failed after {retries + 1} attempts: {last_err}")


def normalize_verdict(v: dict, rubric: dict, shot_type: str) -> dict:
    """Enforce verdict consistency + stamp shot_type into guardrail candidates."""
    defects = v.get("defects") or []
    known = set(rubric["shot_types"][shot_type]["codes"])
    for d in defects:
        if d.get("code") not in known:
            d["code"] = "OTHER:" + str(d.get("code"))
    if any(d.get("severity") == "fail" for d in defects):
        v["verdict"] = "fail"
    elif defects and v.get("verdict") == "pass":
        v["verdict"] = "warn"
    for g in v.get("guardrail_candidates") or []:
        g.setdefault("shot_type", shot_type)
    return v


def qa_one(path: Path, shot_type: str, rubric: dict, context: str, refs: list[Path],
           model: str, key: str, workdir: Path) -> dict:
    """QA one asset (image, or video -> first+last frames; worst frame wins)."""
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    if path.suffix.lower() in VID_EXTS:
        frames = extract_frames(path, workdir)
        if not frames:
            return {"asset": str(path), "shot_type": shot_type, "verdict": "fail", "score": 0,
                    "defects": [{"code": "FRAME_EXTRACT_FAILED", "severity": "fail",
                                 "description": "could not extract frames with ffmpeg"}],
                    "regenerate_hint": "", "guardrail_candidates": [], "checked_at": started}
        sub = []
        for tag, fpath in frames:
            v = normalize_verdict(
                gemini_qa(fpath, build_prompt(shot_type, rubric, f"{context} [{tag} frame of the clip]",
                                              any("base-character" in str(r) for r in refs),
                                              any("s22" in r.name.lower() or "props" in str(r) for r in refs),
                                              any("brand" in str(r) or "ui" in r.name.lower() for r in refs)),
                          refs, model, key),
                rubric, shot_type)
            for d in v.get("defects", []):
                d["region"] = f"[{tag} frame] " + (d.get("region") or "")
            sub.append(v)
        order = {"pass": 0, "warn": 1, "fail": 2}
        worst = max(sub, key=lambda x: order.get(x.get("verdict"), 2))
        merged = {
            "verdict": worst["verdict"],
            "score": min(x.get("score", 0) for x in sub),
            "defects": [d for x in sub for d in x.get("defects", [])],
            "regenerate_hint": worst.get("regenerate_hint", ""),
            "guardrail_candidates": [g for x in sub for g in (x.get("guardrail_candidates") or [])],
        }
        v = merged
    else:
        v = normalize_verdict(
            gemini_qa(path, build_prompt(shot_type, rubric, context,
                                         any("base-character" in str(r) for r in refs),
                                         any("s22" in r.name.lower() or "props" in str(r) for r in refs),
                                         any("brand" in str(r) or "ui" in r.name.lower() for r in refs)),
                      refs, model, key),
            rubric, shot_type)
    v.update({"asset": rl.rel_to_root(path) if hasattr(rl, "rel_to_root") else str(path),
              "shot_type": shot_type, "qa_model": model, "checked_at": started})
    return v


def append_log(log_path: Path, entry: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    data: list = []
    if log_path.exists():
        try:
            data = json.loads(log_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            data = []
    data.append(entry)
    log_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="AI-vision QA for generated assets (Gemini)")
    ap.add_argument("--input", type=Path, help="candidate image or clip")
    ap.add_argument("--batch", type=Path, help="QA every image/clip in this directory (shot types inferred)")
    ap.add_argument("--shot-type", dest="shot_type",
                    help="persona|environment|grid|extract|phone-shot|broll-still|aroll-clip|broll-clip")
    ap.add_argument("--persona", type=Path, help="persona base-character.png (identity anchor)")
    ap.add_argument("--props", type=Path, help="phone prop reference image")
    ap.add_argument("--app-ui", dest="app_ui", type=Path, help="app UI/logo reference (screen-content anchor)")
    ap.add_argument("--context", default="", help="what SHOULD be in frame (script beat, pose, reveal-frame note)")
    ap.add_argument("--rubric", type=Path, default=DEFAULT_RUBRIC)
    ap.add_argument("--out", type=Path, help="write verdict JSON here (single input)")
    ap.add_argument("--out-dir", type=Path, help="verdict dir for --batch (default .tmp/qa)")
    ap.add_argument("--log", type=Path, help="generation-log.json to append a qa record to")
    ap.add_argument("--label", help="log label (should match the generation record's label)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--attempt", type=int, default=1, help="regeneration attempt number (for the log)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.input and not args.batch:
        sys.exit("need --input <file> or --batch <dir>")
    rubric = json.loads(args.rubric.read_text(encoding="utf-8"))

    targets: list[tuple[Path, str]] = []
    if args.input:
        st = args.shot_type or infer_shot_type(args.input)
        if not st:
            sys.exit(f"cannot infer shot type for {args.input.name} — pass --shot-type")
        targets.append((args.input, st))
    if args.batch:
        for p in sorted(args.batch.iterdir()):
            if p.suffix.lower() not in IMG_EXTS + VID_EXTS:
                continue
            st = args.shot_type or infer_shot_type(p)
            if st:
                targets.append((p, st))
            else:
                print(f"[qa] skip (no shot type): {p.name}")

    refs = [p for p in (args.persona, args.props, args.app_ui) if p]
    for r in refs:
        if not r.exists():
            sys.exit(f"reference not found: {r}")
    for t, _ in targets:
        if not t.exists():
            sys.exit(f"input not found: {t}")

    if args.dry_run:
        for t, st in targets:
            print(f"[dry-run] would QA {t} as {st} with {len(refs)} reference(s) on {args.model}")
        print(f"[dry-run] ~{len(targets)} Gemini call(s), well under $0.01 each. Nothing spent.")
        return 0

    env = rl.load_env()
    key = env.get("GEMINI_API_KEY", "")
    if not key:
        sys.exit("GEMINI_API_KEY not found in .env")

    workdir = PROJECT_ROOT / ".tmp" / "qa" / "frames"
    out_dir = args.out_dir or (PROJECT_ROOT / ".tmp" / "qa")
    worst = "pass"
    order = {"pass": 0, "warn": 1, "fail": 2}
    last_verdict: dict = {}

    for t, st in targets:
        v = qa_one(t, st, rubric, args.context, refs, args.model, key, workdir)
        v["attempt"] = args.attempt
        last_verdict = v
        if order[v["verdict"]] > order[worst]:
            worst = v["verdict"]
        icon = {"pass": "[ OK ]", "warn": "[warn]", "fail": "[FAIL]"}[v["verdict"]]
        print(f"{icon} {t.name} ({st}) score={v.get('score', 0):.2f}")
        for d in v.get("defects", []):
            print(f"       - {d['code']} ({d['severity']}): {d['description']}"
                  + (f"  @ {d['region']}" if d.get("region") else ""))
        if v["verdict"] == "fail" and v.get("regenerate_hint"):
            print(f"       hint: {v['regenerate_hint']}")

        vp = args.out if (args.out and len(targets) == 1) else out_dir / f"{t.stem}.verdict.json"
        vp.parent.mkdir(parents=True, exist_ok=True)
        vp.write_text(json.dumps(v, indent=2, ensure_ascii=False), encoding="utf-8")
        if args.log:
            append_log(args.log, {"type": "qa", "label": args.label or t.stem, **v})

    # last stdout line = machine-readable verdict summary (repo convention)
    print(json.dumps({"verdict": worst,
                      "defect_codes": sorted({d["code"] for d in last_verdict.get("defects", [])})
                      if len(targets) == 1 else None}))
    return {"pass": 0, "warn": 2, "fail": 1}[worst]


if __name__ == "__main__":
    raise SystemExit(main())
