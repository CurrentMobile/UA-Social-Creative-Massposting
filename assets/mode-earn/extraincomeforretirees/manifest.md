---
app: mode-earn
title: ExtraIncomeForRetirees
slug: extraincomeforretirees
status: review        # scripting | assets | editing | review | posted
platform: [tiktok, instagram]
aspect: 9:16
runtime_target_s: 30
persona: retiree-female-poc   # assets/_shared/personas/<slug>/
hook: "I'm retired… the last thing I wanted was another job."
created: 2026-06-15
---

# ExtraIncomeForRetirees

> Per-video manifest. Lists every asset for this video: path · type · purpose · when-to-use.
> Keep this current as assets are added — it is what the editor reads to assemble the cut.

## Concept
A warm Mode Earn retiree testimonial: a 66-year-old grandmother explains how she earns
rewards from everyday phone use to stretch a fixed income, ending on a Google Play CTA.
Persona `retiree-female-poc` (shared library). 8 talking-head A-roll beats; B-roll planned.

## A-roll clips (voiced, 9:16, Kling 3.0 Pro, sound ON)
Generated via `workflows/generate_assets.md`. Each clip's first frame is the matching `img-N`.

| Clip | Section | First frame | Dur | Line |
|------|---------|-------------|-----|------|
| Clip 1 | HOOK | ai-images/img-1.png (sofa) | 5s | "I'm retired. The last thing I wanted was another job." |
| Clip 2 | PROBLEM | ai-images/img-2.png (kitchen) | 6s | "I'm on a fixed income, so I have to be careful with how I spend." |
| Clip 3 | SOLUTION | ai-images/img-3.png (table) | 4s | "My grandson showed me this app, Mode Earn App." |
| Clip 4 | SOLUTION | ai-images/img-4.png (window) | 5s | "At first I thought it was a scam, but it's actually simple." |
| Clip 5 | HOW | ai-images/img-5.png (phone) | 5s | "I just listen to music, scroll a bit, and it adds up points." |
| Clip 6 | RESULT | ai-images/img-6.png (sofa, mug) | 8s | "I've been using it to get grocery gift cards, so that's one less thing out of my pocket." |
| Clip 7 | CTA | ai-images/img-7.png (standing) | 5s | "If you're already on your phone, you might as well get something back." |
| Clip 8 | CTA | ai-images/img-8.png (table) | 3s | "Just search Mode Earn App on Google Play." |

## B-roll (generated — muted overlay on the A-roll)
| Over clip | File | Dur | Screen |
|-----------|------|-----|--------|
| Clip 3 | ai-videos/grandson-app_b-roll.mp4 | 4s | grandson holds phone, MEA Home UI |
| Clip 5 | ai-videos/music_b-roll.mp4 | 5s | OTSS, MEA Music screen |
| Clip 6 | ai-videos/cashout_b-roll.mp4 | 8s | OTSS, MEA Cashout (PayPal/Amazon, $45) |
| Clip 7 | ai-videos/phone-to-camera_b-roll.mp4 | 5s | reveal turn, MEA Home (Kling first+last frame) |
| (overlay) | `assets/mode-earn/MEA Reviews/*.png` | — | social-proof cards — add at edit stage, not a clip |

## Source assets
- Persona: `assets/_shared/personas/retiree-female-poc/` (base-character.png + voice-tag.md)
- Stills: `ai-images/` (environment, grid-1..8, img-1..8)
- A-roll: `ai-videos/Clip 1..8.mp4`
- Real app UI: `MEA Screenshots/` (Home, Music, News, Offers, Cashout)
- Reviews (social proof): `assets/mode-earn/MEA Reviews/` (app-wide, reusable across MEA videos)
- Logo: `assets/mode-earn/brand/MEA-logo.png`
- Provenance: `generation-log.json`
- Chunk plan: `edit/chunks.json`; VO: `scripts/vo-script.md`

## Audio choices
- Each A-roll clip carries its own Kling-generated voice (sound ON). Background music + SFX
  are added at the edit stage (`workflows/edit_video.md`).

## Output
- Final: `outputs/mode-earn_extraincomeforretirees_9x16.mp4` (edited + per-app CTA appended) — 1080×1920 @ 30fps, 40.4s, −14 LUFS.
- Status: Edited & delivered (status: review). Awaiting human review.
- Posted: <date / link when done>
