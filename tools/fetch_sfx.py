"""Download royalty-free sound effects into assets/sfx/ and log them.

Same engine as fetch_music.py but tuned for short clips: defaults to a 60s max
duration filter so searches return actual effects, not long videos. Each effect
is logged in assets/sfx/library.json.

Usage:
    python tools/fetch_sfx.py "whoosh transition sound effect" --count 3 --tags whoosh,transition
    python tools/fetch_sfx.py "<YouTube URL>"

Then place effects at timestamps with tools/mix_audio.py --sfx file@time ...
"""

from __future__ import annotations

import argparse
from pathlib import Path

import _media_lib as ml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SFX_ROOT = PROJECT_ROOT / "assets" / "sfx"
DEFAULT_OUT = SFX_ROOT / "downloads"          # yt-dlp fallback cache
LIB_PATH = SFX_ROOT / "library.json"          # unified catalog (curated + downloads)
DEFAULT_LICENSE_NOTE = (
    "Verify license before commercial use. Prefer CC0 / royalty-free sound-effect sources."
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Download royalty-free sound effects")
    ap.add_argument("query", help="YouTube URL or search terms")
    ap.add_argument("--count", type=int, default=1, help="results to fetch for a search query")
    ap.add_argument("--max-duration", type=int, default=60, help="skip results longer than N seconds")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--tags", default="", help="comma-separated tags")
    ap.add_argument("--format", default="mp3", help="audio format (mp3, m4a, wav, ...)")
    ap.add_argument("--license-note", default=DEFAULT_LICENSE_NOTE)
    args = ap.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    print(f"Fetching SFX -> {args.out_dir}")
    info_jsons = ml.download_audio(
        args.query,
        args.out_dir,
        count=args.count,
        audio_format=args.format,
        max_duration=args.max_duration,
    )
    if not info_jsons:
        print("No new effects downloaded.")
        return

    new = ml.update_library(
        info_jsons, "sfx", tags, args.license_note,
        lib_path=LIB_PATH, source="download",
    )
    print(f"\nAdded {len(new)} effect(s) to {LIB_PATH}:")
    for e in new:
        dur = f"{e['duration_s']}s" if e.get("duration_s") else "?"
        print(f"  - {e['title']} ({dur})  {e['file']}")


if __name__ == "__main__":
    main()
