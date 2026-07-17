---
id: reaction
name: "Video Reaction"
version: 0.1.0
status: draft
family: video
feasibility: feasible
sub_formats: [green-screen-style, corner-cam]
aspect: "9:16"
durations: [30, 45]
default_duration: 30
vo: true
personas: {min: 1, max: 1, roles: [reactor]}
anatomy: formats/_shared/anatomies/interview-turns.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/reaction/recipes/assets.md
  edit: formats/reaction/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 4, clips: 7, approx_credits: 650}
  note: "One reactor setup + a reaction clip per turn; the reacted-to content is imported/our-own, not per-turn generated."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/reaction/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\reaction\'
locked_rules:
  - react-to-owned-or-generated-content-only
  - reactor-talks-over-muted-source
  - phone-screen-faces-viewer-with-app-ui
  - endscreen-cta-on-spoken-line
---

# Video Reaction

A creator reacts to a piece of content — the reactor fills most of the frame with the
reacted-to clip shown large (green-screen style, reactor as a cutout over it) or in a
corner cam. Unlike Play/Pause, the source keeps playing while the reactor talks over it
(commentary), rather than hard-pausing.

**Sub-styles:** `green-screen-style` (reactor cut out, floating over the full-frame
source) and `corner-cam` (source full-frame, reactor in a corner bubble).

**Source policy (LOCKED):** react ONLY to content we own or generate — our own app
footage, our own prior ad, or an AI-generated "claim" clip. Never scrape or react to a
third party's copyrighted video without the owner's explicit clearance.

**When to use:** commentary-native audiences; reacting to our own bold claim or a
"reply" to a comment; hot-take energy.

**One-liner for the intake form:** "A creator reacts and talks over the footage —
green-screen or corner-cam — hot takes on our own app clip or claim."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
