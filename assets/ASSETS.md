# Assets — Map & Rules

Global map of the asset tree for the Mode Mobile UGC pipeline. Skills/agents use this to
locate anything. **The authoritative detail per app lives in each app's `manifest.md`** —
read that first. Full SOP: `workflows/asset_organization.md`.

## Layout

```
assets/
├── ASSETS.md                     ← this file
├── _templates/                   ← app/video manifest templates (used by scaffold.py)
├── _shared/                      ← cross-app PERSISTENT assets
│   └── screen-recordings/<app>/  ← reusable app screen recs, named <action>-SR (e.g. playing-music-SR.mp4)
├── sfx/
│   ├── curated/                  ← user-dropped default SFX (checked FIRST)
│   ├── downloads/                ← yt-dlp fallback cache
│   └── library.json              ← unified SFX catalog (curated + downloaded)
├── music/                        ← background music (always downloaded) + library.json
└── <app>/                        ← one per app (slugs below)
    ├── manifest.md               ← APP manifest — READ FIRST
    ├── brand/                    ← logo, colors, fonts, voice/guidelines
    ├── cta/                      ← per-app CTA end-screen clip(s)
    └── <video-title>/
        ├── manifest.md           ← per-video manifest (asset list + status)
        ├── ai-videos/            ← AI / B-roll clips (drop here; Higgsfield later)
        ├── ai-images/            ← AI images / stills
        ├── audio/                ← VO / generated audio
        ├── scripts/              ← avatar dialogue scripts
        ├── sops/                 ← per-video brief / SOP
        └── edit/                 ← video-use working dir (transcripts, edl.json, renders)
```

## App slugs
`mode-earn` · `applock` · `ngl` · `gallery` · `cleaner` · `trimbox`

## Naming conventions
- **App / video folders**: kebab-case slugs (`mode-earn`, `music-tab-promo`).
- **Screen recordings**: `<action>-SR` describing the content
  (`playing-music-SR`, `lock-app-SR`, `clean-storage-SR`).
- **Finals**: `outputs/<app>_<video-slug>_9x16.mp4`.

## Standing rules (enforced by `workflows/asset_organization.md`)
1. **Read the app `manifest.md` + the video `manifest.md` before acting.** They are the
   single source of truth.
2. **SFX local-first**: `tools/resolve_sfx.py` checks `sfx/curated/` before the yt-dlp route.
3. **Background music is always downloaded** (`tools/fetch_music.py` → `music/`).
4. **Every final gets the per-app CTA appended** (`tools/append_cta.py`).

## Scaffolding
```
.venv\Scripts\python.exe tools\scaffold.py app <slug>
.venv\Scripts\python.exe tools\scaffold.py video <app> <video-title>
```
