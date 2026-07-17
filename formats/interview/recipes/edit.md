# Edit Recipe — interview (POV interviewer)

Executed by `workflows/core/edit_stage.md`.

```yaml
timeline: turns             # question (off-cam) -> answer (on-cam), documentary rhythm
layout: fullframe
graphics_slots:
  - {slot: hook,  card: hook-sticker, at: "opening question"}
  - {slot: demo,  card: app-ui-demo,  at: "the 'it earns points' beat"}
  - {slot: brand, card: logo-pop,     at: "spoken app name"}
cut_style: {punch_zoom: 0.10, punch_on: reactions, handheld_energy: true, flicker_ratio: 0.20}
captions: canonical         # big-caption optional for punchy answers
music: {level: 0.20, duck: false}
sfx: curated-first
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- POV: the interviewer is heard, not seen (mic/establishing cutaway over their lines).
- Cut between off-camera question and on-camera answer with documentary pacing.
- ugc-single audio/hook-sticker/endscreen/editable-timeline LOCKED rules carry over.
<!-- /LOCKED -->

Per-app skin from `assets/<app>/brand/`. Handheld street energy is the look — don't
over-stabilize.
