---
app: mode-earn
title: Laziest Way To Earn
slug: laziest-way-to-earn
status: review            # scripting | assets | editing | review | posted
platform: [tiktok, instagram]
aspect: 9:16
runtime_target_s: 45
persona: gen-z-ashley, student-chloe   # PERSON1 = Ashley (mouthy), PERSON2 = Chloe (deadpan); interviewer POV off-camera
hook: "Chase cold-open — interviewer sprints after the girls: 'Wait wait wait — ladies!'"
created: 2026-07-10
format: street-interview-2@draft
sub_format: meme-vox-pop
script_library_id: ashley-chloe-duo-laziest-way-to-earn
---

# Laziest Way To Earn

> Per-video manifest. Street-Interview Format-2 (meme-heavy Gen Z vox pop) — first run.
> Creative direction: repo root `street-interview-2-creative-direction.md`.

## Concept
POV interviewer literally SPRINTS after two college girls (shaky running camera, panting VO, mic
bobbing) — they turn around startled. Question: "laziest way you've ever earned money?" → paid-to-nap
sleep study + professional line-sitter answers → pitch → mock outrage ("That's illegal") with a
hard-cut judge-gavel meme → skepticism with a suspicious-pug-cop meme → realization → phone-up buy-in.
Format-2 grammar: 1-3s cuts, word-pop center captions (yellow/green/cyan), floating emoji + gift-card
graphics OVER the A-roll (no blur-outs), glowing logo drop on the app name, endscreen on the spoken CTA.

## Asset plan
| Asset | Kind | Speaker/beat | Notes |
|-------|------|--------------|-------|
| environment.png | still | run | sunny campus walkway, punchy saturated Format-2 grade |
| grid/img 2 | 2-shot still | c2 Ashley speaks | both girls turned around startled+amused |
| grid/img 4 | grid→extract | c4 Chloe | proud/smug nap story |
| grid/img 5 | grid→extract | c5 Ashley | deadpan line-sitter story |
| grid/img 7 | grid→extract | c7 Ashley | mock outrage "illegal" |
| grid/img 8 | grid→extract | c8 Chloe | skeptical side-eye "bro" |
| grid/img 10 | grid→extract | c10 Chloe | dawning realization |
| grid/img 11 | grid→extract | c11 Ashley | hooked, phone up (blank glowing screen, S22 Ultra) |
| Clips 2,4,5,7,8,10,11 | kling3_0 sound-on | answers | 3-5s each, voice tags verbatim |
| broll-chase | still→clip muted | c1 | POV sprint toward girls from behind |
| broll-listen | still→clip muted | c3/c6 | girls listening, amused/curious 2-shot |
| broll-looks | still→clip muted | c9 | girls exchanging "is this real" looks |
| broll-huddle | still→clip muted | c12 | girls huddled over the phone |
| meme-judge.png | still | after c7 | deep-fried judge slamming gavel "GUILTY!" (AI-generated, no scraped memes) |
| meme-pugcop.png | still | after c8 | suspicious pug in police hat (AI-generated) |
| interviewer-1/3/6/9/12.mp3 | TTS | interviewer | ElevenLabs, energetic; c1 breathless/panting |
| Clips 1,3,6,9,12 | built | interviewer | VO muxed onto muted B-roll, setpts-stretched |
| cards (emoji float, giftcard fan, stat pop, logo drop) | alpha WebM | edit | HyperFrames, Format-2: no blur behind floating cards |

## Audio choices
- Music: energetic hip-hop from `assets/music/` @ 20%, no duck
- Interviewer VO: ElevenLabs (same energetic male voice throughout, breathless take for the chase)
- SFX: whooshes on floats, gavel + "GUILTY!" on meme 1, siren blip on meme 2, cash register on
  gift-card fan, bass-drop on logo, camera shutters on flickers

## Built assets (V1, superseded where noted below)
| Path | Type | Purpose |
|------|------|---------|
| ai-videos/Clip 2/4/5/7/8/10/11.mp4 | a-roll (Kling, sound on) | girls' answers; Clip 7 EDL-trimmed 0.76→3.02 (hallucinated lead-in + whisper end-time overshoot) |
| ai-videos/Clip 1/3/6/9/12.mp4 | a-roll (built, V1) | ElevenLabs interviewer VO over muted B-roll — **superseded, see V2 below** |
| ai-videos/chase/listen/looks/huddle_b-roll.mp4 | b-roll (raw, muted) | mux sources |
| edit/animations/card_guilty.mp4, card_fraud.mp4 | meme cutaways (EDL sources) | judge GUILTY!! / pug FRAUD DEPT. |
| audio/meme-guilty.mp3 | TTS | Adam "GUILTY!!" shout |

## V2 revision (2026-07-11) — owner feedback pass
Every change below responds to explicit owner feedback on the V1 cut.

| Fix | What changed |
|-----|--------------|
| Interviewer voice sounded robotic (TTS banned) | **All ElevenLabs interviewer VO replaced.** Each line now generated via `kling3_0` sound-on using `student-jake`'s persona (face discarded, only audio kept — an "audio vehicle") + a persona-style voice tag, then muxed under REAL interviewee B-roll (not TTS+B-roll as before). See [[interviewer-vo-no-elevenlabs]]. |
| Chase needed panting + heavier camera shake | `Clip 1_v2.mp4`: chase B-roll regenerated with explicit heavy running-camera-shake prompt; interviewer's audio-vehicle line baked with breathless/gasping performance direction in the SAME generation (audio+visual combined, no B-roll overlay needed for this beat). |
| "He's actually sprinting" said after both parties fully stopped | `Clip 2_v2.mp4`: turnaround clip regenerated with residual handheld shake/stumble-settle carrying over from the chase, decaying to a stop mid-clip, so the line lands while motion is still visible. |
| Music too loud / same track as before | Swapped to `Happy_x_Macklemore_Type_Beat_2023...mp3`; `music_volume` cut from 0.2 → 0.08. |
| No ambient crowd presence | Added `audio/ambience_campus.mp3` (looped/faded "Courtyard Ambience" via `resolve_sfx.py`, 60s) as a background bed at gain 0.2. |
| Clip 11 phone faced the viewer with a blank white screen | `img-11-v2.png` + `Clip 11_v2.mp4`: Ashley now holds the phone naturally at chest height, looking DOWN at it as if searching/typing — never facing the lens. (QA's `PHONE_BACK_TO_VIEWER` flag on this shot is an intentional exception, not a defect.) |
| Missing "haven't tried Mode Earn App" beat | New line inserted after Clip 8 + the fraud meme: `Clip Newline.mp4` ("That's because you haven't tried Mode Earn App."); old turn 9 trimmed to drop its leading "Mode Earn." (now just the gift-card/stats proof). Logo pop moved to sync with this new line's spoken app name. |

### V2 built assets
| Path | Type | Purpose |
|------|------|---------|
| audio_vehicle/A1-A6_*.mp4 | Kling audio vehicles | student-jake face (discarded) + voice tag, one per interviewer line — audio extracted via `ffmpeg -vn` |
| audio/interviewer-1/3/6/newline/9/12.mp3 | extracted audio | Kling-generated interviewer VO (replaces all ElevenLabs files) |
| audio/ambience_campus.mp3 | ambient bed | looped campus crowd ambience, gain 0.2 |
| ai-images/img-11-v2.png | still | Ashley looking down at phone (fixes the blank-screen-to-viewer issue) |
| ai-videos/chase_b-roll_v2.mp4 | b-roll (muted) | heavier running-camera shake |
| ai-videos/Clip 1/2/3/6/9/11/12_v2.mp4, Clip Newline.mp4 | a-roll (built/regenerated) | all V2 fixes above |
| edit/build_new_edl.py | helper script | computes exact segment offsets + card word-sync points from real durations/transcripts |
| edit/edl.json, mix.json, master.srt, make_srt.py | edit spec (V2) | 15 beats, 20 SFX incl. ambience bed, 56 color-coded cues, new running order |
| edit/animations/card_emojifan/giftcards/stats.webm | alpha overlay cards | GSAP pop offsets re-tuned to the NEW Kling-VO word timings |

## Output
- Final: `outputs/MEA/laziestWayToEarn/MEA_V1_laziestWayToEarn_9x16.mp4` (~70.3s incl. endscreen)
- CTA: endscreen `../cta/Endscreen_9x16.mp4` fires on spoken "Mode Earn App — Google Play"
- Disclaimer: "Earnings vary. Rewards are given as redeemable points." + "Generative AI used."
- Synced: `G:\Shared drives\Mode AI Creative Loop\Videos\MEA\laziestWayToEarn\` + `format-examples\street-interview-2\`
