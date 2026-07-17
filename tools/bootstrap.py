"""Idempotent, resumable machine setup for a fresh clone (Windows).

The Stage-B workhorse behind `/setup` / `workflows/onboard.md`. Run it with the
freshly-installed SYSTEM python (Stage A — winget installs of Python/git/ffmpeg/node —
happens before this, driven by the agent). Each step does check -> do -> verify and
records state in .bootstrap-state.json, so a re-run skips finished steps and resumes
after a failure.

Three things this DELIBERATELY does not do (they need a human — see workflows/onboard.md):
  1. paste API keys into .env       (secrets never touch the agent transcript)
  2. `higgsfield auth login`         (browser OAuth)
  3. Google Drive for desktop mount  (G: drive sign-in)

Usage (system python, from the project root):
    python tools\\bootstrap.py                 # run all steps
    python tools\\bootstrap.py --status         # show step states
    python tools\\bootstrap.py --step venv       # run one step
    python tools\\bootstrap.py --from sitecustomize   # run from a step onward
"""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE = PROJECT_ROOT / ".bootstrap-state.json"
VENV = PROJECT_ROOT / ".venv"
VENV_PY = VENV / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
SITECUSTOMIZE_TMPL = PROJECT_ROOT / "tools" / "templates" / "sitecustomize.py"


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def save_state(s: dict) -> None:
    STATE.write_text(json.dumps(s, indent=2), encoding="utf-8")


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"    $ {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, cwd=PROJECT_ROOT, text=True, **kw)


# --------------------------------------------------------------------------- #
# Steps: each returns (ok: bool, message: str). Idempotent.
# --------------------------------------------------------------------------- #
def step_assert_windows() -> tuple[bool, str]:
    if platform.system() != "Windows":
        return False, ("This pipeline targets Windows (paths, PowerShell, G: drive, the "
                       "cp1252 UTF-8 fix). Other OSes are unsupported — set up manually "
                       "via workflows/setup_environment.md.")
    return True, f"Windows {platform.release()}"


def step_venv() -> tuple[bool, str]:
    if not VENV.exists():
        r = run([sys.executable, "-m", "venv", str(VENV)])
        if r.returncode != 0:
            return False, "python -m venv failed"
    # ensure pip exists in the venv (some Windows pythons ship venvs without it)
    r = run([str(VENV_PY), "-m", "pip", "--version"], capture_output=True)
    if r.returncode != 0:
        run([str(VENV_PY), "-m", "ensurepip", "--default-pip"], capture_output=True)
    run([str(VENV_PY), "-m", "pip", "install", "--upgrade", "pip", "-q"], capture_output=True)
    r = run([str(VENV_PY), "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    if r.returncode != 0:
        return False, "pip install -r requirements.txt failed"
    return True, "venv built + requirements installed"


def step_sitecustomize() -> tuple[bool, str]:
    # Forces UTF-8 stdio so helper tools don't crash on cp1252 consoles.
    site = VENV / "Lib" / "site-packages" / "sitecustomize.py"
    if not VENV.exists():
        return False, "run the venv step first"
    if SITECUSTOMIZE_TMPL.exists():
        site.write_text(SITECUSTOMIZE_TMPL.read_text(encoding="utf-8"), encoding="utf-8")
    else:  # fallback: write it inline
        site.write_text(
            "import sys\n"
            "for s in (sys.stdout, sys.stderr):\n"
            "    try: s.reconfigure(encoding='utf-8')\n"
            "    except Exception: pass\n", encoding="utf-8")
    return True, f"wrote {site.relative_to(PROJECT_ROOT).as_posix()}"


def step_env() -> tuple[bool, str]:
    env = PROJECT_ROOT / ".env"
    example = PROJECT_ROOT / ".env.example"
    if not env.exists():
        if example.exists():
            env.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            return False, ".env.example missing"
    # report empty required keys (do NOT prompt for secrets)
    text = env.read_text(encoding="utf-8")
    required = ["HIGGSFIELD_API_ID", "HIGGSFIELD_API_KEY", "GEMINI_API_KEY", "ELEVENLABS_API_KEY"]
    empties = [k for k in required
               if not any(ln.strip().startswith(f"{k}=") and ln.split("=", 1)[1].strip()
                          for ln in text.splitlines())]
    if empties:
        return True, (".env present but these keys are EMPTY — a human must fill them "
                      "from the team vault (never paste secrets into Claude chat): "
                      + ", ".join(empties))
    return True, ".env present with required keys set"


def step_permissions() -> tuple[bool, str]:
    settings = PROJECT_ROOT / ".claude" / "settings.json"
    local = PROJECT_ROOT / ".claude" / "settings.local.json"
    if not settings.exists():
        return False, ".claude/settings.json (the shared allowlist) is missing"
    if not local.exists():
        local.write_text('{\n  "permissions": {\n    "allow": []\n  }\n}\n', encoding="utf-8")
    return True, "project allowlist present; settings.local.json ready for local one-offs"


def step_higgsfield() -> tuple[bool, str]:
    import shutil
    if shutil.which("higgsfield") is None:
        return True, ("higgsfield CLI not found — install it, then run `higgsfield auth "
                      "login` (a human step): "
                      "curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh")
    # On Windows the CLI is a .cmd shim; probe via shell so subprocess can find it.
    try:
        r = run(["higgsfield", "--version"], capture_output=True,
                shell=(platform.system() == "Windows"))
        if r.returncode != 0:
            return True, "higgsfield on PATH but --version failed; verify the install manually"
    except Exception as e:  # noqa: BLE001  (advisory step — never hard-fail here)
        return True, f"higgsfield on PATH but couldn't probe it ({e}); verify manually"
    return True, "higgsfield CLI present (run `higgsfield auth login` if the session is expired)"


def step_drive() -> tuple[bool, str]:
    drive = Path(r"G:\Shared drives\Mode AI Creative Loop")
    if not drive.exists():
        return True, ("G: shared drive not mounted — install Google Drive for desktop and "
                      "sign in so finals sync + format examples resolve (a human step).")
    return True, "shared drive mounted at G:"


def step_verify() -> tuple[bool, str]:
    if not VENV_PY.exists():
        return False, "venv python missing"
    r = run([str(VENV_PY), "tools/env_check.py", "--strict"])
    if r.returncode != 0:
        return False, "env_check --strict reported missing required items (see its output above)"
    return True, "env_check --strict passed — studio ready"


STEPS = [
    ("assert-windows", step_assert_windows),
    ("venv", step_venv),
    ("sitecustomize", step_sitecustomize),
    ("env", step_env),
    ("permissions", step_permissions),
    ("higgsfield", step_higgsfield),
    ("drive", step_drive),
    ("verify", step_verify),
]


def main() -> int:
    ap = argparse.ArgumentParser(description="Idempotent fresh-clone setup (Windows)")
    ap.add_argument("--status", action="store_true", help="show step states and exit")
    ap.add_argument("--step", help="run only this step")
    ap.add_argument("--from", dest="from_step", help="run from this step onward")
    args = ap.parse_args()

    state = load_state()
    names = [n for n, _ in STEPS]

    if args.status:
        for n in names:
            print(f"  [{state.get(n, {}).get('status', 'pending'):>7}] {n}")
        return 0

    to_run = names
    if args.step:
        if args.step not in names:
            sys.exit(f"unknown step '{args.step}'. steps: {', '.join(names)}")
        to_run = [args.step]
    elif args.from_step:
        if args.from_step not in names:
            sys.exit(f"unknown step '{args.from_step}'. steps: {', '.join(names)}")
        to_run = names[names.index(args.from_step):]

    stepmap = dict(STEPS)
    failed = False
    for n in to_run:
        if not args.step and not args.from_step and state.get(n, {}).get("status") == "done":
            print(f"  [   done] {n}  (skipping; --step {n} to re-run)")
            continue
        print(f"  [running] {n}")
        try:
            ok, msg = stepmap[n]()
        except Exception as e:  # noqa: BLE001
            ok, msg = False, f"exception: {e}"
        state[n] = {"status": "done" if ok else "failed", "message": msg}
        save_state(state)
        print(f"  [{'   done' if ok else ' FAILED'}] {n}: {msg}")
        if not ok:
            failed = True
            print(f"\nStopped at '{n}'. Fix the above, then re-run "
                  f"`python tools\\bootstrap.py` (it resumes) or `--step {n}`.")
            break

    if not failed:
        print("\nBootstrap complete. Remaining HUMAN steps (see workflows/onboard.md):")
        print("  1. Fill empty keys in .env from the team vault.")
        print("  2. `higgsfield auth login` (browser).")
        print("  3. Google Drive for desktop sign-in (G:).")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
