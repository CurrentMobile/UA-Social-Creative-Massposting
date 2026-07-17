---
description: Deep technical breakdown of a reference video/image into a recreation blueprint (Gemini, Step 3b)
argument-hint: [source: winner-rank | file-path | URL] [app-slug]
model: claude-opus-4-8
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion, Bash(.venv/Scripts/python.exe tools/*), PowerShell(.venv\Scripts\python.exe tools\*)
---

Read `workflows/analyze_video.md` and execute it end-to-end.

Source resolution for **$1**:
- a bare integer → winner rank from the most recent
  `assets/<app>/competitor-research/<date>/winners.json` (pass `--winner N --date <that date>`)
- starts with `http` → `--url`
- anything else → `--file` (a `.png/.jpg/.webp` auto-runs static mode)
- missing or ambiguous → ask which reference to analyze.

App slug: **$2** (default `mode-earn`).

Honor the dry-run-first cost gate (confirm spend before the live Gemini call) and the
max-2-attempts retry rule. Finish by reporting the `blueprint.md` path plus the
handoff map (script stage inspiration, edit-stage chunk/B-roll/transition mapping).
