# Asset Recipe — ranking

Executed by `workflows/core/asset_stage.md`. Same shape as ugc-single, keyed on ranked
items.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: prompts/a-roll-still.md#environment, qa: {shot_type: environment, gate: A}}
  - {id: pose-grid, kind: still, model: gpt_image_2, per: chunk, refs: [persona.base-character, environment], prompt: prompts/a-roll-still.md#grid, qa: {shot_type: grid, gate: A}}
  - {id: first-frame, kind: still, model: gpt_image_2, per: chunk, from: pose-grid, prompt: prompts/a-roll-still.md#extract, qa: {shot_type: extract, gate: B, max_regens: 2}}
  - {id: a-roll, kind: clip, model: kling3_0, per: chunk, from: first-frame, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}, prompt: prompts/a-roll-clip.md, qa: {shot_type: aroll-clip, gate: D, advisory: true}}
  - {id: b-roll, kind: clip, model: kling3_0, per: section, count: {min: 1}, params: {aspect_ratio: "9:16", sound: "off", duration: match_a_roll}, prompt: prompts/b-roll-bank.md, qa: {shot_type: broll-still, gate: C}}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; A-roll sound ON, B-roll sound OFF.
- **Competitors stay GENERIC:** ranks 5-2 B-roll (and any prop) describe the category
  only — NO real competitor name, logo, or UI. Only rank 1 (our app) is named + real UI.
- **Phone reveal / real app UI ONLY on the rank-1 segment**; phone visibility grammar.
- Every required `broll_slots` slot filled before clips; `check_assets.py` enforces.
- QA gates A-D; Gate-B regen loop caps at 2 then stops for the owner.
- Guardrails injected before prompting.
<!-- /LOCKED -->

Judgment calls: the per-rank expression arc (unimpressed low ranks → excitement at #1),
which generic visual represents each category safely, pose variety per rank.
