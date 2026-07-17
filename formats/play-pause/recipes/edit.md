# Edit Recipe — play-pause

Executed by `workflows/core/edit_stage.md` (`layout: pip-corner`).

```yaml
timeline: turns              # watch beats + reactor talk turns, gated by PAUSE events
layout: pip-corner           # reactor full-frame; overlay clip in a top corner window
graphics_slots:
  - {slot: hook,   card: hook-sticker, at: "0s..end-of-HOOK"}
  - {slot: pause,  card: pause-freeze, at: "every PAUSE edit_event"}
  - {slot: brand,  card: logo-pop,     at: "spoken app name"}
pip: {position: top-corner, plays_during: watch-beats, freezes_on: PAUSE}
cut_style: {punch_zoom: 0.10, punch_on: pause-reaction, flicker_ratio: 0.20}
captions: {preset: canonical, clear_of: pip-window}
music: {level: 0.20, duck: false}
sfx: {pause: tape-stop/record-scratch, resume: soft-play, curated_first: true}
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- The PiP plays during watch beats and FREEZES at every PAUSE edit event with the
  pause-freeze card + a tape-stop SFX; a soft play SFX on resume.
- The reactor talks only while the PiP is paused; PiP audio is muted (reactor narrates).
- Captions never overlap the PiP window.
- ugc-single audio/music/hook-sticker/endscreen/editable-timeline LOCKED rules carry over.
<!-- /LOCKED -->

Layout note: `pip-corner` needs positioned-track support; if `build_editable_timeline.py`
lacks it, compose the PiP + freeze via ffmpeg per `core/edit_stage.md` §5 and flag it.
Per-app skin from `assets/<app>/brand/`.
