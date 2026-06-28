# Mode Earn — Creative Direction (distilled brief)

> **Single source of truth for voice, messaging, and personas. Every script run reads this first.**
> Distilled from the source briefs in `MEA-SCRIPT-WRITING-GUIDES-AND-BRIEF/` (kept as the archive).
> Maintained by `workflows/input_briefing.md`. When new briefs are dropped, re-distill into here.

## App snapshot
Mode Earn is a **B2C rewards app (Android / Google Play only)** that rewards users for everyday
phone activities — **listening to music, playing games, charging the phone, reading the news, and
taking surveys**. Routine screen time → redeemable points → **gift cards (Amazon, Best Buy) or PayPal**.
USP: *"Earn effortlessly"* — low barrier, flexible rewards, transparent redemption.

## Voice & tone
- **Conversational / UGC-native.** Sounds like a friend sharing a cool discovery — *never* a
  spokesperson or an ad read.
- **Friendly & approachable** — no jargon.
- **Energetic & motivational** — celebrates the win, keeps pace lively.
- **Transparent & trustworthy** — clear about how earning and redemption work.
- **Grounded, not hype.** Real, modest wins beat get-rich-quick energy.

## Language rules (must follow)
| Don't say | Say instead |
|-----------|-------------|
| Pay / paying / paid | Reward / rewarding / rewarded |
| Cash / money | Gift cards / real rewards |
| "Make $100 instantly" / get-rich-quick | "Earn rewards for daily habits" |
| iPhone / any Apple device | Modern **Android** only (it's Android-exclusive) |

- Frame everything as **redeemable rewards/points**, not direct payment.
- **Don't overpromise** earnings or sound salesy/pushy.
- Specific, modest dollar proof is good (e.g. "$53 from gaming and music"); inflated claims are not.

## Compliance & disclaimers
- Always frame as rewards given as redeemable points.
- Keep a disclaimer available for captions/description: **"Earnings vary. Rewards are given as
  redeemable points."**
- No guaranteed-income or "instant cash" language.

## Social-proof toolkit (use these numbers, keep them consistent)
- **10M+ downloads** on Google Play
- **4.5★ rating** from **3M+ reviews**
- Thousands of gift cards redeemed daily
> ⚠️ Some older sample scripts say "50 million downloads" or "4.4 stars" — **inconsistent, do not
> reuse**. Standardize on the figures above.

## Psychological triggers
- **"You're already doing it anyway"** — music/gaming/scrolling you do for free → get points for it.
- **FOMO / urgency** — "don't let that screen time go to waste."
- **Social proof** — downloads, rating, reviews; "now my [friend/partner] uses it too."
- **No catch** — "no catch, no tricks, just real rewards"; "it's free"; "no hidden fees."
- **Simplicity** — "stupid simple," open the app and pick how you earn.
- **Skeptic → believer** — "thought it was a scam… turns out it's legit."

## Earning methods (pick the few that fit the angle — don't list all every time)
Listen to music · Play games · Charge your phone · Read the news · Take surveys
→ points build up → redeem for **gift cards (Amazon, Best Buy) or PayPal**.

## Script anatomy (the section labels are sacred)
Scripts are written with these all-caps labels, in order. `tools/chunk_script.py` uses them as beat
boundaries downstream, so **always use them verbatim**:

`HOOK` → `PROBLEM` → `SOLUTION` → `HOW IT WORKS` → `RESULT` → `CTA`

- **HOOK** (first ~3s): the scroll-stopper. Relatable problem, persona intro, direct challenge, or
  outcome-first. Pairs with an on-screen **sticker overlay**.
- **PROBLEM**: the relatable pain (broke, screen-time guilt, bored).
- **SOLUTION**: discovering Mode Earn (often "thought it was a scam… but").
- **HOW IT WORKS**: the simple mechanism (open app, pick how you earn).
- **RESULT**: the concrete, modest win + redemption + a social-proof beat.
- **CTA**: download now / search "Mode Earn App" on Google Play; tie back to the hook.
- Target ~110–160 words total → ~30–60s. Conversational fragments, not corporate sentences.

## Target personas → presenter avatars
The 6 creative-brief audience archetypes each map to a ready avatar in `assets/_shared/personas/`
(set `persona: <slug>` in the video manifest; paste that persona's `voice-tag.md` into A-roll prompts).

| Audience persona | Core pain → desire | Presenter avatar (slug) | Status |
|------------------|--------------------|-------------------------|--------|
| Broke Student Jake (20) | Time/funds scarce → easy income | `student-jake` | exists |
| Single Mommy Maria (34) | Overwhelmed → convenience, saving | `single-mom-maria` | exists |
| Side Hustle Jake (28) | Burnout, uneven income → passive income | `side-hustle-jake` | exists |
| **Gen Z Ashley (19)** | Bored, broke-but-curious → fun, novelty, instant rewards | `gen-z-ashley` | exists (V1+V2) |
| Crypto-Curious Tom (30) | Skeptical → transparency, ROI | `crypto-curious-tom` | exists |
| Guilt-Free Mama Grace (32) | Screen-time guilt → earn without sacrificing family | `guilt-free-mama-grace` | exists |
| (Retiree angle, used in early MEA videos) | Fixed income → extra back | `retiree-female-poc` / `male-poc` | exists |

## Competitive edge (mention only if relevant)
Mode Earn earns by **music, charging, and reading news** — angles competitors (Sweatcoin, Mistplay,
Swagbucks) don't cover — plus multiple earning methods and gift-card/PayPal redemption.

## Shooting / format notes (for downstream steps)
- Vertical **9:16**, 30–60s, bright natural look, casual wardrobe (no logos).
- Phone = modern Android model named explicitly; app UI composited from `MEA Screenshots/`.
- Social-proof review cards: `assets/mode-earn/MEA Reviews/`.

## Source briefs (archive — do not edit, re-distill into this file)
- `MEA-SCRIPT-WRITING-GUIDES-AND-BRIEF/MEA Ad Creative Direction.docx` — positioning, personas, rules.
- `MEA-SCRIPT-WRITING-GUIDES-AND-BRIEF/MEA_CB_GFRoasting_..._SideHustleJake_UGC_....docx` — a full
  creator brief + 7-scene script + alt hooks + B-roll list (use for tone/structure only).
- `MEA-SCRIPT-WRITING-GUIDES-AND-BRIEF/mode scripts mashup.docx` — 10 past script variations
  (inspiration for tone/style — **never copycat**).
