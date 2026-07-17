# Prompts — ranking stills (environment, grid, extract)

Same mechanics as ugc-single (`formats/ugc-single/prompts/a-roll-still.md`); the
difference is the per-rank expression arc. Cross-format rules apply
(`formats/_shared/prompts/*`). Inject guardrails first.

## environment {#environment}
Same as ugc-single — one 9:16 plate matching the vibe, no people. Reuse that worked
example.

## 3x3 pose grid (per chunk, refs: base-character + environment) {#grid}

The expression maps to the rank's position in the countdown:

| Beat | Expression / pose direction |
|------|-----------------------------|
| HOOK | confident setup, "I tried them all" energy, direct address |
| RANK 5-3 (low) | measured, mildly unimpressed, small shrug, counting on fingers, "it's fine I guess" |
| RANK 2 | getting warmer, lean-in, raised eyebrow, "now we're talking" |
| RANK 1 | big excitement, phone up screen-to-viewer showing the app, delighted |
| CTA | warm, sincere, direct address |

> A 3x3 grid of the exact same `<persona>` from the reference, same face and `<exact
> wardrobe>`, in `<environment>`, `<expression + gesture from the table>`. Looking at
> the camera in all nine, naturally grounded (feet planted / seated on the cushion),
> identity + wardrobe + lighting identical across all nine. Photorealistic.

Rank-1 grid adds the phone (screen-to-viewer clause + `s22-ultra-front.png` + app-UI
refs).

## extract {#extract}
Same as ugc-single — cleanest, most on-character grounded cell; Gate-B QA.
