# Workflow: Set up the environment on a fresh pull

**Objective:** Take a freshly-cloned copy of this repo on a new Windows or macOS machine and
get it to a state where the full video pipeline runs. The agent (Claude) drives this: detect
what's missing, install it, then verify.

**When to run:** The first time the repo is opened on a machine, or whenever
`tools/env_check.py` reports failures.

---

## Inputs / prerequisites

- This repo, cloned locally (`git clone` of `CurrentMobile/UA-Social-Creative-Massposting`).
- A package manager: **winget** (Windows, built in) or **Homebrew** (macOS — install from https://brew.sh if absent).
- The API keys (from your team admin) to fill into `.env`.

## The single source of truth for "what's needed"

`tools/env_check.py` is the checker. It reports, per item, `[ OK ]` / `[FAIL]` / `[warn]` and
prints the exact per-OS install command on any miss. **Always start and end with it.**

```powershell
# Windows (use system python the first time; the venv may not exist yet)
python tools\env_check.py
```
```bash
# macOS / Linux
python3 tools/env_check.py
```

## Steps

### 1. Run the checker, read the misses
Run `env_check.py`. It checks: Python + `.venv`, the binaries (ffmpeg, ffprobe, node, npx,
yt-dlp, git, gh, bun, uv), the Python packages, and every `.env` key. Each `[FAIL]` line is
followed by `↳ install: <command>`. Work the list top to bottom.

### 2. Install missing binaries
Run the install command the checker printed. Examples:

| Tool | Windows (winget) | macOS (brew) |
|------|------------------|--------------|
| ffmpeg/ffprobe | `winget install Gyan.FFmpeg` | `brew install ffmpeg` |
| node/npx | `winget install OpenJS.NodeJS.LTS` | `brew install node` |
| git | `winget install Git.Git` | `brew install git` |
| gh (GitHub CLI) | `winget install GitHub.cli` | `brew install gh` |

After installing, **open a new shell** so PATH refreshes, then re-run the checker.

### 3. Create the Python venv and install requirements
```powershell
# Windows
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```
```bash
# macOS / Linux
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```
`requirements.txt` includes `yt-dlp`, so it lands in the venv (that's where `env_check.py`
looks for it first).

### 4. Windows only — restore the UTF-8 shim
The helper tools print Unicode; Windows consoles default to cp1252 and crash without this.
Recreate `sitecustomize.py` in the venv's site-packages so stdio is forced to UTF-8:
```powershell
$sp = ".venv\Lib\site-packages\sitecustomize.py"
@'
import sys
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8")
    except Exception: pass
'@ | Out-File -Encoding utf8 $sp
```
(See the studio-setup notes — this is a known recurring gotcha.)

### 5. Create `.env` from the template and fill keys
```powershell
Copy-Item .env.example .env   # Windows
# cp .env.example .env        # macOS/Linux
```
Then fill in the keys (from your team admin). **Required** for the core pipeline:
`HIGGSFIELD_API_ID`, `HIGGSFIELD_API_KEY`, `GEMINI_API_KEY`, `ELEVENLABS_API_KEY`.
Optional: `OPENROUTER_API_KEY`, `APIFY_API_KEY`, `POSTIZ_API_KEY`, `HEYGEN_API_KEY`.
`.env` is gitignored — never commit it.

### 6. HyperFrames (motion graphics)
No install step — it's invoked as `npx --yes hyperframes <cmd>` and downloads itself on
first run. Just confirm `node`/`npx` passed in step 1.

### 7. Heavy assets (not in git)
The repo intentionally ships only the reusable, lightweight assets (CTA, brand, screenshots,
reviews, script-writing guide, SFX, music, props, fonts — see `.gitignore`). The big
per-video AI clips, rendered edits, and the persona library live in the **Google Shared
Drive** (`Mode AI Creative Loop`). Pull what a given task needs from there; SFX/music also
re-download on demand via `tools/fetch_sfx.py` / `tools/fetch_music.py`.

### 8. Verify
Re-run the checker in strict mode — it must exit clean:
```powershell
.venv\Scripts\python.exe tools\env_check.py --strict
```
Optionally validate the keys actually work (read-only, spends no credits):
```powershell
.venv\Scripts\python.exe tools\test_api_keys.py
```

## Done when
`env_check.py --strict` exits 0 and prints "All required checks passed. Studio is ready."

## Edge cases / learnings
- **winget/brew missing:** install the package manager first (winget ships with Windows 11;
  brew from https://brew.sh).
- **PATH not updated after install:** always open a fresh terminal before re-checking.
- **yt-dlp "not found" though pip says installed:** it must be in the *venv*, not global —
  install via the venv interpreter (step 3), which is where `env_check.py` resolves it.
- **Unicode crash on Windows** (`UnicodeEncodeError`): step 4 wasn't applied to this venv.
