# Workflow: Generate AI Assets (talking-head A-roll + B-roll)

Stage 6 of the mass-posting pipeline. Turns a video brief/script into upload-ready
**voiced A-roll talking-head clips** and **muted B-roll clips**, dropped into the
video's asset folder so `edit_video.md` can assemble them with zero changes.

This codifies the owner's proven manual SOP (the one that produced
`outputs/mode-earn_backinthe-80s_9x16.mp4`) as a fully automated **Higgsfield CLI**
pipeline. Claude writes the creative prompts; the tools handle chunking, submit ->
wait -> download -> rename -> log.

**Read `workflows/asset_prompts.md` first — it holds the prompt templates that
reproduce the owner's exact style.** This file is the orchestration; that file is the
voice.

## Objective

Given a per-video brief + script and the app's reusable persona, deliver:
- `ai-videos/Clip 1.mp4 … Clip N.mp4` — voiced A-roll, one per script chunk, in order.
- `ai-videos/<scene>_b-roll.mp4` — muted B-roll for cued moments.
- `ai-images/…` — the intermediate stills (environment, grids, extracts, phone frames).
- `scripts/vo-script.md` + `edit/chunks.json` — the chunk plan the editor reads.
- `generation-log.json` — provenance of every generated asset.
- `manifest.md` status -> `assets`.

## Layers used

| Need | Use |
|------|-----|
| Chunk the VO into Kling-sized beats | `tools/chunk_script.py` |
| Generate any image/clip + download + log | `tools/higgsfield_gen.py` (wraps `higgsfield` CLI) |
| **AI-vision QA every image / clip frame** | `tools/qa_image.py` (Gemini; rubric `qa/rubrics.json`) |
| **Inject learned prompt rules / log new defects** | `tools/guardrails.py` (ledger in `guardrails/`) |
| QC the asset set + flip manifest status | `tools/check_assets.py` |
| Scaffold the video folder | `tools/scaffold.py` |
| Prompt style templates | `workflows/asset_prompts.md` |

## Models (fixed for this workflow)

- **Images -> `gpt_image_2`** (primary; `--aspect_ratio`, `--resolution 2k`; repeat
  `--image` for multiple references, up to ~8). Used for base character, environment,
  character+env combine, 3x3 pose grids, grid-cell extraction, and phone-screen logo
  compositing. In a 5-model bake-off (GPT Image 2 vs Flux 2 / Seedream 4.5 / Seedream V5
  Lite / Flux Kontext), **GPT Image 2 won decisively** for faithful UI compositing +
  framing + DOF; keep it as the default image model.
  - **Reliable input pattern:** when a shot is hard (tight phone-screen composite, strong
    bokeh), **edit an existing clean frame + the asset** (e.g. first-frame + logo) rather
    than composing from scratch (base-character + environment). The edit pattern both
    avoided GPT Image 2's NSFW false-positive AND produced the best result.
  - **Fallback image model: Nano Banana 2 = `--model nano_banana_flash`.** ⚠️ NOT
    `nano_banana_2` — that job_set_type is "Nano Banana Pro", a different model. **Always
    visually confirm the fallback's output is correct before using it** (it is less
    reliable than GPT Image 2).
- **Video -> `kling3_0`** (`--start-image`, optional `--end-image`, `--aspect_ratio 9:16`,
  `--duration <3-15>`, `--mode pro`, `--sound on|off`). A-roll = **`--sound on`** (Kling
  speaks the dialogue). B-roll = **`--sound off`** (overlaid muted in the edit).

## Creative direction (STANDING RULES — apply to every video, image + clip)

**1. B-roll: invent fresh, creative ideas every time. Do NOT reuse the SOP samples.**
The B-roll examples in `asset_prompts.md` and the `backinthe-80s` SOP (grandchild OTSS,
phone-to-camera, playing-game / listening-music / reading-news) are **illustrative format
references only** — never copy them as the actual ideas. For each new video, brainstorm
*new*, scroll-stopping, platform-native B-roll that fits the specific script beat, persona,
and app. Start from the category scaffolding in `assets/_shared/b-roll-bank/bank.md`
(metaphor, POV, meme gag, before/after, prop gag, reaction insert, transition), brainstorm
**≥ 2 ideas per slot across ≥ 3 different categories**, then grep the bank's
**used-concepts registry** and discard any collision — the registry is what makes "never
repeat" checkable instead of memory-based. After generating, **append every shipped
concept to the registry** (date · category · concept · video). (Still: muted overlay,
duration ≤ its A-roll beat, and for MEA show the real app UI on a modern Android phone
where relevant.)

**1b. B-roll QUOTA (hard minimum — fixes low pattern-interruption).**
Every video gets **at least 1 B-roll per script beat** (HOOK / PROBLEM / SOLUTION /
HOW IT WORKS / RESULT / CTA) and targets **a cutaway every 3–5 seconds of A-roll**:
`n_broll >= max(beats, ceil(total_duration_s / 5) - n_clips)`, with a floor of
`n_chunks - 1` for typical chunk counts. `chunk_script.py` emits a `broll_slots` array in
`edit/chunks.json` marking which chunks REQUIRE a cutaway — fill every required slot
(write the chosen concept into the chunk's `b_roll` field) BEFORE generating clips;
`check_assets.py` fails the Step-7 QC while required slots are unfilled.

**2. A-roll: make characters LIVELY — perform in the persona's personality.**
Talking-head delivery must never be flat/generic. Give each persona real personality in
**both the image prompts (expression + pose in grids/extracts) and the Kling clip prompts
(delivery tone + gestures)**. Pick 1-2 traits that fit the persona's **age group and
culture** — e.g. sassy, feisty, playful, goofy, sarcastic, deadpan, hype, warm-and-wry —
and direct the performance accordingly. The voice tag stays consistent; the *performance*
gets characterful. Suggested mapping (adapt per persona/script):

| Persona age/type | Personality + delivery cues |
|---|---|
| Gen Z teen (e.g. `gen-z-ashley`, 19) | Playful, sassy, ironic, meme-aware; fast, expressive, big reactions, trendy direct-to-cam energy, hand-to-face, eye-rolls |
| 20s student/hustler (`student-jake`, `side-hustle-jake`) | Goofy, high-energy, funny, hype; animated hands, lean-ins, comedic exaggeration, casual slang cadence |
| 30s parent/pro (`single-mom-maria`, `guilt-free-mama-grace`, `crypto-curious-tom`) | Warm, relatable, dry/sarcastic wit; grounded, conversational, knowing looks, the occasional eye-roll or smirk |
| Retiree (`retiree-female-poc`, `male-poc`) | Warm, wry, knowing; gentle humor, measured but characterful, a twinkle, subtle shade |

Keep the declarative-intonation rule for statements, but let the energy and gestures be
alive and on-character. Match cultural cadence to the persona too.

## QA gates (STANDING — every image is checked before it costs money)

`tools/qa_image.py` sends each generated asset to Gemini Flash (~$0.002/check, ~45
checks/video ≈ under $0.10 total) with a per-shot-type rubric (`qa/rubrics.json`) and
returns `pass | warn | fail` + defect codes + a regenerate hint. **A `fail` asset must
NEVER feed a paid Kling job.** The tool judges; YOU decide (regenerate vs escalate):

- **Gate A — after each pose grid:** `qa_image.py --input grid-<N>.png --shot-type grid
  --persona <base.png>` before choosing a cell (tool + eyeball, not instead of eyeball).
- **Gate B — after each first-frame extract (THE MONEY GATE, be strict):**
  `qa_image.py --input img-<N>.png --shot-type extract --persona <base.png>
  --context "<chunk beat + pose + phone note>"`. On `fail`: regenerate loop, **max 2
  re-attempts** — attempt 1 re-extract another cell, attempt 2 regenerate the grid —
  rewriting the prompt from the verdict's `regenerate_hint` plus the injected guardrails.
  After 2 fails: **STOP and show the owner** (never silently burn a 3rd attempt).
- **Gate C — B-roll stills (incl. phone-ui frames) before their Kling calls:** same loop
  as Gate B with `--shot-type broll-still|phone-shot --app-ui <brand ui png>`.
- **Gate D — after clips download (ADVISORY):** `qa_image.py --input "Clip <N>.mp4"
  --shot-type aroll-clip --persona <base.png>` (extracts first+last frames). Verdict is
  recorded; **never auto-regenerate a paid clip** — on warn/fail, pause and show the
  owner the flagged frames; the owner decides re-rolls.

Autonomy On: gates A–C auto-loop within the max-2 cap; a Gate-D fail still pauses.
Autonomy Off: every fail pauses. Every QA call logs to `generation-log.json`
(`--log … --label <same label as the generation record>`) so cost_report can show QA
overhead. QA checks defects only — creative taste stays human.

**Guardrail loop (both directions, every video):**
- **Before authoring prompts** for a shot type, run
  `guardrails.py inject --model <gen model> --shot-type <type>` and honor every rule.
- **After any QA fail**, feed it back:
  `guardrails.py add --from-verdict <verdict.json> --model <gen model> --failed-fragment
  "<the prompt phrase that failed>"`. Candidates await human promotion — see
  `guardrails/README.md` for lifecycle + anti-bloat rules.

## Project conventions (read before running)

- **Python**: always `.\.venv\Scripts\python.exe tools\<script> …` — never bare `python`.
- **Run from the project root** (`mode-ai-creative-loop\`).
- **Higgsfield auth is browser-based.** `higgsfield account status` must show an account
  with credits; if it says `Session expired` / `Not authenticated`, the owner runs
  `higgsfield auth login` (interactive) — Claude cannot. `higgsfield_gen.py` pre-checks this.
- **Default format: vertical 9:16, 1080×1920** to match the editor. Grids use `1:1`; the
  base character portrait uses `2:3` (or `9:16`).
- **Reusable persona library.** Base character image + voice tag live in the shared
  library `assets/_shared/personas/<slug>/` (e.g. `retiree-female-poc`, `male-poc`,
  `female-caucasian`, `student-jake`) and are reused across apps. Each video's
  `manifest.md` records which one it uses via the `persona:` frontmatter field. Generate
  a new persona (Steps 1-3) only when none fits.
- **Consistent phone prop + screen visibility (MEA + any Android brand).** Whenever a
  persona holds a phone — in ANY image (grid, extract, B-roll frame) or clip first-frame —
  follow the **Phone visibility grammar** at the top of `asset_prompts.md`: the screen
  faces the viewer showing the real app logo/home UI (the character is presenting the app).
  Pass TWO additional `--image` references: `assets/_shared/props/s22-ultra-front.png`
  (screen-facing shots; `s22-ultra-back.png` ONLY for a reveal first-frame) AND the app's
  UI/logo still from `assets/<app>/brand/`. Write "holding the same Black Samsung Galaxy
  S22 Ultra from the reference, its bright screen facing the camera showing the <app> home
  screen" in the prompt. Never write bare "holding a phone" — that's how the
  back-of-phone-to-viewer defect happens. This keeps the device one consistent modern
  Android and the app visible across every asset.
- **The camera rule (non-negotiable in A-roll prompts):** only a completely static camera
  OR a slight, natural handheld drift. **No zoom-in, no dolly, no other camera move.**
- **Paid API.** Image + (especially) video generation spend Higgsfield credits. Per
  `CLAUDE.md`, **estimate cost and confirm with the owner before the Step 5/6 batch.**
- **CDN URLs expire** — `higgsfield_gen.py` downloads each result immediately.
- **Read manifests first** (`assets\<app>\manifest.md`, then the video manifest).

## Steps

### 0. Preflight, scaffold, load persona
```
higgsfield account status                                  # auth + credits
.venv\Scripts\python.exe tools\scaffold.py video <app> "<Title>"   # if folder missing
```
Read `assets\<app>\manifest.md` + the brief in `sops\`. **Pick a persona** from
`assets\_shared\personas\` that fits the brief and set the video manifest's `persona:`
field to its slug — then skip Steps 1-3. Only if none fits, create a new one now.

### 1. Character description (Claude, free)
Write a detailed front-view, passport-style close-up description of a character that
fits the brief (see the character template in `asset_prompts.md`). Pick a slug, e.g.
`student-jake`.

### 2. Base character image — persona (`gpt_image_2`)
```
.venv\Scripts\python.exe tools\higgsfield_gen.py --model gpt_image_2 ^
  --prompt "<description>, extreme realism, detailed skin, realistic facial imperfections, natural daylight lighting, front-view close-up portrait looking directly at camera" ^
  --param aspect_ratio=2:3 --param resolution=2k ^
  --out assets\_shared\personas\<slug>\base-character.png ^
  --log assets\_shared\personas\<slug>\persona-log.json --label "base-character"
```
Keep wardrobe plain and casual (no logos/graphics/prints). Show it to the owner.
**Wait for persona approval** — it anchors every clip. Save the description to
`assets\_shared\personas\<slug>\character.md`.

### 3. Voice tag (Claude, free)
Write a voice tag matching the face + age (format in `asset_prompts.md`) to
`assets\_shared\personas\<slug>\voice-tag.md`. **This text is pasted into every A-roll prompt.**

### 4. Chunk script -> environment -> grids -> extracts
Save the raw script to `scripts\source.md`, then chunk it:
```
.venv\Scripts\python.exe tools\chunk_script.py scripts\source.md ^
  --title "<Title>" --out edit\chunks.json --vo-script scripts\vo-script.md
```
Generate the environment still, then per chunk a 3x3 pose grid and an extracted frame:
```
:: environment
... higgsfield_gen.py --model gpt_image_2 --prompt "<environment matching script vibe>" ^
    --param aspect_ratio=9:16 --param resolution=2k --out ai-images\environment.png --log generation-log.json --label environment

:: per chunk N: 3x3 grid (character + environment as references)
... higgsfield_gen.py --model gpt_image_2 ^
    --image assets\_shared\personas\<slug>\base-character.png --image ai-images\environment.png ^
    --prompt "3x3 grid of <character> in different sitting positions and camera angles in <environment>, looking at the camera in all nine shots, identical identity and wardrobe" ^
    --param aspect_ratio=1:1 --param resolution=2k --out ai-images\grid-<N>.png --log generation-log.json --label grid-<N>

:: per chunk N: extract the best cell
... higgsfield_gen.py --model gpt_image_2 --image ai-images\grid-<N>.png ^
    --prompt "Extract the image in row R column C as a single clean 9:16 portrait of the character, no grid lines" ^
    --param aspect_ratio=9:16 --param resolution=2k --out ai-images\img-<N>.png --log generation-log.json --label img-<N>
```
**QC realism BEFORE extracting (Gate A), then QC the extract (Gate B — the money gate).**
GPT Image can hallucinate (duplicate/merged furniture, "pinned between two tables",
warped anatomy, floating/ungrounded characters). Run the QA gates from the standing
section above:
```
:: Gate A — per grid, before choosing a cell
... qa_image.py --input ai-images\grid-<N>.png --shot-type grid ^
    --persona assets\_shared\personas\<slug>\base-character.png --log generation-log.json --label grid-<N>
:: Gate B — per extract, before ANY paid clip
... qa_image.py --input ai-images\img-<N>.png --shot-type extract ^
    --persona assets\_shared\personas\<slug>\base-character.png ^
    --context "chunk <N>: <beat + pose + phone note>" --log generation-log.json --label img-<N>
```
On a Gate-B `fail`: max 2 re-attempts (re-extract another cell, then regenerate the
grid), rewriting from the verdict's `regenerate_hint` + injected guardrails, then STOP
and show the owner. Also still **eyeball each `img-<N>`** — QA is a filter, not a
replacement. Never feed a bad frame into a paid Kling clip.

### 5. A-roll clips (`kling3_0`, sound ON) — CONFIRM COST FIRST
Author each clip prompt from the A-roll template in `asset_prompts.md` (pose-match +
camera rule + **voice tag** + **dialogue chunk**). Duration = the chunk's
`recommended_duration_s` (tune per clip). Then, per chunk:
```
.venv\Scripts\python.exe tools\higgsfield_gen.py --model kling3_0 ^
  --start-image ai-images\img-<N>.png --prompt "<clip prompt>" ^
  --param aspect_ratio=9:16 --param duration=<D> --param mode=pro --param sound=on ^
  --timeout 30m --out "ai-videos\Clip <N>.mp4" --log generation-log.json --label "Clip <N>"
```
Tip: preview the batch with `--dry-run` first; estimate credits with
`higgsfield generate cost kling3_0 …`. Generate sequentially.

### 6. B-roll clips (`gpt_image_2` -> `kling3_0`, sound OFF)
For each cued moment (every REQUIRED `broll_slots` slot + any extras), generate the
image(s), run **Gate C** on each still (`qa_image.py --shot-type broll-still|phone-shot
--app-ui assets\<app>\brand\<ui>.png --context "<the concept>"`), then the muted clip,
**duration matched to the underlying A-roll**. Templates (grandchild OTSS, phone-UI
first+last, activity shots) are in `asset_prompts.md`.
- **Grandchild / activity:** one start image -> `kling3_0 --start-image … --param sound=off`.
- **Phone-UI display (first+last frame):** generate the first frame (holding phone),
  generate the last frame, then composite the **real app UI/logo** onto the last frame:
  ```
  ... higgsfield_gen.py --model gpt_image_2 ^
      --image ai-images\phone-ui-last-raw.png --image assets\<app>\brand\<app-ui>.png ^
      --prompt "the phone screen shows this exact app UI/logo, sharp and bright" ^
      --param aspect_ratio=9:16 --out ai-images\phone-ui-last.png --log generation-log.json --label phone-ui-last
  ```
  Then: `kling3_0 --start-image ai-images\phone-ui-first.png --end-image ai-images\phone-ui-last.png --param mode=pro --param sound=off`.

### 7. QC + manifest
Gate D (advisory) on the finished clips, then the structural QC:
```
.venv\Scripts\python.exe tools\qa_image.py --batch assets\<app>\<video>\ai-videos ^
  --persona assets\_shared\personas\<slug>\base-character.png --log assets\<app>\<video>\generation-log.json
.venv\Scripts\python.exe tools\check_assets.py assets\<app>\<video> --update-manifest
```
On any Gate-D warn/fail: show the owner the flagged frames (never auto-regenerate a
paid clip). Then append every shipped B-roll concept to
`assets\_shared\b-roll-bank\bank.md`'s used-concepts registry.
Fill the manifest Assets table (clips + B-roll + cue lines, mirroring the
`backinthe-80s` manifest), confirm `status: assets`. The folder is now consumable by
`edit_video.md` unchanged.

## Cost discipline

- Persona (1 image) + environment (1) + grids (N) + extracts (N) are cheap; the **video
  steps dominate cost**. Always `--dry-run` the clip batch and confirm with the owner
  before spending on Step 5/6.
- Reuse the persona across videos — never regenerate a character that already works.

## Edge cases & learnings

- **Identity drift across grids** — always pass `base-character.png` as a reference; if a
  grid cell looks off, regenerate before extracting. `check_assets.py` flags missing
  extracts but cannot judge likeness — eyeball each `img-<N>`.
- **Grid-cell extraction imperfect** — `gpt_image_2` may leave grid artifacts; re-prompt
  with explicit row/column, or crop the cell manually and drop it in as `img-<N>.png`.
- **Kling sound** — `--sound on` is what makes A-roll speak (owner-confirmed); B-roll uses
  `--sound off` since it is overlaid muted. The schema default is `on`.
- **Kling duration** is an integer 3–15s; longer dialogue -> longer clip (~2.7 words/sec).
- **Transient API failures (HTTP 502 / job status `failed`)** — Higgsfield intermittently
  fails a job server-side, more often when many are launched at once. `higgsfield_gen.py`
  auto-retries (`--retries`, default 2). Keep image fan-out to ~4-6 concurrent and
  generate clips sequentially to reduce 502s. If a job still fails after retries, just
  re-run that one call.
- **Content-filter false positives (`status: nsfw` / `ip_detected`)** — GPT Image 2
  occasionally false-flags wholesome *from-scratch* composites (e.g. an extreme close-up of
  a person + phone built from base-character + environment). `higgsfield_gen.py` detects
  these terminal statuses and stops retrying immediately. Fixes, in order: (1) **switch to
  the edit pattern** — feed a clean existing frame (e.g. the first frame) + the asset and
  prompt the edit ("turn the phone around, close up on the screen, blur the background");
  this reliably clears the filter and gives the best output. (2) Rephrase as a "clean,
  family-friendly advertisement-style product shot". (3) Fall back to
  `--model nano_banana_flash` (Nano Banana 2) and **visually confirm** the result.
- **Session expired mid-batch** — re-run `higgsfield auth login`, then resume from the
  next missing `Clip <N>` (downloads are idempotent by `--out` path).
- **app-UI asset missing** — the phone-display B-roll needs a still PNG of the real app
  UI/logo in `assets\<app>\brand\`; mode-earn currently ships only a logo `.mov`.
