# Asset Recipe — play-pause

Executed by `workflows/core/asset_stage.md`. One watching-setup still → a reaction clip
per talk turn; the overlay (PiP) clip is imported/reused, not per-turn.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: prompts/reactor-still.md#environment, qa: {shot_type: environment, gate: A}}
  - id: watching-still
    kind: still
    model: gpt_image_2
    per: run
    refs: [persona.base-character, environment]
    prompt: prompts/reactor-still.md
    qa: {shot_type: extract, gate: B, max_regens: 2}
  - id: reaction
    kind: clip
    model: kling3_0
    per: chunk                 # one per reactor talk turn (PAUSE lines are edit events, not clips)
    from: watching-still
    params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}
    prompt: prompts/reaction-clip.md
    qa: {shot_type: aroll-clip, gate: D, advisory: true}
  - id: overlay-clip
    kind: import               # PREFER a real screen recording; generate on miss
    source: assets/_shared/screen-recordings/<app>/
    fallback: {kind: clip, model: kling3_0, prompt: prompts/overlay-clip.md, params: {sound: "off"}}
    per: run                   # one clip, reused across PiP windows
    qa: {shot_type: broll-clip, gate: C}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; reaction clips sound ON, overlay muted.
- The watching setup is a static angled front view with clean top-corner space for the
  PiP.
- The overlay content shows the REAL app UI (screen recording preferred); phone/screen
  follows the phone visibility grammar.
- QA gates; guardrails injected before prompting.
<!-- /LOCKED -->

Judgment calls: reactor pose/energy, which app moment the PiP plays before each pause,
where the PiP window sits (top corner clear of captions).
