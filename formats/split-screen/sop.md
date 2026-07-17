# SOP — Split Screen (`split-screen` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`, `feasibility: feasible`.

---

## 1. Format overview

Two synchronized lanes in one 9:16 frame. Primary lane = presenter A-roll (ugc-single
engine). Secondary lane = continuous demo content: real app screen recordings (preferred
— from `assets/_shared/screen-recordings/<app>/`) or generated satisfying/ambient loops.
The demo lane runs the whole time, giving constant motion while the presenter sells.

**Sub-styles:** `top-bottom` (presenter top, demo bottom), `side-by-side` (L/R halves).
**Personas:** 1.

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/hook-problem-solution.yaml` (the six beats — same as
ugc-single). Chunk normally (no `--anatomy` flag). The script drives the presenter lane;
the demo lane is chosen to match each beat.

**Worked sample (45s):**
```
HOOK        "I'm just gonna leave this playing while I tell you why my phone pays me now."
PROBLEM     "You scroll for hours a day and get nothing back."
SOLUTION    "Mode Earn rewards the stuff you already do."
HOW IT WORKS "Watch — music, games, charging, news. Points stacking up in real time."
RESULT      "Those points became a $25 gift card. Bottom lane's the actual app."
CTA         "Search Mode Earn App on Google Play."
```
The "watch / bottom lane" language leans into the format — the demo is always visible.

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. Stills ALWAYS `gpt_image_2`; A-roll `kling3_0` sound ON.
Inject guardrails. <!-- LOCKED --> The presenter is framed CROP-SAFE for the lane — the
lane crops the frame, so the subject must sit centered with headroom for the crop.
<!-- /LOCKED -->

**3.1 Environment + crop-safe grids.** Grid/extract prompts state the composition for
the lane: for `top-bottom` the presenter fills a wide-ish upper band; for `side-by-side`
a half-width vertical crop — keep the subject centered, framed as a MEDIUM shot, key
action/face inside the safe band.

Grid prompt note:
> …composed for a `<top 60% band / left vertical half>` crop: the woman centered with
> comfortable headroom, medium framing, nothing important near the frame edges that the
> lane crop would cut.

**3.2 A-roll clips (per chunk).** Standard ugc-single clip prompt
(`prompts/a-roll-clip.md`), pose-matched to the crop-safe extract. If the presenter
holds a phone, phone visibility grammar applies.

**3.3 Demo lane sourcing.** <!-- LOCKED --> Prefer REAL app screen recordings from
`assets/_shared/screen-recordings/<app>/` (listed in the app manifest). <!-- /LOCKED -->
Pick clips matching each beat (earning grid at HOW, cashout at RESULT). Only if no
recording exists, generate an ambient/"satisfying" loop (gpt_image_2 still → muted Kling
loop) or use the app-ui-demo card content. The demo lane's screen is always the real UI.

**3.4 QC.** Gate-D on presenter clips; confirm crop-safe framing on extracts;
`check_assets.py`. B-roll quota is satisfied by demo-lane switches (see §4), not overlay
B-roll.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`. Lane geometry (1080×1920):
- **top-bottom:** presenter 1080×1152 (top 60%), demo 1080×768 (bottom 40%) — tune to
  taste; a thin brand divider between.
- **side-by-side:** presenter 540×1920 (left), demo 540×1920 (right).
- **Demo-lane switches = the pattern interrupt (quota):** switch the demo content at
  least once per beat (earning grid → activity → cashout), each switch SFX-tapped.
- **Captions:** <!-- LOCKED --> caption MarginV adjusted so text sits fully within the
  PRESENTER lane and clears the lane seam — never straddling the divider. <!-- /LOCKED -->
- Hook sticker + logo-pop on the presenter lane; punch zooms within the presenter lane
  only (don't zoom the demo). Music 20% no duck.
- **CTA:** <!-- LOCKED --> at the CTA beat the presenter lane takes over FULL FRAME
  (the split resolves) for the endscreen CTA, starting on the spoken CTA line.
  <!-- /LOCKED -->
- **Layout note:** if `build_editable_timeline.py` lacks positioned dual-track support,
  compose the two lanes via ffmpeg per `workflows/core/edit_stage.md` §5 and still
  deliver the editable preview for the tracks that support it (tell the owner).

## 5. QA + guardrails hooks

Shot-types: `environment`, `grid`, `extract` (crop-safe), `aroll-clip`, `phone-shot`,
`broll-still`/`broll-clip` (generated demo loops). Codes: IDENTITY_DRIFT / WARDROBE_DRIFT,
plus a manual check that the crop-safe framing survives the lane crop, and
SCREEN_CONTENT_MISSING on any generated demo. Inject guardrails; fails feed the ledger.

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/…_9x16.mp4`, shared-drive sync, seed
`format-examples/split-screen/`, manifest `format: split-screen@0.1.0` + sub_format +
intake ref, `check_manifest.py`, propose `draft → beta` after the first validated output.
