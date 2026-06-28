# Mode AI Creative Loop

Local project for the Mode AI Creative Loop shared drive collaboration with Gianne.
Set up as an **AI video editing studio**: drop in raw A-roll / B-roll or AI clips and get
back an edited, captioned, scored vertical video.

## What it does (full pipeline)

Remove dead space + filler words · cut on word boundaries · color grade · add motion
graphics + animated captions · mix royalty-free background music + sound effects ·
render vertical 9:16 (1080×1920) · deliver to `outputs/`.

Built on two open-source skills plus local glue tools (WAT framework):

| Layer | What |
|-------|------|
| **`video-use`** skill | Editing engine — transcribe (ElevenLabs Scribe), cut, grade, captions, render. `.claude/skills/video-use/` |
| **`hyperframes`** skill | Motion graphics + animated captions (HTML→MP4). Run via `npx --yes hyperframes`. |
| `tools/fetch_music.py` | Download royalty-free background music (yt-dlp) → `assets/music/` |
| `tools/fetch_sfx.py` | Download sound effects (yt-dlp) → `assets/sfx/` |
| `tools/mix_audio.py` | Duck music under dialogue, sync SFX, normalize to −14 LUFS |
| `tools/env_check.py` | Preflight: verify binaries, deps, and ELEVENLABS_API_KEY |

## How to use

Tell Claude what you want, e.g. *"Edit these clips in `.tmp/launch/`, cut the filler, add
captions and a whoosh on each cut, score it with calm lofi, vertical."* Claude follows
`workflows/edit_video.md`. To preflight manually:

```powershell
.venv\Scripts\python.exe tools\env_check.py --strict
```

The end-to-end SOP is `workflows/edit_video.md`; sub-workflows cover music, SFX, and motion
graphics. **Always run Python via the project venv** (`.venv\Scripts\python.exe`) and from the
project root (so the ElevenLabs key in `.env` resolves).

## Structure

```
mode-ai-creative-loop/
├── .claude/skills/      ← installed skills: video-use, hyperframes, gsap, css-animations, …
├── vendor/hyperframes/  ← hyperframes monorepo clone (registry/blocks reference)
├── tools/               ← fetch_music, fetch_sfx, mix_audio, env_check
├── workflows/           ← WAT SOPs (edit_video is the spine)
├── assets/music|sfx/    ← downloaded audio (+ library.json catalog)
├── .venv/               ← project Python env (regenerable)
├── .tmp/                ← per-project working dir; <project>/edit/ holds artifacts
├── outputs/             ← final deliverables
└── .env                 ← API keys (gitignored; do NOT sync)
```

## First-time setup (fresh pull / new machine)

Cloning onto a new Windows or Mac? Follow **`workflows/setup_environment.md`** — or just ask
Claude to *"set up the environment,"* which runs the same SOP: it runs `tools/env_check.py`,
installs whatever's missing (each failure prints the exact per-OS install command), creates
the venv from `requirements.txt`, and helps you fill `.env` from `.env.example`.

```powershell
python tools\env_check.py            # see what's missing (works on any OS, no venv needed)
```

Heavy media (per-video AI clips, rendered edits, personas) is **not** in git — it lives in
the Google Shared Drive. The repo ships the reusable, lightweight assets only (CTA, brand,
screenshots, reviews, script guide, SFX, music, props, fonts).

## Prerequisites

Python 3.11, ffmpeg/ffprobe, Node/npx, git, yt-dlp (in venv); optional: gh, Bun, uv.
`env_check.py` verifies all of them. If the venv is recreated, also recreate
`.venv/Lib/site-packages/sitecustomize.py` (forces UTF-8 stdio so the helpers' Unicode
output doesn't crash on Windows — see setup workflow step 4).

## .env Setup

Real keys live in `.env` (gitignored **and** must be excluded from any shared-drive sync).
Never put real keys in `.env.example`. Keys: Higgsfield, OpenRouter, Apify, Postiz, HeyGen,
and **ElevenLabs** (transcription).

## Sync to Shared Drive

Files build locally and copy to `G:\Shared drives\Mode AI Creative Loop\osasenaga\`.

> ⚠️ **Exclude heavy regenerable dirs from the sync**: `.venv/`, `vendor/`, `node_modules/`,
> `.tmp/`, and `assets/music|sfx/`. They are large and rebuildable; syncing them bloats the
> shared drive. `.gitignore` already excludes them from git — the robocopy/Drive sync needs
> the same exclusions. `.env` must always stay excluded.
