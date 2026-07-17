"""Preflight lock check for formats/ — agents may only write learnings.md files.

Format templates (SOPs, recipes, prompts, manifests) are LOCKED: the self-improvement
loop appends to formats/<slug>/learnings.md, and promotion into a recipe is a human
act via the promote-learnings flow (bumps `version` in format.md). This tool detects
drift: any uncommitted modification/deletion under formats/ that is NOT a learnings.md
(or a brand-new format directory being authored) fails preflight.

Usage:
    .venv\\Scripts\\python.exe tools\\check_formats_lock.py           # check
    .venv\\Scripts\\python.exe tools\\check_formats_lock.py --explain # show allowed writes

Exit codes: 0 = clean, 1 = locked files modified (stop the run and show the owner).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def git_status_formats() -> list[tuple[str, str]]:
    r = subprocess.run(
        ["git", "status", "--porcelain", "--", "formats/"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    if r.returncode != 0:
        return []
    out = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        code, path = line[:2], line[3:].strip().strip('"')
        out.append((code.strip(), path))
    return out


def is_allowed(code: str, path: str) -> bool:
    p = path.replace("\\", "/")
    if p.endswith("/learnings.md") or p.endswith("learnings.md"):
        return True          # the one agent-writable file
    if code in ("??", "A"):
        return True          # brand-new files = a format being authored, allowed
    return False             # modification/deletion of an existing template = locked


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify formats/ lock integrity")
    ap.add_argument("--explain", action="store_true")
    args = ap.parse_args()

    if args.explain:
        print("Allowed under formats/: appending to any learnings.md; ADDING brand-new "
              "files (authoring a new format). Everything else (modifying/deleting "
              "committed SOPs, recipes, prompts, format.md, REGISTRY.md) is LOCKED — "
              "promote learnings via the human promote-learnings flow instead.")
        return 0

    changes = git_status_formats()
    violations = [(c, p) for c, p in changes if not is_allowed(c, p)]
    if not violations:
        print(f"[formats-lock] OK ({len(changes)} change(s), all allowed)")
        return 0
    print("[formats-lock] LOCKED FILES MODIFIED — stop and show the owner:")
    for code, path in violations:
        print(f"  {code:>2} {path}")
    print("Templates are locked; append run learnings to formats/<slug>/learnings.md "
          "instead, or have the owner run the promote-learnings flow (version bump).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
