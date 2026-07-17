# Edit Recipe — lofi-text

Executed by `workflows/core/edit_stage.md` (`timeline: loop`). Minimal graphics — the
opposite of the UGC five-card set.

```yaml
timeline: loop              # concatenate scene loops; whole piece eases back to opener
layout: fullframe
graphics_slots:
  - {slot: cards, card: overlay-text, at: "each overlay-plan card over its scene"}
  - {slot: mark,  card: logo-watermark, at: "0s..end (low-opacity corner)"}
  - {slot: cta,   card: soft-cta, at: "final scene"}
cut_style:
  transitions: beat-crossfade   # crossfade or hard-cut on the lo-fi beat
  aesthetic_filter: grain+vignette+warm   # over everything, glues the scenes
captions: none              # the overlay-plan text cards ARE the on-screen text
music: {level: 0.55, duck: false}
sfx: subtle                 # optional vinyl crackle / rain bed / soft CTA chime
cta: soft-card              # NOT the UGC endscreen takeover
disclaimer: on-cta-card     # tiny, inside the aesthetic
```

<!-- LOCKED -->
- NONE of the five UGC motion-graphic cards; NO punchy shutters/flickers/zoom punches —
  this format's energy is calm and cohesive.
- Music at 0.55 with NO ducking (it is the soul; no VO to duck under).
- Text cards carry the message in dreamy typography (soft serif / typewriter,
  lowercase, gentle fade/blur-in) inside the safe zone; they double as the captions.
- The piece loops: the final scene eases back toward the opening frame.
- Editable per-track HyperFrames timeline before the final render — wait for edits.
<!-- /LOCKED -->

Per-app skin: brand palette, logo watermark, CTA text, and disclaimer come from
`assets/<app>/manifest.md` + `brand/` — never hardcoded. Optional
`brand/edit-overrides.yaml` may tune card colors/type.
