"""Download royalty-free background music into assets/music/ and log it.

Pulls audio via yt-dlp from a YouTube URL / playlist, or from a search query
(default: creator-cleared "No Copyright Music" sources). Each track is logged in
assets/music/library.json with title, duration, source URL, your tags, and a
license note to confirm before commercial use.

Usage:
    python tools/fetch_music.py "<YouTube URL>"
    python tools/fetch_music.py "lofi chill no copyright" --count 3 --tags lofi,calm
    python tools/fetch_music.py "<playlist URL>"

Then mix it under your edit with tools/mix_audio.py.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import _media_lib as ml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "assets" / "music"
DEFAULT_LICENSE_NOTE = (
    "Verify license before commercial use. Prefer YouTube Audio Library / "
    "Creative-Commons / royalty-free 'No Copyright Music' sources."
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Download royalty-free background music")
    ap.add_argument("query", help="YouTube URL, playlist URL, or search terms")
    ap.add_argument("--count", type=int, default=1, help="results to fetch for a search query")
    ap.add_argument("--max-duration", type=int, default=600,
                    help="skip results longer than N seconds (default 600 — guards against multi-hour tracks)")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--tags", default="", help="comma-separated mood/genre tags")
    ap.add_argument("--format", default="mp3", help="audio format (mp3, m4a, wav, ...)")
    ap.add_argument("--license-note", default=DEFAULT_LICENSE_NOTE)
    args = ap.parse_args()

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    print(f"Fetching music -> {args.out_dir}")
    info_jsons = ml.download_audio(
        args.query, args.out_dir, count=args.count, audio_format=args.format,
        max_duration=args.max_duration,
    )
    if not info_jsons:
        print("No new tracks downloaded.")
        return

    new = ml.update_library(
        info_jsons, "music", tags, args.license_note,
        lib_path=args.out_dir / "library.json",
    )
    print(f"\nAdded {len(new)} track(s) to {args.out_dir / 'library.json'}:")
    for e in new:
        dur = f"{e['duration_s']}s" if e.get("duration_s") else "?"
        print(f"  - {e['title']} ({dur})  {e['file']}")


if __name__ == "__main__":
    main()
