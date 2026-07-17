---
id: street-interview-2
name: "Street-Interview Format-2 (meme vox pop, chase hook)"
version: 0.1.0
status: draft
family: video
feasibility: feasible
sub_formats: []
aspect: "9:16"
durations: [45, 60]
default_duration: 45
vo: true
personas: {min: 2, max: 2, roles: [interviewee, interviewee]}
anatomy: formats/_shared/anatomies/interview-turns.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/street-interview-2/recipes/assets.md
  edit: formats/street-interview-2/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 16, clips: 12, approx_credits: 260}
  note: "First run (laziest-way-to-earn, 2026-07-10): 2 personas -> 6 grids + 6 extracts + 5 duo stills + 2 meme stills; 7 sound-on + 5 muted Kling clips. Meme cutaways + all cards render locally (free)."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/street-interview-2/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\street-interview-2\'
locked_rules:
  - pov-interviewer-never-on-camera
  - chase-or-motion-cold-open-hook
  - meme-cutaways-are-ai-generated-never-scraped
  - floating-cards-over-aroll-no-blur
  - no-app-ui-on-held-phones-blank-glow-plus-cards
  - interviewee-never-holds-mic-or-cable
  - endscreen-cta-on-spoken-line
---

# Street-Interview Format-2 (meme vox pop, chase hook)

Second styled edition of the street-interview family — the fast, meme-heavy Gen Z vox pop from
the root brief `street-interview-2-creative-direction.md`, first shipped as
`outputs/MEA/laziestWayToEarn/MEA_V1_laziestWayToEarn_9x16.mp4` (mode-earn, gen-z-ashley +
student-chloe duo, ~59s, 2026-07-10).

Differences from Format-1 (`street-interview-1`):
- **Two interviewees** (a duo with contrasting energies: one mouthy, one deadpan) instead of one.
- **Chase cold open:** the POV interviewer SPRINTS after the interviewees — running camera shake,
  breathless TTS VO, mic bobbing in frame; they turn around startled. Scroll-stopper by motion.
- **Meme interruptions:** 1s full-frame hard-cut meme cutaways (AI-generated meme-style stills +
  impact text + punch zoom + meme SFX/VO, built as tiny HyperFrames mp4s used as EDL *sources*) —
  never scraped internet clips (copyright).
- **Floating graphics, no blur:** emoji pops, brand chips, and stat cards float OVER the live
  A-roll near the speakers (alpha WebM overlays); Format-1's blur-out popup rule does not apply.
  Cards are word-synced from the VO transcripts (whisper word timestamps).
- **Color-coded captions:** bold uppercase center-lower captions; yellow for the hook window,
  green for money/reward words, white otherwise. 2-4 word cues, cuts every 1-3s.

**When to use:** maximum-retention Gen Z paid social; goofy street energy; product pitch delivered
through a comedy duo's skeptic→sold arc rather than polished proof cards.

Full SOP: `sop.md`. Recipes: `recipes/`.
