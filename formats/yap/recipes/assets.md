# Asset Recipe — yap

Executed by `workflows/core/asset_stage.md`. Like ugc-single but selfie-framed and with
the B-roll quota intentionally relaxed.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: prompts/a-roll-still.md#environment, qa: {shot_type: environment, gate: A}}
  - {id: pose-grid, kind: still, model: gpt_image_2, per: chunk, refs: [persona.base-character, environment], prompt: prompts/a-roll-still.md#grid, qa: {shot_type: grid, gate: A}}
  - {id: first-frame, kind: still, model: gpt_image_2, per: chunk, from: pose-grid, prompt: prompts/a-roll-still.md#extract, qa: {shot_type: extract, gate: B, max_regens: 2}}
  - {id: a-roll, kind: clip, model: kling3_0, per: chunk, from: first-frame, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}, prompt: prompts/a-roll-clip.md, qa: {shot_type: aroll-clip, gate: D, advisory: true}}
  - {id: b-roll, kind: clip, model: kling3_0, per: section, count: {min: 0, max: 2}, params: {aspect_ratio: "9:16", sound: "off"}, prompt: prompts/b-roll-bank.md, qa: {shot_type: broll-still, gate: C}}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; A-roll sound ON.
- Framing is a CLOSE, slightly-high SELFIE angle, face filling the frame, raw/unpolished
  — never a styled studio setup.
- B-roll is minimal (count.min 0, max ~2) — the raw talking IS the format; do NOT apply
  the ugc B-roll quota here. (check_assets.py won't flag missing B-roll for this format.)
- Phone shots (holding up to show the app) follow the phone visibility grammar.
- QA gates; guardrails injected before prompting.
<!-- /LOCKED -->

Judgment calls: rant cadence and energy, expression variety per chunk, whether to
include the 1-2 app-reveal cutaways or run pure talking.
