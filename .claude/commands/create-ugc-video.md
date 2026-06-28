---
description: Run the full UGC pipeline (script → assets → edit → render all variations)
argument-hint: <persona-slug> [app-slug]
model: claude-opus-4-8
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash(.venv/Scripts/python.exe tools/*), Bash(.venv/Scripts/python.exe .claude/skills/video-use/helpers/*), Bash(npx --yes hyperframes *), Bash(npx hyperframes *), Bash(higgsfield *), PowerShell(.venv\Scripts\python.exe tools\*), PowerShell(.venv\Scripts\python.exe .claude\skills\video-use\helpers\*), PowerShell(npx --yes hyperframes *), PowerShell(robocopy *)
---

Read `workflows/create_ugc_video.md` and execute it end-to-end.

- Persona slug: **$1**  (required — must already exist under `assets/_shared/personas/<slug>/`)
- App slug: **$2**  (optional — default `mode-earn`)

Follow that workflow exactly, including its Phase 0 preflight (stop early if the persona is missing,
ffmpeg is blocked, or the Higgsfield session is expired), the one-time `AskUserQuestion` form, the
script-approval loop, and the Autonomy On/Off behavior. Honor every standing rule in `CLAUDE.md`,
`workflows/generate_scripts.md`, `workflows/generate_assets.md`, `workflows/edit_video.md`, and the
project memory files. Save approved scripts verbatim so future runs never repeat them, and finish by
returning the output directory with all rendered variations.
