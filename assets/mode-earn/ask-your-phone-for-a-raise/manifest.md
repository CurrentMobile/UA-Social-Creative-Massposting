---
app: mode-earn
title: Ask Your Phone For A Raise
slug: ask-your-phone-for-a-raise
status: review           # scripting | assets | editing | review | posted
platform: [tiktok, instagram]
aspect: 9:16
runtime_target_s: 30
persona: student-jake     # PERSON1 (only rendered face; interviewer is POV off-camera)
hook: "Would you let your phone earn rewards while you scroll?"
created: 2026-07-09
format: interview@0.1.0
sub_format: pov-interviewer
intake: .tmp/intake/intake-20260709-154812.json
script_library_id: student-jake-ask-your-phone-for-a-raise
---

# Ask Your Phone For A Raise

> Per-video manifest. Lists every asset for this video: path · type · purpose · when-to-use.
> Keep this current as assets are added — it is what the editor reads to assemble the cut.

## Concept
Fast-paced street vox pop (POV interviewer, never on camera): an off-camera interviewer
stops Broke Student Jake on a campus walkway; Jake goes skeptic → sold in 8 rapid turns
and pulls out his phone (S22 Ultra, screen-to-camera, real app UI) on "downloading it
right now." Endscreen CTA fires on the spoken "Mode Earn App — Google Play" line.

## Assets
| Path | Type | Purpose | When to use |
|------|------|---------|-------------|
| ai-videos/Clip 2.mp4 | a-roll | Jake skeptic answer (Kling, sound on) — range starts 1.15s to trim a hallucinated extra line | turn 2 |
| ai-videos/Clip 4.mp4 | a-roll | Jake curious answer (Kling, sound on) | turn 4 |
| ai-videos/Clip 6.mp4 | a-roll | Jake disbelief answer (Kling, sound on) | turn 6 |
| ai-videos/Clip 8.mp4 | a-roll | Jake sold + phone up, blank glowing screen (v2 re-roll) | turn 8 |
| ai-videos/Clip 1.mp4 | a-roll (built) | interviewer VO over establishing POV | turn 1 (hook) |
| ai-videos/Clip 3.mp4 | a-roll (built) | interviewer VO over listening B-roll (slowed to VO length) | turn 3 |
| ai-videos/Clip 5.mp4 | a-roll (built) | interviewer VO over double-take + establishing tail, blur baked from 0.55s (cashout popup) | turn 5 |
| ai-videos/Clip 7.mp4 | a-roll (built) | interviewer VO over look-around, blur baked from 0.3s (reviews popup) | turn 7 |
| ai-videos/Clip 9.mp4 | a-roll (built) | interviewer CTA VO over squint (under endscreen) | turn 9 (CTA) |
| ai-videos/establishing_b-roll.mp4 | b-roll (raw) | interviewer POV approach, mic thrusting in | source for Clips 1/5 |
| ai-videos/listening_b-roll.mp4 | b-roll (raw) | Jake listening, eyebrows rising | source for Clip 3 |
| ai-videos/double-take_b-roll.mp4 | b-roll (raw) | comedic double-take at the mic | source for Clip 5 |
| ai-videos/look-around_b-roll.mp4 | b-roll (raw) | "is this a prank?" glance around | source for Clip 7 |
| ai-videos/squint-insert_b-roll.mp4 | b-roll (raw) | skeptic squint insert | source for Clip 9 |
| audio/interviewer-1.mp3 | audio | interviewer VO (ElevenLabs "Liam") | Clip 1 |
| audio/interviewer-3.mp3 | audio | interviewer VO | Clip 3 |
| audio/interviewer-5.mp3 | audio | interviewer VO | Clip 5 |
| audio/interviewer-7.mp3 | audio | interviewer VO | Clip 7 |
| audio/interviewer-9.mp3 | audio | interviewer CTA VO | Clip 9 |
| edit/animations/card_cashout.webm | alpha card | real cashout screenshot popup + reward chips | 12.58s (blur behind) |
| edit/animations/card_reviews.webm | alpha card | 4.5★ count-up + real review cards | 18.68s (blur behind) |
| edit/animations/card_free.webm | alpha card | NO CATCH / 100% FREE stamp | 4.95s |
| edit/edl.json | edit spec | ranges, overlays, flickers, hook sticker, endscreen, disclaimer | drives timeline + render |
| edit/mix.json | edit spec | music @20% no-duck + 16 SFX | timeline audio tracks |
| edit/master.srt | captions | word-accurate captions (build_srt.py) | caption track |

**Popup-UI rule (owner, this run):** no app UI composited on held phones — UI/reviews/logo pop up
as cards while the interviewee blurs behind (blur baked into Clips 5/7). `check_assets.py` reports
slots 1/3/5/7/9 as "missing b-roll" because they're covered by the VO-muxed clips + popup cards —
structural false positive for the interview format.

## Screen recordings used
| Name (in _shared/screen-recordings/mode-earn/) | When to use |
|---|---|
| | |

## Audio choices
- Background music: upbeat hip-hop — `assets/music/Energetic_Hip_Hop_Background_Music_For_Videos_No_Copyright [rjkH08kM1BQ].mp3` @ 20%, no duck
- Interviewer VO: ElevenLabs "Liam" (energetic social-media creator), 5 lines in `audio/`
- SFX: pops (hook/cards/logo/chips), camera shutters (4 flickers + review slams), deep whooshes (cutaway + endscreen), cash register (cashout card) — full plan in `edit/mix.json`

## Output
- Final: `outputs/MEA/askYourPhoneForARaise/MEA_V1_askYourPhoneForARaise_9x16.mp4` (31.3s)
- CTA: endscreen overlay (per-app `../cta/Endscreen_9x16.mp4`) starting on the spoken "Mode Earn App — Google Play" line (23.75s), per the interview recipe
- Synced: `G:\Shared drives\Mode AI Creative Loop\Videos\MEA\askYourPhoneForARaise\` + seeded `format-examples\interview\`
- Posted: <date / link when done>
