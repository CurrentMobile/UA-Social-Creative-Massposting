# Asset Recipe — clone-triple

Executed by `workflows/core/asset_stage.md`. Composite still per scene-state → A-roll
clip per turn keyed on the speaking clone.

```yaml
assets:
  - {id: environment, kind: still, model: gpt_image_2, per: run, refs: [], prompt: prompts/composite-still.md#environment, qa: {shot_type: environment, gate: A}}
  - id: composite
    kind: composite
    model: gpt_image_2
    per: scene_state           # one per distinct arrangement/poses of the clones
    refs: [persona.base-character]
    prompt: prompts/composite-still.md
    qa: {shot_type: broll-still, gate: B, max_regens: 2, focus: [IDENTITY_DRIFT, SPATIAL_INTERSECTION]}
  - id: a-roll
    kind: clip
    model: kling3_0
    per: chunk                 # one per turn; chunk.speaker -> which clone talks
    from: composite
    params: {aspect_ratio: "9:16", mode: pro, sound: "on", duration: "min(chunk.recommended_duration_s, 8)"}
    prompt: prompts/clone-clip.md
    qa: {shot_type: aroll-clip, gate: D, advisory: true, focus: [IDENTITY_DRIFT, WARDROBE_DRIFT]}
  - {id: b-roll, kind: clip, model: kling3_0, per: section, count: {min: 1}, params: {aspect_ratio: "9:16", sound: "off"}, prompt: prompts/b-roll-bank.md, qa: {shot_type: broll-still, gate: C}}
```

<!-- LOCKED -->
- Image gen ALWAYS `gpt_image_2` — the composite is built with GPT Image 2 from the
  persona base-character reference (never Nano Banana or another model).
- ALL clones use the SAME voice tag (one person); attitude/gesture varies per clone.
- Turns are ≤8s (Kling drifts the non-speaking clone on longer takes).
- QA checks EVERY clone (identity + wardrobe) at first AND last frame; re-roll on drift.
- Phone reveal follows the phone visibility grammar.
<!-- /LOCKED -->

Judgment calls: clone roles + poses per composite; optional subtle distinguishing
accessory per clone; how many scene-states (one composite can serve several
consecutive turns if the arrangement holds); clone-triple vs falling back to
clone-double when drift is bad.
