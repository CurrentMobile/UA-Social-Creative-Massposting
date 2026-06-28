# Workflow: Asset & SOP Organization

The canonical SOP for where assets live and how to locate them across the multi-app UGC
pipeline (Mode Earn, AppLock, NGL, Gallery, Cleaner, Trimbox → TikTok/IG). Global map:
`assets/ASSETS.md`. This file defines the rules every skill/agent follows.

## The tree (summary)

```
assets/
├── _templates/                   manifest templates (used by scaffold.py)
├── _shared/screen-recordings/<app>/   reusable app screen recs, named <action>-SR
├── sfx/{curated,downloads}/ + library.json   curated-first, yt-dlp fallback
├── music/ + library.json         background music (always downloaded)
└── <app>/
    ├── manifest.md               APP manifest (brand, CTA, conventions, video index)
    ├── brand/                    logo, colors, fonts, voice
    ├── cta/                      per-app CTA end-screen clip(s)
    └── <video-title>/
        ├── manifest.md           per-video asset list + status
        ├── ai-videos/ ai-images/ audio/ scripts/ sops/ edit/
```

## Standing rules

1. **Read manifests first.** Before any work on an app, read `assets/<app>/manifest.md`,
   then the specific `assets/<app>/<video-title>/manifest.md`. They are the single source of
   truth — asset paths, brand rules, what to use when. Don't hunt the filesystem blindly.
2. **SFX local-first.** Resolve every effect via `tools/resolve_sfx.py "<keywords>"`. It checks
   `assets/sfx/curated/` (your dropped library) before falling back to the yt-dlp route into
   `assets/sfx/downloads/`. It prints the resolved path as its last line.
3. **Background music is always downloaded** via `tools/fetch_music.py` → `assets/music/`.
   There is no curated music library.
4. **Append the per-app CTA to every final** via `tools/append_cta.py` before delivering.
5. **Keep manifests current.** When you add/choose an asset, record it in the video manifest
   (path · type · purpose · when-to-use). Validate with `tools/check_manifest.py <app-or-video>`.

## Naming conventions

- **App / video folders**: kebab-case slugs (`mode-earn`, `music-tab-promo`). `scaffold.py`
  slugifies titles automatically.
- **Screen recordings**: `<action>-SR.<ext>` describing the content, in
  `assets/_shared/screen-recordings/<app>/` — e.g. `playing-music-SR.mp4`, `lock-app-SR.mp4`,
  `clean-storage-SR.mp4`. Reusable across that app's videos.
- **Finals**: `outputs/<app>_<video-slug>_9x16.mp4`.

## Scaffolding new work

```
.venv\Scripts\python.exe tools\scaffold.py app <slug>            # once per app
.venv\Scripts\python.exe tools\scaffold.py video <app> "<Title>" # per video; auto-indexes in app manifest
```

## Manifest schema

- **App manifest** front-matter: `app, display_name, platforms, brand_dir, cta_dir,
  default_music_mood, posting_cadence, status` + a **Video index** table (folder · status ·
  platform · notes). `scaffold.py video` appends rows.
- **Video manifest** front-matter: `app, title, slug, status (scripting|assets|editing|review|
  posted), platform, aspect, runtime_target_s, hook, created` + an **Assets** table and
  **Output** section.

## Current temporary mode (until Higgsfield CLI is wired in)

The user manually drops AI clips into `assets/<app>/<video-title>/ai-videos/` and images into
`ai-images/`. Edit from there. When the Higgsfield CLI lands, it will populate these same
folders — no workflow change needed.

## Future phases (homes already reserved)

Research notes and dialogue scripts → `scripts/` + `sops/`; performance/posting metadata →
video-manifest front-matter and Output section. New steps slot in without restructuring.
