# Edit Recipe — clone-triple

Executed by `workflows/core/edit_stage.md`. ugc-single base + conversation cutting.

```yaml
timeline: turns             # cut between turns like a dialogue
layout: fullframe           # the clones share one composite frame (not split-screen)
graphics_slots:
  - {slot: hook,  card: hook-sticker, at: "0s..end-of-HOOK"}
  - {slot: demo,  card: app-ui-demo,  at: "the turn where the hyped clone shows the app"}
  - {slot: brand, card: logo-pop,     at: "spoken app name"}
  - {slot: value, card: free-stamp,   at: "payoff turn (optional)"}
cut_style: {punch_zoom: 0.10, punch_on_speaker: true, flicker_ratio: 0.20}
grade: {per_clone_accent: "subtle cool=skeptic / warm=hyped (optional)"}
captions: canonical
music: {level: 0.20, duck: false}
sfx: curated-first
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- Cut between turns; punch-in slightly on the speaking clone.
- All ugc-single LOCKED rules carry over (hook sticker, endscreen CTA on spoken line,
  audio single-source, music 20% no duck, editable timeline before final render).
<!-- /LOCKED -->

Per-app skin from `assets/<app>/manifest.md` + `brand/`. The per-clone color accent is
optional flair, not a locked rule.
