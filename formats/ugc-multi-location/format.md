---
id: ugc-multi-location
name: "UGC Talking Head — Multi-Location"
version: 0.1.0
status: draft
family: video
feasibility: feasible
sub_formats: []
aspect: "9:16"
durations: [30, 45, 60]
default_duration: 45
vo: true
personas: {min: 1, max: 1, roles: [presenter]}
anatomy: formats/_shared/anatomies/hook-problem-solution.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/ugc-multi-location/recipes/assets.md
  edit: formats/ugc-multi-location/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 16, clips: 12, approx_credits: 950}
  note: "Multiple environments + per-location outfit consistency = a few extra stills vs ugc-single; clips similar."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/ugc-multi-location/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\ugc-multi-location\'
locked_rules:
  - same-person-across-all-locations
  - one-consistent-wardrobe-per-location-plan
  - location-changes-on-beat-boundaries
  - phone-screen-faces-viewer-with-app-ui
  - broll-quota-every-beat
  - endscreen-cta-on-spoken-line
---

# UGC Talking Head — Multi-Location

The same presenter delivers the script across MULTIPLE locations doing different
actions — on the couch, then walking outside, then at a coffee shop, then in bed — a
day-in-the-life energy that reads as more authentic and higher-production than a single
static setup. Same person and wardrobe (or a deliberate per-location outfit plan)
throughout; location changes land on beat boundaries.

**Feasibility `feasible`:** identity + wardrobe consistency across 3-4 environments is
the challenge — the reference-chain discipline from `identity-consistency.md` is
mandatory, and QA checks every location.

**When to use:** more dynamic, "real creator" energy; showing the app fits into a whole
day; when a single location feels static.

**One-liner for the intake form:** "One creator, one story, told across a whole day —
couch, street, coffee shop — same person moving through real life with the app."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
