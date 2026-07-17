# Identity & Continuity Clauses (cross-format)

Every prompt showing a recurring character carries these clauses — they encode the
hard-won consistency that keeps the presenter "clearly the same person" across shots:

- **Reference anchoring:** pass the persona's `base-character.png` as an `--image`
  reference on EVERY image showing them, and open with "the exact same <age>
  <identity> from the reference image, same face and identity".
- **Wardrobe lock:** name the exact garments every time ("wearing the same mauve
  cardigan over a cream blouse") — never "the same outfit" alone.
- **Continuity close (clips):** end every clip prompt with
  "…lighting, wardrobe, and all background details staying completely consistent
  throughout — a seamless single take."
- **Grid rule:** "identical identity, wardrobe, and lighting across all shots; looking
  at the camera in every one."
- **Grounding clause (anti-floating):** state physical support explicitly — "she sits
  naturally ON the seat cushion, feet on the floor, anatomically correct, one surface
  only". (QA codes: SPATIAL_INTERSECTION, FLOATING_CHARACTER, UNNATURAL_SEATING;
  guardrail GR-004.)
- **Multi-character shots** (interview, clone): anchor EACH character with their own
  reference image and give each a distinguishing wardrobe line; for clones of the same
  persona, state "the SAME person appears N times, identical face and wardrobe,
  different poses".

Voice consistency (clips): paste the persona's `voice-tag.md` verbatim into every
voiced clip prompt. Never paraphrase it.
