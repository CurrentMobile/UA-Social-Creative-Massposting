# SOP — Ranking / Top-N Countdown (`ranking` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`. Builds on the ugc-single engine; only the differences
are spelled out where it matters.

---

## 1. Format overview

One AI presenter (one persona, one location, straight to camera) counts down a Top-N
list of a category, building to a #1 reveal that is always the promoted app. Each rank
gets a slamming badge ("#5" … "#1"), the presenter's energy escalates as the count
climbs, and the #1 segment carries the app demo cards + celebration treatment.
Reference feel: confident, punchy listicle with rising momentum.

**Personas:** exactly 1 (ugc-single library). **Sub-styles:** none.

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/ranked-list.yaml` — `RANK N:` labels are beat
boundaries; chunks carry `item_index`. Structure: HOOK → RANK 5 → RANK 4 → RANK 3 →
RANK 2 → RANK 1 (reveal) → CTA. Chunk with:
```
chunk_script.py scripts\source.md --anatomy formats\_shared\anatomies\ranked-list.yaml ^
  --out edit\chunks.json --vo-script scripts\vo-script.md
```

**Worked sample (Top 5, 45s):**
```
HOOK
"I tried every 'get paid on your phone' app so you don't have to. Top five, counting down."
RANK 5: "Number five — a walking-rewards app. Cute, but it caps out in about a week."
RANK 4: "Four — the survey grinders. Real money, painfully slow."
RANK 3: "Three — a games-for-gift-cards app. Fun, but it wants hours."
RANK 2: "Two — receipt cashback. Easy, but the payouts are tiny."
RANK 1: "Number one, and it's not close — the Mode Earn App. Music, charging, news, games — it all earns, in the background."
CTA
"Search Mode Earn App on Google Play. You'll thank me."
```
<!-- LOCKED --> Ranks 5-2 describe a generic CATEGORY only — no real competitor name,
logo, or UI. Rank 1 is always our app, named, with real UI. <!-- /LOCKED -->

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. Stills ALWAYS `gpt_image_2`; A-roll `kling3_0` sound ON;
B-roll sound OFF. Inject guardrails. Same environment/grid/extract flow as ugc-single
(`formats/ugc-single/prompts/a-roll-still.md`), but the pose/expression PROGRESSION per
rank is the special sauce.

**3.1 Environment + per-rank pose direction.** One environment; one grid per chunk. The
expression arc: HOOK = confident setup; low ranks (5-3) = measured, mildly unimpressed,
counting on fingers / dismissive hand; rank 2 = "getting warmer" lean-in; **RANK 1 =
big excitement, phone up showing the app**; CTA = warm direct address.

Grid prompt (rank 4, unimpressed):
> A 3x3 grid of the exact same `<persona>` from the reference, same face and wardrobe,
> standing/seated in `<environment>`, giving a mildly unimpressed "it's fine, I guess"
> expression with a small shrug, holding up four fingers in some tiles. Looking at the
> camera in all nine, naturally grounded, identity + wardrobe + lighting identical.

**3.2 A-roll clips (per chunk).** From `prompts/a-roll-clip.md`: pose-match, voice tag
verbatim, exact rank line, escalating energy. Phone reveal ONLY on the rank-1 clip
(phone visibility grammar, screen to viewer, real UI). Confirm cost, generate
sequentially, Gate-D QA.

**3.3 B-roll (quota per beat).** Each rank gets ≥1 cutaway. Ranks 5-2: GENERIC
category B-roll (e.g. a generic pedometer ring, a faceless survey form, a generic
arcade glow, a blurred receipt) — never a real competitor asset. Rank 1: the real app
UI (activity insert / phone reveal). Brainstorm from the bank; append to its registry.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`. ugc-single cut style (punch zooms, ~30% flicker, hook
sticker, captions, music 20% no duck) PLUS:
- **ranking-badge card at every `item:*`** (`formats/_shared/graphics/ranking-badge`):
  the rank number slams in on the item's first chunk, holds, exits on its last.
- **SFX escalation:** each rank's badge slam is a beat; pitch/impact climbs 5→1.
- **RANK 1 celebration:** #1 badge gets gold/glow + confetti + the biggest SFX; the
  app-ui-demo, cashout-counter, and logo-pop cards all fire on the RANK 1 segment
  (that's where the demo lives); free-stamp optional on the CTA.
- **Endscreen CTA** starts on the spoken CTA line; hook sticker on the HOOK.

## 5. QA + guardrails hooks

Shot-types: `environment`, `grid`, `extract`, `phone-shot` (rank-1 only),
`broll-still`, `aroll-clip`. Critical codes: IDENTITY_DRIFT / WARDROBE_DRIFT across the
many rank shots, PHONE_* on the rank-1 reveal, plus a manual review that ranks 5-2 B-roll
carries NO real competitor branding (compliance). Inject guardrails; fails feed the
ledger.

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/<videoTitleCamel>/…_9x16.mp4`, shared-drive
sync, seed `format-examples/ranking/`, manifest `format: ranking@0.1.0` + intake ref,
`check_manifest.py`, propose `draft → beta` after the first validated output.
