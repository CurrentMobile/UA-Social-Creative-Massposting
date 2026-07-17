# Phone Visibility Grammar (cross-format standing rule)

The character is presenting the app, so **whenever a character holds a phone, the
screen faces the viewer clearly showing the app logo or home UI.** Bare "holding a
phone" is **BANNED** — image models resolve the ambiguity by drawing the back panel.
Every phone mention in every prompt uses one of three positive clauses:

1. **Screen-to-viewer (DEFAULT):**
   > "she holds the phone up with its bright screen facing the camera, clearly showing
   > the <app> home screen / logo exactly as in the reference image, glowing and legible"
2. **Screen-to-character (rare — private scrolling/reading beats only):**
   > "the screen is tilted toward her own face, seen in three-quarter profile — the
   > viewer sees the side edge of the phone and the glow on her face, never its back panel"
3. **Back-to-viewer (EXCEPTION — only the tagged first frame of a phone-reveal clip):**
   > "holding the phone with its back panel to the camera, about to turn it around"

**References per phone shot (pass BOTH as extra `--image`):**
- `assets/_shared/props/s22-ultra-front.png` for screen-facing shots
  (`s22-ultra-back.png` ONLY for a reveal first-frame; combined image only when both
  surfaces appear). Pass only the surface that should be visible.
- `assets/<app>/brand/<app-home-ui>.png` (or logo still) so the screen shows the REAL app.

**Device phrasing is positive:** "a Black Samsung Galaxy S22 Ultra with centered
punch-hole front camera and squared corners, matching the reference exactly" — never
rely on "not an iPhone" (the reference image + QA's WRONG_DEVICE check are the guards).

QA enforcement: `qa/rubrics.json` codes `PHONE_BACK_TO_VIEWER`, `WRONG_DEVICE`,
`SCREEN_CONTENT_MISSING`. Guardrails: GR-001 / GR-002 / GR-003.
