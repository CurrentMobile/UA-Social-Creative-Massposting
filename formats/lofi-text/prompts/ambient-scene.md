# Prompt — lofi-text ambient scene still (`gpt_image_2`, aspect 9:16)

One atmospheric still per overlay card. Cozy/dreamy mood, shallow DOF, film grain,
gentle vignette, NO people (a partial anonymous hand is OK). When the copy references
the app, the phone glows in-scene per the phone visibility grammar (screen to viewer,
real app UI, `s22-ultra-front.png` + the app home-UI still as refs). Inject guardrails
first (`--model gpt_image_2 --shot-type broll-still`).

## Template

> A `<cozy setting: rainy bedroom desk at night / under-the-covers with phone glow /
> quiet coffee-shop table by a window / soft morning kitchen>`, `<warm dim lighting>`,
> `<atmospheric detail: rain on glass / fairy-light bokeh / steam / dust motes>`.
> `<If the app appears:>` a Black Samsung Galaxy S22 Ultra `<propped on a stand /
> resting on the surface>`, its bright screen facing the camera clearly showing the
> <app> home screen exactly as in the reference image, glowing and legible. Shallow
> depth of field, film grain, gentle vignette, moody lo-fi aesthetic, no people.
> Photorealistic.

Keep scenes visually varied across the video (different rooms/times of day) but tied by
the same warm grade and grain so they read as one aesthetic.

## Worked example (under-the-covers scroll)

> A cozy dark bedroom seen from under soft white duvet folds, warm amber string-light
> bokeh in the blurred background, late-night calm. A Black Samsung Galaxy S22 Ultra
> rests on the pillow, its bright screen facing the camera clearly showing the Mode
> Earn App home screen exactly as in the reference image, glowing softly and legible;
> an anonymous hand rests relaxed beside it. Very shallow depth of field, heavy soft
> bokeh, film grain, gentle vignette, dreamy lo-fi aesthetic, no faces. Photorealistic.
