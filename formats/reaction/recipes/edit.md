# Edit Recipe — reaction

Executed by `workflows/core/edit_stage.md`.

```yaml
timeline: turns
layout: pip-corner           # corner-cam; green-screen-style = matted reactor over full-frame source
graphics_slots:
  - {slot: hook,  card: hook-sticker, at: "0s..end-of-HOOK"}
  - {slot: pause, card: pause-freeze, at: "optional emphasis PAUSE events"}
  - {slot: brand, card: logo-pop,     at: "spoken app name"}
source: {plays: continuous, muted: true, layout: "full-frame behind reactor"}
reactor: {green-screen-style: "matted cutout over source", corner-cam: "corner bubble"}
cut_style: {punch_zoom: 0.10, punch_on: big-reactions, flicker_ratio: 0.20}
captions: {preset: canonical, clear_of: "reactor bubble + source key areas"}
music: {level: 0.20, duck: false}
sfx: curated-first
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- The source plays continuously and MUTED; the reactor's audio carries.
- green-screen-style requires a clean reactor matte; corner-cam keeps the source
  full-frame with the reactor in a bordered bubble.
- ugc-single audio/hook-sticker/endscreen/editable-timeline LOCKED rules carry over.
<!-- /LOCKED -->

Layout note: matte/PiP compositing may need the ffmpeg fallback per `core/edit_stage.md`
§5. Per-app skin from `assets/<app>/brand/`.
