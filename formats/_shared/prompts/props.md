# Shared Props (cross-format)

Reusable prop reference images in `assets/_shared/props/`. Pass the relevant prop as
an extra `--image` reference whenever it appears, and describe it positively in the
prompt ("the same <prop> from the reference").

| Prop | File | Use |
|------|------|-----|
| Phone — front (screen) | `s22-ultra-front.png` | ANY screen-facing phone shot (the default per the phone visibility grammar) |
| Phone — back | `s22-ultra-back.png` | ONLY the tagged first frame of a phone-reveal clip |
| Phone — combined front+back | `samsung-galaxy-s22-ultra.png` | Only when both surfaces appear in one shot |

Rules:
- Pass only the surface that should be visible — showing the model the back invites it
  to draw the back.
- MEA and all Mode apps are **Android / Google Play only** — the S22 Ultra is the one
  device across every asset of every video.
- New props (e.g. a handheld interview mic, earbuds) get added here with the same
  pattern: one clean reference image, kebab-case filename, a row in this table, and a
  positive description clause in the format's prompt templates.
- Planned (create when their formats validate): `handheld-mic.png` (interview),
  `earbuds.png` (lofi/music beats).
