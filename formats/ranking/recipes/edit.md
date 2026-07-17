# Edit Recipe — ranking

Executed by `workflows/core/edit_stage.md`. ugc-single cut style + a ranking-badge per
item + a #1 celebration.

```yaml
timeline: chunks
layout: fullframe
graphics_slots:
  - {slot: hook,   card: hook-sticker,    at: "0s..end-of-HOOK"}
  - {slot: rank,   card: ranking-badge,   at: "item:* (enter item-first-chunk, exit item-last-chunk)"}
  - {slot: demo,   card: app-ui-demo,     at: "RANK 1 segment"}
  - {slot: payout, card: cashout-counter, at: "RANK 1 segment"}
  - {slot: brand,  card: logo-pop,        at: "spoken app name (rank 1 + CTA)"}
  - {slot: value,  card: free-stamp,      at: "CTA (optional)"}
cut_style: {punch_zoom: 0.10, within_clip_splits: true, flicker_ratio: 0.30, sfx_escalation: "badge impact climbs 5->1"}
captions: canonical
music: {level: 0.20, duck: false}
sfx: curated-first
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- ranking-badge fires on EVERY item; #1 gets the celebration treatment (gold/glow +
  confetti + biggest SFX).
- The app demo cards (app-ui-demo, cashout-counter, logo-pop) live on the RANK 1
  segment — that's the only place real app UI appears.
- All ugc-single LOCKED rules carry over (hook sticker, punch zooms, endscreen CTA on
  spoken line, audio single-source, editable timeline before final render).
<!-- /LOCKED -->

Per-app skin from `assets/<app>/manifest.md` + `brand/`. Badge colors may be re-skinned
via `brand/edit-overrides.yaml`; the badge-every-item rule can't be removed.
