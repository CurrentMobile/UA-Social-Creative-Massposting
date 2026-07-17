# Prompts — ugc-single B-roll (`gpt_image_2` still → `kling3_0`, sound OFF)

⚠️ **Concepts are invented fresh per video** — brainstorm from the categories in
`assets/_shared/b-roll-bank/bank.md` (≥2 ideas per slot across ≥3 categories), grep
the used-concepts registry, discard collisions, and append winners after shipping.
The templates below are MECHANICS ONLY. Every required `broll_slots` slot gets filled.
B-roll is overlaid muted; duration matches its A-roll beat.

## Mechanic: single start-image cutaway
Generate one still (refs: base-character + environment + any props/UI needed), Gate-C
QA it, then `kling3_0 --start-image … --param sound=off --param duration=<match>`.

**Still prompt shape:**
> A high-quality `<angle: over-the-shoulder / low side-angle / POV / close-up>`
> photograph of `<subject + the concept's action>`, `<what's sharp vs soft-focus>`,
> `<lighting matching the environment>`, shallow depth of field, candid high-detail
> texture. `<Phone grammar clause if a phone is in frame.>`

**Clip prompt shape:**
> `<The subject>` `<does the concept's single simple motion>`, `<camera: completely
> static | slight natural handheld drift>`, natural motion only, no camera moves.

## Mechanic: first+last frame reveal (the phone-UI display)
1. First frame (the ONE back-to-viewer exception, tagged): character holding the S22
   Ultra back-to-camera, about to turn it (refs: base-character + `s22-ultra-back.png`).
2. Last frame: phone turned, bright screen to camera showing the REAL app UI (refs:
   first frame + `s22-ultra-front.png` + `assets/<app>/brand/<ui>.png`) — "the phone
   screen shows this exact app UI, sharp and bright"; screen fills ~70% of frame,
   character in soft bokeh. (Edit an existing clean frame + the asset — the reliable
   pattern that clears content filters.)
3. Clip (3s): `kling3_0 --start-image first --end-image last --param mode=pro
   --param sound=off`:
   > Maintaining her warm expression, she smoothly rotates the phone forward in a
   > single fluid motion so its bright screen faces the camera, extending it closer;
   > the focus racks from her face to the device, blurring her and the room into soft
   > warm bokeh and resolving on a tight, sharp close-up of the screen. Slight natural
   > handheld only.

## Mechanic: activity insert
Character genuinely using the app (screen visible per phone grammar clause 1 or 2):
> low side-angle shot of `<character>` smiling, holding her phone vertically with its
> bright screen angled toward the camera, `<the activity: gameplay / music player /
> news feed>` clearly visible and legible on screen.
