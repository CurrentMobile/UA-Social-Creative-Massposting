---
id: street-interview-1
name: "Street-Interview Format-1 (skeptic→sold, popup cards)"
version: 1.0.0
status: beta
family: video
feasibility: feasible
sub_formats: []
aspect: "9:16"
durations: [30, 45]
default_duration: 30
vo: true
personas: {min: 1, max: 1, roles: [interviewee]}
anatomy: formats/_shared/anatomies/interview-turns.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/street-interview-1/recipes/assets.md
  edit: formats/street-interview-1/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 14, clips: 10, approx_credits: 150}
  note: "Measured on the validated first output (~145 credits actual): 4 A-roll answers + 5 muted interviewer B-rolls; interviewer VO is TTS (ElevenLabs, ~free); popup cards render locally."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/street-interview-1/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\interview\'
locked_rules:
  - pov-interviewer-never-on-camera
  - no-app-ui-on-held-phones-popup-cards-instead
  - blur-behind-every-popup-card
  - interviewee-never-holds-mic-or-cable
  - four-phase-card-lifecycle-motion-language
  - endscreen-cta-on-spoken-line
---

# Street-Interview Format-1 (skeptic→sold, popup cards)

The first *styled edition* of the street-interview family — the exact creative direction, editing
structure, and popup motion-graphics system used in the validated
`outputs/MEA/askYourPhoneForARaise/MEA_V1_askYourPhoneForARaise_9x16.mp4` (mode-earn,
`student-jake`, ~31s, delivered 2026-07-10).

Relationship to the generic `interview` format: `interview` defines the base *mechanics*
(turn anatomy, POV-interviewer asset generation, per-face QA). Format-1 layers a specific
**editing structure** on top: skeptic→sold arc in ~8 rapid turns, TTS interviewer VO muxed over
muted B-roll, and every piece of app proof (UI screenshots, ratings, reviews, logo) arriving as a
**popup graphic card over a blur-out of the interviewee** — never composited onto a held phone.
Pick THIS card in the intake dropdown to get that exact style; pick `interview` for the unstyled
base mechanics. Future styled editions (Format-2: fast meme-heavy Gen Z vox-pop — creative
direction already at repo root `street-interview-2-creative-direction.md`) get sibling directories
`street-interview-2/` etc.

**When to use:** authentic "real people react" social proof with polished, brand-safe motion
graphics; a single consistent interviewee; product proof that must be pixel-perfect (real
screenshots, not AI-rendered screens).

**One-liner for the intake form:** "Street vox pop, skeptic→sold in 8 rapid turns — off-camera
interviewer, real-screenshot popup cards springing over a blurred interviewee (the
askYourPhoneForARaise editing style)."

Full SOP: `sop.md`. Recipes: `recipes/`. Reusable GSAP card skeletons: `cards/`.
