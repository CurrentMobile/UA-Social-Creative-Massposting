---
id: static-ad
name: "Static Ad (image creatives)"
version: 0.1.0
status: draft
family: static
feasibility: proven
sub_formats: [lifestyle-photo, ugc-screenshot-style, feature-callout, meme-style, review-proof]
aspect: ["9:16", "1:1", "4:5"]
durations: []
vo: false
personas: {min: 0, max: 1, roles: [subject]}
anatomy: formats/_shared/anatomies/no-vo-overlay.yaml
pipeline:
  script: workflows/core/script_stage.md
  assets: formats/static-ad/recipes/assets.md
  deliver: workflows/core/deliver.md
models: {stills: gpt_image_2}
cost_estimate:
  per_set: {stills: 8, approx_credits: 150}
  note: "Base visuals only (gpt_image_2); text compositing is free (HyperFrames 1-frame render). ~5-10 stills per creative set."
form_fields: [persona, variations, script_source, autonomy, extra_notes]
defaults:
  script_source: claude
preview:
  poster: formats/static-ad/preview/poster.jpg
  examples: 'G:\Shared drives\Mode AI Creative Loop\format-examples\static-ad\'
locked_rules:
  - no-edit-stage
  - gpt-image-2-always
  - copy-through-script-library
  - composited-text-must-render-clean
  - phone-screen-faces-viewer-with-app-ui
  - real-brand-assets-only
---

# Static Ad (image creatives)

Image ad creatives for organic posts and paid social — no motion, no VO. The pipeline
SKIPS the edit stage: approved copy (headline / subhead / CTA) is composited over a
GPT-Image-2 base visual with a HyperFrames one-frame render, exported as PNGs at every
declared aspect (9:16, 1:1, 4:5). Five sub-styles cover the workhorse paid-social
creatives.

**Sub-styles:** `lifestyle-photo` (a person using the app in a real moment),
`ugc-screenshot-style` (looks like an organic screenshot/testimonial), `feature-callout`
(hero product shot with a labeled feature), `meme-style` (native meme template),
`review-proof` (star rating + review quotes as the hero).

**When to use:** scroll-stopping paid-social image ads; high-volume A/B copy testing;
organic feed posts; anywhere a video is overkill.

**One-liner for the intake form:** "Scroll-stopping image ads — lifestyle, meme,
feature-callout, or review-proof — copy composited over an AI visual, exported in every
aspect."

Full SOP: `sop.md`. Recipes: `recipes/`. Prompts: `prompts/`.
