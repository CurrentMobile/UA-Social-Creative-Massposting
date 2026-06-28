---
app: mode-earn
title: Extra Cushion On A Budget
slug: extra-cushion-on-a-budget
status: review        # scripting | assets | editing | review | posted
platform: [tiktok, instagram]
aspect: 9:16
runtime_target_s: 45
persona: female-caucasian   # persona slug in assets/_shared/personas/<slug>/ (for AI asset gen)
hook: "I'm a widowed 52 year old, not a good time to be on a tight budget. But I just found a way to cover groceries with gift cards from my phone."
created: 2026-06-28
---

# Extra Cushion On A Budget

> Per-video manifest. Lists every asset for this video: path · type · purpose · when-to-use.
> Keep this current as assets are added — it is what the editor reads to assemble the cut.

## Concept
A budget-conscious widowed 52-yo mom (`female-caucasian`) turns the screen time she's already
spending into gift cards that cushion groceries & family treats — no extra spending, no second job.
Approved script: `assets/mode-earn/script-library/approved/2026-06-28_female-caucasian_extra-cushion-on-a-budget.md`.
**Edit steer:** fast-paced, lots of movement & energy.

## Variations (shared body; only HOOK + its 0–3s sticker + CTA differ per cut)
| Cut | Hook (spoken) | Sticker (0–3s) | CTA |
|-----|---------------|----------------|-----|
| V1 | "I'm a widowed 52 year old, not a good time to be on a tight budget. But I just found a way to cover groceries with gift cards from my phone." | Groceries on gift cards now 🛒 | "If your grocery bill keeps climbing, let your phone help. Download Mode Earn App on Google Play. It's free." |
| V2 | "Everything's become more expensive lately. So here's the little trick that's been giving my budget some breathing room." | Everything at the store costs more lately? 😓 | "Give your budget a little breathing room. Search Mode Earn App on the Play Store, it's free to download." |
| V3 | "If money's tight right now, come closer — this is how my phone helps without me spending a thing." | your phone can help 📱 | "You're on your phone anyway! Why not make it count? Get Mode Earn App on Google Play, it's totally free." |

Source files: `scripts/source-v1.md`, `scripts/source-v2.md`, `scripts/source-v3.md` (each = its HOOK + shared body + its CTA, all six sacred labels). Body A-roll generated once and reused across cuts; only hook + CTA clips differ.

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
- Background music: <mood / chosen track path>
- SFX: <effect @ timestamp, …>

## Output
Rendered 2026-06-28 via the editable-timeline → `npx hyperframes render` path (VO+music+SFX+endscreen
baked in; CTA is the EDL `endscreen` overlay on the spoken download line — NOT append_cta.py). 9:16, 30fps.
- V1 (Hook A + CTA 1): `outputs/MEA/extraCushionOnABudget/MEA_V1_extraCushionOnABudget_9x16.mp4` — 63.2s
- V2 (Hook B + CTA 2): `outputs/MEA/extraCushionOnABudget/MEA_V2_extraCushionOnABudget_9x16.mp4` — 60.2s
- V3 (Hook C + CTA 3): `outputs/MEA/extraCushionOnABudget/MEA_V3_extraCushionOnABudget_9x16.mp4` — 60.6s
- Mirrored to the shared drive Videos tree under MEA/extraCushionOnABudget.
- CTA: per-app endscreen (app-level CTA 9x16 clip) baked into each render. Posted: <date / link when done>

## Assets generated
- A-roll: 15 Kling clips in ai-videos (hook1, hook2, Clip 3..Clip 10, cta1, hookB, cta2, hookC, cta3) — body shared, hook+CTA per cut.
- B-roll (muted, in ai-videos): broll-receipt, broll-reveal (phone-to-camera Mode Earn Home reveal), broll-news (used); broll-giftcards (generated, held).
- First frames: img-N PNGs in ai-images (direct medium-shot generation, persona female-caucasian + Samsung S22 prop).
- Cards reused (app-level, content-identical) under edit/animations: mg_reviews, mg_home, mg_cashout_switch, mg_free, + brand logo pop.
- Edit dirs: editable-timeline-v1/v2/v3 (per-variation HyperFrames projects); edl.json/mix.json/master.srt under edit hold the LAST-built (v3).
