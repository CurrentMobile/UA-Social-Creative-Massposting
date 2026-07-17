"""Generate one TTS line via the ElevenLabs API and save it as MP3.

Deterministic execution layer for interviewer/VO lines (street-interview formats:
the off-camera interviewer's turns are TTS'd, then ffmpeg-muxed onto muted B-roll).
Reads ELEVENLABS_API_KEY from the root .env. One call = one line, so file naming
stays consistent with the chunk ids.

Usage:
    python tools/tts_elevenlabs.py --text "What's the laziest way..." \
        --voice Liam --out assets/<app>/<video>/audio/interviewer-3.mp3
    python tools/tts_elevenlabs.py --list-voices          # name -> voice_id table

--voice accepts a voice name (resolved via /v1/voices) or a raw voice_id.
--style/--stability tune expressiveness (defaults suit an energetic street host).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
API = "https://api.elevenlabs.io/v1"


def load_key() -> str:
    p = PROJECT_ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ELEVENLABS_API_KEY") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("ELEVENLABS_API_KEY not found in .env")


def list_voices(key: str) -> list[dict]:
    r = requests.get(f"{API}/voices", headers={"xi-api-key": key}, timeout=30)
    r.raise_for_status()
    return r.json().get("voices", [])


def resolve_voice(key: str, name_or_id: str) -> str:
    if len(name_or_id) >= 20 and " " not in name_or_id:  # looks like a voice_id
        return name_or_id
    for v in list_voices(key):
        if v.get("name", "").lower() == name_or_id.lower():
            return v["voice_id"]
    sys.exit(f"voice '{name_or_id}' not found — run --list-voices")


def main() -> None:
    ap = argparse.ArgumentParser(description="One ElevenLabs TTS line -> MP3")
    ap.add_argument("--text")
    ap.add_argument("--voice", default="Liam", help="voice name or voice_id")
    ap.add_argument("--model-id", default="eleven_multilingual_v2")
    ap.add_argument("--stability", type=float, default=0.35)
    ap.add_argument("--similarity", type=float, default=0.75)
    ap.add_argument("--style", type=float, default=0.6)
    ap.add_argument("--speed", type=float, default=None, help="0.7-1.2 voice speed")
    ap.add_argument("--out")
    ap.add_argument("--list-voices", action="store_true")
    args = ap.parse_args()

    key = load_key()
    if args.list_voices:
        for v in list_voices(key):
            print(f"{v['voice_id']}  {v.get('name','')}  ({v.get('category','')})")
        return
    if not args.text or not args.out:
        sys.exit("--text and --out are required")

    voice_id = resolve_voice(key, args.voice)
    settings = {
        "stability": args.stability,
        "similarity_boost": args.similarity,
        "style": args.style,
        "use_speaker_boost": True,
    }
    if args.speed is not None:
        settings["speed"] = args.speed
    body = {"text": args.text, "model_id": args.model_id, "voice_settings": settings}
    r = requests.post(
        f"{API}/text-to-speech/{voice_id}?output_format=mp3_44100_128",
        headers={"xi-api-key": key, "content-type": "application/json"},
        data=json.dumps(body),
        timeout=120,
    )
    if r.status_code != 200:
        sys.exit(f"TTS failed {r.status_code}: {r.text[:500]}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(r.content)
    print(out)


if __name__ == "__main__":
    main()
