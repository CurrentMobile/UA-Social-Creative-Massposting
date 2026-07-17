# Asset Recipe — ugc-single

Executed by `workflows/core/asset_stage.md` (today: `workflows/generate_assets.md`).
The YAML inventory declares WHAT to generate and its cardinality; the prose after it is
the SOP judgment. `per:` expansion: `run` = once per video; `persona_env` = once per
(persona × environment); `chunk` = one per `chunks.json` entry; `section` = per script
beat.

```yaml
assets:
  - id: environment
    kind: still
    model: gpt_image_2
    per: run
    refs: []
    prompt: prompts/a-roll-still.md#environment
    qa: {shot_type: environment, gate: A}
  - id: pose-grid
    kind: still
    model: gpt_image_2
    per: chunk
    refs: [persona.base-character, environment]
    prompt: prompts/a-roll-still.md#grid
    qa: {shot_type: grid, gate: A}
  - id: first-frame
    kind: still
    model: gpt_image_2
    per: chunk
    from: pose-grid
    prompt: prompts/a-roll-still.md#extract
    qa: {shot_type: extract, gate: B, max_regens: 2}
  - id: a-roll
    kind: clip
    model: kling3_0
    per: chunk
    from: first-frame
    params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}
    prompt: prompts/a-roll-clip.md
    qa: {shot_type: aroll-clip, gate: D, advisory: true}
  - id: b-roll
    kind: clip
    model: kling3_0
    per: section
    count: {min: 1}          # HARD quota — see broll_slots in chunks.json
    params: {aspect_ratio: "9:16", sound: "off", duration: match_a_roll}
    prompt: prompts/b-roll-bank.md
    qa: {shot_type: broll-still, gate: C}
```

<!-- LOCKED -->
- Image generation is ALWAYS `gpt_image_2` (standing owner rule — never another image
  model unless the user explicitly asks; documented fallback for content-filter false
  positives only, visually confirmed).
- A-roll = `--sound on` (Kling speaks the dialogue with the persona voice tag pasted
  verbatim); B-roll = `--sound off` (overlaid muted).
- Every required `broll_slots` slot is filled BEFORE clip generation; `check_assets.py`
  fails QC otherwise.
- Every phone shot follows `formats/_shared/prompts/phone-visibility-grammar.md`.
- QA gates A-D per `workflows/generate_assets.md` — a `fail` asset never seeds a paid
  Kling job; Gate-B regenerate loop caps at 2 attempts then stops for the owner.
- Guardrails injected before prompt authoring: `guardrails.py inject --model <m>
  --shot-type <s>`.
<!-- /LOCKED -->

Judgment calls (yours): pose variety per grid (fresh location-in-location/pose per
beat = pattern interruption), which grid cell to extract (clean + realistic + grounded
beats "best pose"), B-roll concepts (bank categories, never repeat the registry),
per-clip gesture direction matched to the persona's personality table.
