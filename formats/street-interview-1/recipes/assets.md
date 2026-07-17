# Asset Recipe — street-interview-1

Executed by `workflows/core/asset_stage.md`. Inherits the base interview mechanics
(`formats/interview/recipes/assets.md`) with Format-1 overrides marked ★.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: formats/interview/prompts/interviewee-still.md#environment, qa: {shot_type: environment, gate: A}}
  - {id: interviewee-grid, kind: still, model: gpt_image_2, per: chunk, refs: [speaker.base-character, environment, _shared/props/handheld-mic], prompt: formats/interview/prompts/interviewee-still.md#grid, qa: {shot_type: grid, gate: A}}
  - {id: interviewee-frame, kind: still, model: gpt_image_2, per: chunk, from: interviewee-grid, prompt: formats/interview/prompts/interviewee-still.md#extract, qa: {shot_type: extract, gate: B, max_regens: 2, focus: [IDENTITY_DRIFT, WARDROBE_DRIFT]}}
  - {id: answer, kind: clip, model: kling3_0, per: chunk, from: interviewee-frame, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}, prompt: formats/interview/prompts/answer-clip.md, qa: {shot_type: aroll-clip, gate: D, advisory: true, focus: [IDENTITY_DRIFT, WARDROBE_DRIFT]}}
  - {id: interviewer-broll, kind: clip, model: kling3_0, per: interviewer-chunk, params: {aspect_ratio: "9:16", mode: pro, sound: "off", duration: 3-5}, note: "★ establishing POV / listening / double-take / look-around / squint — muted footage for the VO mux", qa: {shot_type: broll-still, gate: C}}
  - {id: interviewer-vo, kind: tts, provider: elevenlabs, per: interviewer-chunk, note: "★ one energetic voice verbatim across all lines"}
  - {id: interviewer-clip, kind: built, per: interviewer-chunk, note: "★ ffmpeg mux: VO onto muted B-roll, setpts-stretched to VO length, gblur baked from the popup in-point"}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; interviewee answer clips sound ON; interviewer B-roll sound OFF.
- POV v1: the interviewer is NEVER rendered — voice + mic-in-frame only.
- ★ **No app UI on held phones.** The phone-up beat's first-frame shows a bright BLANK glowing
  screen facing the camera (never the back panel). All UI/proof arrives as edit-time popup cards.
- ★ **The interviewee never holds the mic or its cable** — the unseen interviewer does. Prompt it
  positively ("his other hand is relaxed at his side — he holds NOTHING else").
- ★ **VO timing is the anchor:** stretch/tile footage to the TTS length via `setpts`, never trim
  or speed up the VO to fit footage.
- QA checks the interviewee's identity + wardrobe across every turn (the core risk).
<!-- /LOCKED -->

Gotchas measured on the validated run (details in `learnings.md` + `formats/interview/learnings.md`):
Kling adds unscripted dialogue to sound-on clips (trim via EDL range start from the transcript);
GPT Image 2's img2img pathway can fail server-side while text-only works (A/B test, fall back
`nano_banana_flash` WITH the persona base passed as an identity reference, visually confirm);
GPT Image 2 NSFW-false-positives person+phone closeups (PIL-crop the grid cell, edit-pattern the
expansion).
