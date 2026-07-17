# SOP — Video Reaction (`reaction` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`, `feasibility: feasible`.

---

## 1. Format overview

A creator reacts to a clip that plays large in-frame, talking over it with commentary.
`green-screen-style`: the reactor is a cutout floating over the full-frame source (the
classic "react" look). `corner-cam`: source full-frame, reactor in a corner bubble.
The source stays muted; the reactor's voice carries.

**Personas:** 1 (reactor). **Source (LOCKED):** owned or generated content only.

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/interview-turns.yaml` (turns mode) with one speaker
(the reactor) commenting in beats. Optional `PAUSE` markers for emphasis freezes (like
play-pause, but reaction usually keeps rolling). Chunk with `--anatomy` that file.

**Worked sample (30s, green-screen-style, reacting to our own claim clip):**
```
HOOK
REACTOR: "This ad says you can earn gift cards just by charging your phone. Let's fact-check."
BODY
REACTOR: "Okay it's showing the earning grid — music, games, news. That part's real."
REACTOR: "And there's the cashout… twenty-five dollar gift card. Huh."
REACTOR: "I hate that it actually works. Fine. It's legit."
CTA
REACTOR: "Mode Earn App, Google Play. Go be annoyed at me later."
```

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. Stills ALWAYS `gpt_image_2`; reaction clips `kling3_0`
sound ON. Inject guardrails.

**3.1 Reactor setup still (1).** For `green-screen-style`, generate the reactor against
a clean, easily-keyable background (or plan to matte via the video-use background
removal). For `corner-cam`, a normal setup with the reactor framed for a corner bubble.

**Worked example (green-screen-style):**
> A medium shot of `<persona>` from the reference facing the camera, expressive and
> animated, against a plain evenly-lit `<solid neutral>` background suitable for
> background removal, `<casual wardrobe>`, natural key light, no props. Naturally
> framed head-and-shoulders, photorealistic. Camera completely static.

**3.2 Reaction clips (per turn, `kling3_0` sound ON).** The reactor reacts/comments
(voice tag verbatim), big expressive energy (this format lives on reactions —
eyebrows, laughs, pointing at the footage). Continuity close.

**Worked example:**
> Begin on the medium shot of `<persona>` from the reference against the neutral
> background, reacting with animated skepticism turning to grudging belief in `<voice
> tag verbatim>`: "And there's the cashout… twenty-five dollar gift card. Huh." Eyes
> widening, a pointing gesture toward where the footage is, a reluctant impressed nod.
> Wardrobe, lighting, and background completely consistent, camera static — a seamless
> single take.

**3.3 Reacted-to source.** <!-- LOCKED --> Owned/generated only. <!-- /LOCKED --> Use
our own app footage / prior ad / a generated app-UI "claim" clip (phone/screen to
viewer, real UI). Imported once; muted.

**3.4 Matte + QC.** For green-screen-style, matte the reactor (video-use background
removal → transparent overlay). Gate-D QA on reaction clips; `check_assets.py`.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`.
- `green-screen-style`: source full-frame behind; reactor cutout composited over a
  corner/lower third, scaled so both read. `corner-cam`: source full-frame; reactor in
  a corner bubble with a subtle border.
- The source plays muted throughout; the reactor's audio carries. Optional PAUSE
  freezes on emphasis beats (pause-freeze card + SFX).
- ugc-single polish: hook sticker, captions (clear of the reactor bubble/source key
  areas), logo-pop on the app name, punch zooms on the reactor at big reactions, music
  20% no duck, endscreen CTA on the spoken CTA line (source resolves to full frame or
  the app UI at the CTA).

## 5. QA + guardrails hooks

Shot-types: `persona`/`extract` (reactor setup), `aroll-clip` (reactions),
`broll-clip`/`phone-shot` (generated source). Codes: IDENTITY_DRIFT / WARDROBE_DRIFT,
clean-matte check for green-screen-style, SCREEN_CONTENT_MISSING + PHONE_* on the
source. Inject guardrails; fails feed the ledger.

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/…_9x16.mp4`, shared-drive sync, seed
`format-examples/reaction/`, manifest `format: reaction@0.1.0` + sub_format + intake
ref, `check_manifest.py`, propose `draft → beta` after the first validated output.
