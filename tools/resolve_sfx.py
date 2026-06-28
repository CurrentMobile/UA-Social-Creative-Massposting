"""Resolve a sound effect: curated local library FIRST, yt-dlp fallback if not found.

The edit workflow calls this before mix_audio.py. It (1) indexes any user-dropped files
in assets/sfx/curated/ into the catalog, (2) searches the catalog (curated preferred, then
downloads) for the query terms, and (3) only if nothing matches, downloads via yt-dlp into
assets/sfx/downloads/.

The resolved file path is printed as the LAST stdout line (diagnostics are prefixed with
[resolve]) so callers can capture it.

Usage:
    python tools/resolve_sfx.py "whoosh"
    python tools/resolve_sfx.py "ui pop click" --no-download    # local-only
    python tools/resolve_sfx.py "swoosh transition" --max-duration 30
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import _media_lib as ml

SFX_ROOT = ml.PROJECT_ROOT / "assets" / "sfx"
CURATED = SFX_ROOT / "curated"
DOWNLOADS = SFX_ROOT / "downloads"
LIB_PATH = SFX_ROOT / "library.json"
# the user's primary, prioritized curated library
PRIMARY_SUBDIR = "sound effects and documentation"


def _score(entry: dict, tokens: list[str]) -> int:
    """Rank an SFX against the query. Whole-word matches only (so 'ting' does NOT match
    'editing'); ALL tokens must match somewhere or the entry is rejected (-1). The user's
    'Sound effects and documentation' library is preferred."""
    if not tokens:
        return -1
    title = str(entry.get("title") or "").lower()
    fil = str(entry.get("file") or "").lower()
    tags = " ".join(entry.get("tags") or []).lower()
    title_words = re.findall(r"[a-z0-9]+", title)
    file_words = re.findall(r"[a-z0-9]+", Path(fil).stem)
    score = 0
    for t in tokens:
        if t in title_words:
            score += 3
        elif any(w.startswith(t) for w in title_words):
            score += 2
        elif re.search(rf"\b{re.escape(t)}\b", tags):
            score += 2
        elif t in file_words or any(w.startswith(t) for w in file_words):
            score += 1
        else:
            return -1  # a query token matched nothing → not a real hit
    if title == " ".join(tokens):
        score += 5
    if PRIMARY_SUBDIR in fil:
        score += 2  # prefer the user's primary curated library
    return score


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve an SFX local-first, yt-dlp fallback")
    ap.add_argument("query", help="keyword(s) describing the effect")
    ap.add_argument("--no-download", action="store_true", help="local library only; no yt-dlp fallback")
    ap.add_argument("--max-duration", type=int, default=60, help="max duration for downloaded fallback")
    args = ap.parse_args()

    # make sure user-dropped curated files AND any uncatalogued downloads are indexed.
    # Prefer rich metadata for downloads that still have their .info.json.
    added = ml.index_local_dir(CURATED, "sfx", LIB_PATH, source="curated")
    dl_info = sorted(DOWNLOADS.glob("*.info.json")) if DOWNLOADS.exists() else []
    if dl_info:
        ml.update_library(dl_info, "sfx", [],
                          "Verify license before commercial use.",
                          lib_path=LIB_PATH, source="download")
    ml.index_local_dir(DOWNLOADS, "sfx", LIB_PATH, source="download")
    if added:
        print(f"[resolve] indexed {len(added)} new curated effect(s)")

    tokens = args.query.lower().split()
    library = ml.load_library(LIB_PATH)

    def best(entries: list[dict]) -> tuple[int, dict] | None:
        scored = [(_score(e, tokens), e) for e in entries]
        scored = [(s, e) for s, e in scored if s > 0]
        return max(scored, key=lambda x: x[0]) if scored else None

    curated = best([e for e in library if e.get("source") == "curated"])
    download = best([e for e in library if e.get("source") != "curated"])

    hit = curated or download
    if hit:
        kind = "curated" if curated else "download"
        path = ml.PROJECT_ROOT / hit[1]["file"]
        print(f"[resolve] matched {kind} (score {hit[0]}): {hit[1].get('title')}")
        print(str(path))
        return 0

    if args.no_download:
        print(f"[resolve] no local match for '{args.query}' (--no-download set)", file=sys.stderr)
        return 1

    print(f"[resolve] no local match for '{args.query}' — downloading via yt-dlp...")
    info_jsons = ml.download_audio(args.query, DOWNLOADS, count=1, max_duration=args.max_duration)
    new = ml.update_library(
        info_jsons, "sfx", tokens,
        "Verify license before commercial use. Prefer CC0 / royalty-free sources.",
        lib_path=LIB_PATH, source="download",
    )
    if new:
        path = ml.PROJECT_ROOT / new[0]["file"]
        print(f"[resolve] downloaded: {new[0].get('title')}")
        print(str(path))
        return 0

    print(f"[resolve] could not resolve '{args.query}'", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
