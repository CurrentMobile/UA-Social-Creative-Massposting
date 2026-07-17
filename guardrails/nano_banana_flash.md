# Guardrails — nano_banana_flash

> GENERATED from index.json by tools/guardrails.py — do not hand-edit.
> Only `active` rules inject into prompts. Review candidates with `guardrails.py report`.

## candidate (3)

### GR-008 · extract · IDENTITY_DRIFT · candidate · hits:1 · added:2026-07-09
- **Failed fragment:** "Expand this exact photo... preserve every detail (no persona reference passed)"
- **Rule (inject):** Maintain consistent facial features, age, and hair style as the provided persona reference. Ensure the character's appearance is identical to the reference.

### GR-009 · broll-still · ANATOMY · candidate · hits:1 · added:2026-07-09
- **Failed fragment:** "held by the unseen interviewer's arm"
- **Rule (inject):** Ensure all characters have naturally formed hands and fingers. Every limb should appear anatomically correct and clearly defined.

### GR-010 · phone-shot · ANATOMY · candidate · hits:1 · added:2026-07-09
- **Failed fragment:** "bring the phone much closer to the camera, screen fills seventy percent of frame (hand wrapped around phone edge)"
- **Rule (inject):** Ensure all hands are anatomically correct with five fingers.

