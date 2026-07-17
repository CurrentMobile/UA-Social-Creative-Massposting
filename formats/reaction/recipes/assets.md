# Asset Recipe — reaction

Executed by `workflows/core/asset_stage.md`. Reactor setup + a reaction clip per turn;
the reacted-to source is imported (owned/generated), not per-turn generated.

```yaml
assets:
  - {id: reactor-setup, kind: still, model: gpt_image_2, per: run, refs: [persona.base-character], prompt: prompts/reactor-still.md, qa: {shot_type: extract, gate: B, max_regens: 2}}
  - {id: reaction, kind: clip, model: kling3_0, per: chunk, from: reactor-setup, params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: chunk.recommended_duration_s}, prompt: prompts/reaction-clip.md, qa: {shot_type: aroll-clip, gate: D, advisory: true}}
  - id: source-clip
    kind: import               # owned/generated ONLY
    source: assets/<app>/ (our footage / prior ad) OR generated app-UI claim clip
    fallback: {kind: clip, model: kling3_0, prompt: prompts/source-clip.md, params: {sound: "off"}}
    per: run                   # one source, reused
    qa: {shot_type: broll-clip, gate: C}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2`; reaction clips sound ON, source muted.
- React ONLY to owned or generated content (never a third party's copyrighted video
  without the owner's explicit clearance).
- green-screen-style setup uses a keyable background (matte via video-use bg-removal).
- Source shows the REAL app UI where the app appears; phone visibility grammar.
- QA gates; guardrails injected before prompting.
<!-- /LOCKED -->

Judgment calls: sub-style (green-screen vs corner-cam), reactor energy, what owned/
generated clip to react to, reactor placement over the source.
