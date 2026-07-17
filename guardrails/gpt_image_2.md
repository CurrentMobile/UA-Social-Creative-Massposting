# Guardrails — gpt_image_2

> GENERATED from index.json by tools/guardrails.py — do not hand-edit.
> Only `active` rules inject into prompts. Review candidates with `guardrails.py report`.

## active (4)

### GR-001 · phone-shot, extract, grid, broll-still · PHONE_BACK_TO_VIEWER · active · hits:4 · added:2026-07-08
- **Defect:** Character holds phone with back panel / camera bump to viewer when the screen should be presenting the app.
- **Failed fragment:** "holding a phone naturally"
- **Rule (inject):** State positively which phone surface faces the camera: "she holds the phone up with its bright screen facing the camera, clearly showing the <app> home screen exactly as in the reference image". Never write bare "holding a phone"; never mention the back of the phone unless the shot is a tagged reveal first-frame.

### GR-002 · phone-shot, extract, grid, broll-still · WRONG_DEVICE · active · hits:2 · added:2026-07-08
- **Defect:** Model draws an iPhone (notch/Dynamic Island/Apple logo) or a mismatched Android instead of the S22 Ultra prop.
- **Failed fragment:** "never an iPhone"
- **Rule (inject):** Describe the device positively and pass the per-surface prop crop as a reference: "a Black Samsung Galaxy S22 Ultra with centered punch-hole front camera and squared corners, matching the reference exactly" + --image assets/_shared/props/s22-ultra-front.png.

### GR-004 · grid, extract · SPATIAL_INTERSECTION · active · hits:2 · added:2026-07-08
- **Defect:** Character pinned between two tables / merged with furniture / seated inside a sofa arm (the classic GPT Image grid hallucination).
- **Failed fragment:** "sitting at the table in the cozy room"
- **Rule (inject):** Anchor the character to ONE surface: "single normal <room> with one <sofa/table>, she sits naturally ON the seat cushion, feet on the floor, anatomically correct, one surface only". If the best grid pose sits at a busy multi-surface area, prefer a simpler standing/single-surface cell.

### GR-003 · phone-shot, broll-still · SCREEN_CONTENT_MISSING · active · hits:1 · added:2026-07-08
- **Defect:** Visible phone screen is blank, generic, or shows a hallucinated UI instead of the real app home screen/logo.
- **Rule (inject):** Pass the real app UI/logo still from assets/<app>/brand/ as an --image reference and prompt "the phone screen shows this exact app UI, sharp, bright, and legible" — for hard composites, edit an existing clean frame + the UI asset instead of composing from scratch.

## candidate (2)

### GR-006 · grid · ANATOMY · candidate · hits:2 · added:2026-07-09
- **Failed fragment:** "one hand gesturing 'wait, really?'"
- **Rule (inject):** Render hands and fingers with natural proportions and articulation. Ensure all fingers are clearly defined and appropriately sized.

### GR-007 · grid · WARPED_TEXT · candidate · hits:1 · added:2026-07-09
- **Failed fragment:** "happily tapping the screen while still angling it toward the lens"
- **Rule (inject):** Display all on-screen text as sharp, clear, and perfectly legible. Render branding and app store logos with accurate details.

