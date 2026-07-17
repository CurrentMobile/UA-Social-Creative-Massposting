# SOP — Lo-Fi Text-on-Screen Aesthetic Loop (`lofi-text` v0.1.0)

The locked step-by-step guide for this format. Agents follow it exactly; learnings go
to `learnings.md`, never edited in here. Sections marked <!-- LOCKED --> are
non-negotiable. `status: draft` — first real run validates it; then promote to beta.

---

## 1. Format overview

No human presenter and no spoken voiceover. The video is 3-5 short (4-6s) ambient AI
loops stitched into a seamless 15-30s piece, with soft on-screen text cards carrying
the message and a lo-fi beat carrying the mood. Reference feel: cozy "study-with-me" /
rainy-day aesthetic posts — dim warm light, shallow depth of field, film grain, gentle
vignette. The app appears diegetically (glowing on a phone screen within the scene),
never pitched to camera.

**Sub-styles:** none. **Personas:** none — no character library is used. If a hand or
partial body appears in a scene it is anonymous (no face-consistency burden).

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/no-vo-overlay.yaml` — there is no VO, so
`chunk_script.py --anatomy <this>` emits an **overlay-plan** (`overlay-plan.json`) of
text cards with reading-speed durations, not Kling chunks. The "script" IS the overlay
copy; it still goes through drafting → approval → the script library (format-tagged
`lofi-text`).

Structure: a HOOK card, 1-3 body cards, a soft CTA card. Copy is short, lowercase,
mood-forward — reads like a caption, not a slogan.

**Worked sample (15s, 3 scenes):**
```
HOOK
"pov: your phone finally pays you back"
BODY
"scrolling. charging. music playing."
"all of it quietly earning gift cards."
CTA
"mode earn app · free on google play"
```
Card count ≈ scene count (one thought per loop). Brand language from
`assets/<app>/brand/creative-direction.md` (MEA: "reward"/"gift cards" not
"cash/pay", Android only). The tiny disclaimer rides the CTA card.

## 3. Asset generation — step by step (worked prompt at every step)

Recipe: `recipes/assets.md`. Models: <!-- LOCKED --> stills = `gpt_image_2` ALWAYS
(standing owner rule); loop clips = `kling3_0 --param sound=off`. No voiced clips.
<!-- /LOCKED --> Prompt templates: `prompts/ambient-scene.md`, `prompts/loop-clip.md`.

**3.0 Preflight.** `higgsfield account status`; scaffold the video folder; read the app
+ video manifests (brand palette, the app UI/home-screen still, logo, CTA text). Inject
guardrails: `guardrails.py inject --model gpt_image_2 --shot-type broll-still`.

**3.1 Overlay plan.**
```
chunk_script.py scripts\source.md --anatomy formats\_shared\anatomies\no-vo-overlay.yaml ^
  --out edit\chunks.json --vo-script scripts\vo-script.md
```
Gives the text cards + per-card durations. Pick 3-5 ambient scenes (one per card, or
one card riding across two scenes) whose mood matches the copy.

**3.2 Ambient scene stills (1 per scene, `gpt_image_2`, aspect 9:16).** Cozy,
atmospheric, shallow DOF; the phone (screen-to-viewer per phone grammar) glows in-scene
where the copy references the app. Gate-C QA each still (`--shot-type broll-still`; if
a phone is in frame add `--app-ui assets\<app>\brand\<ui>.png`).

**Worked example (rainy-desk scene):**
> A cozy dim bedroom desk at night, warm lamp glow, rain streaking a window in soft
> focus behind. On the wooden desk a Black Samsung Galaxy S22 Ultra lies propped on a
> small stand, its bright screen facing the camera clearly showing the <app> home
> screen exactly as in the reference image, glowing and legible. A steaming mug and
> fairy lights bokeh beside it. Shallow depth of field, film grain, gentle vignette,
> moody lo-fi aesthetic, no people. Photorealistic.

**3.3 Loop clips (1 per scene, `kling3_0`, sound OFF, 4-6s).** <!-- LOCKED --> The
motion must return NEAR the first frame so the loop point is invisible. <!-- /LOCKED -->
Prompt only gentle, cyclic ambient motion (rain falling, steam curling, a slow light
flicker, a thumb slowly scrolling) — no camera moves beyond a slight drift, and the
scene should look the same at 0s and end.

**Worked example (rainy-desk loop):**
> Gentle continuous rain streaks down the window behind, steam curls slowly upward from
> the mug, the fairy lights softly twinkle, and the phone screen's glow subtly pulses;
> everything drifts calmly and the frame looks the same at the start and end of the
> loop. The camera holds completely static. Cozy, hypnotic, seamless.

**3.4 QC.** Gate-D advisory QA on the loops (`--shot-type broll-clip`); eyeball the
loop point (first vs last frame). `check_assets.py` (B-roll quota is satisfied by the
scenes themselves — one loop per card).

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`. Engine = `video-use` + `workflows/core/edit_stage.md`
(`timeline: loop`).

- **Assembly:** concatenate the scene loops in copy order; crossfade or hard-cut on the
  lo-fi beat; the whole piece can itself loop (last scene eases back toward the first).
- **Text cards:** one card per scene, dreamy typography (soft serif or typewriter,
  lowercase, gentle fade/blur-in, subtle drift), centered or lower-third, comfortably
  inside the safe zone. The text cards ARE the captions — no separate caption track.
- **Watermark:** subtle app logo, low opacity, a corner, full duration.
- **CTA:** one soft CTA card on the final scene (app name + "free on Google Play" +
  tiny disclaimer) — NOT the UGC endscreen takeover; it stays in the aesthetic.
- **Aesthetic filter:** film grain + vignette + slight warm grade over everything so
  the AI scenes read as one cohesive piece (`edit_video.md` grade step).
- **Music:** <!-- LOCKED --> lo-fi beat at level 0.55, NO ducking — it is the soul,
  and there is no VO to duck under. <!-- /LOCKED --> Source via `fetch_music.py "lofi
  chill beats no copyright"`.
- **SFX (subtle):** optional vinyl crackle bed, soft rain, a gentle chime on the CTA —
  curated-first via `resolve_sfx.py`. No punchy UGC shutters/flickers.
- <!-- LOCKED --> Editable per-track HyperFrames timeline before the final render,
  always — wait for the owner's edits. <!-- /LOCKED -->

## 5. QA + guardrails hooks

Rubric shot-types: `environment`, `broll-still`, `broll-clip`. Critical codes:
`WARPED_TEXT` (any legible text in the scene, and confirm composited card text renders
clean at review), `SCREEN_CONTENT_MISSING` + `PHONE_BACK_TO_VIEWER` + `WRONG_DEVICE`
(phone-in-scene shots), `DUPLICATED_OBJECTS` / `SPATIAL_INTERSECTION` (busy cozy scenes
invite object merges). No identity/wardrobe codes (no persona). Inject guardrails before
prompting; every fail feeds `guardrails.py add`.

## 6. Delivery

Naming: `outputs/<APP-CODE>/<videoTitleCamel>/<APP-CODE>_V<n>_<videoTitleCamel>_9x16.mp4`.
Sync `outputs\` → `G:\Shared drives\Mode AI Creative Loop\Videos`. First
production-quality output seeds `G:\…\format-examples\lofi-text\`. Update the video
manifest (status, output path, `format: lofi-text@0.1.0`, intake JSON ref), append a
`project.md` session entry, `check_manifest.py`. Propose REGISTRY promotion
`draft → beta` after the first validated output.
