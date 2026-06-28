# Workflow: Input & Briefing (Step 1)

Turn raw inputs the user drops (creative direction, UGC creator briefs, sample scripts) into a
distilled, machine-readable brief that every later step reads. This is **Step 1** of the
mass-posting workflow and the foundation Step 5 (Script Generation) depends on.

## Objective
Keep one **single source of truth per app** — `assets/<app>/brand/creative-direction.md` — and a
current app `manifest.md`, so script writing and asset generation never have to re-read raw `.docx`.

## Inputs
- Dropped briefs in `assets/<app>/<some-brief-folder>/` (`.docx`, `.md`, `.pdf`, `.txt`).
  For Mode Earn these live in `assets/mode-earn/MEA-SCRIPT-WRITING-GUIDES-AND-BRIEF/`.
- The existing app `manifest.md` and any existing `brand/creative-direction.md`.

## Tools
- `tools/extract_docx.py` — `.docx → text`. Stdlib-only, reusable.
  `.venv\Scripts\python.exe tools/extract_docx.py "<file.docx>"` (add `--out file.md` to save).
  For `.pdf` use the `pdf` skill; `.md`/`.txt` read directly.
- `tools/check_manifest.py` — validate manifest paths after editing.

## Steps
1. **Read what exists first.** `assets/<app>/manifest.md`, then `brand/creative-direction.md` if
   present. Don't duplicate — you're updating, not starting over.
2. **Extract every dropped brief** to text with `extract_docx.py` (or the right reader per type).
3. **Distill, don't dump.** Update `brand/creative-direction.md` with:
   - App snapshot, voice & tone
   - **Language rules** (do/don't word swaps) and **compliance disclaimers**
   - **Social-proof stats** — standardize one set of numbers; flag inconsistent ones in source copy
   - Psychological triggers, messaging pillars
   - **Script anatomy** with the sacred section labels (`HOOK/PROBLEM/SOLUTION/HOW IT WORKS/RESULT/CTA`)
   - **Target personas → presenter-avatar mapping** (slugs in `assets/_shared/personas/`, with status)
   - Keep the source files in place as the archive; note them at the bottom of the brief.
4. **Update the app manifest** — fill `About the app`, `Brand`, and `Voice` sections; point to
   `brand/creative-direction.md` for detail. Don't fork a parallel doc.
5. **Validate** with `tools/check_manifest.py <app>` and fix any broken paths.

## Outputs
- `assets/<app>/brand/creative-direction.md` (updated, the source of truth)
- `assets/<app>/manifest.md` (About/Brand/Voice filled, pointing to the brief)

## Edge cases & notes
- **Persona mismatch.** The brief may define audience archetypes that don't yet have avatars in
  `assets/_shared/personas/`. Record the mapping with a status (`exists` / `to create`); avatar
  creation itself is Step 6, not here.
- **Stat drift.** Sample scripts often disagree on download/rating numbers. Pick the official set
  from the creative-direction doc and note which to ignore.
- **Never paste secrets** into brief/manifest files (they sync to the shared Drive). Keys stay in
  root `.env` only.
- **FUTURE (Steps 2–4):** competitor research and winning-video breakdowns will also feed this step.
  Add a "Competitor inspiration" section to the brief when that lands — leave the hook ready.
