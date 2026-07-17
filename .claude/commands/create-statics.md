---
description: Create static image ad creatives (one-shot intake form → copy → images → deliver)
argument-hint: [format-slug] [app-slug]
model: claude-opus-4-8
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion, Bash(.venv/Scripts/python.exe tools/*), Bash(npx --yes hyperframes *), Bash(npx hyperframes *), Bash(higgsfield *), PowerShell(.venv\Scripts\python.exe tools\*), PowerShell(npx --yes hyperframes *), PowerShell(robocopy *)
---

Read `workflows/create.md` and execute it end-to-end with **family = static**.

Optional prefills from the arguments (validate in preflight; drop silently if invalid):
- Format slug: **$1** (must exist in `formats/REGISTRY.md` with family `static`)
- App slug: **$2** (default `mode-earn`)

Flow: Phase-0 silent preflight → launch `tools/intake_form.py --family static`
(+ `--prefill` for any valid args) and wait for the ONE form submit → resolve the
format's `format.md` + `sop.md` → run the static pipeline (copy variants → approval →
GPT Image 2 generation → text compositing → deliver PNGs at every declared aspect).
Statics skip the edit stage; the copy still goes through the script library
(format-tagged) and images still pass the QA gates. Image generation is ALWAYS
`gpt_image_2` unless the user explicitly overrides.
