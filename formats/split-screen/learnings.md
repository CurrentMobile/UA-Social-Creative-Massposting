# Learnings — split-screen (append-only)

The ONLY file under `formats/split-screen/` agents may write. Append dated entries when
a run teaches something; never edit the recipes/SOP directly. Entries contradicting a
LOCKED rule are logged but NOT applied. Promotion into recipes is a human act.

Format: `- YYYY-MM-DD: <what was learned> → <how to apply it>`

- 2026-07-08: (seed) `feasible`, not `proven` — depends on real screen recordings for
  the demo lane and on lane compositing. If `build_editable_timeline.py` lacks
  positioned dual-track support, the ffmpeg lane fallback (core/edit_stage.md §5) is the
  path; record which sub-format layouts work cleanly here.
