# Edit Recipe — split-screen

Executed by `workflows/core/edit_stage.md`.

```yaml
timeline: split
layout: split-h              # split-h = top-bottom; split-v = side-by-side (per sub_format)
lanes:
  top-bottom: {presenter: "1080x1152 @ y=0", demo: "1080x768 @ y=1152"}
  side-by-side: {presenter: "540x1920 @ x=0", demo: "540x1920 @ x=540"}
graphics_slots:
  - {slot: hook,  card: hook-sticker, at: "0s..end-of-HOOK (presenter lane)"}
  - {slot: brand, card: logo-pop,     at: "spoken app name (presenter lane)"}
demo_switches: ">=1 per beat, each SFX-tapped"
cut_style: {punch_zoom: 0.10, zoom_scope: presenter-lane-only, flicker_ratio: 0.20}
captions: {preset: canonical, margin: within-presenter-lane, clear_seam: true}
music: {level: 0.20, duck: false}
sfx: curated-first
cta: fullframe-takeover      # presenter lane resolves to full frame at the CTA beat
disclaimer: always
```

<!-- LOCKED -->
- Two synchronized lanes; the demo lane runs continuously and switches ≥1×/beat (the
  pattern interrupt — no overlay B-roll needed).
- Captions live fully inside the presenter lane and clear the lane seam.
- Zoom punches apply to the presenter lane only (never zoom the demo).
- CTA is a full-frame takeover (the split resolves) starting on the spoken CTA line.
- ugc-single audio/music/editable-timeline LOCKED rules carry over.
<!-- /LOCKED -->

Layout support note: if `build_editable_timeline.py` can't position dual video tracks
yet, compose lanes via ffmpeg per `workflows/core/edit_stage.md` §5; still deliver the
editable preview for supported tracks and flag the limitation to the owner.
Per-app skin (divider color, logo, CTA) from `assets/<app>/brand/`.
