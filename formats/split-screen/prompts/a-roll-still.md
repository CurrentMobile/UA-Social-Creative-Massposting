# Prompts — split-screen stills (crop-safe presenter framing)

Same mechanics as ugc-single (`formats/ugc-single/prompts/a-roll-still.md`); the
difference is CROP-SAFE composition for the lane. Cross-format rules apply. Inject
guardrails first.

## environment {#environment}
Same as ugc-single — one 9:16 plate, no people.

## 3x3 pose grid (per chunk) {#grid}
> A 3x3 grid of the exact same `<persona>` from the reference, same face + `<exact
> wardrobe>`, in `<environment>`, `<on-character expression + gesture>`, **composed for
> a `<top ~60% horizontal band | left vertical half>` crop: the woman centered with
> comfortable headroom, MEDIUM framing, key face/hands well inside the band, nothing
> important near the frame edges the lane crop would cut.** Looking at the camera in all
> nine, naturally grounded, identity + wardrobe + lighting identical. Photorealistic.

## extract {#extract}
> Extract row `<R>` col `<C>` as a clean 9:16 portrait, crop-safe for the `<lane>`
> (subject centered, medium, headroom), no grid lines, preserve exact face + `<wardrobe>`
> + background.

The lane crop is applied in the edit; the still is still generated full 9:16 so the
timeline can position it.
