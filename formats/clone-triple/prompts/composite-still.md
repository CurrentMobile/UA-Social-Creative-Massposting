# Prompt — clone-triple composite still (`gpt_image_2`)

The multi-instance frame: the SAME persona appears 2-3 times, identical face + wardrobe,
different attitudes. Reference = the persona `base-character.png`. Cross-format identity
rules apply (`formats/_shared/prompts/identity-consistency.md`, multi-character note).
Inject guardrails first.

## environment {#environment}
> `<A setting wide enough for the clones side by side: a couch, a kitchen counter, a
> park bench>`, warm even lighting, no people. Photorealistic, natural daylight.

## composite (double)
> A single wide 9:16 shot in `<environment>`. The EXACT SAME `<persona>` from the
> reference image appears TWICE in the same frame, identical face, identical `<exact
> wardrobe>`, clearly the same person, no seam between them. On the LEFT: `<pose +
> attitude, e.g. arms crossed, skeptical, unimpressed>`. On the RIGHT: `<pose +
> attitude, e.g. leaning in eager, bright and excited, open-hand gesture>`. Both
> naturally seated/standing on the same `<surface>`, feet planted, consistent lighting.
> Photorealistic. `<optional: the left one wears her glasses, the right one doesn't — a
> subtle tell.>`

## composite (triple)
Same, with a third instance in the CENTER: `<calm, wise mediator pose, hands settling
the two>`. Triple is harder to keep consistent — QA all three; fall back to double if
drift is bad.

## Worked example (double, skeptic vs hyped)
> A single wide 9:16 shot in a cozy living room. The EXACT SAME 20-something woman from
> the reference appears TWICE in the same frame, identical face, identical grey hoodie
> and jeans, clearly the same person. On the LEFT she sits with arms crossed and a flat,
> skeptical expression. On the RIGHT the same woman leans forward eagerly, bright-eyed,
> one hand raised mid-explanation. Both seated on the same couch, feet on the floor,
> warm window light, photorealistic, seamless — no visible seam or blur between the two.
