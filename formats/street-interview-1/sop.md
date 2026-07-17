# SOP — Street-Interview Format-1 (`street-interview-1` v1.0.0)

Step-by-step law for this styled edition. Validated end-to-end by
`outputs/MEA/askYourPhoneForARaise/MEA_V1_askYourPhoneForARaise_9x16.mp4` (2026-07-10).
<!-- LOCKED --> sections are non-negotiable; run learnings go to `learnings.md` only.

Base mechanics inherited from the `interview` format (turn anatomy, grid→extract→clip generation,
per-face QA): read `formats/interview/sop.md` §2–3 and §5 for those details — this SOP documents
what Format-1 ADDS or overrides.

---

## 1. Creative overview

- **Arc:** skeptic → curious → sold, in ~8 rapid turns (2–6s each), one interviewee. Very fast
  documentary pacing; no turn runs long enough to go static.
- <!-- LOCKED --> POV interviewer: heard, never seen. Mic (and only the mic — no hand/arm of the
  interviewee on it, no cable in their hands) enters frame held by the unseen interviewer. <!-- /LOCKED -->
- **Persona:** one interviewee, library persona preferred. Give the performance real personality
  per the persona's age/culture (goofy high-energy for a student, wry for a retiree).
- **Setting:** sunny public walkway/plaza, blurred passersby, handheld street energy. Camera rule
  in every clip prompt: static or slight natural handheld drift only — all "camera energy" in the
  final comes from punch-zoom cuts and flicker transitions at edit time, never from the AI footage.
- <!-- LOCKED --> **The popup rule (this format's signature):** never composite app UI onto a phone
  the interviewee holds — image models warp small screen text under motion. The held phone shows a
  bright BLANK glowing screen (screen-to-viewer; the back panel stays banned per the phone
  grammar). Every piece of real proof — UI screenshots, star ratings, review cards, the app logo —
  arrives at EDIT time as a popup graphic card while the interviewee BLURS OUT behind it. <!-- /LOCKED -->

## 2. Script

Anatomy `interview-turns.yaml` (speaker-tagged turns, HOOK/CTA labels). Worked shape from the
validated output (~78 words → ~31s at street pace):

```
HOOK
INTERVIEWER: <one-line scroll-stopper question>
PERSON1: <skeptical pushback, names the catch>
INTERVIEWER: <the pitch: app name + 2-3 earning methods>
PERSON1: <hooked: "stuff I already do?">
INTERVIEWER: <reward proof: gift cards / redemption options>
PERSON1: <social-proof check-back question>
INTERVIEWER: <rating / downloads stat>
PERSON1: <sold: "that's genius, downloading it right now">
CTA
INTERVIEWER: <app name + store + kicker line>
```

Rules: interviewer lines carry the facts; interviewee lines carry the emotion. Keep every turn
6–20 words. The final PERSON turn is the phone-up beat; the endscreen fires on the interviewer's
spoken CTA line.

## 3. Assets — what Format-1 does differently

Recipe: `recipes/assets.md`. Beyond the base interview pipeline:

- **Phone-up beat first-frame:** bright BLANK glowing screen (no readable text — a popup covers it
  at edit), one hand on the phone, other hand free, mic in frame from out-of-shot. QA context must
  say so, or the QA rubric will flag missing screen content.
- **Interviewer turns are BUILT, not generated:** TTS the interviewer's lines (one energetic voice
  used verbatim throughout), then ffmpeg-mux each VO line onto a muted B-roll (establishing POV /
  listening / double-take / look-around / squint). Stretch the footage to the VO length via
  `setpts` — VO timing is the anchor, never the reverse.
- **Blur baked at mux time:** for beats that host a popup card, bake
  `gblur=sigma=22:enable='gte(t,X)'` into the muxed clip starting at the card's local in-point.
  The blur travels with the clip — zero extra wiring downstream.
- Kling can hallucinate EXTRA unscripted dialogue in sound-on clips — always read the transcript
  and trim to the scripted words via the EDL range start.

## 4. Edit — the Format-1 editing structure

Recipe: `recipes/edit.md` (the motion-graphics system — the heart of this format). Summary:

- `timeline: turns`, alternating 1.0↔1.1 punch zooms per segment, one smooth push opener,
  ~30% of cuts get a white flicker + camera-shutter SFX.
- Hook sticker on the opening question (leaves when the question ends). Captions canonical
  lower-third, blacked out under full-attention popup windows.
- Popup cards per `recipes/edit.md` §2–3: standalone HyperFrames alpha-WebM projects following the
  four-phase lifecycle (enter → staggered secondaries → idle float/wobble → exit), wired as EDL
  `overlays` over the blur-baked windows.
- Logo pop on the spoken app name; endscreen CTA starts on the spoken CTA line; disclaimer
  full-duration; music 20% no duck; SFX curated-first, one per card entrance/flicker/slam.
- **Editable per-track timeline before the final render — always.** Final = hyperframes render of
  that timeline → loudnorm −14 LUFS → deliver per `workflows/core/deliver.md`.

## 5. QA + delivery

Same gates as the base interview format (A grids / B extracts / C B-roll stills / D clips
advisory). Extra Format-1 checks before final: blackdetect the render (frame-snap), eyeball every
card window frame, confirm captions don't collide with cards, confirm the FREE-style stamp isn't
covering the interviewee's face (position it in an empty screen third — caught by self-eval on the
first run). Delivery, naming, shared-drive sync, example seeding: `workflows/core/deliver.md`.
