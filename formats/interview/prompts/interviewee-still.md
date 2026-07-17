# Prompts — interview interviewee stills (handheld street framing)

Per interviewee (keyed on the chunk's `speaker`). Refs: that interviewee's
`base-character.png` + the street environment + `_shared/props/handheld-mic.png`.
Cross-format rules apply. Inject guardrails first. The interviewer is NEVER rendered.

## environment {#environment}
> A `<public street / plaza / campus walkway>` in `<daylight>`, real and candid, with
> blurred passersby in the background bokeh (no faces in focus). No foreground subject.
> Photorealistic, documentary feel.

## 3x3 grid (per chunk) {#grid}
> A 3x3 grid of the exact same `<interviewee: age + look>` from the reference, same face
> + `<their exact wardrobe>`, standing on `<the street plate>`, being interviewed:
> reacting to an off-camera question with candid expressions (curious, surprised,
> laughing, considering), a handheld microphone from the reference just entering the
> lower/side frame in some tiles. Looking toward the off-camera interviewer / into the
> lens, handheld street framing, blurred passersby behind. Identity + wardrobe
> consistent across all nine. Photorealistic, candid, documentary.

## extract {#extract}
> Extract row `<R>` col `<C>` as a clean 9:16 handheld-framed portrait of the
> interviewee, mic just in frame if present, no grid lines, preserve exact face +
> `<wardrobe>` + street background. Gate-B QA (identity + wardrobe focus).
