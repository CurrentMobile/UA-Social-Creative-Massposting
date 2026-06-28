"""Shared helpers for downloading royalty-free audio with yt-dlp and tracking it
in a per-folder library.json.

Used by fetch_music.py and fetch_sfx.py. Not a CLI itself.

The YouTube Audio Library proper requires a logged-in session, so these tools work
from explicit URLs / playlists you supply, or from YouTube search queries — pointed
at creator-cleared "No Copyright Music" / royalty-free sources. The license is NOT
auto-verified: each library.json entry carries a `license_note` you should confirm
before publishing commercially.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

AUDIO_EXTS = {".mp3", ".m4a", ".opus", ".wav", ".flac", ".ogg", ".aac"}

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def rel_to_root(path: Path, root: Path | None = None) -> str:
    """Path relative to the project root (posix), or absolute if outside it."""
    root = root or PROJECT_ROOT
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path.resolve())


def load_library(lib_path: Path) -> list[dict]:
    if lib_path.exists():
        try:
            return json.loads(lib_path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return []
    return []


def save_library(lib_path: Path, library: list[dict]) -> None:
    lib_path.parent.mkdir(parents=True, exist_ok=True)
    lib_path.write_text(json.dumps(library, indent=2), encoding="utf-8")


def find_ytdlp() -> str | None:
    """Resolve yt-dlp, preferring the one in this interpreter's venv Scripts dir
    (a real .exe) over a PATH shim, then falling back to PATH."""
    scripts = Path(sys.executable).parent
    for name in ("yt-dlp.exe", "yt-dlp"):
        cand = scripts / name
        if cand.exists():
            return str(cand)
    return shutil.which("yt-dlp")


def require_ytdlp() -> str:
    path = find_ytdlp()
    if not path:
        sys.exit(
            "yt-dlp not found. Install it into the project venv:\n"
            "  uv pip install --python .venv\\Scripts\\python.exe yt-dlp"
        )
    return path


def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")


def download_audio(
    query_or_url: str,
    out_dir: Path,
    count: int = 1,
    audio_format: str = "mp3",
    max_duration: int | None = None,
    search_provider: str = "ytsearch",
) -> list[Path]:
    """Download audio into out_dir. Returns paths to newly written .info.json files.

    For a URL, downloads it directly. Otherwise runs a search for `count` results.
    """
    ytdlp = require_ytdlp()
    out_dir.mkdir(parents=True, exist_ok=True)

    target = query_or_url if is_url(query_or_url) else f"{search_provider}{count}:{query_or_url}"

    before = {p for p in out_dir.glob("*.info.json")}

    cmd = [
        ytdlp,
        "-x",
        "--audio-format", audio_format,
        "--audio-quality", "0",
        "--write-info-json",
        "--no-write-playlist-metafiles",  # don't emit a playlist-level .info.json
        "--no-playlist" if is_url(query_or_url) and "list=" not in query_or_url else "--yes-playlist",
        "--restrict-filenames",
        "-o", str(out_dir / "%(title)s [%(id)s].%(ext)s"),
    ]
    if max_duration:
        cmd += ["--match-filter", f"duration < {max_duration}"]
    cmd.append(target)

    print(f"  yt-dlp: {target}", flush=True)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  yt-dlp exited {result.returncode} (some items may still have downloaded)")

    after = {p for p in out_dir.glob("*.info.json")}
    return sorted(after - before)


def _audio_for_info(info_json: Path) -> Path | None:
    stem = info_json.name[: -len(".info.json")]
    for ext in AUDIO_EXTS:
        cand = info_json.with_name(stem + ext)
        if cand.exists():
            return cand
    # fall back: any audio file sharing the stem prefix
    for p in info_json.parent.iterdir():
        if p.suffix.lower() in AUDIO_EXTS and p.stem == stem:
            return p
    return None


def update_library(
    info_jsons: list[Path],
    kind: str,
    tags: list[str],
    license_note: str,
    lib_path: Path,
    source: str = "download",
    rel_root: Path | None = None,
) -> list[dict]:
    """Merge new downloads into the catalog at lib_path. Returns the new entries.

    Asset `file` paths are stored relative to the project root so they resolve no
    matter how the library/download dirs are nested.
    """
    library = load_library(lib_path)
    known_ids = {e.get("id") for e in library}
    known_files = {e.get("file") for e in library}
    new_entries: list[dict] = []

    for ij in info_jsons:
        try:
            info = json.loads(ij.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        # skip playlist/search wrappers and any entry without an actual audio file
        if info.get("_type") == "playlist":
            continue
        audio = _audio_for_info(ij)
        if audio is None:
            continue
        rel = rel_to_root(audio, rel_root)
        entry = {
            "id": info.get("id"),
            "kind": kind,
            "source": source,
            "title": info.get("title"),
            "uploader": info.get("uploader"),
            "duration_s": info.get("duration"),
            "source_url": info.get("webpage_url"),
            "file": rel,
            "tags": tags,
            "license_note": license_note,
            "added": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        if entry["id"] in known_ids or rel in known_files:
            continue
        library.append(entry)
        new_entries.append(entry)

    save_library(lib_path, library)
    return new_entries


def index_local_dir(
    directory: Path,
    kind: str,
    lib_path: Path,
    tags: list[str] | None = None,
    license_note: str = "User-curated local asset.",
    rel_root: Path | None = None,
    source: str = "curated",
) -> list[dict]:
    """Add catalog entries for audio files in `directory` that aren't already tracked
    (e.g. user-dropped curated SFX with no .info.json). Dedupes by relative file path."""
    if not directory.exists():
        return []
    library = load_library(lib_path)
    known_files = {e.get("file") for e in library}
    new_entries: list[dict] = []

    for p in sorted(directory.rglob("*")):   # recurse subfolders (e.g. curated/Sound effects and documentation/)
        if p.is_dir() or p.suffix.lower() not in AUDIO_EXTS:
            continue
        rel = rel_to_root(p, rel_root)
        if rel in known_files:
            continue
        entry = {
            "id": f"{source}:{p.stem}",
            "kind": kind,
            "source": source,
            "title": p.stem,
            "uploader": None,
            "duration_s": None,
            "source_url": None,
            "file": rel,
            "tags": tags or [],
            "license_note": license_note,
            "added": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        library.append(entry)
        new_entries.append(entry)

    save_library(lib_path, library)
    return new_entries
