---
description: Create video content in ANY format (one-shot intake form → script → assets → edit → deliver)
argument-hint: [format-slug] [persona-slug] [app-slug]
model: claude-opus-4-8
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash(.venv/Scripts/python.exe tools/*), Bash(.venv/Scripts/python.exe .claude/skills/video-use/helpers/*), Bash(npx --yes hyperframes *), Bash(npx hyperframes *), Bash(higgsfield *), PowerShell(.venv\Scripts\python.exe tools\*), PowerShell(.venv\Scripts\python.exe .claude\skills\video-use\helpers\*), PowerShell(npx --yes hyperframes *), PowerShell(robocopy *)
---

Read `workflows/create.md` and execute it end-to-end with **family = video**.

Optional prefills from the arguments (validate in preflight; drop silently if invalid):
- Format slug: **$1** (must exist in `formats/REGISTRY.md`)
- Persona slug: **$2** (must exist under `assets/_shared/personas/<slug>/`)
- App slug: **$3** (default `mode-earn`)

Flow: Phase-0 silent preflight → launch `tools/intake_form.py --family video`
(+ `--prefill` for any valid args) and wait for the ONE form submit → resolve the
format's `format.md` + `sop.md` + `learnings.md` → run the pipeline stages with the
format's recipes. The ONLY interactive loops after the form are script approval and
the editable-timeline review. Honor every standing rule in `CLAUDE.md`, the format's
LOCKED sections, and the QA gates + guardrail loop in `workflows/generate_assets.md`.
Finish by returning the output directory with all rendered variations.
