# Asset Recipe — lofi-text

Executed by `workflows/core/asset_stage.md`. No presenter, no VO — the inventory is
ambient scene stills → short muted loops, plus the overlay-plan text (from the script
stage, not an asset).

```yaml
assets:
  - id: ambient-scene
    kind: still
    model: gpt_image_2
    per: run
    count: {min: 3, max: 5}    # one per overlay card / thought
    refs: [app.brand.home-ui]  # + s22-ultra-front when a phone glows in-scene
    prompt: prompts/ambient-scene.md
    qa: {shot_type: broll-still, gate: C}
  - id: ambient-loop
    kind: clip
    model: kling3_0
    per: run                   # one per ambient-scene still
    from: ambient-scene
    params: {aspect_ratio: "9:16", sound: "off", duration: 5}
    prompt: prompts/loop-clip.md
    qa: {shot_type: broll-clip, gate: D, advisory: true}
```

<!-- LOCKED -->
- Image generation is ALWAYS `gpt_image_2` (standing owner rule).
- NO voiced clips, NO persona/character library — scenes are anonymous and atmospheric.
- Every loop's motion returns near its first frame (invisible loop point).
- Any phone glowing in a scene follows `formats/_shared/prompts/phone-visibility-grammar.md`
  (screen to viewer, real app UI, S22 Ultra front prop) — the app is placed
  diegetically, never held up and pitched.
- QA gate C on stills before their paid loops; a `fail` still never seeds a loop.
- Guardrails injected before prompting (`--model gpt_image_2 --shot-type broll-still`).
<!-- /LOCKED -->

Judgment calls (yours): scene selection matched to the copy's mood (rain/night/coffee/
morning), how the app is placed diegetically in each scene, which scene ends the piece
(should ease back toward the opener so the whole video can loop), grain/vignette
intensity. B-roll quota: satisfied by the scene loops themselves (one per card) — no
separate overlay B-roll.
