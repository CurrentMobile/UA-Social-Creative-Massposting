# Asset Recipe — ugc-multi-location

Executed by `workflows/core/asset_stage.md`. Like ugc-single but one environment per
location and per-location grids/extracts, with a strict reference chain.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: location, refs: [], prompt: prompts/a-roll-still.md#environment, qa: {shot_type: environment, gate: A}}
  - {id: pose-grid, kind: still, model: gpt_image_2, per: chunk, refs: [persona.base-character, location.environment], prompt: prompts/a-roll-still.md#grid, qa: {shot_type: grid, gate: A}}
  - {id: first-frame, kind: still, model: gpt_image_2, per: chunk, from: pose-grid, prompt: prompts/a-roll-still.md#extract, qa: {shot_type: extract, gate: B, max_regens: 2, focus: [IDENTITY_DRIFT, WARDROBE_DRIFT]}}
  - {id: a-roll, kind: clip, model: kling3_0, per: chunk, from: first-frame, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}, prompt: prompts/a-roll-clip.md, qa: {shot_type: aroll-clip, gate: D, advisory: true, focus: [IDENTITY_DRIFT, WARDROBE_DRIFT]}}
  - {id: b-roll, kind: clip, model: kling3_0, per: section, count: {min: 1}, params: {aspect_ratio: "9:16", sound: "off"}, prompt: prompts/b-roll-bank.md, qa: {shot_type: broll-still, gate: C}}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; A-roll sound ON.
- `base-character.png` passed on EVERY still (reference chain); wardrobe named
  identically per the wardrobe policy at every location.
- `per: location` expands environments; each chunk's grid uses THAT chunk's location.
- QA checks identity + wardrobe against the base at every location (Gate B + Gate D).
- Phone shots follow the phone visibility grammar; B-roll quota per beat enforced.
<!-- /LOCKED -->

Judgment calls: the location arc (which beat where), wardrobe policy (one outfit vs
per-location plan), per-location action, how many locations (3-4; fewer if drift is bad).
