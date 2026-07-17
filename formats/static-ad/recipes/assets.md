# Asset Recipe — static-ad

Executed by `workflows/core/asset_stage.md`. Base visuals (GPT Image 2) → text
compositing (HyperFrames 1-frame render). No edit stage, no clips.

```yaml
assets:
  - id: base-visual
    kind: still
    model: gpt_image_2
    per: variation             # one base per copy/angle variation
    refs: []                   # + persona.base-character (lifestyle), s22-ultra-front + app.brand.ui (phone in frame)
    prompt: prompts/base-visual.md   # sub-style section chosen from the intake sub_format
    qa: {shot_type: phone-shot, gate: C}   # broll-still for meme/review backgrounds
  - id: composite
    kind: composite            # HyperFrames 1-frame HTML render, per aspect
    engine: hyperframes-still
    per: aspect                # 9:16, 1:1, 4:5 from format.md aspect list
    from: base-visual
    prompt: prompts/compose-layout.md
    qa: {shot_type: broll-still, gate: C, focus: WARPED_TEXT}
```

<!-- LOCKED -->
- Base visuals are ALWAYS `gpt_image_2` (standing owner rule).
- Prefer clean negative-space / plate areas in the base and composite REAL text on top
  (HyperFrames) rather than letting the model bake headline text — baked text warps.
- Every phone in a base follows `formats/_shared/prompts/phone-visibility-grammar.md`.
- Brand font/colors/logo/badge/disclaimer come from `assets/<app>/brand/` — never
  hardcoded, and the disclaimer appears on every creative.
- QA gate C on every base AND every composite (WARPED_TEXT on the composite is a hard
  gate — text is the point of a static ad).
- Guardrails injected before prompting.
<!-- /LOCKED -->

Judgment calls (yours): sub-style selection matched to the angle; where to leave
negative space for copy; layout hierarchy; how "polished" vs "organic" per sub-style
(ugc-screenshot-style deliberately rough, feature-callout deliberately clean).
