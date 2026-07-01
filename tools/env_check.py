"""Verify the video-editing studio environment is ready.

Checks the external binaries the pipeline shells out to, the project virtualenv's
Python packages, and that ELEVENLABS_API_KEY resolves from the project-root .env
(the single source of truth — never duplicate the key into the synced skill dirs).

Usage:
    python tools/env_check.py
    python tools/env_check.py --strict   # exit 1 if any REQUIRED check fails
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# (command, version_args, required?)
BINARIES = [
    ("ffmpeg", ["-version"], True),
    ("ffprobe", ["-version"], True),
    ("node", ["--version"], True),
    ("npx", ["--version"], True),
    ("yt-dlp", ["--version"], True),   # music / SFX / URL sourcing
    ("git", ["--version"], True),      # version control
    ("gh", ["--version"], False),      # GitHub CLI — push/pull/PRs
    ("bun", ["--version"], False),     # only needed for hyperframes monorepo dev
    ("uv", ["--version"], False),
]

PY_PACKAGES = ["requests", "librosa", "matplotlib", "PIL", "numpy", "docx", "yt_dlp"]

# Keys the core pipeline needs vs. nice-to-haves. See .env.example for what each does.
REQUIRED_ENV_KEYS = ["HIGGSFIELD_API_ID", "HIGGSFIELD_API_KEY", "GEMINI_API_KEY", "ELEVENLABS_API_KEY"]
OPTIONAL_ENV_KEYS = ["OPENROUTER_API_KEY", "APIFY_API_KEY", "POSTIZ_API_KEY", "HEYGEN_API_KEY"]

# Per-OS install command for each external binary (printed when a check fails).
_INSTALL_HINTS = {
    "Windows": {
        "ffmpeg": "winget install Gyan.FFmpeg", "ffprobe": "winget install Gyan.FFmpeg",
        "node": "winget install OpenJS.NodeJS.LTS", "npx": "winget install OpenJS.NodeJS.LTS",
        "yt-dlp": r".venv\Scripts\python.exe -m pip install -U yt-dlp",
        "git": "winget install Git.Git", "gh": "winget install GitHub.cli",
        "bun": 'powershell -c "irm bun.sh/install.ps1 | iex"', "uv": "winget install astral-sh.uv",
    },
    "Darwin": {
        "ffmpeg": "brew install ffmpeg", "ffprobe": "brew install ffmpeg",
        "node": "brew install node", "npx": "brew install node",
        "yt-dlp": ".venv/bin/python -m pip install -U yt-dlp",
        "git": "brew install git", "gh": "brew install gh",
        "bun": "brew install oven-sh/bun/bun", "uv": "brew install uv",
    },
    "Linux": {
        "ffmpeg": "sudo apt install -y ffmpeg", "ffprobe": "sudo apt install -y ffmpeg",
        "node": "sudo apt install -y nodejs npm", "npx": "sudo apt install -y nodejs npm",
        "yt-dlp": ".venv/bin/python -m pip install -U yt-dlp",
        "git": "sudo apt install -y git", "gh": "sudo apt install -y gh",
        "bun": "curl -fsSL https://bun.sh/install | bash", "uv": "curl -LsSf https://astral.sh/uv/install.sh | sh",
    },
}


def install_hint(cmd: str) -> str:
    return _INSTALL_HINTS.get(platform.system(), {}).get(cmd, "see workflows/setup_environment.md")


def _first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line
    return ""


def _resolve(cmd: str) -> str | None:
    """Resolve a binary, preferring the project venv's Scripts dir (for yt-dlp etc.)."""
    scripts = Path(sys.executable).parent
    for name in (f"{cmd}.exe", cmd):
        cand = scripts / name
        if cand.exists():
            return str(cand)
    return shutil.which(cmd)


def check_binary(cmd: str, version_args: list[str]) -> tuple[bool, str]:
    path = _resolve(cmd)
    if not path:
        return False, "not found on PATH"
    try:
        # On Windows, .CMD/.bat shims (npx, bun) need a shell to execute.
        if os.name == "nt":
            quoted = '"{}" {}'.format(path, " ".join(version_args))
            out = subprocess.run(quoted, capture_output=True, text=True, timeout=30, shell=True)
        else:
            out = subprocess.run([path, *version_args], capture_output=True, text=True, timeout=30)
        info = _first_line(out.stdout or out.stderr)
        return True, info or f"found ({path})"
    except Exception as e:  # noqa: BLE001
        return True, f"found ({path}) but version probe failed: {e}"


def check_py_packages() -> list[tuple[str, bool]]:
    results = []
    for pkg in PY_PACKAGES:
        try:
            __import__(pkg)
            results.append((pkg, True))
        except Exception:  # noqa: BLE001
            results.append((pkg, False))
    return results


def read_env_key(key: str) -> str | None:
    """Read a key from the project-root .env (then environment)."""
    import os

    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            if k.strip() == key:
                v = v.strip().strip('"').strip("'")
                if v:
                    return v
    return os.environ.get(key) or None


def main() -> None:
    ap = argparse.ArgumentParser(description="Check the video studio environment")
    ap.add_argument("--strict", action="store_true", help="exit 1 if a required check fails")
    args = ap.parse_args()

    ok = "[ OK ]"
    bad = "[FAIL]"
    warn = "[warn]"
    failures = 0

    print("== Runtime ==")
    print(f"{ok}  Python {sys.version.split()[0]}  ({sys.executable})")
    venv = PROJECT_ROOT / ".venv"
    running_venv = str(venv).lower() in sys.executable.lower()
    if venv.exists():
        note = "" if running_venv else "  (present, but you are NOT running it — use the .venv interpreter)"
        print(f"{ok}  .venv present{note}")
    else:
        print(f"{warn}  .venv missing — create it:  python -m venv .venv  &&  pip install -r requirements.txt")

    print("\n== Binaries ==")
    for cmd, version_args, required in BINARIES:
        found, info = check_binary(cmd, version_args)
        if found:
            print(f"{ok}  {cmd:<8} {info}")
        else:
            tag = bad if required else warn
            print(f"{tag}  {cmd:<8} {info}" + ("" if required else "  (optional)"))
            print(f"        ↳ install: {install_hint(cmd)}")
            if required:
                failures += 1

    print("\n== Python packages (run with the project .venv) ==")
    print(f"  interpreter: {sys.executable}")
    for pkg, found in check_py_packages():
        print(f"{ok if found else bad}  {pkg}")
        if not found:
            failures += 1

    print("\n== Secrets (.env) ==")
    if not (PROJECT_ROOT / ".env").exists():
        print(f"{bad}  .env not found — copy .env.example to .env and fill in keys (get them from your team admin)")
        failures += 1
    for k in REQUIRED_ENV_KEYS:
        v = read_env_key(k)
        if v:
            masked = v[:4] + "..." + v[-4:] if len(v) > 8 else "***"
            print(f"{ok}  {k} resolved ({masked})")
        else:
            print(f"{bad}  {k} missing — add it to {PROJECT_ROOT / '.env'}")
            failures += 1
    for k in OPTIONAL_ENV_KEYS:
        v = read_env_key(k)
        print(f"{ok if v else warn}  {k} {'resolved' if v else 'not set (optional)'}")

    print("\n== HyperFrames (motion graphics) ==")
    found, info = check_binary("npx", ["--version"])
    print(f"{ok if found else warn}  use: npx --yes hyperframes <cmd>  (CLI downloads on first run)")

    print()
    if failures:
        print(f"{failures} required check(s) failed.")
        if args.strict:
            sys.exit(1)
    else:
        print("All required checks passed. Studio is ready.")


if __name__ == "__main__":
    main()
