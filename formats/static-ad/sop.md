# SOP — Static Ad (`static-ad` v0.1.0)

Locked step-by-step guide. Learnings go to `learnings.md`. <!-- LOCKED --> sections are
non-negotiable. `status: draft` — first real set validates it.

---

## 1. Format overview

Image-only ad creatives. No timeline, no VO, no motion — a base visual (GPT Image 2)
with brand copy composited on top, exported as PNGs at 9:16, 1:1, and 4:5. The
`edit` stage is omitted entirely (see `recipes/edit.md`).

**Sub-styles:**
- **lifestyle-photo** — a persona/subject using the app in a believable moment; warm,
  authentic, phone screen-to-viewer showing the real UI.
- **ugc-screenshot-style** — mimics an organic phone screenshot / text-post /
  testimonial; low-fi authenticity beats polish.
- **feature-callout** — a clean hero shot of the phone/app with one labeled feature and
  a benefit line.
- **meme-style** — a native meme template (top/bottom text or reaction layout) that
  lands the value prop as a joke.
- **review-proof** — 5-star rating + short review quotes as the hero, social-proof led.

## 2. Copy anatomy

Anatomy: `formats/_shared/anatomies/no-vo-overlay.yaml` (no VO). The "script" is the
copy set: **headline** (the scroll-stopper), optional **subhead**, **CTA**, and the
**disclaimer**. It goes through drafting → approval → the script library, tagged
`static-ad`. Draft `variations` distinct headline/angle sets sharing the base-visual
direction. Brand language from `assets/<app>/brand/creative-direction.md`.

**Worked sample — lifestyle-photo:**
```
HEADLINE   "your phone's just sitting there. it could be earning."
SUBHEAD    "music, games, charging — all rewarded."
CTA        "Get Mode Earn — free on Google Play"
DISCLAIMER "Earnings vary. Rewards are given as redeemable points."
```
**Worked sample — review-proof:**
```
HEADLINE   "3M+ reviews. 4.5 stars. not a scam."
SUBHEAD    "\"I cashed out a $25 gift card the first week.\" — real review"
CTA        "Join 10M+ on Mode Earn"
DISCLAIMER "Earnings vary. Rewards are given as redeemable points."
```

## 3. Asset generation — step by step (worked prompt per sub-style)

Recipe: `recipes/assets.md`. <!-- LOCKED --> Base visuals = `gpt_image_2` ALWAYS.
<!-- /LOCKED --> Inject guardrails (`--model gpt_image_2 --shot-type <phone-shot|
broll-still>`). Any phone follows the phone visibility grammar (screen to viewer, real
UI, `s22-ultra-front.png` + app-UI still as refs). Persona subject (if used): pass the
persona `base-character.png` as a ref. Gate-C QA every base visual before compositing;
`WARPED_TEXT` matters most here.

**3.1 lifestyle-photo base:**
> A warm, candid lifestyle photo of `<persona/subject>` `<in a real moment: on a couch
> with coffee / on a commute / in a kitchen>`, holding a Black Samsung Galaxy S22 Ultra
> with its bright screen facing the camera clearly showing the <app> home screen
> exactly as in the reference image, a natural relaxed smile. Soft natural light,
> shallow depth of field, authentic UGC feel, leave clean negative space at the
> `<top/bottom>` for a headline. Photorealistic.

**3.2 feature-callout base:**
> A clean studio hero shot of a Black Samsung Galaxy S22 Ultra floating at a slight
> angle on a `<brand-color>` gradient background, its bright screen facing the camera
> clearly showing the <app> `<feature screen>` exactly as in the reference image,
> soft product lighting and reflection, generous negative space around the phone for a
> headline and a callout label. Photorealistic, crisp, ad-ready.

**3.3 meme-style base:** a recognizable, brand-safe meme composition (reaction shot /
two-panel) with clear flat areas for top/bottom text (the meme text is composited in
step 4, not baked — keeps it legible). **3.4 ugc-screenshot-style:** generate a
believable phone-in-hand or flat-lay; the "screenshot" chrome + text post are
composited in step 4. **3.5 review-proof:** a simple branded background / soft product
vignette leaving room for the star row + quote cards composited in step 4.

## 4. Compositing recipe — per layout (HyperFrames 1-frame render)

Prompts: `prompts/compose-layout.md`. Compose the copy over the base visual as an HTML
layout and render ONE frame per aspect (reuses the HyperFrames render infra):

- **Safe zones per aspect:** design a master 1080×1920 (9:16), then reflow for 1080×1080
  (1:1) and 1080×1350 (4:5) — keep headline + CTA inside each aspect's safe area; never
  just crop the 9:16.
- **Type + brand:** brand font, colors, and logo from `assets/<app>/brand/`; headline
  hierarchy (headline > subhead > CTA); high-contrast text with a scrim/plate over busy
  areas so it stays legible.
- **Required marks:** app logo, Google Play badge, and the disclaimer (small, legible)
  on every creative.
- **Export:** render at 2x, output PNG per aspect.
- <!-- LOCKED --> Composited text must render crisp and correct (spelling, kerning,
  no clipping) — this is a review gate, since text is the whole point of a static ad.
  <!-- /LOCKED -->

Show the composed set to the owner for approval before delivery (the static analog of
the editable-timeline gate).

## 5. QA + guardrails hooks

Rubric shot-types: `phone-shot` (lifestyle/feature/screenshot), `broll-still`
(meme/review backgrounds). Critical codes: `WARPED_TEXT` (any text in the AI base —
prefer clean plates and composite real text on top), `ANATOMY` (lifestyle subjects),
`WRONG_DEVICE`, `SCREEN_CONTENT_MISSING`, `PHONE_BACK_TO_VIEWER`. Inject guardrails
before prompting; every fail feeds `guardrails.py add`.

## 6. Delivery

Naming: `outputs/<APP-CODE>/<title>/<APP-CODE>_S<n>_<title>_<aspect>.png` (S = static).
Sync `outputs\` → `G:\Shared drives\Mode AI Creative Loop\Videos` (same tree; statics
alongside videos). First production-quality set seeds
`G:\…\format-examples\static-ad\`. Update the app's video index / a statics manifest
entry with `format: static-ad@0.1.0` + the intake JSON ref; `check_manifest.py`.
Propose REGISTRY `draft → beta` after the first validated set.
