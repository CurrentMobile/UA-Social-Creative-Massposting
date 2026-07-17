# Workflow: Onboard a New Machine (fresh clone → ready studio)

Goal: a non-technical teammate pastes a GitHub link into Claude and the agent sets up
almost everything. Only three human steps remain (secrets, Higgsfield auth, Drive).

## Trigger

The teammate says (put this exact sentence in `docs/TEAM_ONBOARDING.md`):
> "Set up https://github.com/<org>/<repo> — follow the repo's onboarding."

Or, already inside a clone, they run `/setup`.

## Stage 0 — Clone (if not already cloned)

Claude runs `git clone <url> mode-ai-creative-loop` and `cd`s in. For a private repo,
git's credential manager handles the browser sign-in (an unavoidable one-time human
prompt). Then read `CLAUDE.md`.

## Stage A — System dependencies (agent-run, before Python exists)

Windows only (the pipeline asserts this). Install with winget (idempotent — winget
no-ops if already present):
```
winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
winget install -e --id Git.Git            --accept-package-agreements --accept-source-agreements
winget install -e --id Gyan.FFmpeg        --accept-package-agreements --accept-source-agreements
winget install -e --id OpenJS.NodeJS.LTS  --accept-package-agreements --accept-source-agreements
```
(If a teammate lacks winget, point them at `workflows/setup_environment.md`.)

## Stage B — `tools/bootstrap.py` (idempotent, resumable)

Run with the freshly-installed SYSTEM python (not the venv — it doesn't exist yet):
```
python tools\bootstrap.py            # runs all steps; resumes after any failure
python tools\bootstrap.py --status   # see step states
python tools\bootstrap.py --step venv  # re-run one step
```
Steps: assert-windows → venv (+pip+requirements) → sitecustomize (UTF-8 fix) → env
(.env from example, report empty keys) → permissions (verify tracked settings.json,
create local one) → higgsfield (detect CLI) → drive (check G:) → verify
(`env_check.py --strict`). State persists in `.bootstrap-state.json` (gitignored).

## Stage C — The three human steps ("the 10 human minutes")

Bootstrap deliberately does NOT do these; walk the teammate through them:
1. **API keys** — the admin shares them via the team password-manager vault. Open
   `.env` in Notepad and fill the empty keys bootstrap reported. **Never paste secrets
   into Claude chat** (session transcripts persist) and never commit `.env`.
2. **`higgsfield auth login`** — run it in a terminal; complete the browser OAuth; then
   `higgsfield account status` should show credits.
3. **Google Drive for desktop** — install + sign in so `G:\Shared drives\Mode AI
   Creative Loop` mounts (finals sync + format-example previews depend on it).

## Stage D — Verify + first media pull

```
.venv\Scripts\python.exe tools\env_check.py --strict     # must pass clean
.venv\Scripts\python.exe tools\sync_assets.py pull --all --dry-run   # preview media to fetch
```
Green env_check = the studio is ready. A fresh clone has the knowledge layer (workflows,
tools, formats, personas, brand, manifests); heavy per-video media lives on G: and is
pulled on demand by `sync_assets.py`.

## What cannot be automated

The three Stage-C steps (browser/secret/mount actions). Everything else is hands-off.
Set this expectation up front so "zero-touch" isn't over-promised.
