---
id: ranking
name: "Ranking / Top-N Countdown"
version: 0.1.0
status: draft
family: video
feasibility: proven
sub_formats: []
aspect: "9:16"
durations: [30, 45, 60]
default_duration: 45
vo: true
personas: {min: 1, max: 1, roles: [presenter]}
anatomy: formats/_shared/anatomies/ranked-list.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/ranking/recipes/assets.md
  edit: formats/ranking/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 14, clips: 12, approx_credits: 900}
  note: "Presenter A-roll per rank + B-roll per rank; #1 reveal segment is the richest. Similar cost to ugc-single."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/ranking/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\ranking\'
locked_rules:
  - competitors-stay-generic
  - rank-1-is-always-our-app
  - ranking-badge-every-item
  - rank-1-celebration-treatment
  - phone-reveal-only-at-rank-1
  - endscreen-cta-on-spoken-line
---

# Ranking / Top-N Countdown

One presenter counts down a ranked list ("Top 5 reward apps — counting down to the one
I actually use every day"), with a slamming rank badge on every item and the energy
building to a #1 reveal that is always our app. Reuses the ugc-single presenter engine
(one persona, one location, punch-zoom cuts) with a ranked-list anatomy and a
ranking-badge card per item.

**Compliance (LOCKED):** competitor ranks stay GENERIC — describe the category
("a walking-rewards app", "a survey app"), never a real competitor name, logo, or UI.
Only OUR app (rank 1) is named and shows real UI. This keeps the creative legally safe.

**When to use:** listicle-native audiences; "which app is actually worth it" comparison
angle; a confident #1 reveal for the promoted app.

**One-liner for the intake form:** "A presenter counts down the top reward apps —
badges slamming in — building to the #1 they actually use (always ours)."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
