# SOP — UGC Talking Head, Single Location (`ugc-single` v1.0.0)

The locked step-by-step guide for producing this format end-to-end. Agents follow it
exactly; learnings go to `learnings.md`, never edited in here. Sections marked
<!-- LOCKED --> are non-negotiable.

---

## 1. Format overview

One AI presenter, one location, talking straight to camera about the app for 30-60s.
The energy comes from the EDIT: a B-roll pattern interrupt on nearly every beat,
punch-zoom jump-cuts, five SFX-synced motion-graphic cards, a white hook sticker in
the first 3 seconds, and the per-app CTA endscreen starting on the spoken CTA line.
Reference look: `outputs/mode-earn_backinthe-80s_9x16.mp4` (and
`G:\…\format-examples\ugc-single\`).

**Sub-styles:** none (multi-location is its own format: `ugc-multi-location`).
**Personas:** exactly 1, from `assets/_shared/personas/` (create via
`generate_assets.md` Steps 1-3 only if none fits — needs owner approval).

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/hook-problem-solution.yaml` — the six sacred
all-caps labels, in order:

```
HOOK → PROBLEM → SOLUTION → HOW IT WORKS → RESULT → CTA
```

- Chunking: whole sentences packed to 10-20 words, never across sections
  (`chunk_script.py`, default anatomy). ~2.7 words/sec → 3-15s Kling clips.
- Each script ships with 3 hooks (each with its 0-3s sticker text) + 3 CTAs; approved
  hooks/CTAs pair index-wise into variations sharing one body (cost-smart).
- Worked sample (compressed):
  ```
  HOOK
  "I'm retired… the last thing I wanted was another job."     [sticker: "retired & still earning?"]
  PROBLEM
  "But everything costs more now, and my fixed income doesn't stretch."
  SOLUTION
  "Then my grandson showed me the Mode Earn App."
  HOW IT WORKS
  "I earn points for things I already do. Music. News. Even charging my phone."
  RESULT
  "Those points became real gift cards. No catch, it's free."
  CTA
  "Search Mode Earn App on Google Play. Thank me later."
  ```
- Brand language per `assets/<app>/brand/creative-direction.md` (MEA: "reward" not
  "pay", gift cards not cash, Android only, standard stats, disclaimer line).

## 3. Asset generation — step by step

Recipe: `recipes/assets.md`. Prompt templates with worked examples: `prompts/`.
Models: <!-- LOCKED --> stills = `gpt_image_2` ALWAYS (standing owner rule); clips =
`kling3_0`. A-roll sound ON, B-roll sound OFF. <!-- /LOCKED -->

**3.0 Preflight.** `higgsfield account status`; scaffold the video folder; read the
app + video manifests; pick the persona (its `base-character.png` + `voice-tag.md`
anchor everything).

**3.1 Chunk the script.**
```
chunk_script.py scripts\source.md --title "<Title>" --out edit\chunks.json --vo-script scripts\vo-script.md
```
Gives per-chunk durations + the REQUIRED `broll_slots` quota plan.

**3.2 Environment (1 still).** One 9:16 plate matching the script's vibe, NO people
(`prompts/a-roll-still.md#environment`). Gate-A QA (`--shot-type environment`).

**3.3 Pose grids (1 per chunk).** Refs: base-character + environment. Each grid =
nine poses/angles of the SAME identity/wardrobe, looking at camera, naturally
grounded — one grid per chunk so every beat opens on a fresh pose
(`prompts/a-roll-still.md#grid`). Poses per beat: HOOK = relaxed direct address;
PROBLEM = concerned lean-in; SOLUTION = brightening, phone entering frame
(screen-to-viewer!); HOW = explaining with hands; RESULT = satisfied, phone up showing
the app; CTA = warm direct address. Gate-A QA each grid.

**3.4 First-frame extracts (1 per chunk).** Extract the cleanest, most on-character
grounded cell (`prompts/a-roll-still.md#extract`). **Gate-B QA — the money gate**
(`--shot-type extract --persona <base> --context "<beat + pose + phone note>"`); fail
⇒ max 2 regens (other cell → new grid) using the verdict hint + injected guardrails,
then STOP for the owner. Eyeball every extract too.

**3.5 A-roll clips (1 per chunk) — CONFIRM COST FIRST.** `--dry-run` the batch +
`higgsfield generate cost`; owner confirms (Autonomy On pre-authorizes). Author each
prompt from `prompts/a-roll-clip.md`: pose-match the extract, camera static/drift,
voice tag verbatim, exact dialogue, on-character gesture, continuity close. Generate
sequentially; Gate-D advisory QA after download.

**3.6 B-roll (every required slot + extras).** Brainstorm per
`assets/_shared/b-roll-bank/bank.md` (≥2 ideas/slot, ≥3 categories, grep the
registry); write concepts into each chunk's `b_roll` field; generate stills → Gate-C
QA → muted clips, duration matched to the covered A-roll
(`prompts/b-roll-bank.md` mechanics: single-image cutaway, first+last reveal,
activity insert). Phone in ANY frame ⇒ phone visibility grammar.

**3.7 QC.** Gate-D batch QA on `ai-videos/`, then
`check_assets.py <videodir> --update-manifest` (fails on unfilled required slots);
append shipped concepts to the bank registry; fill the manifest assets table.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`; engine = `video-use` skill + `edit_video.md` steps
(transcribe → strategy → EDL → cards → render → mix → self-eval → **editable
timeline** → final).

- **Per chunk:** its A-roll segment carries the VO; punch-zoom alternates 1.0 ↔ 1.1
  at every cut; long clips get contiguous within-clip splits at phrase boundaries;
  ~30% of cuts get light-flicker + camera-shutter SFX.
- **Per required slot:** its B-roll overlays the segment muted, filling the span (no
  end gap; stretch/tile per `build_editable_timeline.stage_broll`).
- **Cards at beats** (all five, SFX-synced — `formats/_shared/graphics/`):
  hook-sticker (0s → end of HOOK) · app-ui-demo (HOW) · reviews-montage (social-proof
  line) · cashout-counter (payoff line) · free-stamp (free/no-catch line) · logo-pop
  (every spoken app name, on A-roll AND B-roll).
- **Captions:** canonical preset (Arial bold, lower-third, MarginV=90, heavy outline);
  `caption_blackout` under large center cards. Disclaimer always, full duration.
- **Music:** downloaded royalty-free, 20% volume, NO ducking. **SFX:** curated-first
  via `resolve_sfx.py`; every card entrance + shutter + flicker synced in `mix.json`.
- **CTA:** EDL `endscreen` over the last A-roll clip untrimmed, starting on the spoken
  "download/search" line from `master.srt`; `append_cta.py` for delivery.
- <!-- LOCKED --> Editable per-track HyperFrames timeline BEFORE the final render,
  always — wait for the owner's edits. <!-- /LOCKED -->

## 5. QA + guardrails hooks

Rubric shot-types used: `environment`, `grid`, `extract`, `phone-shot`, `broll-still`,
`aroll-clip`, `broll-clip`. Format-critical codes: PHONE_BACK_TO_VIEWER, WRONG_DEVICE,
SCREEN_CONTENT_MISSING, SPATIAL_INTERSECTION, FLOATING_CHARACTER, UNNATURAL_SEATING,
IDENTITY_DRIFT, WARDROBE_DRIFT. Inject guardrails before prompting
(`--model gpt_image_2 --shot-type <s>`, plus `kling3_0 x aroll-clip`); every QA fail
feeds back via `guardrails.py add`.

## 6. Delivery

Output naming: `outputs/<APP-CODE>/<videoTitleCamel>/<APP-CODE>_V<n>_<videoTitleCamel>_9x16.mp4`
(mode-earn → MEA). Sync `outputs\` → `G:\Shared drives\Mode AI Creative Loop\Videos`
(robocopy, exit 0-7 = success). First production-quality output also seeds
`G:\…\format-examples\ugc-single\`. Update the video manifest (status, output path,
`format: ugc-single@1.0.0`), append a `project.md` session entry, validate with
`check_manifest.py`.
