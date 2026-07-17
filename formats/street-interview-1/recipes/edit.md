# Edit Recipe — street-interview-1 (the Format-1 editing structure)

Executed by `workflows/core/edit_stage.md`. This recipe IS the format — the exact editing
structure and popup motion-graphics system of the validated
`outputs/MEA/askYourPhoneForARaise/MEA_V1_askYourPhoneForARaise_9x16.mp4`.

## 1. Timeline shape

```yaml
timeline: turns             # question (off-cam VO-muxed clip) -> answer (on-cam), documentary rhythm
layout: fullframe
graphics_slots:
  - {slot: hook,   card: hook-sticker,        at: "opening question, leaves when it ends"}
  - {slot: claim,  card: popup-impact-stamp,  at: "the single most emphatic claim (e.g. 'No catch') — ONCE per video"}
  - {slot: brand,  card: logo-pop,            at: "spoken app name (brand webm)"}
  - {slot: proof1, card: popup-phone-chips,   at: "the reward/redemption beat — real UI screenshot + fanned chips"}
  - {slot: proof2, card: popup-stat-proof,    at: "the rating/downloads beat — count-up + sliding review cards"}
cut_style: {punch_zoom: 0.10, alternate: true, smooth_push_opener: true, flicker_ratio: 0.30, handheld_energy: true}
captions: canonical         # lower-third; caption_blackouts under every full-attention card window
music: {level: 0.20, duck: false}
sfx: curated-first          # one pop per card entrance, shutter per flicker + per proof-card slam, cash register on the money card, whoosh on cutaway + endscreen
cta: endscreen-on-spoken-cta
disclaimer: always
```

<!-- LOCKED -->
- POV: the interviewer is heard, never seen (their turns are VO-muxed clips, see the asset recipe).
- **Popup rule:** all app proof (UI screenshots / ratings / reviews / logo) fires as popup cards
  over a BLURRED interviewee (blur baked into the underlying clip for exactly the card window);
  captions blacked out under each full-attention card.
- **Four-phase card lifecycle** (§3) on every card. Impact-slam entrances at most ONCE per video.
- ugc-single audio/hook-sticker/endscreen/editable-timeline LOCKED rules carry over.
<!-- /LOCKED -->

## 2. Popup cards, mechanically

Each card is a **standalone HyperFrames project** (own `index.html`, short `data-duration`,
transparent background) rendered once to **alpha WebM** (`hyperframes render --format webm`) and
wired into the EDL as an `overlays` entry — never baked into the main composition's markup. This
keeps every card independently tweakable/re-renderable and reusable across videos (swap the
screenshot, keep the motion). Render + eyeball each card standalone BEFORE wiring it.

```jsonc
// edl.json
"overlays": [
  { "file": "animations/card_<name>.webm",
    "start_in_output": 12.58,        // when it appears in the final timeline
    "duration": 3.9,                  // ≤ the card's own data-duration
    "keep_audio": false,
    "note": "what this card is / why it fires here" }
],
"caption_blackouts": [[12.58, 16.48]] // suppress captions for the same window
```

## 3. The motion language (the reusable grammar)

Every card follows the same four-phase shape:

```
ENTER → (SECONDARY POP-INS, staggered, if multi-element) → IDLE (float/wobble/breathe) → EXIT
```

| Phase | What | Ease | Duration |
|---|---|---|---|
| **Enter** | Primary element pops/drops/slams in | `back.out(1.8–2.2)` friendly pop · `power3.in` impact slam | 0.28–0.55s |
| **Secondaries** | Chips/pills/proof cards, staggered ~0.2s apart, each with its OWN ± rotation so a fan feels organic | `back.out(2.0–2.2)` pop · `power3.out` long-travel slide | 0.4s each |
| **Idle** | Slow small yoyo — vertical drift, rotation wobble, or scale breathe — offset per element so nothing bobs in unison and nothing ever freezes | `sine.inOut`, `yoyo:true`, `repeat:1` | 0.7–1.6s |
| **Exit** | Everything shrinks+fades together, ~0.02s stagger — never a hard vanish | `power2.in` | 0.2–0.25s |

**Easing vocabulary by intent:**
- `back.out(N)` — springy overshoot for anything *friendly/bouncy* (cards, chips, pills). Higher N = punchier.
- `power3.in` — accelerating slam, no overshoot. The impact-stamp entrance ONLY; once per video.
- `power3.out` — fast start, soft landing. For long-travel slides (off-screen → on-screen) where an overshoot would fly back off-frame.
- `power2.in` — the universal EXIT across all cards (consistent exits make many cards feel like one system).
- `sine.inOut` + yoyo — the universal IDLE. Breathing, not animating.
- `ease:"none"` — ONLY for a literal impact shake (x:±10, 0.05s, repeat:3); linear is what makes it percussive.

**Seek-safe count-ups:** tween a plain JS object and write `textContent` in `onUpdate`, paired
with a width tween on a clipped "fill" glyph layer (stars/progress) at the same rate — scrubs and
renders frame-accurately.

## 4. The three card archetypes (skeletons in `../cards/`)

| Archetype | Folder | Use when | In the validated output |
|---|---|---|---|
| **A — Phone Card + Fanned Chips** | `cards/popup-phone-chips/` | a screenshot needs 2-3 labels fanning around it | cashout screenshot + PayPal/Amazon/Best Buy chips |
| **B — Stat + Count-Up + Sliding Proof** | `cards/popup-stat-proof/` | a number counts up with proof sliding in beside it | 4.5★ count-up + 10M+ pill + two review screenshots |
| **C — Impact Stamp** | `cards/popup-impact-stamp/` | ONE punchy claim slams in | "NO CATCH. / 100% FREE" |

Each skeleton has the GSAP timeline inlined with WHY-comments; `REPLACE_ME_*` markers show where
new content goes — keep the choreography (timings/eases/stagger offsets), swap the content. Lint
flags the placeholder images as missing until real ones are dropped in (expected). Position the
impact stamp in an EMPTY screen third — never over the interviewee's face (self-eval catch from
the first run).

## 5. Assembly + final

- Brand skin from `assets/<app>/manifest.md` + `brand/` (logo webm, endscreen, disclaimer lines).
- `build_editable_timeline.py` → per-track editable preview (mandatory review gate) →
  `npx hyperframes render --quality high` → loudnorm −14 LUFS → deliver.
- Post-render QC: blackdetect, frame-grab every card window, caption/card collisions.
