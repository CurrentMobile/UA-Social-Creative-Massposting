# Asset Recipe — street-interview-2

Executed by `workflows/core/asset_stage.md`. Inherits base interview mechanics
(`formats/interview/recipes/assets.md`) with Format-2 overrides marked ★.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: formats/interview/prompts/interviewee-still.md#environment, qa: {shot_type: environment, gate: A}, note: "★ punchy saturated high-contrast grade in the prompt"}
  - {id: duo-chase, kind: still, model: gpt_image_2, per: run, refs: [persona1.base, persona2.base, environment, _shared/props/handheld-mic], note: "★ POV sprint from BEHIND the duo, motion blur, mic thrusting in", qa: {shot_type: broll-still, gate: C}}
  - {id: duo-turnaround / duo-listen / duo-looks / duo-huddle, kind: still, model: gpt_image_2, per: run, refs: [persona1.base, persona2.base, environment, mic, (+s22 for huddle)], note: "★ direct 9:16 duo singles, no grid; identical per-video wardrobe phrase in EVERY prompt", qa: {shot_type: broll-still, gate: C}}
  - {id: interviewee-grid, kind: still, model: gpt_image_2, per: solo-chunk, refs: [speaker.base, environment, mic], prompt: formats/interview/prompts/interviewee-still.md#grid, qa: {shot_type: grid, gate: A}}
  - {id: interviewee-frame, kind: still, model: gpt_image_2, per: solo-chunk, from: interviewee-grid, qa: {shot_type: extract, gate: B, max_regens: 2, focus: [IDENTITY_DRIFT]}, note: "★ on drift, re-extract WITH the persona base as an extra reference"}
  - {id: meme-still, kind: still, model: gpt_image_2, per: meme-beat, refs: [], note: "★ AI-generated meme-style photo, deep-fried grade, NO text (text added at edit)", qa: {eyeball only}}
  - {id: answer, kind: clip, model: kling3_0, per: chunk, from: interviewee-frame|duo-still, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: 3-5}, note: "★ duo clips: name WHICH girl speaks; transcribe every clip (hallucinated lead-ins → EDL trim)"}
  - {id: muted-broll, kind: clip, model: kling3_0, per: interviewer-chunk, params: {sound: "off", duration: 4-5}, note: "★ chase/listen/looks/huddle"}
  - {id: interviewer-vo, kind: tts, provider: elevenlabs, per: interviewer-chunk, note: "★ tools/tts_elevenlabs.py, voice Liam TX3LPaxmHKxFdv7VOQHJ; chase line style 0.85 stability 0.3"}
  - {id: interviewer-clip, kind: built, per: interviewer-chunk, note: "★ ffmpeg: VO anchor — trim when footage longer, setpts when shorter, CONCAT two B-rolls for long VO lines. NO gblur (no blur cards in Format-2)"}
  - {id: word-timings, kind: built, per: vo+clip, note: "★ hyperframes transcribe → edit/transcripts/*.words.json (drives card sync + master.srt); the tool writes audio/transcript.json — mv it per file"}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; interviewee answer clips sound ON; muted B-roll sound OFF.
- POV: the interviewer is NEVER rendered — voice + mic-in-frame only. Interviewees never hold
  the mic or its cable.
- ★ Meme cutaways are AI-generated — never scraped/spliced real internet memes.
- ★ Held phones: bright BLANK glowing screen facing the viewer (never the back panel).
- ★ Per-video wardrobe is allowed to differ from the persona base — name it identically in every
  prompt; QA context must state the intent (wardrobe-vs-base mismatch = expected false positive,
  cross-asset consistency is the real gate).
- Higgsfield concurrency: max 8 jobs in flight per model family — batch submissions.
<!-- /LOCKED -->
