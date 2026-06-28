"""Submit one Higgsfield generation, download the result, and log it.

The deterministic execution layer for the asset-generation SOP (Steps 2,4,5,6 in
workflows/generate_assets.md). Wraps the `higgsfield` CLI: builds the command, runs
`generate create ... --wait --json`, parses the result URL, downloads it to --out,
and appends a provenance record to generation-log.json. One call = one asset, so
naming/logging stay consistent across every image and clip.

Higgsfield outputs are CDN URLs with no built-in download, and they expire — this
tool downloads immediately after the job completes.

Auth is interactive/browser (`higgsfield auth login`); this tool only checks status.

Usage (image — repeat --image for multiple references, up to ~8):
    python tools/higgsfield_gen.py --model gpt_image_2 \
        --prompt "3x3 grid of the character ..." \
        --image assets/mode-earn/persona/base-character.png \
        --image assets/mode-earn/extraincomeforretirees/ai-images/environment.png \
        --param aspect_ratio=1:1 --param resolution=2k \
        --out assets/mode-earn/extraincomeforretirees/ai-images/grid-3.png \
        --log assets/mode-earn/extraincomeforretirees/generation-log.json \
        --label "grid-3"

Usage (A-roll clip — Kling, voiced, sound ON):
    python tools/higgsfield_gen.py --model kling3_0 \
        --prompt "<clip prompt incl voice tag + dialogue>" \
        --start-image assets/.../ai-images/img-1.png \
        --param aspect_ratio=9:16 --param duration=4 --param mode=pro --param sound=on \
        --timeout 30m \
        --out assets/.../ai-videos/Clip 1.mp4 --log assets/.../generation-log.json \
        --label "Clip 1"

Usage (phone-UI B-roll — Kling first+last frame, muted):
    python tools/higgsfield_gen.py --model kling3_0 --prompt "turn phone to camera ..." \
        --start-image .../phone-ui-first.png --end-image .../phone-ui-last.png \
        --param aspect_ratio=9:16 --param duration=5 --param mode=pro --param sound=off \
        --timeout 30m --out ".../ai-videos/phone-ui_b-roll.mp4" --log .../generation-log.json

Add --dry-run to print the command without spending credits. The downloaded file
path is printed as the LAST stdout line so callers can capture it.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def find_higgsfield() -> str:
    hf = shutil.which("higgsfield")
    if not hf:
        sys.exit(
            "higgsfield CLI not found on PATH. Install it:\n"
            "  curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh"
        )
    return hf


def run_cli(args: list[str], timeout_s: int | None = None) -> subprocess.CompletedProcess:
    hf = find_higgsfield()
    return subprocess.run(
        [hf, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_s,
    )


def check_auth() -> None:
    r = run_cli(["account", "status"], timeout_s=60)
    blob = (r.stdout or "") + (r.stderr or "")
    if r.returncode != 0 or "Session expired" in blob or "Not authenticated" in blob:
        sys.exit(
            "Higgsfield not authenticated. Run:  higgsfield auth login\n"
            f"(account status said: {blob.strip()[:200]})"
        )
    print(f"[hf] auth ok: {blob.strip()[:80]}")


def parse_json_array(stdout: str) -> list:
    """Parse the --json result, tolerating leading diagnostic lines."""
    stdout = stdout.strip()
    try:
        data = json.loads(stdout)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        pass
    # fall back: parse from the first JSON bracket to the end
    for opener in ("[", "{"):
        idx = stdout.find(opener)
        if idx != -1:
            try:
                data = json.loads(stdout[idx:])
                return data if isinstance(data, list) else [data]
            except json.JSONDecodeError:
                continue
    raise ValueError("could not find JSON in CLI output")


TERMINAL_REJECT = {"nsfw", "ip_detected"}  # content-filter rejections — retrying won't help


def pick_result(jobs: list) -> dict:
    """Pick the completed job object carrying a result_url."""
    for j in jobs:
        if isinstance(j, dict) and j.get("status") == "completed" and j.get("result_url"):
            return j
    for j in jobs:
        if isinstance(j, dict) and j.get("result_url"):
            return j
    statuses = {j.get("status") for j in jobs if isinstance(j, dict)}
    rejected = statuses & TERMINAL_REJECT
    if rejected:
        raise ValueError(f"content filter rejected (status={'/'.join(sorted(rejected))}); "
                         "rephrase the prompt — NOT RETRYING")
    raise ValueError("no result_url in CLI output (job may have failed or been filtered)")


def download(url: str, out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "mode-ai-creative-loop"})
    with urllib.request.urlopen(req, timeout=300) as resp, open(out, "wb") as f:
        shutil.copyfileobj(resp, f)
    return out.stat().st_size


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


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


def timeout_to_seconds(t: str) -> int:
    t = t.strip().lower()
    if t.endswith("m"):
        return int(float(t[:-1]) * 60)
    if t.endswith("s"):
        return int(float(t[:-1]))
    return int(float(t))


def main() -> int:
    ap = argparse.ArgumentParser(description="Submit one Higgsfield job, download + log it")
    ap.add_argument("--model", required=True, help="job_set_type, e.g. gpt_image_2 / kling3_0")
    ap.add_argument("--prompt", help="text prompt")
    ap.add_argument("--image", action="append", default=[], help="reference image (repeatable)")
    ap.add_argument("--start-image", dest="start_image", help="first frame (image-to-video)")
    ap.add_argument("--end-image", dest="end_image", help="last frame (image-to-video)")
    ap.add_argument("--param", action="append", default=[], metavar="key=value",
                    help="schema param, e.g. aspect_ratio=9:16 (repeatable)")
    ap.add_argument("--out", type=Path, required=True, help="download target (include extension)")
    ap.add_argument("--log", type=Path, help="generation-log.json to append to")
    ap.add_argument("--label", help="human label for the log (e.g. 'Clip 1')")
    ap.add_argument("--timeout", default="20m", help="--wait-timeout (default 20m; use 30m for video)")
    ap.add_argument("--retries", type=int, default=2, help="retry attempts on transient failure (default 2)")
    ap.add_argument("--skip-auth-check", action="store_true", help="skip the account status pre-check")
    ap.add_argument("--dry-run", action="store_true", help="print the command, do not submit")
    args = ap.parse_args()

    # build the CLI command
    cmd = ["generate", "create", args.model]
    if args.prompt:
        cmd += ["--prompt", args.prompt]
    for img in args.image:
        cmd += ["--image", img]
    if args.start_image:
        cmd += ["--start-image", args.start_image]
    if args.end_image:
        cmd += ["--end-image", args.end_image]
    params: dict[str, str] = {}
    for p in args.param:
        if "=" not in p:
            sys.exit(f"--param must be key=value, got: {p}")
        k, v = p.split("=", 1)
        params[k] = v
        cmd += [f"--{k}", v]
    cmd += ["--wait", "--wait-timeout", args.timeout, "--json"]

    if args.dry_run:
        print("higgsfield " + " ".join(
            (f'"{c}"' if " " in c else c) for c in cmd))
        return 0

    if not args.skip_auth_check:
        check_auth()

    media = {"image": args.image, "start_image": args.start_image, "end_image": args.end_image}
    print(f"[hf] {args.model} -> {args.out}  ({args.label or ''})", flush=True)

    # submit with retries — Higgsfield jobs can transiently fail server-side (status
    # 'failed' / empty result_url) even on benign prompts, so retry before giving up.
    attempts = args.retries + 1
    job = None
    last_err = ""
    last_proc: subprocess.CompletedProcess | None = None
    for i in range(attempts):
        proc = run_cli(cmd, timeout_s=timeout_to_seconds(args.timeout) + 120)
        last_proc = proc
        if proc.returncode != 0:
            last_err = f"rc {proc.returncode}: {(proc.stderr or proc.stdout or '').strip()[:200]}"
        else:
            try:
                job = pick_result(parse_json_array(proc.stdout))
                break
            except ValueError as e:
                last_err = str(e)
                if "NOT RETRYING" in last_err:
                    break  # content-filter reject — retrying is pointless
        if i < attempts - 1:
            print(f"[hf] attempt {i + 1}/{attempts} failed ({last_err}); retrying...", flush=True)
    if job is None:
        if last_proc is not None:
            sys.stderr.write(last_proc.stdout or "")
            sys.stderr.write(last_proc.stderr or "")
        sys.exit(f"[hf] generation failed after {attempts} attempt(s) for "
                 f"{args.label or args.model}: {last_err}")

    url = job["result_url"]
    size = download(url, args.out)
    print(f"[hf] downloaded {size} bytes")

    if args.log:
        append_log(args.log, {
            "label": args.label,
            "asset": rel(args.out),
            "model": args.model,
            "prompt": args.prompt,
            "media": {k: v for k, v in media.items() if v},
            "params": params,
            "job_id": job.get("id"),
            "result_url": url,
            "bytes": size,
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })

    print(str(args.out))  # last line: resolved path for callers
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
