# Asset Prompt Templates (the owner's style)

Reference prompts for `generate_assets.md`. These reproduce the exact prompting style
that produced `mode-earn/backinthe-80s`. Fill the `<…>` slots; keep the fixed phrasing —
it encodes hard-won quality (continuity language, the camera rule, voice consistency).

Two invariants run through everything:
- **Identity & continuity:** wardrobe, lighting, and background "remain completely
  consistent / unchanged"; the character is "clearly the same person."
- **Camera rule (A-roll & most B-roll):** only **completely static** OR a **slight,
  natural handheld drift**. Never zoom, dolly, pan, or any other move.

---

## Step 1 — Character description (LLM, text out)

> Generate a well-detailed image description of a character that fits this video:
> `<one line on who they are + why they fit the brief>`. Give a front view, a direct
> close-up shot of the character looking directly at the camera — a passport-style
> portrait containing only the close-up.

## Step 2 — Base character image (`gpt_image_2`)

Append this fixed realism suffix to the Step 1 description:

> `<character description>`, extreme realism, detailed skin, realistic facial
> imperfections, natural daylight lighting, front-view close-up portrait looking
> directly at the camera.

`--param aspect_ratio=2:3 --param resolution=2k` -> `assets/<app>/persona/base-character.png`.

## Step 3 — Voice tag (LLM, text out -> `voice-tag.md`)

> This is the character I am using; the video is regular-paced. Give me a voice tag
> that fits her/his face and age, to keep a consistent voice across all Kling 3.0 Pro
> clips. The voice tag should read like a prompt.

**Format (one paragraph), e.g.:**
> Voice Tag: A 70-year-old African American woman. Warm, soothing, and trustworthy
> grandmotherly tone. Slightly raspy texture indicating age, with a rich, resonant
> lower register. Slow, deliberate pacing with natural, thoughtful pauses.
> Conversational, intimate, and authentic, as if giving gentle advice to a friend over
> a cup of tea.

The voice tag is **pasted verbatim into every A-roll clip prompt** (Step 5).

## Step 4 — Environment, grid, extract (`gpt_image_2`)

**Environment** (no people): `<environment that matches the script's vibe and era>,
suitable as the single setting for the video.` `--param aspect_ratio=9:16`.

**3x3 pose grid** (references: `base-character.png` + `environment.png`):
> Give me a 3x3 grid of the character in different sitting positions and camera angles
> in `<environment>`. Different pose and angle in each shot, but looking at the camera
> in all nine. Identical identity, wardrobe, and lighting across all shots.

`--param aspect_ratio=1:1` -> `ai-images/grid-<N>.png`. Generate one grid per chunk so
each beat gets a fresh location/pose (pattern interruption).

**Extract a cell** (reference: that grid):
> Extract the image in row `<R>` column `<C>` from this 3x3 grid as a single clean 9:16
> portrait of the character, no grid lines, no other tiles.

`--param aspect_ratio=9:16` -> `ai-images/img-<N>.png`.

---

## Step 5 — A-roll clip (`kling3_0`, sound ON)

**Template** (first frame = `img-<N>`; fill the slots, keep the structure):

> Begin on the exact `<shot type: frontal close-up / medium close-up / medium / wide-medium>`
> of `<character incl age + identity>` looking directly into the lens, matching the
> reference pose precisely `<pose detail: e.g. chin resting on right hand / hands clasped
> on the table>`, wearing `<wardrobe>`. `<Environment>` with `<lighting>` remains
> completely unchanged. The camera `<is completely static with no movement | introduces
> a slight, natural handheld drift>` throughout the shot. She begins speaking directly to
> the camera in `<VOICE TAG phrasing>`, delivering with slow, deliberate pacing:
> "`<DIALOGUE CHUNK — exact words>`". As she speaks, `<one natural gesture/action tied to
> the line; optionally a small mid-line transition>`. Her expression stays conversational,
> intimate, and authentically warm. The shot resolves with `<ending pose>`, lighting,
> wardrobe, and all background details staying completely consistent throughout — a
> seamless single take.

Rules:
- **Perform in the persona's personality (be lively!).** Match tone + gesture to the
  persona's age group and culture — sassy / feisty / playful / goofy / sarcastic / deadpan
  / hype / warm-and-wry (see the personality table in `generate_assets.md`). Write the
  expression and gestures into the prompt; never leave the delivery flat or generic. This
  applies to the first-frame image prompts too (pick an on-character expression/pose).
- **Paste the voice tag** into the "in `<…>`" slot every time — this is what keeps the
  voice consistent across clips.
- **Duration** = the chunk's `recommended_duration_s` (more words -> longer). `mode=pro`.
- Keep the camera rule; vary only between fully static and slight handheld.
- **Intonation (important):** Kling's voice follows the dialogue punctuation. A trailing
  ellipsis ("I'm retired…") reads as a rising, uncertain, question-like inflection. For a
  statement, end with a firm period and add an explicit delivery note, e.g. *"delivers the
  line as a calm, matter-of-fact STATEMENT with a settled, declarative, falling intonation,
  NOT a question."* Convert mid-line ellipses to commas or periods unless you specifically
  want a hesitant pause. Quote the dialogue exactly as you want it spoken.

**Worked example (chunk 1 of ExtraIncomeForRetirees, ~10 words, duration 4s):**
> Begin on the exact frontal medium close-up of the 60-something woman looking directly
> into the lens, matching her relaxed reference pose with hands resting in her lap,
> wearing a soft cardigan over a blouse, with warm natural window light and a cozy living
> room behind her remaining completely unchanged. The camera remains completely static
> with no movement. She begins speaking directly to the camera in a warm, soothing,
> trustworthy tone with a slightly raspy, rich lower register and slow, deliberate
> pacing: "I'm retired… the last thing I wanted was another job." As she speaks she gives
> a small, knowing shake of the head and a gentle wave-off gesture, her expression candid
> and warm, settling into a relaxed posture as the line concludes — lighting, wardrobe,
> and background completely consistent, a seamless single take.

(For the original 9-clip back-in-the-80s set used as the style reference, see the owner's
SOP. Match that density and phrasing.)

---

## Step 6 — B-roll clips (`gpt_image_2` -> `kling3_0`, sound OFF)

> ⚠️ **The B-roll ideas below are FORMAT EXAMPLES ONLY — do not reuse them as the actual
> concepts.** For every new video, **invent fresh, creative, scroll-stopping B-roll** that
> fits the specific beat, persona, and app (see "Creative direction" in
> `generate_assets.md`). Brainstorm before generating: unexpected visual metaphors, pattern
> interrupts, meme-native gags, POV shots, reaction inserts, props, before/after, comedic
> exaggeration, dynamic transitions. The templates below just show the *mechanics* (OTSS,
> first+last-frame reveal, activity inserts) you can reuse — not the literal ideas.

B-roll is overlaid muted over the A-roll, so only the A-roll VO is heard. **Match each
B-roll's duration to the A-roll clip it covers.**

### Grandchild / over-the-shoulder (OTSS)
Image (references: `base-character.png` + `environment.png`):
> A high-quality over-the-shoulder photograph from just behind the right shoulder of
> `<character>`, who occupies the right foreground in soft focus. Facing her, `<the
> grandchild: age + look>` holds up a `<phone>` pointing the screen toward her and the
> camera; the bright screen is sharp and in focus, clearly showing `<what's on screen,
> e.g. the app's reward confirmation>`. Natural daylight, warm and joyful, shallow depth
> of field with soft bokeh, candid high-detail texture.
Then `kling3_0 --start-image … --param sound=off`, duration = matching A-roll.

### Phone-UI display (Kling first frame + last frame)
**Always name a specific modern phone + color** in phone shots (for MEA: a modern
**Android**, e.g. "Black Samsung Galaxy S22 Ultra" / "Google Pixel 9" — never an iPhone;
MEA is Android/Play Store only). See the app manifest's AI-generation rules.
**Phone-prop consistency:** for ANY phone-holding shot (here or in A-roll/activity frames),
ALSO pass `assets/_shared/props/samsung-galaxy-s22-ultra.png` (front+back reference) as an
extra `--image` and prompt "the same Black Samsung Galaxy S22 Ultra from the reference" so
the device is identical across every asset.
1. **First frame** image: `<character> in <environment> holding a <modern Android model +
   color> in one hand with the back of the phone to the camera, relaxed natural grip,
   warm smile.`
2. **Last frame** image: `<character> turning the phone to face the viewer, the screen
   held close to the camera`, then composite the **real app UI/logo** (reference:
   `assets/<app>/brand/<app-ui>.png`): "the phone screen shows this exact app UI/logo,
   sharp and bright." **Frame it tight: the phone screen fills ~70% of the frame and is
   the clear focus; the character sits behind in soft-focus bokeh.**
3. **Clip** — **3 seconds** for the reveal (`kling3_0 --start-image phone-ui-first.png
   --end-image phone-ui-last.png --param duration=3 --param mode=pro --param sound=off`):
   > Maintaining her warm expression, she smoothly rotates the phone forward in a single
   > fluid motion so its bright screen faces the camera, extending it closer; the focus
   > racks from her face to the device, blurring her and the room into soft warm bokeh
   > and resolving on a tight, sharp close-up of the screen. Slight natural handheld only.

### Activity shots (game / music / news)
References: `base-character.png` + `environment.png`. Phone held vertically; screen shows
the activity. Examples:
- **Game:** "low side-angle shot of `<character>` smiling, using her phone held
  vertically, a game on the screen."
- **Music:** "over-the-shoulder shot; a music player on her phone; she is playing music,
  phone held vertically."
- **News:** "over-the-shoulder shot; news on her phone; she is reading, phone vertical."
Then `kling3_0 --start-image … --param sound=off`, duration = matching A-roll.
