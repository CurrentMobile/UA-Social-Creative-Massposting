# Workflow: Create a UGC Video (one command, end-to-end)

The orchestration SOP behind the `/create-ugc-video` slash command. It runs the whole
script → assets → edit → render → deliver pipeline (Steps 5→7) as **one interactive phase
(questions + a script-approval loop) followed by one execution phase**. This file is the
conductor — it does not re-explain each stage. It **delegates** to the existing per-stage
workflows and obeys every rule in them, in `CLAUDE.md`, and in memory.

> **Control model:** the **script approval** is the pivot. Everything before it is interactive
> (a short form, then iterate-until-approved on the scripts). What happens *after* approval depends
> on the **Autonomy** answer:
> - **Autonomy On** → script approval is the *only* stop; the run goes straight to delivery.
> - **Autonomy Off** → the run stops after each asset stage for you to tweak or approve.

## Scope & inputs
- **Scope:** Steps 5→7 only. Assumes `assets/<app>/brand/creative-direction.md` exists. Reads
  `assets/<app>/competitor-research/<date>/breakdown.md` as extra inspiration **if present** — never
  blocks on it. Does NOT run competitor research/breakdown (Steps 2–4).
- **Args:** `$1` = persona slug (required), `$2` = app slug (optional, default `mode-earn`).
- **Persona is reused from the library** `assets/_shared/personas/<slug>/`. This command does not
  create or approve a *new* persona (that has its own approval gate and can't run unattended).

## Project conventions (inherited — do not restate to the user)
- **Python:** always `.\.venv\Scripts\python.exe tools\<script> …` (never bare `python`); run from
  the project root.
- **Read manifests first:** `assets\<app>\manifest.md`, then the per-video manifest. Single source
  of truth for brand, CTA, screen recordings, asset choices.
- **Brand language (MEA):** *reward* not *pay*; *gift cards / real rewards* not *cash / money*;
  Android only; no get-rich-quick; standard stats 10M+ downloads, 4.5★, 3M+ reviews.
- All STANDING RULES in `generate_assets.md` and `edit_video.md` apply verbatim (persona/grounding/
  Samsung-S22, the five motion-graphic cards, hook sticker, full-duration disclaimer, punch zooms,
  ~30% flicker + shutter SFX, canonical caption preset, endscreen CTA on the spoken line, music 0.20
  no-duck, curated-first SFX, output-path + shared-drive sync).

---

## Phase 0 — Preflight (silent, before any questions)
1. Resolve the app (`$2`, default `mode-earn`) and read `assets\<app>\manifest.md` +
   `assets\<app>\brand\creative-direction.md`. Note the per-app CTA and `<APP-CODE>` (mode-earn → MEA).
2. Resolve the persona: confirm `assets\_shared\personas\<$1>\` exists (has `base-character.png`).
   If it does **not**, list the available personas (glob `assets\_shared\personas\*`) and **stop** —
   tell the user the persona must be created/approved first (see `generate_assets.md` Steps 1–3).
3. `\.venv\Scripts\python.exe tools\env_check.py --strict` and `higgsfield account status`.
   If ffmpeg isn't runnable, or Higgsfield shows `Session expired` / `Not authenticated`, **stop now**
   with the exact remediation (run `higgsfield auth login`; fix ffmpeg/SAC per
   [video-studio-setup]) — do not start a run that will die mid-generation and waste credits.

These two checks are the only **unavoidable** hard-stops; they hold even when Autonomy is On.

## Phase 1 — Questions (the one-time form)

**Round 1 — `AskUserQuestion` (one call, 4 questions):**
1. **Persona** — confirm `$1` (pre-selected) or pick another from the library list.
2. **Video duration** — ~30s / ~45s / ~60s.
3. **Script source** — "I'll provide a script" / "Claude writes it".
4. **Autonomy** — **On** (run straight through after script approval) / **Off** (stop to
   tweak/approve after each asset stage).

Then branch on **Script source**:

### Branch A — user provides a script
1. Ask the user to paste the script or give a file path.
2. **Use it verbatim.** Do **not** rewrite, restructure, or "improve" it. Only apply changes the
   user explicitly asks for, then re-show and confirm.
3. Make sure the six sacred labels (`HOOK / PROBLEM / SOLUTION / HOW IT WORKS / RESULT / CTA`) are
   present for `chunk_script.py`. If the provided script lacks them, **ask the user** whether to add
   the labels around their exact wording (don't silently rewrite). Capture the hook's first-3s
   sticker text (ask if not provided).
4. On approval → go to **Phase 2 (save + execute)** with this single script as the one approved cut.

### Branch B — Claude writes the script(s)
Follow `workflows/generate_scripts.md` exactly. In short:
1. **Round 2 — `AskUserQuestion`:** how many **variations** to draft (2 / 3 / 4; optional free-text
   angle steer). **Terminology (fixed):** one **variation = one distinct script/angle** — its own
   shared `PROBLEM→RESULT` body + 3 hooks + a CTA menu. At approval, **each hook the user keeps
   becomes a final cut (V1/V2/…)** that reuses that angle's body and only swaps the hook + CTA clips.
   So N variations with k kept hooks each → up to N×k final cuts, but only N bodies are generated.
2. **Novelty scan** `assets\<app>\script-library\index.md` + `approved\*.md` so we never repeat a
   prior hook or body for this persona. Briefly report what already exists.
3. Draft **one script per variation**, each = a shared `PROBLEM → SOLUTION → HOW IT WORKS → RESULT`
   body + **3 hooks** (each with its own **0–3s sticker overlay text**) + a CTA menu, in the output
   structure from `generate_scripts.md`. Apply the brand-language rules and persona voice.
4. Present **all** of them and ask **"satisfied, or want to tweak?"** Iterate — **nothing is saved
   yet** — applying edits and re-presenting until the user approves and picks which hooks + CTAs to
   ship per script (index-wise pairing → final cuts V1/V2/…).

## Phase 2 — After approval: save, then execute

**Always, regardless of Autonomy:**
1. **Save approved scripts verbatim.** Assemble each shipped hook+CTA pairing into a complete cut
   (`HOOK_i + BODY + CTA_i`, carrying hook *i*'s sticker), save one file per angle to
   `assets\<app>\script-library\approved\<YYYY-MM-DD>_<persona-slug>_<angle-slug>.md`, then register:
   `\.venv\Scripts\python.exe tools\save_approved_script.py <file>`. This is what the next run reads
   to avoid repeats — **do not skip it.**
2. **Scaffold one video project per angle** and write a complete `scripts\source-v<n>.md` per shipped
   cut (`\.venv\Scripts\python.exe tools\scaffold.py video <app> "<Angle Title>"`); set `persona:` in
   the video manifest; record each cut's sticker + hook/CTA in the manifest/edit notes.
3. **Produce videos only for the approved cuts.** Each cut shares the angle body; only its **hook +
   CTA clips** are generated per cut (the body A-roll is generated once and reused) — the cost-smart
   model from memory.

Then run the asset → edit → deliver chain. **The Autonomy answer only changes where it pauses:**

### If Autonomy is **On** — run straight through (the only stop was script approval)
- **Disable the cost dry-run gate and asset/render reviews.** Skip `--dry-run` / `higgsfield generate
  cost` confirmations and the editable-timeline review; just execute. (Permission prompts are already
  off via the allowlist / bypass launch.)
- Execute end-to-end: `generate_assets.md` (persona reused) → `edit_video.md` with every standing
  edit default → final render per cut → CTA via EDL `endscreen` → output path → robocopy sync →
  manifest/`project.md` updates.

### If Autonomy is **Off** — stop after each stage for tweak/approve, in this order
Run the same chain, but **pause at each boundary, apply the user's edits, re-show that stage, and
loop until they approve** before advancing:
1. **Script** — already approved in Phase 1.
2. **Location / environment images** — generate the environment still(s); **stop → approve.**
3. **A-roll images** — generate the pose grids + extracted talking-head first frames; **stop →
   tweak or approve** (re-prompt / re-extract / regenerate the flagged frame on feedback).
4. **B-roll images** — generate the B-roll first/last frames; **stop → tweak or approve.**
5. **Video clips** — **show the cost estimate first** (`--dry-run` + `higgsfield generate cost`),
   then generate the A-roll + B-roll Kling clips; **stop → tweak or approve** (regenerate any clip
   on feedback).
6. **Edit + render all variations** — assemble per `edit_video.md` (incl. the editable per-track
   timeline), render every cut, then **ask whether the final render needs a tweak or is approved**;
   apply edits and re-render until approved.

Whichever mode: when done, deliver and **return the output directory** and a list of every variation
file.

## Outputs
- Approved scripts saved verbatim in `assets\<app>\script-library\approved\` (+ updated `index.md`).
- One video project per angle under `assets\<app>\<video-title>\` with all assets + `edit\`.
- Final cuts at `outputs\<APP-CODE>\<videoTitleCamel>\<APP-CODE>_V<n>_<videoTitleCamel>_9x16.mp4`,
  mirrored to `G:\Shared drives\Mode AI Creative Loop\Videos`.
- A final message listing the absolute output directory and every variation produced.

## How "no permission prompts" and "disable cost dry-run" are delivered
- **No prompts:** the broad allowlist in `.claude\settings.local.json` (and the optional
  `create-ugc-video.ps1` bypass launcher) pre-authorize the pipeline tools, so the execution phase is
  silent. The `AskUserQuestion` form and the script/asset approval stops are **agent** stops, not
  permission prompts — they still appear regardless of permission mode.
- **Disable cost dry-run** is a *workflow behavior here*, not a permission setting: with Autonomy On
  the chain skips the dry-run/cost-confirm step; with Autonomy Off it surfaces the estimate at the
  video-clips stage before the paid batch.

## Edge cases
- **Persona not in library** → stop in Phase 0; offer to run the persona-creation steps first.
- **Higgsfield session expired / ffmpeg blocked** → stop in Phase 0 with remediation; never start.
- **Provided script missing sacred labels** → ask before adding labels; never silently rewrite.
- **More hooks than CTAs** → pair index-wise; reuse the last CTA (confirm if ambiguous) — per
  `generate_scripts.md`.
- **`breakdown.md` present** → cite which competitor angle inspired each script (Branch B only).
- **A clip/asset fails after retries (HTTP 502 / nsfw false-positive)** → apply the
  `generate_assets.md` recovery (re-run the call, switch to the edit pattern, or fallback model). In
  Autonomy On, retry automatically; only stop if it remains unrecoverable.
