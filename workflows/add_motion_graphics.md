# Workflow: Add Motion Graphics & Animated Captions

Build overlay animations (title cards, lower-thirds, kinetic captions, data viz, transitions)
with **HyperFrames** and composite them into the edit. Called by `edit_video.md` step 4.

## Skills to read
- **`hyperframes`** — composition authoring (HTML/CSS/GSAP), caption effects, transitions, media.
- **`hyperframes-cli`** — `init`, `lint`, `inspect`, `preview`, `render`, `doctor`.
- **`hyperframes-registry`** — install pre-built blocks (`hyperframes add …`): 100+ blocks,
  17+ caption effects, social lower-thirds, charts/maps.
- **`gsap`** / **`css-animations`** — animation references.
- The `video-use` skill's "Animations" section — duration rules, easing, payoff-sync timing.

## Conventions
- **Each animation is one slot**, built in `\.tmp\<project>\edit\animations\slot_<id>\`.
- **Default canvas: 1080×1920 @ 30 fps** (vertical). Set on the stage element:
  `data-width="1080" data-height="1920" data-fps="30"`.
- **Spawn slots in parallel** (one sub-agent per slot via the `Agent` tool) — never sequential.
  Each sub-agent prompt is self-contained (see the `video-use` skill's parallel brief).
- **Transparent overlays**: render to **VP9 WebM with alpha** (`--format webm`); opaque cards render MP4.
  This is the required format for any overlay with transparency — keep it as `.webm`, do **not**
  pre-transcode the overlay to a ProRes 4444 / qtrle MOV (browsers can't decode ProRes, and it is no
  longer needed). `render.py` auto-detects alpha WebM overlays (container `ALPHA_MODE=1` / `yuva*`
  pix_fmt) and decodes them with `-c:v libvpx-vp9` so transparency composites correctly. Without that
  decoder ffmpeg's default vp9 decoder drops the alpha plane and the overlay's transparent regions
  render as opaque, covering the base video — a silent failure.

## Steps (per slot)

1. **Scaffold** inside the slot dir (run from the slot dir):
   ```
   npx --yes hyperframes init . --example blank --non-interactive --skip-skills
   ```

2. **Author** the composition (`index.html`). Set the stage to 1080×1920. Use GSAP timelines
   built synchronously; entrance animations on every element; finite repeats only; cubic easing
   (never linear). For animated captions, pull a caption-effect block from the registry
   (`npx --yes hyperframes add <caption-block>`) and wire it per `hyperframes-registry`.

3. **Sync timing to narration.** If the overlay explains a spoken point, get the payoff word's
   timestamp from `takes_packed.md` / `master.srt` and start the reveal `reveal_duration`
   earlier so the landing frame hits the spoken word. Hold the final frame ≥ 1 s before the cut.

4. **Validate**:
   ```
   npx --yes hyperframes lint .
   npx --yes hyperframes inspect .      # catches text overflow / layout issues
   ```

5. **Render** the overlay clip:
   ```
   npx --yes hyperframes render . -o render.mp4                 # opaque
   npx --yes hyperframes render . --format webm -o render.webm  # transparent (alpha)
   ```
   For transparent overlays the `.webm` (VP9 + alpha) is the deliverable that goes into the EDL —
   `render.py` decodes its alpha automatically (see "Transparent overlays" under Conventions). Don't
   convert it to ProRes/qtrle MOV.

6. **Wire into the EDL.** Add to `edl.json` `overlays`, with `start_in_output` = the second in
   the finished video where the overlay begins, and `duration` = the clip length:
   ```json
   "overlays": [
     {"file": "edit/animations/slot_1/render.mp4", "start_in_output": 0.0, "duration": 5.0}
   ]
   ```
   `render.py` shifts each overlay's PTS to its window and composites it BEFORE burning
   captions (Hard Rules 1 & 4). Verify duration/dimensions with `ffprobe` after rendering.

## Captions: two routes
- **Burned subtitles** (default, whole-video): handled by `render.py --build-subtitles`
  (`master.srt`, applied LAST). For 9:16, raise the style to `MarginV=90` so captions clear
  the platform UI — edit `SUB_FORCE_STYLE` in `render.py` or supply a custom force_style.
- **Kinetic / animated captions** (per-moment emphasis): build as a HyperFrames overlay slot
  using a registry caption effect (karaoke, neon-glow, particle-burst, marker-sweep, …).

## First-run note
`npx --yes hyperframes …` downloads the CLI on first use, and `render` downloads a headless
Chrome via Puppeteer (a few hundred MB) the first time. Subsequent runs are fast.
