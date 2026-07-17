# Prompts — ugc-multi-location stills

Same mechanics as ugc-single (`formats/ugc-single/prompts/a-roll-still.md`); the
difference is PER-LOCATION environments and a strict reference chain for cross-location
consistency. Cross-format rules apply. Inject guardrails first.

## environment (one per location) {#environment}
> `<This location: cozy living room / sunny city sidewalk / modern coffee shop / warm
> bedroom>`, `<time-of-day + lighting>`, inviting and real, no people in the foreground.
> Photorealistic.

Generate all locations up front so the arc is coherent (consistent time-of-day
progression if you want a "one day" read).

## 3x3 pose grid (per chunk, refs: base-character + THIS chunk's location) {#grid}
> A 3x3 grid of the EXACT same `<persona>` from the reference image, same face and
> identity, wearing `<the exact wardrobe for this location per the wardrobe policy>`,
> `<action for this location: seated on the couch / walking along the sidewalk / seated
> at the coffee table / lounging in bed>` in `<this location>`. Looking at the camera in
> all nine, naturally grounded, identity + wardrobe + lighting consistent within this
> location. Photorealistic.

## extract {#extract}
Same as ugc-single — cleanest grounded on-character cell; Gate-B QA with identity +
wardrobe focus against the base.
