# Card: app-ui-demo

**What:** the app's Home/earning-grid screenshot popping in inside a phone bezel —
shows "pick how you earn" while the presenter explains the mechanics.
**Fires at:** the HOW IT WORKS beat (or the format's equivalent explain beat).
**Assets:** `assets/<app>/brand/<home-grid screenshot>.png` (real UI only, never mocked).
**Build:** alpha-WebM HyperFrames card at 1080×1920 under
`<edit>/animations/cards/compositions/app-ui-demo.html` → render `--format webm`.
Phone-bezel pop-in entrance (scale 0.85→1.0 + fade, GSAP back.out), subtle idle float,
pop-out exit. SFX-synced pop on entrance.
**EDL:** `overlays` entry (filename without "broll" ⇒ card) + `caption_blackout` under
it when it occupies the center (large phone card hides captions).
