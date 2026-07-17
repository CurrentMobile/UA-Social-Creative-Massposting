---
id: split-screen
name: "Split Screen"
version: 0.1.0
status: draft
family: video
feasibility: feasible
sub_formats: [top-bottom, side-by-side]
aspect: "9:16"
durations: [30, 45, 60]
default_duration: 45
vo: true
personas: {min: 1, max: 1, roles: [presenter]}
anatomy: formats/_shared/anatomies/hook-problem-solution.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/split-screen/recipes/assets.md
  edit: formats/split-screen/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 10, clips: 8, approx_credits: 700}
  note: "Presenter A-roll per chunk; demo lane is screen recordings (free) or a few loop clips. Cheaper than ugc-single when real recordings exist."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/split-screen/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\split-screen\'
locked_rules:
  - two-synchronized-lanes
  - demo-lane-is-the-pattern-interrupt
  - crop-safe-presenter-framing
  - captions-clear-the-lane-seam
  - cta-fullframe-takeover
  - phone-screen-faces-viewer-with-app-ui
---

# Split Screen

Two synchronized lanes in one 9:16 frame: the presenter (A-roll, like ugc-single) in
one lane and continuous demo content (real app screen recordings, or ambient/satisfying
loops) in the other. `top-bottom` stacks presenter over demo; `side-by-side` splits
left/right. The demo lane runs continuously, so it — not overlay B-roll — is the
pattern interrupt.

**Sub-styles:** `top-bottom` (presenter top ~60%, demo bottom ~40%),
`side-by-side` (50/50 vertical halves). Feasibility `feasible`: the layout compositing
may need an ffmpeg fallback until `build_editable_timeline.py` grows positioned-track
support.

**When to use:** "watch it while I explain it" demos; gameplay/satisfying-content
pairing; keeping a hand on the app UI the whole time while a human sells it.

**One-liner for the intake form:** "Presenter in one lane, live app demo in the other —
they watch the product work while a real voice explains why it's worth it."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
