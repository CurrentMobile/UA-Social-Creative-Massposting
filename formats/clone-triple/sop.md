# SOP — Clone (Double / Triple Clone) (`clone-triple` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`, `feasibility: feasible` — the non-speaking clone can
drift, so this SOP is strict about short turns and per-clone QA.

---

## 1. Format overview

One persona appears 2-3 times in one frame as distinct "selves" (skeptic / hyped /
wise) debating the app. Same face, same wardrobe across clones; attitude and gesture
differ. clone-double is the reliable default; clone-triple is richer but harder to keep
consistent. Reference feel: a single relatable creator playing both sides of an
argument, cut like a real conversation.

**Personas:** 1 (from the library), rendered as N instances.
**Sub-styles:** `clone-double`, `clone-triple`.

## 2. Script anatomy

Anatomy: `formats/clone-triple/anatomy.yaml` (turns mode, speakers CLONE1/CLONE2/
CLONE3, `max_words: 18` ≈ ≤8s turns). Lines are written `CLONE1:` / `CLONE2:` … Chunk:
```
chunk_script.py scripts\source.md --anatomy formats\clone-triple\anatomy.yaml ^
  --out edit\chunks.json --vo-script scripts\vo-script.md
```
Assign roles: CLONE1 = skeptic (left), CLONE2 = hyped (right), CLONE3 = wise mediator
(center, triple only).

**Worked sample (clone-double, 8 turns, ~30s):**
```
HOOK
CLONE1: "Another 'get paid on your phone' app? Hard pass, those are all scams."
CLONE2: "Okay but hear me out — this one's different."
CLONE1: "That's literally what they all say."
CLONE2: "It rewards stuff you already do. Music. Charging. Reading news."
CLONE1: "…go on."
CLONE2: "Points turn into real gift cards. I cashed out twenty-five bucks last week."
CLONE1: "Wait, actually? Okay, show me."
CTA
CLONE2: "Search Mode Earn App on Google Play. Even you can't argue with free."
```

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. <!-- LOCKED --> Stills ALWAYS `gpt_image_2`; ALL clones
share the SAME voice tag (it's one person); turns ≤8s. <!-- /LOCKED --> Inject
guardrails.

**3.1 Environment.** One plate wide enough for the clones to sit/stand side by side
(e.g. a couch with room for 2-3, or a kitchen counter). No people.

**3.2 Composite still per scene-state (`gpt_image_2`, kind: composite).** The SAME
person from the reference appears N times in one frame, identical face + wardrobe,
different poses/attitudes. Pass the persona `base-character.png` as the reference.
Optionally give each clone ONE small distinguishing accessory (glasses / cap / mug) to
help the eye and the model — a sub-choice, keep it subtle.

**Worked example (clone-double composite):**
> A single wide 9:16 shot in `<environment>`. The EXACT SAME `<persona>` from the
> reference image appears TWICE in the same frame, identical face, identical `<exact
> wardrobe>`, clearly the same person. On the LEFT she sits with arms crossed and a
> skeptical, unimpressed expression. On the RIGHT the same woman leans in eagerly with
> a bright, excited expression, one hand raised mid-explanation. Both naturally seated
> on the same couch, feet planted, consistent warm lighting, photorealistic, no
> seam between them.

Gate-C QA the composite (`--shot-type broll-still --persona <base>`; both clones must
read as the same person, grounded, one surface).

**3.3 A-roll clip per turn (`kling3_0`, sound ON, ≤8s).** From the composite still,
the SPEAKING clone talks and gestures while the other(s) HOLD their pose, listening/
reacting. State exactly who speaks. Same voice tag; attitude varies (skeptic = dry,
hyped = energetic).

**Worked example (turn where CLONE2 speaks):**
> Begin on the composite two-shot from the reference, both clones present and
> consistent. The clone on the RIGHT begins speaking directly across to the left clone
> and to camera in `<voice tag verbatim>`, energetic and persuasive: "It rewards stuff
> you already do. Music. Charging. Reading news." She gestures with an open hand. The
> clone on the LEFT stays still, listening with a skeptical, arms-crossed expression,
> a small doubtful eyebrow. Both faces, wardrobe, lighting, and the background stay
> completely consistent — a seamless single take.

**3.4 B-roll (quota).** Cutaways: the app UI (phone reveal by the hyped clone, screen
to viewer, real UI), or a metaphor gag. Bank + registry as usual.

**3.5 QC.** <!-- LOCKED --> Gate-D QA checks EVERY clone at first AND last frame
(identity + wardrobe) — the non-speaking clone is the drift risk. <!-- /LOCKED -->
Re-roll turns where any clone drifts; keep turns short.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`. ugc-single base (punch zooms, hook sticker, cards, captions,
music 20% no duck, endscreen CTA on the spoken line) + conversation cutting:
- Cut BETWEEN turns like a real dialogue; punch-in slightly on whichever clone speaks.
- Optional subtle per-clone color accent in the grade (cool for skeptic, warm for
  hyped) to reinforce who's who — keep it gentle.
- App demo cards (app-ui-demo, logo-pop) fire when the hyped clone shows the app /
  says the name; free-stamp/cashout optional at the payoff turn.

## 5. QA + guardrails hooks

Shot-types: `environment`, `broll-still` (composite), `aroll-clip` (per turn),
`phone-shot`. Critical codes: IDENTITY_DRIFT + WARDROBE_DRIFT (per clone, both frames —
the core risk), SPATIAL_INTERSECTION / FLOATING_CHARACTER (two bodies on one couch),
PHONE_* on the reveal. Inject guardrails; fails feed the ledger. If clone-triple keeps
drifting, fall back to clone-double (log it in learnings).

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/…_9x16.mp4`, shared-drive sync, seed
`format-examples/clone-triple/`, manifest `format: clone-triple@0.1.0` + sub_format +
intake ref, `check_manifest.py`, propose `draft → beta` after the first validated output.
