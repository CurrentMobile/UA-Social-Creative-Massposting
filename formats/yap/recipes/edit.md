# Edit Recipe — yap

Executed by `workflows/core/edit_stage.md`. Raw, caption-forward, minimal graphics.

```yaml
timeline: chunks
layout: fullframe
graphics_slots:
  - {slot: brand, card: logo-pop, at: "spoken app name (quick)"}
  - {slot: demo,  card: app-ui-demo, at: "the reveal beat (quick flash, optional)"}
captions: big-word-by-word     # karaoke-style bouncing, center/upper — the signature
cut_style: {punch_zoom: 0.12, tight_jump_cuts: true, cut_the_breaths: true, flicker_ratio: 0.25}
music: {level: 0.20, duck: false, mood: driving/trending}
sfx: curated-first
cta: endscreen-on-spoken-cta
disclaimer: always
hook_sticker: optional         # big captions often replace it
```

<!-- LOCKED -->
- BIG animated word-by-word/phrase captions are the visual signature — not the small
  ugc lower-third.
- NO five-card motion-graphics package (at most logo-pop + a quick app-UI flash).
- Tight fast jump-cuts (cut the breaths); higher punch-zoom energy.
- ugc-single audio single-source, music 20% no duck, endscreen CTA on spoken line, and
  the editable-timeline-before-final rule carry over.
<!-- /LOCKED -->

Per-app skin from `assets/<app>/brand/`. Keep it raw — don't over-polish or it stops
reading as organic.
