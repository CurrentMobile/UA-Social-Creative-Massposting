# Workflow: Create Content (format-agnostic conductor)

The single entry point behind `/create-videos` and `/create-statics`. Reads the
chosen format's manifest (`formats/<slug>/format.md`) and drives the shared pipeline
— script → assets → edit → render → deliver — with the format's recipes plugged into
each stage. `workflows/create_ugc_video.md` is the ugc-single-only ancestor and stays
valid; this file generalizes it.

## Invocation

`/create-videos [format] [persona] [app]` → family=video
`/create-statics [format] [app]`         → family=static
Args are optional prefills. `$ARGUMENTS` may carry them in that order.

## Phase 0 — Silent preflight (`workflows/core/preflight.md`)

Run BEFORE the form. Hard stops only; no questions the tool can answer itself.

## Phase 1 — ONE intake form round (`workflows/core/intake.md`)

Launch `tools/intake_form.py` — a single browser form capturing EVERYTHING (app,
format + preview, sub-format, persona(s), duration, variations, script source + paste,
autonomy, brief, notes). Read the resulting intake JSON; it is the single source of
run parameters and gets recorded in the video manifest. **No further question rounds**
— the only interactive loops after this are script approval and the editable-timeline
review (quality gates, not intake).

If the user picked "New app": run `workflows/onboard_app.md` (scaffold + draft
creative-direction from their brief + ONE approval), then continue.

## Phase 2 — Resolve the format

Read `formats/<slug>/format.md` frontmatter: anatomy, pipeline stages, models, cost
estimate, personas spec, locked_rules. Read the format's `sop.md` — it is the
step-by-step law for this run. Read `formats/<slug>/learnings.md` and apply entries
that don't contradict LOCKED rules. Print the format's `cost_estimate` to the user
before any paid stage.

## Phase 2.5 — Reference blueprint (conditional)

If the intake carries a `reference_source`, run `workflows/analyze_video.md` on it
now (dry-run cost gate → deep Gemini analysis → `blueprint.md` under
`assets/<app>/reference-analysis/`). Record the blueprint path in the video manifest.
Downstream: the script stage reads its overview + transcript as inspiration; the edit
stage maps its scene table / B-roll triggers / transition specs onto `chunks.json` —
as the structural contract when `reference_mode: recreate`, as style cues when
`inspiration`.

## Phase 3 — Pipeline stages (per the format's `pipeline:` map)

| Stage | Core file | Format plug-in |
|-------|-----------|----------------|
| script | `workflows/core/script_stage.md` | `anatomy:` + format-tagged script library |
| assets | `workflows/core/asset_stage.md` | `formats/<slug>/recipes/assets.md` + `prompts/` |
| edit | `workflows/core/edit_stage.md` | `formats/<slug>/recipes/edit.md` |
| deliver | `workflows/core/deliver.md` | format examples seeding |

A stage omitted from the format's `pipeline:` map is skipped (statics omit `edit`).

## Autonomy (from the intake form)

- **On:** run straight through after script approval — no per-stage stops, cost
  dry-runs pre-authorized. Still stops: script approval, editable timeline (video
  formats), any Gate-D QA fail, any Gate-B double-fail.
- **Off:** stop after each asset stage (environment / grids+extracts / B-roll stills /
  clips with cost estimate / final edit) for review, exactly as
  `create_ugc_video.md` defines.

## Standing rules

- Scripts saved verbatim on approval (`save_approved_script.py --format <slug>`);
  novelty scan filters by format tag.
- `check_formats_lock.py` ran in preflight — agents never modify `formats/` except
  `learnings.md`.
- Video manifest records `format: <slug>@<version>` + the intake JSON path.
- Every deliverable syncs to the shared drive (see `core/deliver.md`).
