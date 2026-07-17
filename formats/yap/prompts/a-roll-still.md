# Prompts — yap stills (selfie framing)

Same mechanics as ugc-single (`formats/ugc-single/prompts/a-roll-still.md`); the
difference is the CLOSE SELFIE framing and raw/unpolished look. Cross-format rules
apply. Inject guardrails first.

## environment {#environment}
> `<A casual, real, slightly-messy everyday spot: a bedroom, a parked car, a kitchen>`,
> natural available light, lived-in, NOT a styled set. No people. Photorealistic.

## 3x3 pose grid (per chunk) {#grid}
> A 3x3 grid of the exact same `<persona>` from the reference, same face + `<casual
> everyday wardrobe>`, at a CLOSE, slightly-high SELFIE angle (as if holding the phone
> at arm's length), face filling most of the frame, direct eye contact, animated
> expressive rant energy — different expressions per tile (incredulous, laughing,
> leaning in, wide-eyed). `<casual real setting>` slightly out of focus behind. Looking
> into the lens in all nine, identity + wardrobe + lighting consistent. Photorealistic,
> raw, unpolished, phone-camera look.

## extract {#extract}
> Extract row `<R>` col `<C>` as a clean 9:16 selfie-framed portrait (face filling the
> frame), no grid lines, preserve exact face + `<wardrobe>` + the casual background.
Gate-B QA.
