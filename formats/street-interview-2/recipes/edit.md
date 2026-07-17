# Edit Recipe — street-interview-2 (the Format-2 editing structure)

Executed by `workflows/core/edit_stage.md`. Worked example:
`assets/mode-earn/laziest-way-to-earn/edit/` (edl.json + mix.json + make_srt.py).

## 1. Timeline shape

```yaml
timeline: turns              # 1-3s cuts; long clips SPLIT into multiple ranges (zoom-alternating jump cuts)
layout: fullframe
graphics_slots:
  - {slot: hook,   card: hook-sticker,     at: "chase cold-open — a meme caption about the chase itself, leaves when the chase VO ends"}
  - {slot: meme1,  card: meme-cutaway mp4, at: "after the mock-outrage turn — EDL SOURCE, 1.0s, meme SFX/VO in mix.json"}
  - {slot: meme2,  card: meme-cutaway mp4, at: "after the flat-skepticism turn — EDL SOURCE, ~1.1s"}
  - {slot: emoji,  card: emoji-fan webm,   at: "earning-methods line — each emoji pops ON its spoken word"}
  - {slot: brand,  card: logo-pop webm,    at: "spoken app name"}
  - {slot: chips,  card: brand-chip fan,   at: "redemption line — chips pop on Amazon/PayPal words"}
  - {slot: stats,  card: stat pop,         at: "social-proof line — 10M+ slide + 4.5★ seek-safe count-up"}
cut_style: {punch_zoom: 0.10, alternate: true, smooth_push_opener: true, flicker_ratio: 0.25, handheld_energy: true}
captions: format2            # bold uppercase center-lower, 2-4 word cues; hook window yellow, money words green
music: {level: 0.20, duck: false}
sfx: curated-first           # meme sounds ARE the format: turntable scratch + shouted VO on meme1, "huh" on meme2, win-rewards on logo, cash register on chips, ting on stars, shutter per flicker
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- Meme cutaways enter as EDL **sources** (opaque mp4), not overlays; floating cards enter as
  alpha-WebM **overlays** with NO blur and NO caption blackout (captions coexist).
- Card pop times come from the VO word transcripts — never eyeballed.
- Word-synced offsets: overlay start_in_output = segment_out_start + (word_t − range_start).
- Editable per-track timeline before the final render — always.
<!-- /LOCKED -->

## 2. Caption identity (Format-2)

Restyle the generated timeline's `.cap` block: Arial 900 uppercase 72px, center-lower
(bottom:560px), heavy black outline; add classes `hookc` (yellow #ffe14d, cues in the hook
window) and `money` (green #3dfc7e, cues containing gift/amazon/paypal/reward/free/earn/paid/
downloads/stars). Strip `<span>` tags before keyword matching.

## 3. Assembly + final

- Brand skin from `assets/<app>/manifest.md` + `brand/` (logo webm, endscreen, disclaimer).
- `build_editable_timeline.py` → caption restyle → `npx hyperframes render --quality high`
  → loudnorm −14 LUFS → deliver per `workflows/core/deliver.md`.
- Post-render QC: blackdetect, frame-grab every card/meme window, caption/card collisions.
