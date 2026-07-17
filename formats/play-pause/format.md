---
id: play-pause
name: "Play/Pause Reaction"
version: 0.1.0
status: draft
family: video
feasibility: feasible
sub_formats: []
aspect: "9:16"
durations: [30, 45]
default_duration: 30
vo: true
personas: {min: 1, max: 1, roles: [reactor]}
anatomy: formats/_shared/anatomies/interview-turns.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/play-pause/recipes/assets.md
  edit: formats/play-pause/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 4, clips: 7, approx_credits: 650}
  note: "One watching-setup still + a reaction clip per talk turn; the overlaid clip is imported/reused, not regenerated per turn."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/play-pause/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\play-pause\'
locked_rules:
  - watching-setup-static
  - overlay-clip-pauses-on-pause-marker
  - reactor-talks-only-when-clip-paused
  - phone-screen-faces-viewer-with-app-ui
  - endscreen-cta-on-spoken-line
---

# Play/Pause Reaction

A slightly-angled front view of a person watching their PC/phone, with a second screen
overlaid in the top corner showing WHAT they're watching (the app demo / a claim). The
overlaid clip plays, then PAUSES abruptly — and the reactor turns to camera and talks
about what they (and the viewer) just saw. Play, pause, react, repeat.

**When to use:** reaction-native audiences; "wait, pause — did you see that?" emphasis
on a specific app moment; letting the product footage make the claim and the human
underline it.

**Feasibility `feasible`:** the setup is asset-simple (one watching pose) but
edit-clever (freeze events, PiP overlay, sync).

**One-liner for the intake form:** "Someone reacts to app footage playing in the
corner — it pauses mid-moment and they turn to you: 'wait, did you catch that?'"

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
