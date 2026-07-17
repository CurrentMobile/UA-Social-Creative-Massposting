---
id: ugc-single
name: "UGC Talking Head — Single Location"
version: 1.0.0
status: production
family: video
feasibility: proven
sub_formats: []
aspect: "9:16"
durations: [30, 45, 60]
default_duration: 45
vo: true
personas: {min: 1, max: 1, roles: [presenter]}
anatomy: formats/_shared/anatomies/hook-problem-solution.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/ugc-single/recipes/assets.md
  edit: formats/ugc-single/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 14, clips: 12, approx_credits: 900}
  note: "8-10 A-roll clips + 5-7 B-roll clips dominate; stills are cheap."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: ask
preview:
  poster: formats/ugc-single/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\ugc-single\'
locked_rules:
  - five-motion-graphic-cards
  - hook-sticker-first-3s
  - endscreen-cta-on-spoken-line
  - phone-screen-faces-viewer-with-app-ui
  - broll-quota-every-beat
  - camera-static-or-drift-only
---

# UGC Talking Head — Single Location

One AI presenter in one location speaking directly to camera about the app, cut with
frequent B-roll pattern interrupts, five standing motion-graphic cards, punch-zoom
jump-cuts, and the per-app CTA endscreen. This is the proven original format (the
`backinthe-80s` reference video) and the exemplar every other format template follows.

**When to use:** default UGC ad for any Mode app; persona-driven trust pitch;
performance creative where a relatable human explains the value prop in ~30-60s.

**One-liner for the intake form:** "One relatable AI creator, one cozy location,
talking straight to camera with app demos popping in — the classic UGC ad."

Full step-by-step SOP: `sop.md`. Recipes: `recipes/assets.md`, `recipes/edit.md`.
Prompt templates with worked examples: `prompts/`.
