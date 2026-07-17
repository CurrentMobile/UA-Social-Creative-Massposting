---
description: Set up this project on a fresh machine (deps, venv, .env, guided human steps)
argument-hint: [github-url]
model: claude-opus-4-8
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(git *), Bash(winget *), Bash(python tools/bootstrap.py*), Bash(.venv/Scripts/python.exe tools/*), PowerShell(git *), PowerShell(winget *), PowerShell(python tools\bootstrap.py*), PowerShell(.venv\Scripts\python.exe tools\*)
---

Read `workflows/onboard.md` and execute it end-to-end to set up this machine.

- Optional GitHub URL: **$1** (if given and we're not already in a clone, `git clone` it first).

Follow the workflow's stages: Stage A winget installs → Stage B `tools/bootstrap.py`
(idempotent/resumable — re-run to resume after any failure) → walk the user through the
three human steps (fill `.env` from the team vault, `higgsfield auth login`, Google
Drive sign-in) → Stage D verify with `env_check.py --strict`. NEVER ask the user to
paste secrets into chat — have them edit `.env` directly. Report what's done and exactly
what human steps remain.
