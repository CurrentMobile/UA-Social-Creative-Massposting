---
app: mode-earn
display_name: Mode Earn
platforms: [tiktok, instagram]
brand_dir: assets/mode-earn/brand/
cta_dir: assets/mode-earn/cta/
default_music_mood: ""        # e.g. "upbeat", "lofi calm", "cinematic"
posting_cadence: ""           # e.g. "3x/week"
status: active
---

# Mode Earn — App Manifest

> **Single source of truth for Mode Earn. Read this FIRST before any work on this app.**
> Then read the relevant video's `manifest.md`. See `workflows/asset_organization.md` for rules.

## About the app
Mode Earn is a B2C rewards app (**Android / Google Play only**) that rewards users for everyday phone
activities — listening to music, playing games, charging the phone, reading news, and taking surveys.
Routine screen time becomes redeemable points → gift cards (Amazon, Best Buy) or PayPal. Audience: the
6 ICP archetypes (Broke Student Jake, Single Mom Maria, Side Hustle Jake, Gen Z Ashley, Crypto-Curious
Tom, Guilt-Free Mama Grace), broadly age 16–45, digitally savvy, money-conscious. Tone: friendly,
energetic, transparent — UGC/"friend sharing a hack," never salesy. Social proof: 10M+ downloads,
4.5★, 3M+ reviews.

## Brand
Logo / colors / fonts / voice live in `brand/`. **Full distilled brief (voice, language rules,
personas, triggers, compliance) → [`brand/creative-direction.md`](brand/creative-direction.md) — read
it before writing any script.** Must-follow rules:
- **Language:** say *reward* not *pay*, *gift cards / real rewards* not *cash / money*; never
  get-rich-quick. Frame as redeemable rewards; keep disclaimer "Earnings vary. Rewards are given as
  redeemable points."
- **Android only:** never show an iPhone (see AI-generation rules below).
- **Voice / do's & don'ts:** conversational, friendly, energetic, transparent. Do show real modest
  wins and social proof; don't overpromise earnings or sound like an ad.
- **Stats:** standardize on 10M+ downloads, 4.5★, 3M+ reviews (ignore older "50M / 4.4★" sample copy).

### AI-generation rules (must follow for every MEA image/clip)
- **Phones = modern Android only.** Mode Earn is Android / Google Play only — NEVER show
  an iPhone. Whenever a phone appears in a prompt, name a specific modern Android model
  and color (e.g. "Black Samsung Galaxy S22 Ultra", "Google Pixel 9"). The Higgsfield
  default tends to draw iPhones; specifying the model prevents it.
- **Consistent phone prop:** for any shot where a persona holds a phone, ALSO pass
  `assets/_shared/props/samsung-galaxy-s22-ultra.png` (front+back reference) as an extra
  `--image` and say "the same Black Samsung Galaxy S22 Ultra from the reference" — keeps
  the exact same device across all assets.
- **App UI on phone screens:** composite from `MEA Screenshots/` (Home, Music, News,
  Offers, Cashout) or the promo `brand/MEA-logo.png`; pass it as a `--image` reference.
- **Phone-to-camera reveal clips: 3 seconds** (Kling), and the reveal last frame should
  put the phone screen at ~70% of the frame with the character in soft-focus bokeh behind.

### Brand assets on disk
- Static promo banner/logo: `assets/mode-earn/brand/MEA-logo.png`; animated: `MEA-Logo-Animation-POP-UP.mov`
- App UI screenshots: `MEA Screenshots/` (project root)
- Social-proof reviews: `assets/mode-earn/MEA Reviews/` (Play Store comment screenshots — overlay cards at edit; app-wide, reusable across MEA videos)

## CTA end screen
Per-app CTA clip(s) in `cta/`, appended to every final video via `tools/append_cta.py`.
- Primary: `assets/mode-earn/cta/<file>.mp4`  — when to use: …

## Relevant screen recordings
Reusable app screen recordings live in `assets/_shared/screen-recordings/mode-earn/`,
named `<action>-SR`. List the key ones:
| Name | Shows | When to use |
|------|-------|-------------|
| playing-music-SR | … | … |

## Video index
| Folder | Status | Platform | Notes |
|--------|--------|----------|-------|
| [music-tab-promo](music-tab-promo/manifest.md) | scripting | tiktok,instagram | Music Tab Promo |
| [backinthe-80s](backinthe-80s/manifest.md) | scripting | tiktok,instagram | Backinthe 80s |
| [extraincomeforretirees](extraincomeforretirees/manifest.md) | review | tiktok,instagram | ExtraIncomeForRetirees |
| [viral-app-guinea-pig](viral-app-guinea-pig/manifest.md) | scripting | tiktok,instagram | Viral App Guinea Pig |
| [funding-my-little-treats](funding-my-little-treats/manifest.md) | scripting | tiktok,instagram | Funding My Little Treats |
| [earning-while-i-sleep](earning-while-i-sleep/manifest.md) | scripting | tiktok,instagram | Earning While I Sleep |
| [extra-cushion-on-a-budget](extra-cushion-on-a-budget/manifest.md) | scripting | tiktok,instagram | Extra Cushion On A Budget |
<!-- scaffold.py appends rows here -->
