---
app: {{APP_SLUG}}
title: {{VIDEO_TITLE}}
slug: {{VIDEO_SLUG}}
status: scripting        # scripting | assets | editing | review | posted
platform: [tiktok, instagram]
aspect: 9:16
runtime_target_s: 30
persona:                  # persona slug in assets/_shared/personas/<slug>/ (for AI asset gen)
hook: ""                  # the opening line / visual hook
created: {{DATE}}
---

# {{VIDEO_TITLE}}

> Per-video manifest. Lists every asset for this video: path · type · purpose · when-to-use.
> Keep this current as assets are added — it is what the editor reads to assemble the cut.

## Concept
One or two sentences: the idea, the angle, the CTA.

## Assets
| Path | Type | Purpose | When to use |
|------|------|---------|-------------|
| ai-videos/ | a-roll/b-roll | AI / recorded clips | source footage |
| ai-images/ | image | stills / overlays | … |
| audio/ | audio | VO / generated audio | … |
| scripts/ | script | avatar dialogue script | drives the cut |
| sops/ | sop | brief / instructions | follow when editing |

## Screen recordings used
| Name (in _shared/screen-recordings/{{APP_SLUG}}/) | When to use |
|---|---|
| | |

## Audio choices
- Background music: <mood / chosen track path>
- SFX: <effect @ timestamp, …>

## Output
- Final: `outputs/{{APP_SLUG}}_{{VIDEO_SLUG}}_9x16.mp4`
- CTA appended: yes (per-app)
- Posted: <date / link when done>
