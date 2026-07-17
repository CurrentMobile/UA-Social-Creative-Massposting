# Card: reviews-montage

**What:** rapid switch through ALL the real review screenshots — social proof burst.
**Fires at:** the social-proof beat ("thought it was a scam… but it's legit").
**Assets:** every screenshot in `assets/<app>/<reviews dir>/` (MEA: `MEA Reviews/`);
for a downloads/stars mention show the ratings image
(`MEA-google-play-ratings-downloads.png`).
**Build:** alpha-WebM card; each review pops/swaps in sequence with **one camera-shutter
SFX per switch** (matching `mix.json` sfx entries), paced so the LAST review lands
before the spoken line ends.
**EDL:** `overlays` entry + shutter SFX times in `mix.json`.
