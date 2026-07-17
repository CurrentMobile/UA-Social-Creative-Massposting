# SOP — Play/Pause Reaction (`play-pause` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`, `feasibility: feasible`.

---

## 1. Format overview

An angled front view of a reactor at a desk/couch watching content on their device,
with a second screen composited in a top corner (PiP) showing what they watch. The PiP
clip plays, hits a PAUSE, and the reactor turns to camera to react/explain. The rhythm
is: watch (reactor quiet, PiP plays) → PAUSE → react (reactor talks, PiP frozen).

**Personas:** 1 (reactor). **Sub-styles:** none.

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/interview-turns.yaml` (turns mode) — used with ONE
speaker (the reactor) plus `PAUSE` marker lines that become edit events (freeze the
PiP), not spoken VO. Chunk:
```
chunk_script.py scripts\source.md --anatomy formats\_shared\anatomies\interview-turns.yaml ^
  --out edit\chunks.json --vo-script scripts\vo-script.md
```
`PAUSE` lines produce `edit_events` in chunks.json. The reactor's lines are the talk
turns (spoken while paused); a short "watch" description (no VO) marks what the PiP is
playing between pauses.

**Worked sample (30s):**
```
HOOK
REACTOR: "Someone sent me this and said it's not a scam. Let's see."
[PiP plays: app earning grid, points ticking up]
PAUSE
REACTOR: "Wait — pause. It's literally rewarding her for playing music?"
[PiP plays: cashout screen, $25 gift card]
PAUSE
REACTOR: "Okay that's a real twenty-five dollar gift card. I'm downloading this."
CTA
REACTOR: "Mode Earn App, Google Play. Go."
```

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. Stills ALWAYS `gpt_image_2`; reaction clips `kling3_0`
sound ON. Inject guardrails.

**3.1 Watching-setup still (1, `gpt_image_2`).** <!-- LOCKED --> Fully static angled
front view; the reactor sits at their device with room in a top corner for the PiP
overlay. <!-- /LOCKED -->

**Worked example:**
> A slightly-angled front-view medium shot of `<persona>` from the reference sitting at
> a desk in `<environment>`, facing the camera at a natural three-quarter angle, a
> laptop/phone in front of them (their gaze toward it, then to camera). Relaxed,
> curious expression, casual wardrobe, soft key light, clean uncluttered upper-corner
> space in the frame for a picture-in-picture overlay. Naturally seated, feet grounded,
> photorealistic. The camera is completely static.

**3.2 Reaction clips (per talk turn, `kling3_0` sound ON).** From the watching still,
the reactor turns to camera and talks (voice tag verbatim). Between turns, a "watch"
beat = the reactor watching quietly (can be a short generated hold or reuse the still).

**Worked example (reaction turn):**
> Begin on the angled front view of `<persona>` from the reference, watching their
> device, then turning to look directly into the lens. They react in `<voice tag
> verbatim>`, surprised and a little skeptical: "Wait — pause. It's literally rewarding
> her for playing music?" A raised-eyebrow, hand-to-chin reaction. Wardrobe, lighting,
> and background completely consistent, camera static — a seamless single take.

**3.3 Overlay (PiP) clip.** <!-- LOCKED --> The overlaid content shows the REAL app UI.
<!-- /LOCKED --> Prefer a real screen recording (`assets/_shared/screen-recordings/
<app>/`); else generate an app-UI demo clip (phone/screen to viewer, real UI, front
prop + app-UI refs). It is imported ONCE and reused across the PiP windows — not
regenerated per turn.

**3.4 QC.** Gate-D on reaction clips; eyeball corner space on the setup still;
`check_assets.py`.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md` (`layout: pip-corner`).
- The reactor is the full-frame base; the overlay clip sits in a top corner PiP window.
- **PiP plays during "watch" beats; at each `PAUSE` edit event the PiP FREEZES** (hold
  last frame) with a pause-UI flash (`formats/_shared/graphics/pause-freeze`: ⏸ icon +
  dim + vignette) and a tape-stop / record-scratch SFX; a soft "play" SFX on resume.
- The reactor's audio is heard only during talk turns; the PiP is muted (the reactor
  narrates it).
- ugc-single polish: hook sticker, captions (clear of the PiP), logo-pop on the app
  name, punch zooms on the reactor at pauses, music 20% no duck, endscreen CTA on the
  spoken CTA line.

## 5. QA + guardrails hooks

Shot-types: `environment`, `extract`/`persona` (watching still), `aroll-clip`
(reactions), `broll-clip`/`phone-shot` (PiP if generated). Codes: IDENTITY_DRIFT /
WARDROBE_DRIFT across reaction turns, SCREEN_CONTENT_MISSING + PHONE_* on the PiP,
FLOATING_CHARACTER / UNNATURAL_SEATING on the desk setup. Inject guardrails; fails feed
the ledger.

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/…_9x16.mp4`, shared-drive sync, seed
`format-examples/play-pause/`, manifest `format: play-pause@0.1.0` + intake ref,
`check_manifest.py`, propose `draft → beta` after the first validated output.
