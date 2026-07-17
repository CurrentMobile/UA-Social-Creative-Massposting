# Asset Recipe — split-screen

Executed by `workflows/core/asset_stage.md`. Presenter A-roll per chunk + a demo lane
(imported screen recordings preferred, generated loops as fallback).

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: prompts/a-roll-still.md#environment, qa: {shot_type: environment, gate: A}}
  - {id: pose-grid, kind: still, model: gpt_image_2, per: chunk, refs: [persona.base-character, environment], prompt: prompts/a-roll-still.md#grid, qa: {shot_type: grid, gate: A}}
  - {id: first-frame, kind: still, model: gpt_image_2, per: chunk, from: pose-grid, prompt: prompts/a-roll-still.md#extract, qa: {shot_type: extract, gate: B, max_regens: 2}}
  - {id: a-roll, kind: clip, model: kling3_0, per: chunk, from: first-frame, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}, prompt: prompts/a-roll-clip.md, qa: {shot_type: aroll-clip, gate: D, advisory: true}}
  - id: demo-lane
    kind: import               # PREFER screen recordings; generate only on miss
    source: assets/_shared/screen-recordings/<app>/
    fallback: {kind: clip, model: kling3_0, prompt: prompts/demo-lane.md, params: {sound: "off"}}
    per: section               # >=1 demo content per beat (the pattern-interrupt quota)
    qa: {shot_type: broll-clip, gate: D, advisory: true}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; A-roll sound ON.
- Presenter stills/clips are framed CROP-SAFE for the lane (subject centered, medium,
  headroom) — the lane crops the 9:16 frame.
- Demo lane prefers REAL app screen recordings (real UI); generate loops only on miss.
- The demo-lane switch per beat satisfies the B-roll quota (no separate overlay B-roll).
- Phone in the presenter lane follows the phone visibility grammar.
- QA gates; guardrails injected before prompting.
<!-- /LOCKED -->

Judgment calls: sub-format (top-bottom vs side-by-side), which recording matches each
beat, lane proportions, when the demo switches.
