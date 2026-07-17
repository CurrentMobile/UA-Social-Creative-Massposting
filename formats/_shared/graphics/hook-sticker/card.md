# Card: hook-sticker

**What:** the hook's on-screen sticker text — ONE merged box wrapping ALL lines (not
per-line pills), **opaque WHITE, curved edges, dark bold centered text**, balanced
across ≥2 lines (never one line).
**Fires at:** 0s; **leaves exactly when the hook clip ends** (auto = end of the last
`beat:"HOOK"` range).
**Build:** baked into `build_editable_timeline.py` (`.hooksticker span`) — EDL
`hook_sticker:{text}` with the script's generated hook sticker text.
