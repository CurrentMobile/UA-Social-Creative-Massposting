# Guardrails — kling3_0

> GENERATED from index.json by tools/guardrails.py — do not hand-edit.
> Only `active` rules inject into prompts. Review candidates with `guardrails.py report`.

## active (1)

### GR-005 · aroll-clip · WARDROBE_DRIFT · active · hits:1 · added:2026-07-08
- **Defect:** Kling drifts the outfit (color/garment) mid-clip or between clips when wardrobe is not restated explicitly.
- **Rule (inject):** Name the exact wardrobe in every clip prompt and close with the continuity clause: "wearing <the exact garments from the reference>… lighting, wardrobe, and all background details staying completely consistent throughout — a seamless single take".

