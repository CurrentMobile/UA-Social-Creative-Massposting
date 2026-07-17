"""Step 3b — Reference Video Analysis. Take ONE reference (a competitor-research
winner approved for recreation, a local file, or a URL) and produce a hyper-detailed
recreation blueprint with Gemini multimodal: scene-by-scene cut table, camera
mechanics, framing, transition/animation behaviors, CTA mechanics, B-roll trigger
rules, and a speaker-tagged transcript. The blueprint is the contract the edit stage
executes 1:1.

Distinct from Step 3 (breakdown_videos.py = coarse triage across MANY winners);
this is a deep single-asset analysis. Runs on the most capable Gemini model available
on the key at analysis time (--model auto picks the newest Pro-tier).

Reads GEMINI_API_KEY from root .env. Nothing is spent under --dry-run.

Usage:
    .venv\\Scripts\\python.exe tools\\analyze_video.py --app mode-earn --winner 1 --date 2026-06-24 --dry-run
    .venv\\Scripts\\python.exe tools\\analyze_video.py --app mode-earn --file ".tmp\\ref\\clip.mp4"
    .venv\\Scripts\\python.exe tools\\analyze_video.py --app mode-earn --url "https://www.tiktok.com/@user/video/123"
    .venv\\Scripts\\python.exe tools\\analyze_video.py --app mode-earn --file ad.png --static

Output: assets/<app>/reference-analysis/<date>/<slug>/blueprint.json + blueprint.md
        assets/<app>/reference-analysis/generation-log.json      (cost entry appended)
Source copies land in .tmp/<app>/reference-analysis/<date>/<slug>/ (disposable —
competitor media never syncs to the Shared Drive).

Exit codes: 0 = clean, 2 = blueprint written with QA warnings, 1 = hard failure.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

import _research_lib as rl
from breakdown_videos import GEMINI_BASE, gemini_list_models, gemini_upload_file, gemini_wait_active

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
VID_MIMES = {".mp4": "video/mp4", ".m4v": "video/mp4", ".mov": "video/quicktime",
             ".webm": "video/webm", ".mkv": "video/x-matroska"}
MAX_UPLOAD_BYTES = int(1.9 * 1024**3)   # Files API caps at 2 GB
MAX_DURATION_S = 15 * 60                # blueprints are for short-form; --force to bypass
WARN_DURATION_S = 3 * 60

# Rough $/1M tokens (input, output) by model-family substring — estimates only.
USD_PER_1M = {"pro": (1.25, 10.0), "flash": (0.30, 2.50)}

# Model ids that are never the right analysis model, even if they contain "pro".
_MODEL_EXCLUDE = ("embedding", "tts", "image", "audio", "live", "lite", "nano", "flash")


# --------------------------------------------------------------------------- #
# Blueprint schema (Gemini structured output, OpenAPI subset)
# --------------------------------------------------------------------------- #
BLUEPRINT_SCHEMA = {
    "type": "object",
    "properties": {
        "overview": {
            "type": "object",
            "properties": {
                "format_and_aspect": {"type": "string", "description": "Overall format (UGC, Street Interview, Skit, VSL...) and aspect ratio."},
                "color_grading": {"type": "string", "description": "Lighting, saturation, contrast, overall color tone."},
                "target_audience": {"type": "string", "description": "Core demographic the ad speaks to."},
                "personas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "person": {"type": "string", "description": "Who (e.g. Host, Interviewee 1, Presenter)."},
                            "persona": {"type": "string", "description": "Physical appearance, wardrobe, demeanor, character archetype."},
                        },
                        "required": ["person", "persona"],
                    },
                },
                "pacing": {"type": "string", "description": "Cut speed, average clip length, overall edit tempo."},
                "creative_direction": {"type": "string", "description": "The big creative idea and why it hooks."},
            },
            "required": ["format_and_aspect", "color_grading", "target_audience", "personas", "pacing", "creative_direction"],
        },
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start": {"type": "string", "description": "MM:SS.mmm of the cut in ('static' for a still image)."},
                    "end": {"type": "string", "description": "MM:SS.mmm of the cut out."},
                    "scene_focus": {"type": "string", "description": "Narrative/marketing purpose (The Hook, The Proof, The CTA...)."},
                    "visuals_broll": {"type": "string", "description": "A-roll action + exactly what B-roll/digital assets show, and how they map to the spoken line."},
                    "camera_shot_angle": {"type": "string", "description": "Shot size (MCU, Wide...) and angle (eye-level, high angle...)."},
                    "framing": {"type": "string", "description": "Subject placement (dead-center single, tight 2-shot, keyed bottom-left...)."},
                    "camera_movement": {"type": "string", "description": "Physical camera motion (handheld pan, tracking back, static, subtle push-in...)."},
                    "transitions_animations": {"type": "string", "description": "Cut style (hard cut, J-cut...) + EXACT in/out animation of every text, B-roll, and UI overlay (scale-in bounce, horizontal slide, word-by-word pop-in; direction, easing feel, rough duration)."},
                },
                "required": ["start", "end", "scene_focus", "visuals_broll", "camera_shot_angle",
                             "framing", "camera_movement", "transitions_animations"],
            },
        },
        "technical_execution": {
            "type": "object",
            "properties": {
                "asset_layering_rotoscoping": {"type": "string", "description": "How multiple B-roll assets appear over one A-roll clip (sequential stacking, background removal, masks...)."},
                "end_card_cta": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Exact on-screen CTA copy."},
                        "logos": {"type": "string", "description": "Logos/badges shown and where."},
                        "implied_sfx": {"type": "string", "description": "Sound effects implied by the graphics."},
                        "animate_on_behavior": {"type": "string", "description": "Exactly how the final graphics animate onto screen."},
                    },
                    "required": ["text", "logos", "implied_sfx", "animate_on_behavior"],
                },
            },
            "required": ["asset_layering_rotoscoping", "end_card_cta"],
        },
        "production_checklist": {
            "type": "object",
            "properties": {
                "a_roll": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "Specific action/reaction needed from the AI avatar."},
                            "environment": {"type": "string", "description": "Environment/setting for the shot."},
                        },
                        "required": ["action", "environment"],
                    },
                },
                "b_roll_digital_assets": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "asset": {"type": "string", "description": "The asset needed (screen record, review card, UI screenshot, PNG logo, meme, lifestyle shot...)."},
                            "asset_type": {"type": "string", "description": "screen-record|review|ui-screenshot|logo-png|meme|lifestyle|brand-asset|other"},
                            "where_used": {"type": "string", "description": "Which scene/beat it appears in."},
                        },
                        "required": ["asset", "asset_type", "where_used"],
                    },
                },
            },
            "required": ["a_roll", "b_roll_digital_assets"],
        },
        "broll_generation_template": {
            "type": "array",
            "minItems": 4,
            "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "trigger_keyword": {"type": "string", "description": "Keyword/phrase family from the video's core themes."},
                    "core_theme": {"type": "string"},
                    "broll_standard": {"type": "string", "description": "Exact rule: whenever this keyword is spoken in ANY future script, cut to <this B-roll standard>."},
                },
                "required": ["trigger_keyword", "core_theme", "broll_standard"],
            },
        },
        "transcript": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "speaker": {"type": "string", "description": "Host, Interviewee 1, Voiceover, ON-SCREEN..."},
                    "start": {"type": "string", "description": "MM:SS the line starts (optional)."},
                    "text": {"type": "string", "description": "Word-for-word dialogue."},
                },
                "required": ["speaker", "text"],
            },
        },
    },
    "required": ["overview", "scenes", "technical_execution", "production_checklist",
                 "broll_generation_template", "transcript"],
}


def build_prompt(is_static: bool, retry_note: str = "") -> str:
    lines = [
        "You are an elite Direct Response organic-social and paid-ads Content Strategist "
        "and Creative Director. Perform a hyper-detailed, technical, structural breakdown "
        "of this creative. Your output is a RECREATION BLUEPRINT: an editor must be able "
        "to recreate the style, pacing, and visual mechanics 1:1 WITHOUT ever watching "
        "the source. Never skip camera mechanics, visual effects, motion graphics, or "
        "animation behaviors — those are the highest-value details.",
        "",
        "Fill every section of the schema:",
        "1. overview — format + aspect ratio, color grading (lighting/saturation/contrast/"
        "tone), target audience best fit, EVERY person's persona (appearance, wardrobe, "
        "demeanor, archetype), and pacing (cut speed, average clip length, tempo).",
        "2. scenes — one row PER CUT or scene change, chronological. Timestamps as "
        "MM:SS.mmm, contiguous from 00:00.000 to the end of the video (no gaps, no "
        "overlaps). For each row: the marketing purpose, the A-roll action AND exactly "
        "what B-roll/digital assets are shown and how they correlate to the spoken line, "
        "shot size + angle, framing, physical camera motion, and the cut style plus the "
        "EXACT in/out animation of every text element, B-roll, and UI overlay (e.g. "
        "scale-in bounce, horizontal slide, word-by-word pop-in — with direction, easing "
        "feel, and rough duration). NEVER leave camera_movement, framing, or "
        "transitions_animations generic or blank — if the camera is locked off, say "
        "'static tripod, no movement'.",
        "3. technical_execution — how B-roll layers over A-roll (stacking order, "
        "background removal / rotoscoping), and a dedicated end-card/CTA breakdown: "
        "exact text, logos, implied SFX, and exactly how the final graphics animate on.",
        "4. production_checklist — every raw/AI asset required to recreate this: A-roll "
        "avatar actions + environments; B-roll & digital assets (screen recordings, "
        "lifestyle shots, review cards, UI screenshots, PNG logos, meme formats...).",
        "5. broll_generation_template — 4 to 5 trigger keywords from the video's core "
        "themes; for each, the exact B-roll standard to cut to whenever that keyword is "
        "spoken in ANY future script (rule-based, programmatic — usable by an automated "
        "editor if the script changes).",
        "6. transcript — word-for-word dialogue, every line tagged with its speaker "
        "(Host, Interviewee 1, Voiceover...).",
    ]
    if is_static:
        lines += [
            "",
            "THIS IS A STATIC IMAGE, not a video. Treat it as a single scene row with "
            "start='static' and end='static'; describe the implied composition in the "
            "camera columns and every design element's visual treatment in "
            "transitions_animations (as if briefing a motion designer to animate it). "
            "The transcript is every piece of on-screen copy, top-to-bottom, each line "
            "tagged speaker='ON-SCREEN'. Pacing describes visual hierarchy / eye flow.",
        ]
    if retry_note:
        lines += ["", f"REVIEWER CORRECTIONS FROM THE PREVIOUS ATTEMPT — address these explicitly: {retry_note}"]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Model selection
# --------------------------------------------------------------------------- #
def pick_model(available: list[str], requested: str = "auto") -> str:
    """Pick the newest, most capable Pro-tier Gemini model on this key."""
    if requested != "auto":
        if available and requested not in available:
            pro = [m for m in available if "pro" in m][:8]
            sys.exit(f"Model '{requested}' not available on this key. Pro-tier options: {', '.join(pro) or '(none)'}")
        return requested

    def version(m: str) -> tuple[int, int]:
        mm = re.match(r"gemini-(\d+)(?:\.(\d+))?", m)
        return (int(mm.group(1)), int(mm.group(2) or 0)) if mm else (0, 0)

    cands = [m for m in available
             if m.startswith("gemini-") and "pro" in m
             and not any(x in m for x in _MODEL_EXCLUDE)]
    if not cands:
        fallback = "gemini-2.5-pro" if "gemini-2.5-pro" in available else "gemini-2.5-flash"
        print(f"[warn] no Pro-tier model found on this key; falling back to {fallback}")
        return fallback
    # newest version first; at equal version prefer stable over preview/exp, then shortest id
    cands.sort(key=lambda m: (version(m), "preview" not in m and "exp" not in m, -len(m)), reverse=True)
    return cands[0]


# --------------------------------------------------------------------------- #
# Source resolution
# --------------------------------------------------------------------------- #
def slugify(text: str, fallback: str = "reference") -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:60] or fallback


def probe_duration(path: Path) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True,
        )
        return float(r.stdout.strip())
    except Exception:  # noqa: BLE001
        return 0.0


def _is_static_path(path: Path, forced: bool) -> bool:
    return forced or path.suffix.lower() in IMG_EXTS


def resolve_source(args, date: str, tmp_dir: Path, download: bool = True) -> dict:
    """Resolve the reference into {slug, local_path, is_static, mime, meta}.

    With download=False (dry-run) no bytes move; local_path may be None.
    """
    if args.winner is not None:
        winners_path = args.winners or (
            PROJECT_ROOT / "assets" / args.app / "competitor-research" / date / "winners.json")
        payload = rl.read_json(winners_path)
        if not payload or "winners" not in payload:
            sys.exit(f"No winners.json at {rl.rel_to_root(winners_path)} — run Step 2 first, or use --file/--url.")
        organic = [w for w in payload["winners"]
                   if w.get("platform") in ("tiktok", "instagram") and w.get("video_url")]
        w = next((x for x in organic if x.get("rank") == args.winner), None)
        if not w:
            ranks = sorted(x.get("rank") for x in organic)
            sys.exit(f"Winner rank {args.winner} is not an organic entry with a video "
                     f"(FB text-only ads can't be blueprinted). Available ranks: {ranks}")
        slug = args.slug or slugify(f"r{w['rank']:02d}-{w['platform']}-{w.get('author') or ''}")
        # reuse the Step-3 download if it exists
        stem = PROJECT_ROOT / ".tmp" / args.app / "competitor-research" / date / "videos" / f"{w['rank']:02d}_{w['platform']}"
        local = next((p for p in stem.parent.glob(stem.name + ".*")
                      if p.suffix.lower() in rl.VIDEO_EXTS), None) if stem.parent.exists() else None
        if local is None and download:
            local = rl.download_video(w["video_url"], tmp_dir / slug / "source", direct=False)
            if not local:
                sys.exit("download failed — check the URL or supply --file with a local copy.")
        meta = {"origin": "competitor-research", "research_date": date, "rank": w.get("rank"),
                "platform": w.get("platform"), "url": w.get("url"), "author": w.get("author"),
                "views": w.get("views"), "engagement_rate": w.get("engagement_rate")}
        return {"slug": slug, "local_path": local, "is_static": False,
                "mime": VID_MIMES.get(local.suffix.lower(), "video/mp4") if local else "video/mp4",
                "meta": meta}

    if args.url:
        parsed = urlparse(args.url)
        last = Path(parsed.path).name
        slug = args.slug or slugify(Path(last).stem or parsed.netloc)
        suffix = Path(last).suffix.lower()
        local = None
        if download:
            direct = suffix in rl.VIDEO_EXTS or suffix in IMG_EXTS
            local = rl.download_video(args.url, tmp_dir / slug / "source", direct=direct)
            if not local and not direct:  # yt-dlp failed; try a direct stream as last resort
                local = rl.download_video(args.url, tmp_dir / slug / "source", direct=True)
            if not local:
                sys.exit("download failed (login-walled or unsupported URL?) — save the file locally and use --file.")
        is_static = _is_static_path(local or Path(last), args.static)
        mime = (VID_MIMES.get(local.suffix.lower(), "video/mp4") if (local and not is_static) else "video/mp4")
        return {"slug": slug, "local_path": local, "is_static": is_static, "mime": mime,
                "meta": {"origin": "url", "url": args.url}}

    # --file
    src = args.file.resolve()
    if not src.exists():
        sys.exit(f"file not found: {src}")
    slug = args.slug or slugify(src.stem)
    is_static = _is_static_path(src, args.static)
    local = src
    if download:
        dst = tmp_dir / slug / f"source{src.suffix.lower()}"
        if src != dst:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            local = dst
    return {"slug": slug, "local_path": local, "is_static": is_static,
            "mime": VID_MIMES.get(src.suffix.lower(), "video/mp4"),
            "meta": {"origin": "file", "path": str(src)}}


# --------------------------------------------------------------------------- #
# Gemini call
# --------------------------------------------------------------------------- #
def image_part(path: Path) -> dict:
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(path.suffix.lower().lstrip("."), "image/png")
    return {"inlineData": {"mimeType": mime, "data": base64.b64encode(path.read_bytes()).decode()}}


def gemini_generate(parts: list[dict], model: str, key: str, *, max_output_tokens: int,
                    media_resolution: str = "default", timeout: int = 300,
                    retries: int = 2) -> tuple[dict, dict]:
    """generateContent against BLUEPRINT_SCHEMA. Returns (blueprint, usageMetadata)."""
    gen_cfg: dict = {
        "responseMimeType": "application/json",
        "responseSchema": BLUEPRINT_SCHEMA,
        "maxOutputTokens": max_output_tokens,
    }
    if media_resolution == "low":
        gen_cfg["mediaResolution"] = "MEDIA_RESOLUTION_LOW"
    body = {"contents": [{"parts": parts}], "generationConfig": gen_cfg}
    last_err: Exception | None = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(
                f"{GEMINI_BASE}/v1beta/models/{model}:generateContent",
                params={"key": key}, json=body, timeout=timeout,
            )
            if r.status_code != 200:
                raise RuntimeError(f"Gemini generateContent HTTP {r.status_code}: {r.text[:300]}")
            data = r.json()
            try:
                cand = data["candidates"][0]
            except (KeyError, IndexError):
                raise RuntimeError(f"Gemini returned no candidates: {json.dumps(data)[:300]}")
            finish = cand.get("finishReason", "")
            if finish == "MAX_TOKENS":
                raise RuntimeError(
                    "Gemini hit MAX_TOKENS before finishing the blueprint — the scene table "
                    "is too big for the output budget. Fixes: lower --fps, use "
                    "--media-resolution low, trim the video to the relevant span, or raise "
                    "--max-output-tokens.")
            try:
                text = cand["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                raise RuntimeError(f"Gemini returned no content (finishReason={finish}): {json.dumps(data)[:300]}")
            return json.loads(text), data.get("usageMetadata", {})
        except Exception as e:  # noqa: BLE001
            last_err = e
            if attempt < retries and "MAX_TOKENS" not in str(e):
                time.sleep(3 * (attempt + 1))
                continue
            break
    raise RuntimeError(f"Gemini analysis failed after {retries + 1} attempt(s): {last_err}")


def estimate_usd(model: str, usage: dict) -> float | None:
    for family, (usd_in, usd_out) in USD_PER_1M.items():
        if family in model:
            pt = float(usage.get("promptTokenCount") or 0)
            ct = float(usage.get("candidatesTokenCount") or 0)
            return round((pt * usd_in + ct * usd_out) / 1_000_000, 4)
    return None


# --------------------------------------------------------------------------- #
# Validation + rendering
# --------------------------------------------------------------------------- #
_STUBS = {"", "n/a", "na", "none", "-", "unknown"}


def _ts_to_s(ts: str) -> float | None:
    m = re.match(r"^(?:(\d+):)?(\d{1,2}):(\d{1,2}(?:\.\d+)?)$", (ts or "").strip())
    if not m:
        return None
    h = int(m.group(1) or 0)
    return h * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def validate_blueprint(bp: dict, duration_s: float, is_static: bool) -> list[str]:
    warns: list[str] = []
    for section in ("overview", "scenes", "technical_execution",
                    "production_checklist", "broll_generation_template", "transcript"):
        if not bp.get(section):
            warns.append(f"section '{section}' is empty")

    scenes = bp.get("scenes") or []
    if not is_static and scenes:
        spans = [(_ts_to_s(s.get("start", "")), _ts_to_s(s.get("end", ""))) for s in scenes]
        if any(a is None or b is None for a, b in spans):
            warns.append("some scene timestamps are not parseable MM:SS(.mmm)")
        else:
            if spans and spans[0][0] is not None and spans[0][0] > 1.0:
                warns.append(f"first scene starts at {spans[0][0]:.1f}s (expected <=1s)")
            for i in range(1, len(spans)):
                prev_end, cur_start = spans[i - 1][1], spans[i][0]
                if cur_start < prev_end - 0.05:
                    warns.append(f"scene {i + 1} overlaps the previous one")
                elif cur_start - prev_end > 1.0:
                    warns.append(f"gap of {cur_start - prev_end:.1f}s before scene {i + 1}")
            if duration_s > 0 and spans[-1][1] is not None:
                if abs(spans[-1][1] - duration_s) > max(1.0, 0.10 * duration_s):
                    warns.append(f"last scene ends at {spans[-1][1]:.1f}s but the video is {duration_s:.1f}s")

        thin = sum(1 for s in scenes
                   if (s.get("camera_movement") or "").strip().lower() in _STUBS
                   or (s.get("transitions_animations") or "").strip().lower() in _STUBS)
        if scenes and thin / len(scenes) > 0.5:
            warns.append("camera/animation detail is thin on >50% of scenes — re-run with --retry-note and/or --fps 5")

    if not is_static and not (bp.get("transcript") or []):
        warns.append("transcript is empty for a video source")
    trig = bp.get("broll_generation_template") or []
    if not (4 <= len(trig) <= 5) or any((t.get("broll_standard") or "").strip().lower() in _STUBS for t in trig):
        warns.append("broll_generation_template needs 4-5 triggers, each with a concrete standard")
    return warns


def _md_cell(text: str) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


def render_markdown(bp: dict, source: dict, model: str, duration_s: float,
                    warnings: list[str], generated_at: str) -> str:
    meta = source["meta"]
    o = bp.get("overview", {})
    te = bp.get("technical_execution", {})
    cta = te.get("end_card_cta", {})
    pc = bp.get("production_checklist", {})

    lines = [f"# Recreation Blueprint — {source['slug']}", ""]
    lines += ["## Source", ""]
    for k, v in {"Origin": meta.get("origin"), "URL": meta.get("url"), "Path": meta.get("path"),
                 "Platform": meta.get("platform"), "Rank": meta.get("rank"),
                 "Author": meta.get("author"), "Research date": meta.get("research_date"),
                 "Duration": f"{duration_s:.1f}s" if duration_s else ("static image" if source["is_static"] else None),
                 "Model": model, "Analyzed": generated_at}.items():
        if v not in (None, ""):
            lines.append(f"- **{k}:** {v}")

    lines += ["", "## 1. Overview & Creative Direction", ""]
    lines += [f"- **Format & aspect:** {o.get('format_and_aspect', '')}",
              f"- **Color grading:** {o.get('color_grading', '')}",
              f"- **Target audience:** {o.get('target_audience', '')}",
              f"- **Pacing:** {o.get('pacing', '')}",
              f"- **Creative direction:** {o.get('creative_direction', '')}",
              "", "**Personas featured:**", ""]
    for p in o.get("personas") or []:
        lines.append(f"- **{p.get('person', '?')}:** {p.get('persona', '')}")

    lines += ["", "## 2. Scene-by-Scene Breakdown", "",
              "| Time | Scene/Clip Focus | Visuals & B-roll (VO link) | Shot & Angle | Framing | Camera Movement | Transitions & Animations |",
              "|------|------------------|----------------------------|--------------|---------|-----------------|--------------------------|"]
    for s in bp.get("scenes") or []:
        t = f"{s.get('start', '')} - {s.get('end', '')}" if s.get("start") != "static" else "static"
        lines.append("| " + " | ".join(_md_cell(x) for x in (
            t, s.get("scene_focus"), s.get("visuals_broll"), s.get("camera_shot_angle"),
            s.get("framing"), s.get("camera_movement"), s.get("transitions_animations"))) + " |")

    lines += ["", "## 3. Technical Execution", "",
              f"**Asset layering & rotoscoping:** {te.get('asset_layering_rotoscoping', '')}", "",
              "**End card / CTA mechanics:**", "",
              f"- **Text:** {cta.get('text', '')}",
              f"- **Logos:** {cta.get('logos', '')}",
              f"- **Implied SFX:** {cta.get('implied_sfx', '')}",
              f"- **Animate-on behavior:** {cta.get('animate_on_behavior', '')}"]

    lines += ["", "## 4. Production Checklist", "", "**A-roll requirements:**", ""]
    for a in pc.get("a_roll") or []:
        lines.append(f"- {a.get('action', '')} — *{a.get('environment', '')}*")
    lines += ["", "**B-roll & digital asset requirements:**", ""]
    for b in pc.get("b_roll_digital_assets") or []:
        lines.append(f"- `{b.get('asset_type', 'other')}` {b.get('asset', '')} — used in: {b.get('where_used', '')}")

    lines += ["", "## 5. B-Roll Generation Template (Keyword Triggers)", "",
              "| Trigger Keyword | Core Theme | B-Roll Standard |",
              "|-----------------|------------|-----------------|"]
    for t in bp.get("broll_generation_template") or []:
        lines.append("| " + " | ".join(_md_cell(x) for x in (
            t.get("trigger_keyword"), t.get("core_theme"), t.get("broll_standard"))) + " |")

    lines += ["", "## 6. Tagged Transcript", ""]
    for line in bp.get("transcript") or []:
        ts = f" [{line.get('start')}]" if line.get("start") else ""
        lines.append(f"**{line.get('speaker', '?')}**{ts} {line.get('text', '')}")
        lines.append("")

    if warnings:
        lines += ["## QA", ""] + [f"- [warn] {w}" for w in warnings]
    return "\n".join(lines).rstrip() + "\n"


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


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Step 3b — deep reference analysis into a recreation blueprint (Gemini)")
    ap.add_argument("--app", default="mode-earn")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--winner", type=int, help="rank from winners.json (organic entries with a video)")
    src.add_argument("--file", type=Path, help="local video or image")
    src.add_argument("--url", help="page URL (yt-dlp) or direct media URL")
    ap.add_argument("--date", default=None, help="research date for --winner; also the output date folder (default today)")
    ap.add_argument("--winners", type=Path, default=None, help="explicit winners.json path")
    ap.add_argument("--slug", default=None, help="override the output slug")
    ap.add_argument("--static", action="store_true", help="force image mode (auto-detected by extension otherwise)")
    ap.add_argument("--model", default="auto", help="Gemini model id, or 'auto' = newest Pro-tier on this key")
    ap.add_argument("--fps", type=int, default=None, help="video sampling fps override (fast-cut edits; default API 1fps)")
    ap.add_argument("--media-resolution", dest="media_resolution", choices=["default", "low"], default="default")
    ap.add_argument("--max-output-tokens", dest="max_output_tokens", type=int, default=65536)
    ap.add_argument("--timeout", type=int, default=300, help="seconds per Gemini upload/generate call")
    ap.add_argument("--retry-note", dest="retry_note", default="", help="corrective note appended to the prompt on a re-run")
    ap.add_argument("--force", action="store_true", help="bypass the 15-minute length gate")
    ap.add_argument("--dry-run", action="store_true", help="resolve source + model, print the plan; spend nothing")
    args = ap.parse_args()

    date = args.date or rl.today_str()
    out_root = PROJECT_ROOT / "assets" / args.app / "reference-analysis"
    tmp_dir = PROJECT_ROOT / ".tmp" / args.app / "reference-analysis" / date

    source = resolve_source(args, date, tmp_dir, download=not args.dry_run)
    slug = source["slug"]
    out_dir = out_root / date / slug

    print("=" * 64)
    print(f"STEP 3b — REFERENCE VIDEO ANALYSIS  ({args.app}, {date})")
    print(f"source : {source['meta'].get('url') or source['meta'].get('path') or 'winner rank ' + str(args.winner)}")
    print(f"slug   : {slug}   mode : {'static image' if source['is_static'] else 'video'}")
    print("=" * 64)

    env = rl.load_env()
    key = env.get("GEMINI_API_KEY", "")

    if args.dry_run:
        model = args.model
        if key:
            models = gemini_list_models(key)
            if models:
                model = pick_model(models, args.model)
        local = source["local_path"]
        dur = probe_duration(local) if (local and not source["is_static"]) else 0.0
        if local:
            print(f"local file : {rl.rel_to_root(local)} ({local.stat().st_size / 1e6:.1f} MB"
                  + (f", {dur:.1f}s" if dur else "") + ")")
        else:
            print("local file : (not downloaded yet — the real run downloads it)")
        print(f"model      : {model}" + ("  (auto-selected)" if args.model == "auto" and key else
                                         "  (pass a key-validated id or 'auto')" if not key else ""))
        if dur > WARN_DURATION_S:
            print(f"[warn] video is {dur / 60:.1f} min — consider --media-resolution low"
                  + (" (over the 15-min gate; needs --force)" if dur > MAX_DURATION_S else ""))
        print(f"would write -> {rl.rel_to_root(out_dir / 'blueprint.md')}")
        print(f"[dry-run] one Gemini call on {model} "
              f"(Pro-tier video analysis is roughly $0.10-0.50 for a short clip). No credits spent.")
        return 0

    if not key:
        sys.exit("GEMINI_API_KEY not found in .env")
    models = gemini_list_models(key)
    model = pick_model(models, args.model)
    print(f"Gemini key OK ({rl.mask(key)}); model {model}"
          + (" (auto-selected: newest Pro-tier)" if args.model == "auto" else "") + "\n")

    local: Path = source["local_path"]
    duration_s = 0.0
    if not source["is_static"]:
        duration_s = probe_duration(local)
        if duration_s > MAX_DURATION_S and not args.force:
            sys.exit(f"video is {duration_s / 60:.1f} min — over the 15-min gate for blueprints. "
                     "Trim to the relevant span with ffmpeg, or pass --force.")
        if duration_s > WARN_DURATION_S and args.media_resolution == "default":
            print(f"[warn] video is {duration_s / 60:.1f} min — consider --media-resolution low to cut tokens.")
    if local.stat().st_size > MAX_UPLOAD_BYTES:
        sys.exit(f"file is {local.stat().st_size / 1e9:.2f} GB — over the Files API ~2 GB cap. Re-encode smaller.")

    # build parts
    prompt = build_prompt(source["is_static"], args.retry_note)
    if source["is_static"]:
        parts = [image_part(local), {"text": prompt}]
    else:
        print(f"uploading {rl.rel_to_root(local)} ({local.stat().st_size / 1e6:.1f} MB) to the Files API…")
        fobj = gemini_upload_file(local, key, mime=source["mime"])
        uri = gemini_wait_active(fobj, key, timeout=args.timeout)
        file_part: dict = {"fileData": {"mimeType": source["mime"], "fileUri": uri}}
        if args.fps:
            file_part["videoMetadata"] = {"fps": args.fps}
        parts = [file_part, {"text": prompt}]
        print("file ACTIVE; analyzing…")

    started = time.monotonic()
    bp, usage = gemini_generate(parts, model, key, max_output_tokens=args.max_output_tokens,
                                media_resolution=args.media_resolution, timeout=args.timeout)
    print(f"analysis done in {time.monotonic() - started:.0f}s "
          f"({usage.get('promptTokenCount', '?')} in / {usage.get('candidatesTokenCount', '?')} out tokens)")

    warnings = validate_blueprint(bp, duration_s, source["is_static"])
    generated_at = rl.now_iso()
    est = estimate_usd(model, usage)

    blueprint_json = {
        "app": args.app, "slug": slug, "generated_at": generated_at, "model": model,
        "source": {**source["meta"], "duration_s": round(duration_s, 2) or None,
                   "local_file": rl.rel_to_root(local), "is_static": source["is_static"]},
        "generation": {"fps": args.fps, "media_resolution": args.media_resolution,
                       "usage": usage, "est_usd": est, "retry_note": args.retry_note or None},
        "qa_warnings": warnings,
        "blueprint": bp,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    rl.write_json(out_dir / "blueprint.json", blueprint_json)
    md = render_markdown(bp, source, model, duration_s, warnings, generated_at)
    (out_dir / "blueprint.md").write_text(md, encoding="utf-8")

    append_log(out_root / "generation-log.json", {
        "type": "video_analysis", "label": slug, "model": model,
        "source": source["meta"].get("url") or source["meta"].get("path") or f"winner r{args.winner}",
        "duration_s": round(duration_s, 2), "usage": {k: usage.get(k) for k in
                                                      ("promptTokenCount", "candidatesTokenCount", "totalTokenCount")},
        "est_usd": est, "created": generated_at,
    })
    if est is not None:
        print(f"estimated cost ~${est:.3f} (usage-based estimate; logged to generation-log.json)")

    n_scenes = len(bp.get("scenes") or [])
    n_lines = len(bp.get("transcript") or [])
    icon = "[warn]" if warnings else "[ OK ]"
    print(f"{icon} blueprint: {n_scenes} scene(s), {n_lines} transcript line(s), "
          f"{len(bp.get('broll_generation_template') or [])} B-roll trigger(s)")
    for w in warnings:
        print(f"       - {w}")
    print(rl.rel_to_root(out_dir / "blueprint.md"))  # last line = machine-readable path
    return 2 if warnings else 0


if __name__ == "__main__":
    raise SystemExit(main())
