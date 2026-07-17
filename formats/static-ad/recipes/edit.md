# Edit Recipe — static-ad

**The edit stage is SKIPPED for statics.** `format.md`'s `pipeline:` intentionally omits
`edit` (script → assets → deliver only). There is no timeline, no motion, no VO.

The compositing that a video's edit stage would do is instead a still-image step,
specified in `sop.md` §4 and driven by `prompts/compose-layout.md`: a HyperFrames
one-frame HTML render lays the approved copy over the base visual and exports a PNG per
aspect (9:16, 1:1, 4:5).

This file exists only to keep every format directory the same shape. Do not add a
timeline here.
