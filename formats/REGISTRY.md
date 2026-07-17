# Format Registry

**The single source of truth for content formats.** A format not listed here does not
exist to `/create-videos` / `/create-statics`. Each row points at `formats/<slug>/`
(manifest `format.md`, full SOP `sop.md`, recipes, prompts, poster).

Status gates exposure: `draft` = SOP written, not yet validated with a real output
(shown in the intake form flagged "not yet validated"); `beta` = one real output
delivered; `production` = proven; `deprecated` = hidden (old manifests still resolve).

Feasibility = how reliably current AI models produce it: `proven` / `feasible` /
`experimental` (badge shown in the intake form; experimental formats may need retries).

| id | name | family | status | feasibility | version | poster | examples (G:) |
|----|------|--------|--------|-------------|---------|--------|----------------|
| ugc-single | UGC Talking Head — Single Location | video | production | proven | 1.0.0 | formats/ugc-single/preview/poster.jpg | format-examples\ugc-single\ |
| ugc-multi-location | UGC Talking Head — Multi-Location | video | draft | feasible | 0.1.0 | formats/ugc-multi-location/preview/poster.jpg | format-examples\ugc-multi-location\ |
| clone-triple | Clone (Double / Triple Clone) | video | draft | feasible | 0.1.0 | formats/clone-triple/preview/poster.jpg | format-examples\clone-triple\ |
| interview | Street Interview (POV interviewer v1) | video | draft | experimental | 0.1.0 | formats/interview/preview/poster.jpg | format-examples\interview\ |
| street-interview-1 | Street-Interview Format-1 (skeptic→sold, popup cards) | video | beta | feasible | 1.0.0 | formats/street-interview-1/preview/poster.jpg | format-examples\interview\ |
| street-interview-2 | Street-Interview Format-2 (meme vox pop, chase hook) | video | beta | feasible | 0.1.0 | formats/street-interview-2/preview/poster.jpg | format-examples\street-interview-2\ |
| lofi-text | Lo-Fi Text-on-Screen Aesthetic Loop | video | draft | proven | 0.1.0 | formats/lofi-text/preview/poster.jpg | format-examples\lofi-text\ |
| reaction | Video Reaction | video | draft | feasible | 0.1.0 | formats/reaction/preview/poster.jpg | format-examples\reaction\ |
| ranking | Ranking / Top-N Countdown | video | draft | proven | 0.1.0 | formats/ranking/preview/poster.jpg | format-examples\ranking\ |
| split-screen | Split Screen (top/bottom, side-by-side) | video | draft | feasible | 0.1.0 | formats/split-screen/preview/poster.jpg | format-examples\split-screen\ |
| play-pause | Play/Pause Reaction | video | draft | feasible | 0.1.0 | formats/play-pause/preview/poster.jpg | format-examples\play-pause\ |
| yap | Yap (Raw Direct-to-Cam Rant) | video | draft | proven | 0.1.0 | formats/yap/preview/poster.jpg | format-examples\yap\ |
| static-ad | Static Ad (image creatives) | static | draft | proven | 0.1.0 | formats/static-ad/preview/poster.jpg | format-examples\static-ad\ |

Full examples path: `G:\Shared drives\Mode AI Creative Loop\format-examples\<slug>\` —
`workflows/core/deliver.md` seeds each folder with the first production-quality output
of its format.

## Rules

- Format slugs are kebab-case and match the directory name exactly.
- **No shared-core change may be motivated by a single format** — format-unique needs
  live in that format's recipes/SOP prose.
- Agents NEVER modify files under `formats/` except `formats/<slug>/learnings.md`
  (enforced by `tools/check_formats_lock.py` in preflight). Rule promotion into recipes
  is a human act via the promote-learnings flow, which bumps `version` in format.md.
- Video manifests record `format: <slug>@<version>`; manifests without a `format:`
  field read as `ugc-single@1.0.0`.
- Posters are ≤400KB JPEGs — the ONLY preview media in git; example MP4s live on G:.
