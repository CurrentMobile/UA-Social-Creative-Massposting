# Card: ranking-badge

**What:** a big rank number badge ("#5" … "#1") that slams in at each list item —
the visual spine of the ranking format.
**Fires at:** every `item:*` beat (chunks carry `item_index` from the ranked-list
anatomy) — badge enters on the item's first chunk, exits on the item's last.
**Build:** alpha-WebM card per rank; number slam entrance (scale 1.5→1.0, hard ease)
with an impact SFX; #1 gets an upgraded treatment (gold/glow + confetti burst + bigger
SFX). Top-left or top-center placement clear of captions (MarginV=90 safe zone).
**EDL:** one `overlays` entry per item + impact SFX times in `mix.json`.
