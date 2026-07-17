# Core: Edit Stage (recipe executor)

Generalizes `workflows/edit_video.md` — read that file for the mechanics (video-use
engine + 12 Hard Rules, transcription, EDL authoring, motion-graphics build, mixing,
self-eval, the mandatory editable timeline, delivery steps). This file adds the format
parameterization.

## How to execute a format's edit recipe

1. Read `formats/<slug>/recipes/edit.md`. Its YAML declares:
   - `timeline:` `chunks` (one segment per chunk) | `turns` (segments per speaker
     turn, cutting between characters) | `loop` (seamless ambient loop, no VO) |
     `split` (two synchronized lanes)
   - `layout:` `fullframe` | `split-h` | `split-v` | `pip-corner` (picture-in-picture
     overlay lane, e.g. play-pause / reaction)
   - `graphics_slots:` which cards from `formats/_shared/graphics/` fire at which
     beats (`section:X`, `item:*` per ranked item, `0-3s`, spoken-line anchors from
     `master.srt`, or `pause` edit events from `chunks.json`)
   - `cut_style`, `captions`, `music`, `sfx`, `cta`, `disclaimer`
2. **Brand skin comes from the app, never the recipe:** CTA clip, logo animation,
   screenshot dirs, disclaimer lines from `assets/<app>/manifest.md` + `brand/`
   (+ optional `brand/edit-overrides.yaml` re-skin; LOCKED cards can't be removed).
3. `edit_events` in `chunks.json` (e.g. `pause`) become edit moments (freeze the PiP
   lane + fire the pause-freeze card + SFX).
4. **Non-negotiable regardless of format:** audio single-source; SFX curated-first;
   captions safe-zone MarginV=90; self-eval loop (max 3 passes); **editable per-track
   HyperFrames timeline before the final render — wait for the owner's edits**; final
   deliverables to `outputs/` + shared-drive sync.
5. `layout:` values other than `fullframe` need `build_editable_timeline.py`'s
   positioned-track support — if it's not built yet for that layout, compose the lanes
   via ffmpeg per the format's SOP §4 and still deliver the editable preview for the
   tracks that support it (note the limitation to the owner).
