# Edit Recipe — ugc-single

Executed by `workflows/core/edit_stage.md` (today: `workflows/edit_video.md`, whose
standing rules this recipe encodes). Cards live in `formats/_shared/graphics/`.

```yaml
timeline: chunks            # one A-roll segment per chunk, B-roll overlaid per slot
layout: fullframe
graphics_slots:
  - {slot: hook,   card: hook-sticker,    at: "0s..end-of-HOOK"}
  - {slot: demo,   card: app-ui-demo,     at: "section:HOW IT WORKS"}
  - {slot: proof,  card: reviews-montage, at: "social-proof line (scam…legit)"}
  - {slot: payout, card: cashout-counter, at: "payoff line (points add up…redeem)"}
  - {slot: value,  card: free-stamp,      at: "free/no-catch line"}
  - {slot: brand,  card: logo-pop,        at: "every spoken app-name mention"}
cut_style:
  punch_zoom: 0.10          # alternate 1.0 <-> 1.1 across consecutive ranges
  within_clip_splits: true  # split long clips at phrase boundaries, contiguous
  smooth_pushes_per_video: 1-2
  flicker_ratio: 0.30       # ~30% of cuts get light-flicker + camera-shutter SFX
captions: canonical         # Arial bold, lower-third bottom:540px, MarginV=90, heavy outline
music: {level: 0.20, duck: false}
sfx: curated-first          # resolve_sfx.py; every card entrance SFX-synced
cta: endscreen-on-spoken-cta  # EDL endscreen over last A-roll clip, starts on the spoken line
disclaimer: always          # tiny centered multi-line, full duration
```

<!-- LOCKED -->
- The five motion-graphic cards are DEFAULT on every edit (don't wait to be asked),
  each SFX-synced at its matching beat.
- Hook sticker: ONE merged opaque-WHITE curved box, dark bold centered text, ≥2
  balanced lines, leaves exactly when the hook clip ends.
- Zoom jump-cuts: visible 10% punch at every cut, alternating in/out, plus within-clip
  contiguous splits at phrase boundaries on long clips.
- Endscreen CTA `start_in_output` = the output time of the spoken "download/search"
  line from `master.srt` — never the last clip's start.
- Audio single-source: A-roll carries its own VO; B-roll muted AND audio-stripped;
  music at 20% with NO ducking.
- **Editable HyperFrames timeline BEFORE the final render, always** — every A-roll
  segment, B-roll, card, and caption its own tweakable track; wait for the owner's edits.
<!-- /LOCKED -->

Per-app skin: CTA clip, logo animation, review/cashout screenshot dirs, and disclaimer
lines come from `assets/<app>/manifest.md` + `brand/` — the recipe never hardcodes an
app. Optional `assets/<app>/brand/edit-overrides.yaml` may re-skin card colors/logo;
apps may never remove a LOCKED card.
