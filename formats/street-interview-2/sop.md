# SOP — Street-Interview Format-2 (`street-interview-2` v0.1.0)

Step-by-step law for the meme-vox-pop edition. Validated end-to-end by
`outputs/MEA/laziestWayToEarn/MEA_V1_laziestWayToEarn_9x16.mp4` (2026-07-10).
<!-- LOCKED --> sections are non-negotiable; run learnings go to `learnings.md` only.
Base interview mechanics (turn anatomy, grid→extract→clip, per-face QA): `formats/interview/sop.md`.

---

## 1. Creative overview

- **Arc:** chase cold-open → absurd street answers → pitch → mock outrage + meme cut → skepticism
  + meme cut → realization → phone-up buy-in → CTA. ~12 turns, 45-60s, cuts every 1-3s.
- <!-- LOCKED --> POV interviewer: heard, never seen. **Chase hook:** the opening interviewer turn
  plays over a sprinting POV B-roll (running shake, mic bobbing, breathless VO) toward the
  interviewees, who turn around startled. <!-- /LOCKED -->
- **Two interviewees**, contrasting energies (one bubbly/mouthy, one dry/deadpan). Their banter
  carries the comedy: answers must sound like real people (false starts, fragments, "bro", "like
  an idiot"), never ad copy. Interviewer lines carry the facts.
- <!-- LOCKED --> **Meme cutaways are AI-GENERATED** meme-style stills (deep-fried grade, harsh
  flash) + Impact-font text + punch zoom, built as ~1s HyperFrames mp4s and cut in as EDL
  *sources* with a meme SFX/VO. Never scrape or splice real internet memes. <!-- /LOCKED -->
- <!-- LOCKED --> **Floating cards over the A-roll:** emoji pops on the earning methods, brand
  chips on redemption, stat pops on social proof — alpha WebM overlays word-synced from VO
  transcripts. No blur-out behind cards (that's Format-1's grammar). Held phones show a bright
  BLANK glow; all UI proof arrives as cards/logo pop. <!-- /LOCKED -->

## 2. Script

Anatomy `interview-turns.yaml`. Worked shape (~143 words → ~55s at street pace):

```
HOOK
INTERVIEWER: <breathless chase line — "Wait wait wait — ladies!">
PERSON1: <reaction to the chase itself>
INTERVIEWER: <the street question — a fresh angle, e.g. "laziest way you've earned money">
PERSON2: <absurd answer #1 (real-life texture: sleep study, line-sitting…)>
PERSON1: <absurd answer #2, deadpan>
INTERVIEWER: <the pitch: app + 2-3 earning methods>
PERSON1: <mock outrage — "That's illegal.">   → meme cut #1
PERSON2: <flat skepticism — "Nobody is giving out free rewards…">  → meme cut #2
INTERVIEWER: <name + redemption + stats>
PERSON2: <realization beat>
PERSON1: <buy-in + phone-up — "what's it called? Spell it.">
CTA
INTERVIEWER: <app name + store + kicker>
```

Rules: never reuse a previous video's street answers (novelty scan the library); keep turns 5-18
words; PERSON turns carry emotion, INTERVIEWER turns carry facts; the buy-in turn is the phone-up
beat; endscreen fires on the spoken CTA line.

## 3. Assets — what Format-2 does differently

Recipe: `recipes/assets.md`. Beyond the base interview pipeline:

- **Duo stills** (both girls in frame) are generated DIRECTLY as 9:16 singles (no grid): chase
  (from behind, motion blur), turnaround, listening, exchanging looks, phone huddle. Both persona
  bases + environment + mic refs in every duo prompt; per-video wardrobe named identically in
  every prompt (QA's wardrobe-vs-persona-ref mismatch is an expected false positive — the real
  gate is cross-asset consistency).
- **Solo emotional beats** stay grid→extract per Format-1 law; on extract identity drift,
  re-extract WITH the persona base passed as an extra identity reference.
- **Meme stills:** gpt_image_2, "deep-fried internet meme aesthetic, harsh flash, no text" —
  text is added crisp at edit time, never generated.
- **Interviewer clips built via ffmpeg:** VO is the anchor — trim footage when longer, setpts
  when shorter; a long VO line may span a CONCAT of two muted B-rolls (internal hard cut = free
  pacing). The chase line gets a high-style breathless TTS take (style ~0.85, stability ~0.3).
- Kling can hallucinate extra lead-in dialogue (measured: Clip 7 gained "Are you charging it?") —
  always transcribe sound-on clips and trim via EDL range start.

## 4. Edit — the Format-2 editing structure

Recipe: `recipes/edit.md`. Summary: 21-ish segments, alternating 1.0↔1.1 punch zooms, smooth push
opener, flicker+shutter on ~25% of cuts, meme cutaways as sources, floating cards word-synced,
logo pop on the spoken app name, hook sticker = a meme caption about the chase ("he ran a whole
block for this 😭"), color-coded uppercase captions, music ~20% no duck, endscreen on the spoken
CTA line, disclaimer full-duration. Editable per-track timeline before the final render — always.

## 5. QA + delivery

Gates A-D as the base interview format. Extra Format-2 checks: meme cards eyeballed standalone
before wiring; caption/card collision scan; phone stays blank-glow in every phone frame.
Delivery per `workflows/core/deliver.md`.
