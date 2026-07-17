"""Sync this repo's functionality into the sanitized public fork (OS-Content Studio).

Mirrors the whitelisted trees below into the sibling repo at OS_STUDIO_DIR
(default C:\\Users\\ADMIN\\Projects\\os-content-studio), applying a Mode->generic
sanitization map to every text file on the way, then scanning the destination for
forbidden Mode-specific terms. THIS FILE ITSELF IS NEVER SYNCED — the fork has no
knowledge of the internal repo.

Three tiers:
  MIRROR+SANITIZE  everything in SYNC_DIRS / SYNC_FILES (minus EXCLUDES): text files
                   get REPLACEMENTS (+ per-file PATCHES) applied; binaries copy as-is.
  MANUAL           files in MANUAL_TRACK are never written by this script (the fork
                   owns its own version); their source hash is tracked and the script
                   WARNS when the internal version drifts so a human/agent re-ports it.
  EXCLUDED         Mode-app asset trees, screen recordings, caches, skill payloads.

State lives in .studio-sync-state.json (gitignored): the synced-file list (so removals
propagate as deletions) and manual-tier hashes. Log appends to .studio-sync.log.

Usage:
    .venv\\Scripts\\python.exe tools\\sync_to_studio.py             # full sync + gate
    .venv\\Scripts\\python.exe tools\\sync_to_studio.py --dry-run   # show what would change
    .venv\\Scripts\\python.exe tools\\sync_to_studio.py --hook      # quiet, never blocks (Stop hook)
    .venv\\Scripts\\python.exe tools\\sync_to_studio.py --sweep     # forbidden-term scan of the whole fork
    .venv\\Scripts\\python.exe tools\\sync_to_studio.py --ack-manual # accept manual-tier hashes after a hand-port

Auto-sync wiring: a Stop hook in .claude/settings.local.json runs `--hook` at the end
of every Claude session in this repo, so the fork continuously tracks internal changes.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
DEST = Path(os.environ.get("OS_STUDIO_DIR", r"C:\Users\ADMIN\Projects\os-content-studio"))
STATE_FILE = SRC / ".studio-sync-state.json"
LOG_FILE = SRC / ".studio-sync.log"

SYNC_DIRS = [
    "tools",
    "workflows",
    "formats",
    "guardrails",
    "qa",
    "docs",
    ".claude/commands",
    ".claude/agents",
    "assets/_shared",
    "assets/_templates",
    "assets/fonts",
    "assets/music",
    "assets/sfx",
]

SYNC_FILES = [
    "requirements.txt",
    "skills-lock.json",
    "create-videos.ps1",
    "create-statics.ps1",
    "create-ugc-video.ps1",
    ".claude/launch.json",
    ".claude/settings.json",
    "street-interview-2-creative-direction.md",
]

# fnmatch patterns on posix-style relative paths
EXCLUDES = [
    "tools/sync_to_studio.py",          # the fork never learns about the internal repo
    "tools/__pycache__/*",
    "*/__pycache__/*",
    "*.pyc",
    "assets/_shared/screen-recordings/*",  # Mode app screen recordings (fork keeps its README)
    "assets/*.info.json",
    "assets/*/*.info.json",
    "*/Thumbs.db",
    "*/desktop.ini",
]

# Fork owns its own version of these; we only warn when the internal version drifts.
MANUAL_TRACK = [
    "README.md",
    "CLAUDE.md",
    ".gitignore",
    ".env.example",
    "assets/ASSETS.md",
]

TEXT_EXTS = {".md", ".py", ".json", ".ps1", ".html", ".txt", ".yml", ".yaml",
             ".excalidraw", ".csv", ".srt", ".js", ".mjs", ".css", ".xml"}

# Ordered. Tuples of (pattern, replacement, is_regex).
REPLACEMENTS = [
    (r"Shared drives([\\/]+)Mode AI Creative Loop", r"Shared drives\1Content Studio", True),
    ("Mode AI Creative\\nLoop", "OS-Content\\nStudio", False),  # \n inside JSON strings (.excalidraw)
    ("Mode AI Creative Loop", "OS-Content Studio", False),
    ("mode-ai-creative-loop", "os-content-studio", False),
    ("transferable_angle_for_mode_earn", "transferable_angle_for_brand", False),
    ("Mode Earn Rewards", "Example App", False),
    ("Mode-Earn", "Example-App", False),
    ("Mode Earn", "Example App", False),
    ("Mode earn", "Example App", False),
    ("mode earn", "example app", False),
    ("mode-earn", "example-app", False),
    ("mode_earn", "example_app", False),
    ("ModeEarn", "ExampleApp", False),
    ("modeearn", "exampleapp", False),
    ("Mode Mobile", "Your Company", False),
    ("modemobile.com", "example.com", False),
    ("CurrentMobile/UA-Social-Creative-Massposting", "your-org/os-content-studio", False),
    ("UA-Social-Creative-Massposting", "os-content-studio", False),
    ("CurrentMobile", "your-org", False),
    (" (Osasenaga)", "", False),
    ("Osasenaga", "your team lead", False),
    ("Gianne", "your team lead", False),
    ("AppLock, NGL, Gallery, Cleaner, Trimbox", "Example Product, and your other brands", False),
    ("applock · ngl · gallery · cleaner · trimbox", "example-product · your-other-brands", False),
    ("AppLock", "Example Product", False),
]

# Per-file regex patches applied BEFORE the generic replacements (match original text).
PATCHES: dict[str, list[tuple[str, str]]] = {
    "tools/scaffold.py": [
        (r'"applock": "AppLock",\s*\n\s*"ngl": "NGL",\s*\n\s*"gallery": "Gallery",'
         r'\s*\n\s*"cleaner": "Cleaner",\s*\n\s*"trimbox": "Trimbox",',
         '"example-product": "Example Product",'),
    ],
}

# Case-insensitive scan of the fork after syncing. Any hit = sanitization leak.
FORBIDDEN = re.compile(
    r"mode[ _-]?earn|mode mobile|modemobile|mode[ _-]?ai[ _-]?creative|osasenaga|gianne"
    r"|currentmobile|ua-social-creative|applock|trimbox|\bngl\b",
    re.IGNORECASE,
)
# Paths in the fork the sweep skips (its own git dir, envs, media, binaries).
SWEEP_SKIP = [".git/*", ".venv/*", "node_modules/*", "outputs/*", ".tmp/*",
              "*.mp3", "*.mp4", "*.wav", "*.png", "*.jpg", "*.jpeg", "*.gif",
              "*.mov", "*.webm", "*.pdf", "*.zip", "*.pyc", "*.woff*", "*.ttf", "*.otf"]


def log(msg: str) -> None:
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}\n")


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def excluded(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in EXCLUDES)


def is_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTS


def sanitize(text: str, rel: str) -> str:
    for pat, repl in PATCHES.get(rel, []):
        text = re.sub(pat, repl, text)
    for pat, repl, is_rx in REPLACEMENTS:
        text = re.sub(pat, repl, text) if is_rx else text.replace(pat, repl)
    return text


def collect_sources() -> list[str]:
    rels: list[str] = []
    for d in SYNC_DIRS:
        root = SRC / d
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(SRC).as_posix()
                if not excluded(rel):
                    rels.append(rel)
    for f in SYNC_FILES:
        if (SRC / f).exists() and not excluded(f):
            rels.append(f)
    return sorted(set(rels))


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            pass
    return {"files": {}, "manual": {}}


def sync(dry_run: bool = False, quiet: bool = False) -> tuple[int, int, list[str], list[str]]:
    """Returns (written, deleted, manual_drift_paths, gate_hits)."""
    state = load_state()
    prev_files: dict = state.get("files", {})
    new_files: dict = {}
    written = deleted = 0
    touched_text: list[str] = []

    for rel in collect_sources():
        src_p = SRC / rel
        dst_p = DEST / rel
        raw = src_p.read_bytes()
        if is_text(src_p):
            try:
                out = sanitize(raw.decode("utf-8"), rel).encode("utf-8")
            except UnicodeDecodeError:
                out = raw  # not actually text; copy as-is
        else:
            out = raw
        digest = sha1(out)
        new_files[rel] = digest
        if dst_p.exists():
            try:
                if dst_p.stat().st_size == len(out) and sha1(dst_p.read_bytes()) == digest:
                    continue  # unchanged
            except OSError:
                pass
        if not dry_run:
            dst_p.parent.mkdir(parents=True, exist_ok=True)
            dst_p.write_bytes(out)
        written += 1
        if is_text(src_p):
            touched_text.append(rel)
        if not quiet:
            print(f"  {'would write' if dry_run else 'wrote':>11}  {rel}")

    # propagate deletions (only files this script previously synced)
    for rel in sorted(set(prev_files) - set(new_files)):
        dst_p = DEST / rel
        if dst_p.exists():
            if not dry_run:
                dst_p.unlink()
                # prune now-empty parents up to DEST
                parent = dst_p.parent
                while parent != DEST and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
            deleted += 1
            if not quiet:
                print(f"  {'would delete' if dry_run else 'deleted':>12}  {rel}")

    # manual-tier drift detection. The stored hash is the last ACKNOWLEDGED state — it
    # only advances via --ack-manual, so the drift warning repeats on every run (incl.
    # quiet hook runs) until a human has ported the change to the fork and acked it.
    manual_prev: dict = state.get("manual", {})
    manual_new: dict = {}
    drifted: list[str] = []
    for rel in MANUAL_TRACK:
        p = SRC / rel
        if not p.exists():
            continue
        h = sha1(p.read_bytes())
        if manual_prev.get(rel) and manual_prev[rel] != h:
            drifted.append(rel)
            manual_new[rel] = manual_prev[rel]  # keep warning until --ack-manual
        else:
            manual_new[rel] = h

    # forbidden-term gate over every text file written this run
    hits: list[str] = []
    if not dry_run:
        for rel in touched_text:
            p = DEST / rel
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if FORBIDDEN.search(line):
                    hits.append(f"{rel}:{i}: {line.strip()[:120]}")

    if not dry_run:
        state = {"files": new_files, "manual": manual_new,
                 "last_run": datetime.now().isoformat(timespec="seconds")}
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return written, deleted, drifted, hits


def sweep() -> list[str]:
    """Scan the ENTIRE fork working tree for forbidden terms."""
    hits: list[str] = []
    for p in DEST.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(DEST).as_posix()
        if any(fnmatch.fnmatch(rel, pat) for pat in SWEEP_SKIP):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if FORBIDDEN.search(line):
                hits.append(f"{rel}:{i}: {line.strip()[:120]}")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync + sanitize into the OS-Content Studio fork")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--hook", action="store_true", help="quiet mode for the Stop hook; never fails")
    ap.add_argument("--sweep", action="store_true", help="forbidden-term scan of the whole fork")
    ap.add_argument("--ack-manual", action="store_true",
                    help="accept current MANUAL_TRACK hashes (after hand-porting drifted files)")
    args = ap.parse_args()

    if args.ack_manual:
        state = load_state()
        state["manual"] = {rel: sha1((SRC / rel).read_bytes())
                           for rel in MANUAL_TRACK if (SRC / rel).exists()}
        STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        print("manual-tier baselines acknowledged.")
        return 0

    if not DEST.exists():
        msg = f"destination fork not found: {DEST}"
        log(f"ERROR {msg}")
        print(f"ERROR: {msg}", file=sys.stderr)
        return 0 if args.hook else 1

    if args.sweep:
        hits = sweep()
        if hits:
            print(f"FORBIDDEN TERMS in fork ({len(hits)}):")
            for h in hits:
                print(f"  {h}")
            return 1
        print("sweep clean: no forbidden terms in the fork.")
        return 0

    written, deleted, drift_list, hits = sync(dry_run=args.dry_run, quiet=args.hook)
    summary = (f"synced {written} file(s), deleted {deleted}, "
               f"manual-drift {len(drift_list)}, gate-hits {len(hits)}")
    log(("DRY " if args.dry_run else "") + summary)
    if not args.hook or written or deleted or drift_list or hits:
        print(f"\n{summary}")
    if drift_list:
        print("MANUAL-TIER files changed internally — hand-port to the fork:")
        for r in drift_list:
            print(f"  {r}")
    if hits:
        print("SANITIZATION GATE FAILED — forbidden terms written to the fork:")
        for h in hits:
            print(f"  {h}")
        for h in hits:
            log(f"GATE {h}")
        return 0 if args.hook else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
