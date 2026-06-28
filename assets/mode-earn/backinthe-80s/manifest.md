---
app: mode-earn
title: Backinthe 80s
slug: backinthe-80s
status: editing          # scripting | assets | editing | review | posted
platform: [tiktok, instagram]
aspect: 9:16
runtime_target_s: 60
hook: "Back in the 80s, if you wanted a little something extra ... you had to go out and work for it."
created: 2026-06-02
---

# Backinthe 80s

Retiree testimonial: a grandmother explains how Mode Earn App lets her earn rewards from
everyday phone use. Talking-head A-roll (AI avatar) with B-roll cutaways at cue points,
ending on the app CTA.

## Edit spec (from brief)
- Order A-roll Clip 1–9 per `scripts/vo-script.md`; remove dead space + filler; cut out any
  next-clip bleed at clip ends.
- Every cut on a clip = jump-cut with a 10% zoom step (alternate in→out→in per successive cut
  on the same clip); mix smooth zooms with cut zooms. Maintain 9:16 (1080×1920).
- Captions: ≤4 words on screen at a time, centered, narrow (not full width).
- Subtle background music; per-app CTA appended at the end.

## Assets
| Path | Type | Purpose | When to use |
|------|------|---------|-------------|
| ai-videos/ | a-roll (avatar VO), Clip 1–9 | talking-head narration | backbone, in script order |
| ai-videos/Girl and Grandma with Phone_b-roll.mp4 | b-roll | grandchild shows app | line 5 ("My grandchild showed me…") |
| ai-videos/Playing a game_b-roll.mp4 | b-roll | gaming | line 8 ("Playing a game") |
| ai-videos/Putting on some music_b-roll.mp4 | b-roll | music | line 8 ("Putting on some music") |
| ai-videos/Reading the news_b-roll.mp4 | b-roll | news + coffee | line 8 ("Reading the news…") |
| ai-videos/Turn Phone to Camera_b-roll.mp4 | b-roll | phone to camera | line 11 ("on that phone anyway") |
| ../brand/MEA-Logo-Animation-POP-UP.mov | logo | Mode Earn logo pop | line 7 ("It's called Mode Earn App") |
| ../cta/CTA_9x16.mp4 | cta | end screen | appended at end (line 12) |
| scripts/vo-script.md | script | VO + B-roll cue map | clip placement |

## Audio choices  (v2)
- Background music: `assets/music/Slow_Acoustic_Guitar_Instrumental_-_Quiet_Place_Original [ZPGi2yBqdqw].mp3`
  at **20% of the A-roll level, NO ducking** (`mix.json` music_volume 0.20).
- Captions: previous style — Arial bold, lower-third, natural case, heavy black outline.
- Turn Phone B-roll: first 4s trimmed (`trim_start: 4.0`), slowed to fill its segment.
- A-roll carries its own VO (single source — fixes the v1 echo/silent-start). B-roll fully muted.
- SFX (curated): **Ting.MP3** (ding) on "the points add up" @31.7s; **Cash register.MP3** (cha-ching)
  on the gift-cards line @36.0s — synced to the pop-ups.

## Build  (v2 — canonical editable-timeline path)
- Source of truth: `edit/edl.json` + `edit/master.srt` (`tools/build_srt.py`) + `edit/mix.json`.
- Timeline: `tools/build_editable_timeline.py edit/` → `edit/editable-timeline/` (A-roll tracks 0/4
  carry own VO + zoom; B-roll tracks 1/5 muted+filled-to-segment; logo+pop-up cards track 2;
  captions track 3; endscreen track 8 overlaying the last clip; music+SFX tracks 11+).
- Pop-ups: `edit/animations/popup_points` & `popup_dollars` → alpha WebM cards.
- Final render: `npx hyperframes render edit/editable-timeline -o edit/final.mp4` (music/SFX/CTA all
  baked in — no separate mix_audio/append_cta).
- Runtime: 61.6s (CTA overlays Clip 9, untrimmed). Captions ≤4 words, centered.

## Output
- Final: `outputs/mode-earn_backinthe-80s_9x16.mp4`  ✅ v2 rendered from editable timeline
- CTA: overlaid on the last A-roll clip, untrimmed (not appended)
- Synced to: `G:\Shared drives\Mode AI Creative Loop\Videos`
- Posted: <date / link when done>
