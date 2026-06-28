"""Step 3 — Winning Video Breakdown. Take the top winners from Step 2, download the
videos, and break each one down into structured creative anatomy with Gemini
multimodal (the LLM watches the clip; this tool handles the deterministic IO).

Organic TikTok/Instagram winners are analyzed from the actual video. Facebook ads
(no video metrics, often image creative) are analyzed text-only from the ad copy.

Reads GEMINI_API_KEY from root .env. Nothing is spent under --dry-run.

Usage:
    .venv\\Scripts\\python.exe tools/breakdown_videos.py --app mode-earn --dry-run
    .venv\\Scripts\\python.exe tools/breakdown_videos.py --app mode-earn --top 3      # small first
    .venv\\Scripts\\python.exe tools/breakdown_videos.py --app mode-earn --top 12

Input:  assets/<app>/competitor-research/<date>/winners.json  (from Step 2)
Output: assets/<app>/competitor-research/<date>/breakdowns.json
        (one breakdown per analyzed item — the agent then synthesizes breakdown.md)
Videos download to .tmp/<app>/competitor-research/<date>/videos/ (disposable).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import requests

import _research_lib as rl

GEMINI_BASE = "https://generativelanguage.googleapis.com"
DEFAULT_MODEL = "gemini-2.5-flash"

# Brand context so the breakdown's "transferable angle" is grounded in Mode Earn.
BRAND_CONTEXT = (
    "Mode Earn is a B2C rewards app (Android / Google Play only) that rewards users for everyday "
    "phone activities — listening to music, playing games, charging the phone, reading news, taking "
    "surveys — redeemable as gift cards (Amazon, Best Buy) or PayPal. Voice: friendly, UGC, 'friend "
    "sharing a hack', never salesy. Say 'reward' not 'pay', 'gift cards/real rewards' not 'cash'. "
    "Its differentiators vs competitors (Sweatcoin, Mistplay, Swagbucks) are earning via music, "
    "charging, and reading news. Scripts follow the beats HOOK / PROBLEM / SOLUTION / HOW IT WORKS / "
    "RESULT / CTA."
)

# Gemini structured-output schema (OpenAPI subset).
BREAKDOWN_SCHEMA = {
    "type": "object",
    "properties": {
        "hook_text": {"type": "string", "description": "The spoken/on-screen opening line (first ~3s)."},
        "hook_type": {"type": "string", "description": "e.g. problem-callout, outcome-first, direct-challenge, story, skeptic."},
        "opening_visual": {"type": "string"},
        "beats": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "label": {"type": "string", "description": "HOOK/PROBLEM/SOLUTION/HOW IT WORKS/RESULT/CTA or closest."},
                    "timestamp": {"type": "string"},
                    "what_happens": {"type": "string"},
                },
                "required": ["label", "what_happens"],
            },
        },
        "on_screen_text": {"type": "array", "items": {"type": "string"}},
        "cta": {"type": "string"},
        "pacing": {"type": "string", "description": "cut frequency, energy, avg shot length."},
        "visual_style": {"type": "string", "description": "shot types, setting, captions, b-roll, graphics."},
        "audio_note": {"type": "string", "description": "music/voice/trending sound."},
        "why_it_works": {"type": "string"},
        "transferable_angle_for_mode_earn": {"type": "string", "description": "How to adapt this for Mode Earn, on-brand."},
    },
    "required": ["hook_text", "hook_type", "beats", "cta", "why_it_works", "transferable_angle_for_mode_earn"],
}

VIDEO_PROMPT = (
    "You are a short-form UGC ad strategist. Watch this video and break down its creative anatomy. "
    "Identify the hook and hook type, the opening visual, the beat-by-beat structure (map beats to "
    "HOOK/PROBLEM/SOLUTION/HOW IT WORKS/RESULT/CTA where possible), on-screen text/stickers, the CTA, "
    "pacing, visual style, and audio. Explain why it works, then propose how to adapt the winning "
    "elements into an on-brand idea for the app below. Be concrete and specific.\n\n"
    f"APP CONTEXT: {BRAND_CONTEXT}"
)

TEXT_PROMPT = (
    "You are a short-form UGC ad strategist. Below is the ad copy from a competitor's Facebook ad "
    "(no video available). Infer the creative anatomy from the copy: hook, hook type, likely beat "
    "structure, the CTA, why this messaging works, and how to adapt it on-brand for the app below. "
    "Leave visual fields brief since you only have text.\n\n"
    f"APP CONTEXT: {BRAND_CONTEXT}\n\nAD COPY:\n"
)


# --------------------------------------------------------------------------- #
# Gemini helpers
# --------------------------------------------------------------------------- #
def gemini_list_models(key: str) -> list[str]:
    try:
        r = requests.get(f"{GEMINI_BASE}/v1beta/models", params={"key": key}, timeout=20)
        r.raise_for_status()
        return [
            m["name"].split("/")[-1]
            for m in r.json().get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
    except Exception:  # noqa: BLE001
        return []


def gemini_upload_file(path: Path, key: str, mime: str = "video/mp4", log=print) -> dict:
    num_bytes = path.stat().st_size
    start = requests.post(
        f"{GEMINI_BASE}/upload/v1beta/files",
        params={"key": key},
        headers={
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(num_bytes),
            "X-Goog-Upload-Header-Content-Type": mime,
            "Content-Type": "application/json",
        },
        json={"file": {"display_name": path.name}},
        timeout=60,
    )
    start.raise_for_status()
    upload_url = start.headers.get("X-Goog-Upload-URL")
    if not upload_url:
        raise RuntimeError("Gemini Files API returned no upload URL.")
    up = requests.post(
        upload_url,
        headers={
            "X-Goog-Upload-Command": "upload, finalize",
            "X-Goog-Upload-Offset": "0",
            "Content-Length": str(num_bytes),
        },
        data=path.read_bytes(),
        timeout=300,
    )
    up.raise_for_status()
    return up.json().get("file", {})


def gemini_wait_active(file_obj: dict, key: str, timeout: int = 180) -> str:
    name = file_obj.get("name")           # "files/abc123"
    state = file_obj.get("state")
    uri = file_obj.get("uri")
    deadline = time.monotonic() + timeout
    while state != "ACTIVE":
        if state == "FAILED":
            raise RuntimeError("Gemini file processing FAILED.")
        if time.monotonic() > deadline:
            raise TimeoutError("Gemini file did not become ACTIVE in time.")
        time.sleep(3)
        r = requests.get(f"{GEMINI_BASE}/v1beta/{name}", params={"key": key}, timeout=30)
        r.raise_for_status()
        fo = r.json()
        state, uri = fo.get("state"), fo.get("uri", uri)
    return uri


def gemini_generate(parts: list[dict], model: str, key: str, timeout: int = 180) -> dict:
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseMimeType": "application/json", "responseSchema": BREAKDOWN_SCHEMA},
    }
    r = requests.post(
        f"{GEMINI_BASE}/v1beta/models/{model}:generateContent",
        params={"key": key},
        json=body,
        timeout=timeout,
    )
    if r.status_code != 200:
        raise RuntimeError(f"Gemini generateContent HTTP {r.status_code}: {r.text[:300]}")
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(f"Gemini returned no content: {json.dumps(data)[:300]}")
    return json.loads(text)


def breakdown_video(video_path: Path, model: str, key: str, log=print) -> dict:
    fobj = gemini_upload_file(video_path, key, mime="video/mp4", log=log)
    uri = gemini_wait_active(fobj, key)
    parts = [
        {"fileData": {"mimeType": "video/mp4", "fileUri": uri}},
        {"text": VIDEO_PROMPT},
    ]
    return gemini_generate(parts, model, key)


def breakdown_text(ad_copy: str, model: str, key: str) -> dict:
    parts = [{"text": TEXT_PROMPT + (ad_copy or "(no copy captured)")}]
    return gemini_generate(parts, model, key)


# --------------------------------------------------------------------------- #
def select_targets(winners: list[dict], top: int, ads: int, no_ads: bool):
    organic = [w for w in winners if w["platform"] in ("tiktok", "instagram") and w.get("video_url")]
    organic.sort(key=lambda w: (w.get("rank", 999), w["platform"]))  # interleave rank-1s first
    organic = organic[:top]
    ad_recs = [] if no_ads else [w for w in winners if w["platform"] == "facebook-ads"][:ads]
    return organic, ad_recs


def main() -> None:
    ap = argparse.ArgumentParser(description="Step 3 — break down winning videos with Gemini")
    ap.add_argument("--app", default="mode-earn")
    ap.add_argument("--date", default=None, help="research date folder (default: today)")
    ap.add_argument("--winners", type=Path, default=None, help="path to winners.json (default: today's)")
    ap.add_argument("--top", type=int, default=12, help="organic videos to download + analyze (default 12)")
    ap.add_argument("--ads", type=int, default=5, help="Facebook ads to analyze text-only (default 5)")
    ap.add_argument("--no-ads", action="store_true", help="skip Facebook ads entirely")
    ap.add_argument("--model", default=DEFAULT_MODEL, help=f"Gemini model (default {DEFAULT_MODEL})")
    ap.add_argument("--timeout", type=int, default=180, help="seconds per Gemini call / upload")
    ap.add_argument("--dry-run", action="store_true", help="list targets; download/analyze nothing")
    args = ap.parse_args()

    date = args.date or rl.today_str()
    persistent, tmp = rl.research_dirs(args.app, date)
    winners_path = args.winners or (persistent / "winners.json")
    payload = rl.read_json(winners_path)
    if not payload or "winners" not in payload:
        sys.exit(f"No winners.json at {rl.rel_to_root(winners_path)} — run Step 2 (scrape_competitors.py) first.")

    winners = payload["winners"]
    organic, ad_recs = select_targets(winners, args.top, args.ads, args.no_ads)

    print("=" * 64)
    print(f"STEP 3 — WINNING VIDEO BREAKDOWN  ({args.app}, {date})")
    print(f"winners file : {rl.rel_to_root(winners_path)}")
    print(f"organic videos to analyze : {len(organic)}  (--top {args.top})")
    print(f"facebook ads to analyze   : {len(ad_recs)}  (--ads {args.ads}{', SKIPPED' if args.no_ads else ''})")
    print(f"model : {args.model}")
    print("=" * 64)

    if args.dry_run:
        for w in organic:
            print(f"  [video] {w['platform']} r{w['rank']} {w.get('author')} — {(w.get('hook_text') or '')[:60]}")
        for w in ad_recs:
            print(f"  [ad]    fb r{w['rank']} {w.get('author')} — {(w.get('hook_text') or '')[:60]}")
        print(f"\n[dry-run] would analyze {len(organic) + len(ad_recs)} item(s) with {args.model}. No credits spent.")
        print(f"[dry-run] would write -> {rl.rel_to_root(persistent / 'breakdowns.json')}")
        return

    env = rl.load_env()
    key = env.get("GEMINI_API_KEY", "")
    if not key:
        sys.exit("GEMINI_API_KEY not found in .env")
    models = gemini_list_models(key)
    if models and args.model not in models:
        sys.exit(f"Model '{args.model}' not available on this key. Try one of: {', '.join(models[:12])}")
    print(f"Gemini key OK ({rl.mask(key)}); model {args.model} available.\n")

    video_dir = tmp / "videos"
    items: list[dict] = []

    # --- organic videos: download then video-analyze --- #
    for w in organic:
        tag = f"{w['rank']:02d}_{w['platform']}"
        print(f"-> {tag} {w.get('author')}")
        vid = rl.download_video(w["video_url"], video_dir / tag, direct=False)
        if not vid:
            print("   download failed; skipping.")
            continue
        try:
            bd = breakdown_video(vid, args.model, key)
        except Exception as e:  # noqa: BLE001
            print(f"   breakdown failed: {str(e)[:200]}")
            continue
        items.append({**_meta(w), "video_file": rl.rel_to_root(vid), "breakdown": bd})
        print(f"   ✓ {bd.get('hook_type', '?')} hook")

    # --- facebook ads: text-only --- #
    for w in ad_recs:
        print(f"-> ad r{w['rank']} {w.get('author')}")
        try:
            bd = breakdown_text(w.get("caption") or "", args.model, key)
        except Exception as e:  # noqa: BLE001
            print(f"   breakdown failed: {str(e)[:200]}")
            continue
        items.append({**_meta(w), "video_file": None, "breakdown": bd})
        print("   ✓ text breakdown")

    if not items:
        print("\nNo breakdowns produced (downloads or Gemini calls all failed). See notes above.")
        sys.exit(1)

    out = {
        "app": args.app,
        "date": date,
        "generated_at": rl.now_iso(),
        "model": args.model,
        "source_winners": rl.rel_to_root(winners_path),
        "count": len(items),
        "items": items,
    }
    out_path = persistent / "breakdowns.json"
    rl.write_json(out_path, out)
    print(f"\nWrote {len(items)} breakdown(s).")
    print("Next: the agent synthesizes breakdown.md (patterns + whitespace angles) from this file.")
    print(rl.rel_to_root(out_path))  # last line = machine-readable path


def _meta(w: dict) -> dict:
    return {
        "rank": w.get("rank"),
        "platform": w.get("platform"),
        "url": w.get("url"),
        "author": w.get("author"),
        "views": w.get("views"),
        "likes": w.get("likes"),
        "engagement_rate": w.get("engagement_rate"),
        "is_ad": w.get("is_ad", False),
    }


if __name__ == "__main__":
    main()
