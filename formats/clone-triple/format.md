---
id: clone-triple
name: "Clone (Double / Triple Clone)"
version: 0.1.0
status: draft
family: video
feasibility: feasible
sub_formats: [clone-double, clone-triple]
aspect: "9:16"
durations: [30, 45]
default_duration: 30
vo: true
personas: {min: 1, max: 1, roles: [presenter-cloned]}
anatomy: formats/clone-triple/anatomy.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/clone-triple/recipes/assets.md
  edit: formats/clone-triple/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 6, clips: 11, approx_credits: 950}
  note: "Composite stills are cheap; a clip per turn (8-12 turns) dominates. Short turns (<=8s) keep drift + cost down."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/clone-triple/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\clone-triple\'
locked_rules:
  - same-person-all-clones
  - same-voice-tag-all-clones
  - turns-max-8s
  - qa-checks-every-clone-each-frame
  - gpt-image-2-always
  - phone-screen-faces-viewer-with-app-ui
---

# Clone (Double / Triple Clone)

ONE persona appears 2-3 times in the same frame, debating the app with itself —
skeptic-me on the left, hyped-me on the right, and (triple) wise-me in the middle
settling it. It's a self-dialogue: same face, same wardrobe, different attitudes. The
comedy of one person arguing with themselves is the hook.

**Sub-styles:** `clone-double` (2 clones — the reliable default) and `clone-triple`
(3 clones — richer, higher drift risk). Feasibility is `feasible` (not proven): the
non-speaking clone can drift, so turns are kept short and QA checks every clone.

**When to use:** objection-handling in a fun frame (skeptic vs believer); "the two
sides of me" relatable comedy; a memorable, native-feeling twist on talking-head.

**One-liner for the intake form:** "One creator, cloned 2-3 times in one frame,
arguing with themselves about the app — skeptic vs hyped, settled by the reveal."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
