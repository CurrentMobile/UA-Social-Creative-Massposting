"""Manifest-driven bridge between local media and the Google Shared Drive.

Heavy per-video media (ai-videos, ai-images, edit, outputs) is gitignored and lives on
G:\\Shared drives\\Mode AI Creative Loop. This tool moves it deterministically:

  pull <app>/<video>   copy missing referenced media  G: -> local
  push <app>/<video>   mirror local media + finals    local -> G:  (hash/size verified)
  pull --all           every tracked video's media
  --dry-run            list what would copy; move nothing

Replaces ad-hoc `robocopy` calls and interprets robocopy exit codes correctly
(0-7 = success, >=8 = failure — the bare-robocopy gotcha).

Usage:
    .venv\\Scripts\\python.exe tools\\sync_assets.py pull mode-earn/backinthe-80s
    .venv\\Scripts\\python.exe tools\\sync_assets.py push mode-earn/backinthe-80s
    .venv\\Scripts\\python.exe tools\\sync_assets.py pull --all --dry-run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS = PROJECT_ROOT / "assets"
OUTPUTS = PROJECT_ROOT / "outputs"
DRIVE = Path(r"G:\Shared drives\Mode AI Creative Loop")
DRIVE_VIDEOS = DRIVE / "Videos"
# per-video media subdirs that are gitignored and live on the drive
MEDIA_SUBDIRS = ["ai-videos", "ai-images", "audio", "edit", "screen-recordings"]


def robocopy(src: Path, dst: Path, dry: bool) -> tuple[bool, str]:
    """robocopy /E /XO; returns (ok, summary). Exit 0-7 = success."""
    if not src.exists():
        return True, f"(source absent, skip) {src}"
    args = ["robocopy", str(src), str(dst), "/E", "/XO", "/NFL", "/NDL", "/NJH", "/NJS", "/NP", "/R:1", "/W:1"]
    if dry:
        args.append("/L")  # list only
    r = subprocess.run(args, capture_output=True, text=True)
    ok = r.returncode < 8
    tail = (r.stdout or r.stderr).strip().splitlines()[-1:] or [""]
    return ok, f"rc={r.returncode} {'OK' if ok else 'FAIL'} {src.name} -> {dst}  {tail[0].strip()}"


def video_dirs(app: str | None = None, video: str | None = None) -> list[Path]:
    out = []
    apps = [ASSETS / app] if app else [d for d in ASSETS.iterdir()
                                       if d.is_dir() and not d.name.startswith(("_", "."))
                                       and (d / "manifest.md").exists()]
    for a in apps:
        if not a.exists():
            continue
        if video:
            vd = a / video
            if (vd / "manifest.md").exists():
                out.append(vd)
        else:
            out += [d for d in a.iterdir() if d.is_dir() and (d / "manifest.md").exists()]
    return out


def rel(p: Path) -> str:
    try:
        return p.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(p)


def cmd_pull(target: str | None, all_: bool, dry: bool) -> int:
    if not DRIVE.exists():
        sys.exit(f"shared drive not mounted: {DRIVE} — install Google Drive for desktop.")
    app, video = _split(target) if target else (None, None)
    vids = video_dirs(app, video) if (target or all_) else []
    if not vids:
        sys.exit("nothing to pull — pass <app>/<video> or --all (and check the app has manifests).")
    okall = True
    for vd in vids:
        app_name, vname = vd.parent.name, vd.name
        for sub in MEDIA_SUBDIRS:
            src = DRIVE_VIDEOS / app_name / vname / sub
            ok, msg = robocopy(src, vd / sub, dry)
            okall &= ok
            print(f"  {msg}")
    print(f"\n{'[dry-run] ' if dry else ''}pull {'ok' if okall else 'had failures'} "
          f"({len(vids)} video(s)).")
    return 0 if okall else 1


def cmd_push(target: str | None, dry: bool) -> int:
    if not DRIVE.exists():
        sys.exit(f"shared drive not mounted: {DRIVE} — install Google Drive for desktop.")
    app, video = _split(target) if target else (None, None)
    vids = video_dirs(app, video)
    okall = True
    for vd in vids:
        app_name, vname = vd.parent.name, vd.name
        for sub in MEDIA_SUBDIRS:
            ok, msg = robocopy(vd / sub, DRIVE_VIDEOS / app_name / vname / sub, dry)
            okall &= ok
            print(f"  {msg}")
    # finals in outputs/
    if OUTPUTS.exists():
        ok, msg = robocopy(OUTPUTS, DRIVE_VIDEOS, dry)
        okall &= ok
        print(f"  {msg}")
    print(f"\n{'[dry-run] ' if dry else ''}push {'ok' if okall else 'had failures'} "
          f"({len(vids)} video(s) + outputs).")
    return 0 if okall else 1


def _split(target: str) -> tuple[str, str | None]:
    parts = target.replace("\\", "/").strip("/").split("/")
    return (parts[0], parts[1] if len(parts) > 1 else None)


def main() -> int:
    ap = argparse.ArgumentParser(description="Manifest-driven G:-drive media sync")
    ap.add_argument("action", choices=["pull", "push"])
    ap.add_argument("target", nargs="?", help="<app> or <app>/<video>")
    ap.add_argument("--all", action="store_true", help="all tracked videos (pull)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.action == "pull":
        return cmd_pull(args.target, args.all, args.dry_run)
    return cmd_push(args.target, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
