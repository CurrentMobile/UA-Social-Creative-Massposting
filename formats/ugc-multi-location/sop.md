# SOP — UGC Talking Head, Multi-Location (`ugc-multi-location` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`, `feasibility: feasible`. Builds on the ugc-single
engine; only the multi-location differences are detailed.

---

## 1. Format overview

Same presenter delivers the script across 3-4 locations doing different actions,
cutting between them on beat boundaries. The consistency burden (same face, coherent
wardrobe across environments) is the whole challenge; the payoff is dynamic,
day-in-the-life energy.

**Personas:** 1. **Sub-styles:** none. **Wardrobe policy (a choice, stated up front):**
either ONE outfit throughout (easiest, reads as "same day, one errand run") or a
deliberate per-location outfit plan (higher production, more drift risk) — pick in the
brief and hold it consistently; never let it drift by accident.

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/hook-problem-solution.yaml` (six beats, same as
ugc-single). Chunk normally. Map beats to locations so the change lands on a boundary:
e.g. HOOK on the couch, PROBLEM walking outside, SOLUTION+HOW at a coffee shop, RESULT
in bed, CTA back on the couch.

**Worked sample (45s):**
```
HOOK        [couch] "I made money on my phone in four different places today. Watch."
PROBLEM     [walking outside] "I used to just doom-scroll on every commute."
SOLUTION    [coffee shop] "Now the Mode Earn App rewards that same time."
HOW IT WORKS [coffee shop] "Music, games, news, even charging — it all earns points."
RESULT      [bed] "By tonight, enough points for a gift card. From doing nothing new."
CTA         [couch] "Search Mode Earn App on Google Play."
```

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. Stills ALWAYS `gpt_image_2`; A-roll `kling3_0` sound ON.
Inject guardrails. <!-- LOCKED --> The persona `base-character.png` is passed on EVERY
still (the reference chain), and the wardrobe is named identically per the wardrobe
policy on every location. <!-- /LOCKED -->

**3.1 Environments (one still per location).** Generate each location plate (no people),
matching the day-in-the-life arc.

**Worked example (coffee-shop plate):**
> A cozy modern coffee shop interior by a window, warm afternoon light, a small wooden
> table with a latte, blurred patrons in the background bokeh, inviting and real. No
> people in the foreground. Photorealistic.

**3.2 Per-location grids + extracts.** One grid per chunk, referenced to
`base-character.png` + that chunk's location plate. Restate the exact wardrobe every
time (or the per-location outfit if using the outfit plan). Action varies by location
(seated on couch, walking on the street, sitting at the coffee table, lounging in bed).

Grid prompt note:
> …the exact same `<persona>` from the reference, same face, wearing `<the exact
> wardrobe for this location per the plan>`, `<action for this location: walking along a
> sunny sidewalk / seated at the coffee table>`, naturally grounded, looking at camera
> in all nine, identity + wardrobe + lighting consistent WITHIN this location.

**3.3 A-roll clips (per chunk).** Standard ugc-single clip prompt, pose-matched, voice
tag verbatim, exact dialogue. For walking beats allow the slight-handheld camera (still
no zoom/pan). Phone shots follow the phone grammar. Confirm cost; Gate-D QA.

**3.4 B-roll (quota per beat).** Cutaways that fit each location (POV walking + phone,
coffee-shop app reveal, bedside charging). Bank + registry.

**3.5 QC.** <!-- LOCKED --> Gate-D QA checks identity + wardrobe against the persona
base at EVERY location (cross-location drift is the core risk). <!-- /LOCKED -->
`check_assets.py`.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`. ugc-single cut style + location transitions:
- Cut to a new location on beat boundaries; a quick whip/match transition on the change
  reads as "next place" (SFX-tapped).
- The five cards fire at their beats as in ugc-single (app-ui-demo at HOW, etc.);
  logo-pop on the app name; hook sticker on HOOK; endscreen CTA on the spoken line.
- Punch zooms, ~30% flicker, captions, music 20% no duck — all as ugc-single.

## 5. QA + guardrails hooks

Shot-types: `environment` (per location), `grid`, `extract`, `aroll-clip`,
`phone-shot`, `broll-still`. Critical codes: IDENTITY_DRIFT + WARDROBE_DRIFT (across
locations — the core risk), ENVIRONMENT_DRIFT (within a location), FLOATING_CHARACTER /
SPATIAL_INTERSECTION, PHONE_*. Inject guardrails; fails feed the ledger. If cross-
location identity keeps drifting, reduce location count or lock to one wardrobe (log it).

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/…_9x16.mp4`, shared-drive sync, seed
`format-examples/ugc-multi-location/`, manifest `format: ugc-multi-location@0.1.0` +
intake ref, `check_manifest.py`, propose `draft → beta` after the first validated output.
