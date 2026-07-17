# Compositing — static-ad (HyperFrames 1-frame render)

Lay the approved copy over the base visual as an HTML layout; render ONE frame per
aspect. Brand font/colors/logo/badge/disclaimer from `assets/<app>/brand/`.

## Method
1. Master layout at 1080×1920 (9:16). Place the base visual full-bleed; add a scrim/
   plate behind text over busy areas for contrast.
2. Copy hierarchy: headline (largest, brand display font) > subhead > CTA button/lockup.
   App logo + Google Play badge + small disclaimer on every creative.
3. Reflow (don't just crop) for 1080×1080 (1:1) and 1080×1350 (4:5) — keep headline +
   CTA inside each aspect's safe area.
4. Render each aspect as a 1-frame HyperFrames capture at 2x → PNG.
5. Review composed set with the owner before delivery. QA the composite for
   `WARPED_TEXT` / clipping (LOCKED gate).

## Sample layout snippet (illustrative)
```html
<div class="ad" style="width:1080px;height:1920px;position:relative;font-family:var(--brand-font)">
  <img src="base-visual.png" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover">
  <div class="scrim" style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.55),transparent 40%)"></div>
  <h1 style="position:absolute;top:90px;left:64px;right:64px;color:#fff;font-size:84px;font-weight:800;line-height:1.05">
    your phone's just sitting there. it could be earning.</h1>
  <div class="cta" style="position:absolute;bottom:150px;left:64px;right:64px;display:flex;flex-direction:column;gap:16px">
    <span style="font-size:40px;color:#fff">music · games · charging — all rewarded</span>
    <span class="btn" style="background:var(--brand-accent);color:#0f1115;font-weight:800;font-size:44px;padding:22px 34px;border-radius:16px;text-align:center">Get Mode Earn — free</span>
  </div>
  <img src="logo.png" style="position:absolute;top:48px;right:48px;height:84px">
  <img src="google-play-badge.png" style="position:absolute;bottom:70px;left:64px;height:56px">
  <p style="position:absolute;bottom:24px;left:64px;right:64px;color:#ddd;font-size:22px;text-align:center">
    Earnings vary. Rewards are given as redeemable points.</p>
</div>
```
Swap `--brand-font` / `--brand-accent` / logo / badge from the app's brand kit.
