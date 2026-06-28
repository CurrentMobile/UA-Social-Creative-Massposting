---
app: mode-earn
title: Viral App Guinea Pig
slug: viral-app-guinea-pig
status: editing          # scripting | assets | editing | review | posted
platform: [tiktok, instagram]
aspect: 9:16
runtime_target_s: 30
persona: gen-z-ashley     # persona slug in assets/_shared/personas/<slug>/ (for AI asset gen)
hook: "I download every viral app so you don't have to… and bestie, this is the first one that actually rewarded me."   # V1 hook
created: 2026-06-21
---

# Viral App Guinea Pig

> Per-video manifest. Lists every asset for this video: path · type · purpose · when-to-use.
> Keep this current as assets are added — it is what the editor reads to assemble the cut.

## Concept
Gen Z Ashley (avatar `gen-z-ashley`) is the friend who tests every viral app — Mode Earn is the rare
legit one that rewards you for what you already do. **3 A/B variations share one body**; each swaps the
hook (with its own 0–3s sticker) and the CTA. Full script:
`../script-library/approved/2026-06-21_gen-z-ashley_viral-app-guinea-pig.md`.

### Variations (hook + sticker → CTA)
| V | Source | Sticker (0–3s overlay) | CTA gist |
|---|--------|------------------------|----------|
| V1 | scripts/source-v1.md | I test viral apps so you don't 🧪 | Download on Google Play |
| V2 | scripts/source-v2.md | every app's a scam… except this 👀 | Download free now |
| V3 | scripts/source-v3.md | delete the rest, keep this one | Search on Play Store |

## Assets
| Path | Type | Purpose | When to use |
|------|------|---------|-------------|
| ai-videos/ | a-roll/b-roll | AI / recorded clips | source footage |
| ai-images/ | image | stills / overlays | … |
| audio/ | audio | VO / generated audio | … |
| scripts/ | script | avatar dialogue script | drives the cut |
| sops/ | sop | brief / instructions | follow when editing |

## Screen recordings used
| Name (in _shared/screen-recordings/mode-earn/) | When to use |
|---|---|
| | |

## Audio choices
- Background music: upbeat pop — `assets/music/FREE_Lauv_Type_Beat_Pop_Type_Beat_-_7AM [XEkbF_vwnPY].mp3` @ 20% (no ducking)
- SFX: pop-1 @0.2s (hook sticker) · A deep whoosh @17.0s & 33.4s (B-roll cutaways) · Cash register @42.0s (reward payoff)
- A-roll clips carry their own Kling VO (single audio source per HF-render rule)

## Output  (status: review — all variations rendered 2026-06-23)
All in `outputs/MEA/viral-app-guinea-pig/`. Two cut styles per script variation: standard + `I2` (in-clip punch-zoom jump cuts). CTA overlaid via EDL endscreen on the spoken CTA word (HF-render path; not append_cta).
| File | Hook+CTA | Cut | Len | Sticker |
|------|----------|-----|-----|---------|
| MEA_V0_…9x16.mp4 | V1 (rough draft) | std | 57.8s | I test viral apps… |
| MEA_V1_…9x16.mp4 | Hook A + CTA 1 | std | 54.1s | I test viral apps so you don't 🧪 |
| MEA_V1I2_…9x16.mp4 | Hook A + CTA 1 | jump-cut | 54.1s | (same) |
| MEA_V2_…9x16.mp4 | Hook B + CTA 2 | std | 55.6s | every app's a scam… except this 👀 |
| MEA_V2I2_…9x16.mp4 | Hook B + CTA 2 | jump-cut | 55.6s | (same) |
| MEA_V3_…9x16.mp4 | Hook C + CTA 3 | std | 51.7s | delete the rest, keep this one |
| MEA_V3I2_…9x16.mp4 | Hook C + CTA 3 | jump-cut | 51.7s | (same) |
- Editable timelines: `edit/editable-timeline` (V2) · `editable-timeline-v3` · `-v2i2` · `-v3i2`.
- New clips: `ai-videos/{hook2,hook3,cta2,cta3}.mp4` (gen-z-ashley, reused keyframes). Body clips 2–9 shared across all.
- Pending: 30-second cut (deferred). Posted: <date / link when done>
