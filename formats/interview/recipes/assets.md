# Asset Recipe — interview (POV interviewer)

Executed by `workflows/core/asset_stage.md`. Per-interviewee stills → per-turn clips;
the interviewer is off-camera (voice/mic only) in v1.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: prompts/interviewee-still.md#environment, qa: {shot_type: environment, gate: A}}
  - {id: interviewee-grid, kind: still, model: gpt_image_2, per: chunk, refs: [speaker.base-character, environment, _shared/props/handheld-mic], prompt: prompts/interviewee-still.md#grid, qa: {shot_type: grid, gate: A}}
  - {id: interviewee-frame, kind: still, model: gpt_image_2, per: chunk, from: interviewee-grid, prompt: prompts/interviewee-still.md#extract, qa: {shot_type: extract, gate: B, max_regens: 2, focus: [IDENTITY_DRIFT, WARDROBE_DRIFT]}}
  - {id: answer, kind: clip, model: kling3_0, per: chunk, from: interviewee-frame, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}, prompt: prompts/answer-clip.md, qa: {shot_type: aroll-clip, gate: D, advisory: true, focus: [IDENTITY_DRIFT, WARDROBE_DRIFT]}}
  - {id: b-roll, kind: clip, model: kling3_0, per: section, count: {min: 1}, params: {aspect_ratio: "9:16", sound: "off"}, prompt: prompts/b-roll-bank.md, qa: {shot_type: broll-still, gate: C}}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; answer clips sound ON.
- POV v1: the interviewer is NEVER rendered — only interviewee faces. Each interviewee
  keyed on the chunk's `speaker`, with their OWN base reference + named wardrobe.
- INTERVIEWER turns are audio-only (voiced clip over a mic/establishing cutaway, or a VO
  track in the edit) — no interviewer face.
- Handheld street framing; a mic prop may enter frame. Phone reveals follow the phone
  grammar.
- QA checks EACH interviewee's identity + wardrobe across their turns.
<!-- /LOCKED -->

Judgment calls: 1 vs 2 interviewees, their looks/wardrobe, street setting, how the mic
sits in frame, when an interviewee pulls out their phone. Fall back to one interviewee
if the second drifts.
