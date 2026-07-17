# Workflow: Edit a Video (full pipeline)

The spine of the video studio. Turns raw A-roll / B-roll / AI clips into a finished,
captioned, scored vertical video. This WAT workflow orchestrates two installed skills
plus three local tools. **Read the `video-use` skill — it is the editing engine and its
12 Hard Rules are non-negotiable.** This file adds our project conventions on top.

## Objective

Given raw footage, deliver an edited video that: removes dead space + filler words,
cuts on word boundaries, color-grades, adds motion graphics + captions, mixes royalty-free
background music + sound effects, and lands in `outputs/`.

## Layers used

| Need | Use |
|------|-----|
| Inventory, transcribe, cut, grade, captions, render | **`video-use` skill** (`.claude/skills/video-use/helpers/*.py`) |
| Motion graphics, animated captions, lower-thirds, transitions | **`hyperframes` skill** (`npx --yes hyperframes …`) |
| Background music | `tools/fetch_music.py` → `tools/mix_audio.py` |
| Sound effects | `tools/fetch_sfx.py` → `tools/mix_audio.py` |
| Preflight | `tools/env_check.py` |
| Editable timeline preview (per-clip/B-roll/caption tracks) before final | `tools/build_editable_timeline.py` → `npx --yes hyperframes preview` |

## Project conventions (read before running)

- **Python**: always run helpers and tools with the project venv:
  `\.venv\Scripts\python.exe <script> …` — never bare `python`.
- **Run from the project root** (`mode-ai-creative-loop\`). `transcribe.py` resolves
  `ELEVENLABS_API_KEY` from the root `.env`. Never copy the key into the skill folder —
  it would sync to the shared drive.
- **Default format: vertical 9:16, 1080×1920, 30 fps** (TikTok / Reels / Shorts).
  Override per-project if the user asks for 16:9 / square.
- **Captions safe-zone**: position higher than `render.py`'s default `MarginV=35` so they
  clear platform UI — use `MarginV=90` for vertical. (See "Captions" below.)
- **Working dir = the video's asset folder**: `assets\<app>\<video-title>\`. Source clips live
  in `ai-videos\` + `ai-images\`; `video-use` writes artifacts to `assets\<app>\<video-title>\edit\`
  (pass `--edit-dir`). Copy only the final deliverable to `outputs\`. See `asset_organization.md`.
- **Read manifests first** (see step 0): `assets\<app>\manifest.md` then the video manifest are
  the single source of truth for brand, CTA, screen recordings, and asset choices.
- **Recreating a reference?** If the manifest points at a recreation blueprint
  (`assets\<app>\reference-analysis\**\blueprint.md`, from `workflows/analyze_video.md`), read it
  before cutting: its scene table maps to `chunks.json` boundaries + B-roll slots, its
  Transitions & Animations column drives the timeline's animation choices, and its End Card
  mechanics drive the CTA/endscreen build. `reference_mode: recreate` = structural contract;
  `inspiration` = style cues only.
- **Paid API**: transcription spends ElevenLabs credits. Per CLAUDE.md, confirm with the
  user before transcribing real footage. Transcripts are cached — never re-transcribe.

### STANDING RULES (2026-06-16, corrected 2026-07-10) — apply to every edit
- **Audio is single-source, but every A-roll/endscreen video is MUTED with its dialogue on a
  paired sibling `<audio>` element** (same src, same timing), never on the video itself. The
  2026-06-16 version of this rule said the opposite (unmuted video carrying `data-has-audio="true"`,
  no separate track) — that plays **silently in HyperFrames Studio's interactive scrubber**, which
  only drives sound through `<audio>` elements per the current HyperFrames media contract
  (`hyperframes-core` skill → `variables-and-media.md`: "Video elements must be muted... Audio must
  be a separate `<audio>` element, even when it uses the same source file"). `hyperframes render`
  still produced correct audio under the old rule (it reads `data-has-audio` as a render-time hint),
  which is why the bug went unnoticed in delivered outputs but every editable-timeline preview was
  silent. Verified fix (waveform-matched against a known-good render, no doubling/echo):
  `build_editable_timeline.py` now emits muted video + a same-timed `<audio>` sibling on its own
  dedicated track for every A-roll segment, the endscreen, and any card with `keep_audio`. **Only
  B-roll is muted AND audio-stripped** (`-an`) with no paired track at all (it has none to pair).
  Always ffprobe B-roll → 0 audio streams. Legacy projects: `tools/fix_editable_timeline_audio.py`
  patches an already-generated editable-timeline in place (idempotent).
- **B-roll fills its A-roll segment — no end gap.** Stretch (slow) a short B-roll to the segment
  span, or play the first-span of a long one; tile multiple B-rolls contiguously, last ends at the
  segment end. (`build_editable_timeline.stage_broll`.)
- **Music = 20% of A-roll, no ducking** (`mix.json` music_volume 0.20).
- **SFX curated-first** via `resolve_sfx.py` (recursive over `assets/sfx/curated/`, prefers
  "Sound effects and documentation/"); yt-dlp only on miss. Synced number pop-ups = alpha-WebM
  cards + `caption_blackouts` + matching `mix.json` sfx entry.
- **CTA overlays the last A-roll clip, untrimmed** (EDL `endscreen`), not appended.
- **Canonical tools:** `build_editable_timeline.py` (+ `build_srt.py` for master.srt) drive the
  timeline; `build_hyperframes.py` / `assemble_jumpcut.py` are legacy.
- **Caption preset (default):** Arial bold, lower-third (`bottom:540px`), centered, natural case,
  heavy black outline. Already the `.cap` default — keep it.
- **Hook sticker (always):** EDL `hook_sticker:{text}` — uses the script's generated hook sticker
  text, center-aligned & balanced across ≥2 lines (never one line), top sticker box; **leaves
  exactly when the hook clip ends** (auto = end of the last `beat:"HOOK"` range).
- **AI/rewards disclaimer (always):** EDL `disclaimer:{lines:[...]}` — tiny centered multi-line at
  the bottom, full duration, over everything incl. the CTA. Keep the exact line breaks; swap app name.
- **Output path:** `outputs/<APP-CODE>/<videoTitleCamel>/<APP-CODE>_V<n>_<videoTitleCamel>_<dim>.mp4`
  (one folder per app, one per video title; all variations inside). mode-earn → `MEA`. Mirror to the
  shared-drive `Videos\` tree.

### STANDING RULES (2026-06-22) — apply to EVERY edit, even the first V0 review render
- **Motion graphics are DEFAULT, at the matching script beats, each SFX-synced** (don't wait to be asked):
  - **App-UI demo (Home grid)** at the HOW beat ("pick how you earn") — Home/earning-grid screenshot, phone-bezel pop-in.
  - **Reviews montage** at the social-proof beat ("scam… but legit"): switch through ALL the real review
    screenshots in `assets/<app>/MEA Reviews/`, **one shutter SFX per switch**, fast enough that the last
    lands before she finishes; for the **downloads/stars** mention show `MEA-google-play-ratings-downloads.png`.
  - **Cashout-balance switch** at the "points add up…redeem" payoff: switch the real cashout screenshots in
    `assets/<app>/brand/MEA Cashout Screenshots/` ascending (3K→24K→100K→redeem), **one shutter per switch**
    (the growing real balance IS the count-up).
  - **"FREE / no catch" stamp** at the free/no-catch beat.
  - **MEA logo POP-UP** (`brand/MEA-Logo-Animation-POP-UP.webm`, alpha, `keep_audio:false`) overlaid on
    BOTH A-roll + B-roll, synced EXACTLY to the spoken app name whenever it's introduced ("I found Mode Earn App").
  Build each as an **alpha-WebM HyperFrames card** under `<edit>/animations/cards/compositions/*.html` →
  render `--format webm` to `<edit>/animations/*.webm`; reference in EDL `overlays` (filename without
  "broll" ⇒ card). Add a `caption_blackout` under any large center (phone) card. Alpha rides the WebM
  container (`ALPHA_MODE=1`) even when pix_fmt reads yuv420p — that's fine.
- **Zoom in/out jump-cuts — between AND within clips (expanded 2026-06-23):** every cut should be a
  visible 10% punch — alternate per-range `zoom` 1.0 ↔ 1.1 across consecutive ranges so the scale flips
  at each cut (punch in, then out, "vice versa"). **Also add jump cuts WITHIN a long clip even with no
  dead space:** split its range at a natural phrase/comma boundary into two CONTIGUOUS sub-ranges (same
  source frames, no gap → VO intact, only scale jumps). Get the split source time from
  `transcripts/Clip N.json` words or `master.srt`. Vary zoom-IN between a **smooth push**
  (`"smooth": true`, tweens 1.0→1.1 — use as opener / after a flicker) and a **hard cut** (omit `smooth`,
  static `scale(1.1)`, punches at the cut); zoom-OUT is the next segment at 1.0. ~1–2 smooth pushes/video.
  Contiguous splits DON'T change total duration, so overlays/SFX/captions/CTA stay in sync — only edit
  `ranges`. Skip clips fully under a full-frame card/B-roll (punch invisible); keep modest where a held
  phone/logo is centered so it isn't cropped. Always do this for fast-paced, high-energy videos.
- **Light-flicker transition on ~30% of cuts**, each synced with a **camera-shutter SFX**: EDL
  `flicker_cuts:[output_time,…]` (+ optional `flicker_duration`, default 0.16) + a `Camera shutter.MP3`
  at each time in `mix.json`. (Supported in `build_editable_timeline.py`.)
- **Hook sticker:** ONE merged box wrapping ALL lines (not per-line pills), **opaque WHITE, curved edges,
  dark bold centered text** (baked into `build_editable_timeline.py` `.hooksticker span`).
- **Endscreen CTA starts on the spoken CTA:** set `endscreen.start_in_output` to the output time the
  character says the "download/search" line (read it from `master.srt`), NOT the last clip's start.

## Steps

### 0. Preflight + read manifests
```
.venv\Scripts\python.exe tools\env_check.py --strict
```
All required checks must pass (ffmpeg, yt-dlp, deps, ELEVENLABS_API_KEY). Then **read the app
manifest and the video manifest first** (`assets\<app>\manifest.md`, `assets\<app>\<video-title>\manifest.md`)
for brand rules, the per-app CTA, relevant screen recordings, and any chosen assets. If the video
folder doesn't exist yet: `python tools\scaffold.py video <app> "<Title>"`.

### 1. Inventory & transcribe
Footage is in `assets\<app>\<video-title>\ai-videos\` (and `ai-images\`). Then (from project root):
```
.venv\Scripts\python.exe .claude\skills\video-use\helpers\transcribe_batch.py assets\<app>\<video-title>\ai-videos
.venv\Scripts\python.exe .claude\skills\video-use\helpers\pack_transcripts.py --edit-dir assets\<app>\<video-title>\edit
```
Sample a couple of `timeline_view.py` PNGs to see the footage. This produces
`takes_packed.md` — your primary reading view for picking cuts.

### 2. Converse & propose strategy
Follow the `video-use` process: describe what you see, ask material-shaped questions,
then propose a 4–8 sentence strategy (shape, take choices, cut direction, motion-graphics
plan, grade, caption style, music/SFX direction, runtime). **Wait for confirmation.**

### 3. Cut (remove dead space + filler) → EDL
Author `edl.json` (schema in the `video-use` skill). Cuts snap to word boundaries; drop
filler words and silences ≥400ms; pad edges 30–200ms. Set grade preset or custom filter.

### 4. Motion graphics (parallel)
For each overlay slot, follow `add_motion_graphics.md`. Scaffold HyperFrames at
**1080×1920**, build, render to `assets\<app>\<video-title>\edit\animations\slot_<id>\render.mp4`,
and reference it in the EDL `overlays` array. Spawn slots in parallel sub-agents.

### 5. Render (cut → grade → overlays → captions)
```
.venv\Scripts\python.exe .claude\skills\video-use\helpers\render.py assets\<app>\<video-title>\edit\edl.json ^
    -o assets\<app>\<video-title>\edit\preview.mp4 --preview --build-subtitles
```
`render.py` does per-segment extract → lossless concat → PTS-shifted overlays →
subtitles LAST, with 30 ms audio fades and loudness normalization (its Hard Rules).

### 6. Background music + sound effects
Handle AFTER `render.py` (see `source_background_music.md`, `add_sound_effects.md`). **SFX are
local-first**: resolve each via `resolve_sfx.py` (curated library, yt-dlp fallback). **Music is
always downloaded.**
```
.venv\Scripts\python.exe tools\fetch_music.py "lofi calm no copyright" --count 3 --tags lofi,calm
.venv\Scripts\python.exe tools\resolve_sfx.py "whoosh"   # prints resolved path (curated or downloaded)

.venv\Scripts\python.exe tools\mix_audio.py assets\<app>\<video-title>\edit\preview.mp4 ^
    -o assets\<app>\<video-title>\edit\preview_mixed.mp4 ^
    --music assets\music\<track>.mp3 ^
    --sfx "<resolved-sfx-path>@2.5" --sfx "<resolved-sfx-path>@7.0:0.8"
```
`mix_audio.py` loops/trims music to length, sidechain-ducks it under dialogue, places
SFX at timestamps, and re-normalizes to −14 LUFS. Video stream is copied untouched.

### 7. Self-eval (before the editable preview)
Per the `video-use` skill: run `timeline_view.py` on the **rendered output** at every cut
(±1.5 s) and 3–4 sample points. Check for cut discontinuities, audio pops, captions hidden
behind overlays, overlay misalignment, music drowning dialogue, SFX timing. Fix → re-render
→ re-eval, capped at 3 passes.

### 8. Editable timeline preview — ALWAYS before the final render (non-negotiable)
Never go from a flattened preview straight to the final. Build an **editable** HyperFrames timeline
where **every A-roll segment, B-roll cutaway, overlay card, and caption is its own tweakable
track/clip** (not one flattened video), serve it, and give the user the Studio URL. **Wait for their
edits.** Apply requested changes to `edl.json` (cuts/order), the overlays, or the captions, regenerate,
and only then render the final.
```
.venv\Scripts\python.exe tools\build_editable_timeline.py assets\<app>\<video-title>\edit
npx --yes hyperframes lint assets\<app>\<video-title>\edit\editable-timeline
:: long-running — start in the BACKGROUND, then report the URL
npx --yes hyperframes preview assets\<app>\<video-title>\edit\editable-timeline --port 3017
```
Report `http://localhost:3017/#project/editable-timeline`. The generator reads `edl.json` +
`master.srt` (+ optional `edit/mix.json` for the music/SFX tracks) and links the source A-roll clips,
prepped B-roll, the alpha card (use the **WebM**, not the ProRes MOV — browsers can't decode ProRes),
music, and SFX into the project as separate tracks. Iterate here until the user is happy; their notes
also feed "what to remember next time" (persist to memory).

### 9. Final render, append CTA & deliver
Re-render without `--preview`, re-run step 6's mix, then **append the per-app CTA** and deliver:
```
.venv\Scripts\python.exe tools\append_cta.py assets\<app>\<video-title>\edit\final_mixed.mp4 ^
    --cta assets\<app>\cta\<cta-clip>.mp4 ^
    -o outputs\<app>_<video-slug>_9x16.mp4
```
The CTA path is listed in the app manifest.

**Then sync the deliverable to the shared drive.** Every final also lives in the team's Google
Shared Drive `Videos` folder — `G:\Shared drives\Mode AI Creative Loop\Videos`:
```
robocopy outputs "G:\Shared drives\Mode AI Creative Loop\Videos" *.mp4 /XO /NFL /NDL /NJH /NJS /NP
```
(robocopy exit codes 0–7 = success.) Run this on every delivery so the final lands on the shared
drive. (A `Stop` hook can fully automate the mirror — add it only with the user's explicit OK.)

Then update the **video manifest** (status →
`posted`/`review`, Output path) and append a session entry to
`assets\<app>\<video-title>\edit\project.md`. Validate with
`python tools\check_manifest.py assets\<app>\<video-title>`.

## Edge cases
- **No ELEVENLABS key** → step 0 fails. Ask the user to add it to `.env`.
- **Source not 9:16** → scale/pad in the extract step or pad to 1080×1920; ask the user if
  cropping vs. letterboxing matters.
- **yt-dlp returns a long compilation, not a clip** → raise/adjust `--max-duration`, or
  pass a direct URL. Only entries with a real downloaded file are logged to `library.json`.
- **Music too loud under speech** → lower `--music-volume` (default 0.18) or keep ducking on.
