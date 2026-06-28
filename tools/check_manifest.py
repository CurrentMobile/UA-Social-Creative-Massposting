"""Validate that asset paths referenced in a manifest.md actually exist on disk.

Keeps the "single source of truth" honest by flagging drift (renamed/missing/extra files).
Heuristic: scans front-matter values, markdown-table first columns, and inline-code spans
for path-like tokens, then checks each one.

Usage:
    python tools/check_manifest.py assets/mode-earn
    python tools/check_manifest.py assets/mode-earn/music-tab-promo
    python tools/check_manifest.py assets/mode-earn/music-tab-promo/manifest.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CODE_SPAN = re.compile(r"`([^`]+)`")
TABLE_CELL = re.compile(r"^\|\s*([^|]+?)\s*\|")
FRONTMATTER_KV = re.compile(r"^(\w+):\s*(.+)$")


def looks_like_path(tok: str) -> bool:
    tok = tok.strip()
    if not tok or tok.startswith("{{") or tok.startswith("#"):
        return False
    if "<" in tok or ">" in tok:           # template placeholders like <file>.mp4
        return False
    if " " in tok.split("/")[0]:
        return False
    # infra / doc references, not video assets
    if tok.startswith(("tools/", "workflows/", ".tmp/", ".venv/", "http://", "https://", "//")):
        return False
    if "/" not in tok and not tok.endswith(("/", ".md", ".mp4", ".mov", ".png", ".jpg", ".mp3", ".wav", ".json")):
        return False
    return True


def extract_candidates(text: str) -> set[str]:
    cands: set[str] = set()
    in_fm = False
    fm_bounds = 0
    for line in text.splitlines():
        if line.strip() == "---":
            fm_bounds += 1
            in_fm = fm_bounds == 1
            continue
        if in_fm:
            m = FRONTMATTER_KV.match(line.strip())
            if m and looks_like_path(m.group(2)):
                cands.add(m.group(2).strip())
            continue
        for m in CODE_SPAN.finditer(line):
            if looks_like_path(m.group(1)):
                cands.add(m.group(1).strip())
        cell = TABLE_CELL.match(line)
        if cell:
            val = cell.group(1)
            # strip markdown link syntax [txt](target)
            link = re.match(r"\[.*?\]\((.+?)\)", val)
            val = link.group(1) if link else val
            if looks_like_path(val):
                cands.add(val.strip())
    return cands


def resolve(cand: str, manifest_dir: Path) -> Path:
    if cand.startswith(("assets/", "outputs/")):
        return PROJECT_ROOT / cand
    return manifest_dir / cand


def _under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def check_manifest(manifest: Path) -> int:
    text = manifest.read_text(encoding="utf-8")
    cands = sorted(extract_candidates(text))
    missing = 0
    print(f"\n{manifest.relative_to(PROJECT_ROOT)}")
    reported = False
    for c in cands:
        p = resolve(c, manifest.parent)
        under_assets = _under(p, PROJECT_ROOT / "assets")
        under_outputs = _under(p, PROJECT_ROOT / "outputs")
        if not (under_assets or under_outputs):
            continue  # skip non-asset references
        reported = True
        if p.exists():
            print(f"  [ OK ]   {c}")
        elif under_outputs:
            print(f"  [pend]   {c}  (deliverable not rendered yet)")
        else:
            print(f"  [MISS]   {c}")
            missing += 1
    if not reported:
        print("  (no asset paths referenced)")
    return missing


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate manifest asset paths exist")
    ap.add_argument("target", type=Path, help="manifest.md, or an app/video dir containing one")
    args = ap.parse_args()

    target = args.target.resolve()
    manifests: list[Path] = []
    if target.is_file():
        manifests = [target]
    elif target.is_dir():
        m = target / "manifest.md"
        if m.exists():
            manifests.append(m)
        # if it's an app dir, also check each video manifest
        for sub in sorted(target.iterdir()):
            vm = sub / "manifest.md"
            if sub.is_dir() and vm.exists():
                manifests.append(vm)
    if not manifests:
        sys.exit(f"no manifest.md found at {target}")

    total_missing = sum(check_manifest(m) for m in manifests)
    print()
    if total_missing:
        print(f"{total_missing} referenced path(s) missing.")
        sys.exit(1)
    print("All referenced paths exist.")


if __name__ == "__main__":
    main()
