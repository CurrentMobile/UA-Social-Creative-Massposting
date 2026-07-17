# SOP — Yap (Raw Direct-to-Cam Rant) (`yap` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`, `feasibility: proven` (it's the simplest video shape).

---

## 1. Format overview

One person, front camera, talking fast and unfiltered — selfie-held or propped close,
like a voice-note to a friend. Deliberately low-production: no styled environment focus,
no five-card motion-graphics package, minimal-to-no B-roll. The hook, delivery energy,
and big word-by-word captions do all the work. It should read as an organic post, not an
ad.

**Personas:** 1. **Sub-styles:** none.

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/hook-problem-solution.yaml` (six beats), but written
in RAW, fast, spoken-word cadence — run-ons, "okay so", "no literally", casual. Chunk
normally (shorter clips, higher energy). The hook must land in the first ~1.5s.

**Worked sample (30s):**
```
HOOK        "okay I need to talk about this because I genuinely thought it was fake."
PROBLEM     "like every 'earn money on your phone' thing is a scam, right? right??"
SOLUTION    "no so this app actually rewards you for stuff you ALREADY do."
HOW IT WORKS "music playing, phone charging, reading the news — points. for real."
RESULT      "I cashed out a twenty-five dollar gift card in a week doing nothing extra."
CTA         "it's called Mode Earn, it's free on Google Play, go, now, I'm serious."
```

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. Stills ALWAYS `gpt_image_2`; A-roll `kling3_0` sound ON.
Inject guardrails.

**3.1 Environment (1, loose).** A casual, real, slightly-messy everyday spot (bedroom,
car, kitchen) — NOT a styled set. It barely matters; the face fills the frame.

**3.2 Selfie-framed grids + extracts (per chunk).** <!-- LOCKED --> Framing is a
close, slightly-high selfie angle (arm's-length front camera), face filling most of the
frame, direct eye contact, raw and real. <!-- /LOCKED --> Ref: `base-character.png` +
environment.

**Worked grid example:**
> A 3x3 grid of the exact same `<persona>` from the reference, same face + `<casual
> everyday wardrobe>`, at a close, slightly-high SELFIE angle (as if holding the phone
> at arm's length), face filling most of the frame, direct eye contact, animated
> expressive rant energy (different expressions: incredulous, laughing, leaning in).
> `<casual real setting>` slightly out of focus behind. Looking into the lens in all
> nine, naturally framed, identity + wardrobe + lighting consistent. Photorealistic,
> raw, unpolished.

**3.3 A-roll clips (per chunk).** Fast, high-energy, expressive delivery; voice tag
verbatim but PACED FAST; slight natural handheld (selfie shake is on-brand — a bit more
drift allowed than ugc-single). Phone shots (holding up to show the app) follow the
phone grammar.

**Worked clip example:**
> Begin on the close selfie-angle shot of `<persona>` from the reference, face filling
> the frame, direct eye contact, wearing `<casual wardrobe>`, `<casual setting>` behind.
> The camera has a slight, natural handheld selfie drift. They talk FAST and animated in
> `<voice tag verbatim>`, incredulous energy: "like every 'earn money on your phone'
> thing is a scam, right? right??" Big expressive eyebrows, a disbelieving head-shake,
> leaning toward the lens. Wardrobe, lighting, and background consistent — a seamless
> single take.

**3.4 B-roll (minimal).** <!-- LOCKED --> Minimal-to-none — the raw talking is the
format. <!-- /LOCKED --> At most 1-2 quick cutaways for the app reveal (phone up, real
UI) at the HOW/RESULT beat. Do NOT hit the ugc B-roll quota; a mostly-continuous talking
cut is correct here.

**3.5 QC.** Gate-D on clips; `check_assets.py` (the B-roll quota is intentionally
relaxed for this format — the recipe sets `count.min: 0` with a note).

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`.
- Fast jump-cuts between chunks (tight — cut the breaths); heavier punch-zoom energy.
- <!-- LOCKED --> BIG animated word-by-word / phrase captions (karaoke-style, bouncing,
  center or upper-center), the visual signature of the format — captions carry it.
  <!-- /LOCKED --> (Built via the video-use / hyperframes caption path, not the small
  ugc lower-third.)
- NO five-card motion-graphics package; at most a logo-pop on the app name and a quick
  app-UI flash at the reveal. Hook sticker optional (the big captions often replace it).
- Music: a driving/trending-style bed, still 20% no duck; punchy SFX on the fast cuts.
- Endscreen CTA on the spoken CTA line, kept raw (no polished endcard takeover unless
  asked).

## 5. QA + guardrails hooks

Shot-types: `environment`, `grid`, `extract`, `aroll-clip`, `phone-shot`. Codes:
IDENTITY_DRIFT / WARDROBE_DRIFT, and confirm the big captions render clean at review
(WARPED_TEXT on the composited captions). Fewer phone shots so PHONE_* less frequent.
Inject guardrails; fails feed the ledger.

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/…_9x16.mp4`, shared-drive sync, seed
`format-examples/yap/`, manifest `format: yap@0.1.0` + intake ref, `check_manifest.py`,
propose `draft → beta` after the first validated output.
