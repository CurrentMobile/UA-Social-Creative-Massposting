"""Scaffold app and video asset folders with manifests.

Creates the standardized asset tree (see assets/ASSETS.md) so every skill can locate
assets deterministically. Manifests are generated from assets/_templates/.

Usage:
    python tools/scaffold.py app <slug>
    python tools/scaffold.py video <app-slug> "<Video Title>"

Examples:
    python tools/scaffold.py app mode-earn
    python tools/scaffold.py video mode-earn "Music Tab Promo"
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS = PROJECT_ROOT / "assets"
TEMPLATES = ASSETS / "_templates"

# Known app display names; unknown slugs fall back to title-cased slug.
APP_NAMES = {
    "mode-earn": "Mode Earn",
    "applock": "AppLock",
    "ngl": "NGL",
    "gallery": "Gallery",
    "cleaner": "Cleaner",
    "trimbox": "Trimbox",
}

VIDEO_SUBDIRS = ["ai-videos", "ai-images", "audio", "scripts", "sops", "edit"]


def slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _gitkeep(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / ".gitkeep").touch()


def _fill(template_name: str, mapping: dict[str, str]) -> str:
    text = (TEMPLATES / template_name).read_text(encoding="utf-8")
    for k, v in mapping.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def scaffold_app(slug: str) -> None:
    slug = slugify(slug)
    name = APP_NAMES.get(slug, slug.replace("-", " ").title())
    app_dir = ASSETS / slug

    _gitkeep(app_dir / "brand")
    _gitkeep(app_dir / "cta")
    _gitkeep(ASSETS / "_shared" / "screen-recordings" / slug)

    manifest = app_dir / "manifest.md"
    if manifest.exists():
        print(f"app manifest already exists: {manifest} (left untouched)")
    else:
        _write(manifest, _fill("app-manifest.template.md",
                               {"APP_SLUG": slug, "APP_NAME": name}))
        print(f"created app: {app_dir}")
    print(f"  brand/ cta/ + _shared/screen-recordings/{slug}/ ready")


def scaffold_video(app_slug: str, title: str) -> None:
    app_slug = slugify(app_slug)
    app_dir = ASSETS / app_slug
    app_manifest = app_dir / "manifest.md"
    if not app_manifest.exists():
        sys.exit(f"app '{app_slug}' not scaffolded yet. Run: scaffold.py app {app_slug}")

    vslug = slugify(title)
    vdir = app_dir / vslug
    if (vdir / "manifest.md").exists():
        sys.exit(f"video already exists: {vdir}")

    for sub in VIDEO_SUBDIRS:
        _gitkeep(vdir / sub)

    _write(vdir / "manifest.md", _fill("video-manifest.template.md", {
        "APP_SLUG": app_slug,
        "VIDEO_TITLE": title,
        "VIDEO_SLUG": vslug,
        "DATE": date.today().isoformat(),
    }))
    print(f"created video: {vdir}")

    # append a row to the app manifest's video index
    marker = "<!-- scaffold.py appends rows here -->"
    text = app_manifest.read_text(encoding="utf-8")
    row = f"| [{vslug}]({vslug}/manifest.md) | scripting | tiktok,instagram | {title} |\n"
    if marker in text:
        text = text.replace(marker, row + marker)
    else:
        text = text.rstrip() + "\n" + row
    app_manifest.write_text(text, encoding="utf-8")
    print(f"  indexed in {app_manifest.name}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Scaffold app / video asset folders")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("app", help="create an app skeleton")
    a.add_argument("slug")

    v = sub.add_parser("video", help="create a video folder under an app")
    v.add_argument("app")
    v.add_argument("title")

    args = ap.parse_args()
    if not TEMPLATES.exists():
        sys.exit(f"templates dir missing: {TEMPLATES}")

    if args.cmd == "app":
        scaffold_app(args.slug)
    elif args.cmd == "video":
        scaffold_video(args.app, args.title)


if __name__ == "__main__":
    main()
