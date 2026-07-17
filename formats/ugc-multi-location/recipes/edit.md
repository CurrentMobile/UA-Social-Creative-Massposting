# Edit Recipe — ugc-multi-location

Executed by `workflows/core/edit_stage.md`. ugc-single cut style + location transitions.

```yaml
timeline: chunks
layout: fullframe
graphics_slots:
  - {slot: hook,   card: hook-sticker,    at: "0s..end-of-HOOK"}
  - {slot: demo,   card: app-ui-demo,     at: "section:HOW IT WORKS"}
  - {slot: proof,  card: reviews-montage, at: "social-proof line"}
  - {slot: payout, card: cashout-counter, at: "payoff line"}
  - {slot: value,  card: free-stamp,      at: "free/no-catch line"}
  - {slot: brand,  card: logo-pop,        at: "every spoken app name"}
location_transitions: "on beat boundaries; quick whip/match transition, SFX-tapped"
cut_style: {punch_zoom: 0.10, within_clip_splits: true, flicker_ratio: 0.30}
captions: canonical
music: {level: 0.20, duck: false}
sfx: curated-first
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- Location changes land on beat boundaries with a transition SFX.
- All ugc-single LOCKED rules carry over (five cards, hook sticker, punch zooms,
  endscreen CTA on spoken line, audio single-source, editable timeline before final).
<!-- /LOCKED -->

Per-app skin from `assets/<app>/manifest.md` + `brand/`.
