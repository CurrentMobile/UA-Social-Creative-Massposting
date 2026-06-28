---
app: ngl
display_name: NGL
platforms: [tiktok, instagram]
brand_dir: assets/ngl/brand/
cta_dir: assets/ngl/cta/
default_music_mood: ""        # e.g. "upbeat", "lofi calm", "cinematic"
posting_cadence: ""           # e.g. "3x/week"
status: active
---

# NGL — App Manifest

> **Single source of truth for NGL. Read this FIRST before any work on this app.**
> Then read the relevant video's `manifest.md`. See `workflows/asset_organization.md` for rules.

## About the app
One-paragraph description: what the app does, target audience, key value props, tone.

## Brand
Logo / colors / fonts / voice live in `brand/`. Summarize the must-follow rules here:
- Colors: …
- Fonts: …
- Voice / do's & don'ts: …

## CTA end screen
Per-app CTA clip(s) in `cta/`, appended to every final video via `tools/append_cta.py`.
- Primary: `assets/ngl/cta/<file>.mp4`  — when to use: …

## Relevant screen recordings
Reusable app screen recordings live in `assets/_shared/screen-recordings/ngl/`,
named `<action>-SR`. List the key ones:
| Name | Shows | When to use |
|------|-------|-------------|
| playing-music-SR | … | … |

## Video index
| Folder | Status | Platform | Notes |
|--------|--------|----------|-------|
<!-- scaffold.py appends rows here -->
