---
id: yap
name: "Yap (Raw Direct-to-Cam Rant)"
version: 0.1.0
status: draft
family: video
feasibility: proven
sub_formats: []
aspect: "9:16"
durations: [20, 30, 45]
default_duration: 30
vo: true
personas: {min: 1, max: 1, roles: [presenter]}
anatomy: formats/_shared/anatomies/hook-problem-solution.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/yap/recipes/assets.md
  edit: formats/yap/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 8, clips: 8, approx_credits: 550}
  note: "Fewer/no B-roll (the point is raw talking), captions do the heavy lifting — cheaper than ugc-single."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/yap/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\yap\'
locked_rules:
  - raw-selfie-energy
  - big-word-by-word-captions
  - minimal-broll
  - phone-screen-faces-viewer-with-app-ui
  - endscreen-cta-on-spoken-line
---

# Yap (Raw Direct-to-Cam Rant)

The lowest-production, highest-authenticity format: one person talking fast and
unfiltered straight to the front camera — selfie-held or propped — like a voice-note to
a friend. No polished setup, no five-card motion-graphics package; the energy, the hook,
and big word-by-word captions carry it. Minimal-to-no B-roll (the raw talking IS the
format). Reads as organic, not an ad.

**When to use:** authentic "I have to tell you about this" energy; comment-reply videos;
Gen-Z native feeds where polish reads as an ad; fast cheap variation testing.

**One-liner for the intake form:** "Fast, raw, selfie-cam rant — no setup, big bouncing
captions, pure 'I have to tell you about this' energy."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
