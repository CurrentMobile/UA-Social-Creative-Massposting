---
id: lofi-text
name: "Lo-Fi Text-on-Screen Aesthetic Loop"
version: 0.1.0
status: draft
family: video
feasibility: proven
sub_formats: []
aspect: "9:16"
durations: [15, 30]
default_duration: 15
vo: false
personas: {min: 0, max: 0, roles: []}
anatomy: formats/_shared/anatomies/no-vo-overlay.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/lofi-text/recipes/assets.md
  edit: formats/lofi-text/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 4, clips: 4, approx_credits: 325}
  note: "3-5 ambient stills → 3-5 short (4-6s) loop clips; ~250 credits at 3 scenes/15s, ~400 at 5 scenes/30s. No voiced clips — the cheapest video format."
form_fields: [duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: ask
preview:
  poster: formats/lofi-text/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\lofi-text\'
locked_rules:
  - no-presenter-no-vo
  - overlay-plan-cards-carry-message
  - loop-ends-near-first-frame
  - music-at-055-no-ducking
  - phone-screen-faces-viewer-with-app-ui
  - soft-cta-card-at-end
---

# Lo-Fi Text-on-Screen Aesthetic Loop

No presenter, no voiceover. 3-5 dreamy ambient AI loops — a rainy window with the
phone glowing on the desk, a cozy under-the-covers scrolling POV, a quiet coffee-shop
table — while soft on-screen text cards carry the entire message and a lo-fi beat
carries the entire mood. The music IS the soul: it sits far louder than in UGC formats
(0.55, never ducked) because there is no voice to compete with. Minimal graphics: the
text cards, a subtle logo watermark, and one soft CTA card at the end — none of the
five UGC motion-graphic cards. Grain + vignette glue the scenes into one aesthetic.

**When to use:** vibe-first awareness creative for any Mode app; audiences that scroll
past talking heads; "ambient product placement" where the app UI glows inside a scene
instead of being pitched; cheap high-variation testing (no persona, no dialogue).

**One-liner for the intake form:** "Rain on the window, lo-fi beats, and dreamy text
cards doing all the talking — the cozy no-face loop where the app just glows in the scene."

Full step-by-step SOP: `sop.md`. Recipes: `recipes/assets.md`, `recipes/edit.md`.
Prompt templates with worked examples: `prompts/`.
