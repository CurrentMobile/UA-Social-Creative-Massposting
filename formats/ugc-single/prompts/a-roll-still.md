# Prompts — ugc-single stills (environment, grid, extract)

Fill `<…>` slots; keep the fixed phrasing — it encodes hard-won quality. Cross-format
rules apply: `formats/_shared/prompts/identity-consistency.md`, `camera-rules.md`,
`phone-visibility-grammar.md`. Inject guardrails first
(`guardrails.py inject --model gpt_image_2 --shot-type <type>`).

## environment (`gpt_image_2`, aspect 9:16, resolution 2k) {#environment}

> `<environment that matches the script's vibe and era>`, suitable as the single
> setting for the video. No people. Photorealistic, natural daylight.

**Worked example:**
> A cozy, warm home interior in soft natural daylight: a comfortable living room with a
> beige sofa and soft cushions, a wooden side table, a large window on the left with
> sheer curtains letting in warm morning light, framed family photos and a couple of
> leafy plants in the background, hardwood floor. Inviting, lived-in, homely but tidy.
> No people. Photorealistic, natural daylight.

## 3x3 pose grid (`gpt_image_2`, aspect 1:1; refs: base-character + environment) {#grid}

One grid per chunk so each beat gets a fresh pose/angle (pattern interruption).

> A 3x3 grid showing the exact same `<age + identity>` from the reference image, same
> face and identity, wearing the same `<exact wardrobe>`, `<seated on the …/standing
> by the …>` in this same `<environment>`. Nine different `<sitting positions/poses>`
> and camera angles, but she is looking directly at the camera in every one of the
> nine shots, `<on-character expression, e.g. warm and a little wry>`. She sits
> naturally ON the seat cushion, feet on the floor, anatomically correct, one surface
> only. Keep her identity, wardrobe, and warm natural daylight identical across all
> nine. Photorealistic, natural skin texture.

If the chunk's beat involves the phone: add the screen-to-viewer clause + pass
`s22-ultra-front.png` and the app home-UI still as extra refs (phone grammar clause 1).

## extract a cell (`gpt_image_2`, aspect 9:16; ref: that grid) {#extract}

> Extract ONLY the single portrait at row `<R>`, column `<C>` of this 3x3 grid, where
> `<what she's doing in that cell>`. Output a clean full-frame 9:16 vertical portrait
> of just her, sharp and upscaled, no grid lines, no other tiles, no collage. Preserve
> her exact face, identity, `<exact wardrobe>`, and the `<environment>` background.

If the source cell sits at a busy surface add: "single normal `<room>`, one surface
only, no duplicate furniture, anatomically correct" (guardrail GR-004).
