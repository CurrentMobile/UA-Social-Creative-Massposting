---
id: interview
name: "Street Interview (POV interviewer)"
version: 0.1.0
status: draft
family: video
feasibility: experimental
sub_formats: [pov-interviewer, on-camera-interviewer]
aspect: "9:16"
durations: [30, 45, 60]
default_duration: 45
vo: true
personas: {min: 1, max: 3, roles: [interviewer, interviewee_1, interviewee_2]}
anatomy: formats/_shared/anatomies/interview-turns.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/interview/recipes/assets.md
  edit: formats/interview/recipes/edit.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2, clips: kling3_0}
cost_estimate:
  per_video: {stills: 12, clips: 12, approx_credits: 950}
  note: "POV v1: interviewer never on camera (no second consistent face). On-camera interviewer (experimental) roughly doubles the identity burden."
form_fields: [persona, duration, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/interview/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\interview\'
locked_rules:
  - pov-interviewer-is-v1-default
  - each-character-own-reference-and-wardrobe
  - handheld-street-energy
  - phone-screen-faces-viewer-with-app-ui
  - endscreen-cta-on-spoken-line
---

# Street Interview (POV interviewer)

Man-on-the-street interview energy: an interviewer asks a question and 1-2 people answer,
with handheld run-and-gun framing. **v1 sub-style is `pov-interviewer`** — the
interviewer is NEVER on camera (their arm/mic may enter frame; we hear them), so only
the interviewee faces are generated. This sidesteps the hardest problem (keeping 2+
distinct faces consistent across chaotic outdoor shots). `on-camera-interviewer`
(interviewer also visible) is `experimental` and waits for stronger multi-character
consistency.

**Feasibility `experimental`:** even POV-interviewer needs consistent interviewee faces
across their turns; the form shows this badge so users expect retries.

**When to use:** authentic "real people react" social proof; vox-pop trend energy;
skeptic-on-the-street converted live.

**One-liner for the intake form:** "Man-on-the-street vox pop — an off-camera
interviewer chases real people for hot takes on the app (POV mic-in-frame)."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
