"""Register an approved UGC script into an app's script library.

Step 5 (Script Generation) helper — see workflows/generate_scripts.md. Takes a verbatim
approved-script markdown file (with YAML-ish front-matter), makes sure it lives under
assets/<app>/script-library/approved/, and upserts a row into that library's index.md so
future runs can scan what's been used and never repeat a script.

Front-matter (between --- fences) — required: id, app, persona, angle, date, chosen_hook,
status. Optional: avatar, sticker, video_folder.

Usage:
    .venv\\Scripts\\python.exe tools/save_approved_script.py <approved-script.md>

Idempotent: re-running with the same `id` replaces that index row (e.g. after you fill in
video_folder during hand-off).
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS = PROJECT_ROOT / "assets"
ROW_MARKER = "<!-- save_approved_script.py upserts rows here -->"
REQUIRED = ["id", "app", "persona", "angle", "date", "chosen_hook", "status"]


def parse_front_matter(text: str) -> dict[str, str]:
    """Parse a simple `key: value` front-matter block fenced by --- lines."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file has no '---' front-matter block at the top")
    fm: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fm
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        fm[key.strip()] = val.strip().strip('"').strip("'").strip()
    raise ValueError("front-matter block was not closed with '---'")


def index_template(app: str) -> str:
    return (
        f"# Script Library Index — {app}\n\n"
        f"> Every **approved** script for `{app}`, banked verbatim in `approved/`. The script\n"
        f"> stage scans this before writing so we never repeat a script — the novelty scan\n"
        f"> filters by the Format column (a Ranking hook doesn't block a UGC hook).\n"
        f"> Rows are upserted by `tools/save_approved_script.py`.\n\n"
        f"| ID | Date | Format | Persona | Angle | Chosen hook | Status | Video | File |\n"
        f"|----|------|--------|---------|-------|-------------|--------|-------|------|\n"
        f"{ROW_MARKER}\n"
    )


def migrate_index(text: str) -> str:
    """Upgrade a pre-format index (8 columns) to include the Format column.

    Old rows are tagged ugc-single (everything before formats existed was UGC)."""
    if "| Format |" in text:
        return text
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("| ID | Date |"):
            out.append(line.replace("| ID | Date |", "| ID | Date | Format |", 1))
        elif s.startswith("|") and set(s) <= {"|", "-", " "}:
            # separator row — rebuild with one group per header column (9)
            out.append("|" + "----|" * 9)
        elif s.startswith("|") and s != ROW_MARKER and not s.startswith("| ID") and "---" not in s:
            cells = line.split("|")
            if len(cells) >= 9:  # | id | date | persona | ... -> insert after date
                cells.insert(3, " ugc-single ")
                out.append("|".join(cells))
            else:
                out.append(line)
        else:
            out.append(line)
    return "\n".join(out)


def esc(val: str) -> str:
    return val.replace("|", "\\|").strip()


def build_row(fm: dict[str, str], file_rel: str) -> str:
    hook = esc(fm.get("chosen_hook", ""))
    if len(hook) > 80:
        hook = hook[:77] + "…"
    video = esc(fm.get("video_folder", "") or "—")
    name = Path(file_rel).name
    fmt = esc(fm.get("format", "ugc-single"))
    return (
        f"| {esc(fm['id'])} | {esc(fm['date'])} | {fmt} | {esc(fm['persona'])} | {esc(fm['angle'])} | "
        f"{hook} | {esc(fm['status'])} | {video} | [{name}]({file_rel}) |"
    )


def upsert_row(index_path: Path, app: str, row: str, row_id: str) -> str:
    if index_path.exists():
        text = migrate_index(index_path.read_text(encoding="utf-8"))
    else:
        text = index_template(app)
    if ROW_MARKER not in text:
        text = text.rstrip() + "\n" + ROW_MARKER + "\n"

    # Replace an existing row for this id, else insert above the marker.
    id_cell = f"| {esc(row_id)} |"
    out_lines, replaced = [], False
    for line in text.splitlines():
        if line.startswith(id_cell):
            out_lines.append(row)
            replaced = True
        else:
            out_lines.append(line)
    if not replaced:
        out_lines = [
            (row + "\n" + ROW_MARKER) if line.strip() == ROW_MARKER else line
            for line in out_lines
        ]
    index_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
    return "updated" if replaced else "added"


def main() -> int:
    ap = argparse.ArgumentParser(description="Register an approved script into the library")
    ap.add_argument("file", type=Path, help="the approved-script markdown file")
    ap.add_argument("--format", dest="format_slug",
                    help="content-format slug (default: front-matter `format:` or ugc-single)")
    args = ap.parse_args()

    if not args.file.exists():
        sys.exit(f"file not found: {args.file}")
    text = args.file.read_text(encoding="utf-8")
    fm = parse_front_matter(text)
    fm["format"] = args.format_slug or fm.get("format") or "ugc-single"

    missing = [k for k in REQUIRED if not fm.get(k)]
    if missing:
        sys.exit(f"front-matter missing required keys: {', '.join(missing)}")

    app = fm["app"]
    approved_dir = ASSETS / app / "script-library" / "approved"
    approved_dir.mkdir(parents=True, exist_ok=True)

    # Make sure the file lives under approved/ (copy it in if authored elsewhere).
    target = approved_dir / args.file.name
    if args.file.resolve() != target.resolve():
        shutil.copy2(args.file, target)
        print(f"copied script -> {target.relative_to(PROJECT_ROOT).as_posix()}")

    file_rel = f"approved/{target.name}"
    index_path = ASSETS / app / "script-library" / "index.md"
    action = upsert_row(index_path, app, build_row(fm, file_rel), fm["id"])

    print(f"{action} index row '{fm['id']}' in {index_path.relative_to(PROJECT_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
