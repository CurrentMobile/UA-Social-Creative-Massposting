# Mode AI Creative Loop

An AI creative studio that turns a short brief into finished, on-brand **vertical (9:16)
UGC-style videos** for Mode's apps. You pick a presenter and answer a few quick questions;
it writes the script, generates the AI presenter footage and B-roll, then edits everything
together with animated captions, motion graphics, music, sound effects, and the app's
call-to-action — and hands you ready-to-post videos, usually in several variations.

Built on the **WAT framework** (Workflows, Agents, Tools): plain-language playbooks guide the
AI, which runs reliable, repeatable tools under the hood.

## What you get

- **Finished 9:16 videos** (1080×1920) — often multiple variations from a single run
- An **AI presenter (persona)** plus **B-roll** cutaways
- **Animated captions**, **motion-graphic cards** (app UI, social proof, count-ups, "FREE"),
  **background music**, and **sound effects**
- The correct **app CTA / endscreen** added automatically
- On-brand copy and visuals throughout (persona voice, brand language, required disclaimers)

## How to use it — one command

Everything runs through the **`/create-ugc-video`** command inside Claude. You don't touch code.

1. **Start it** — run `/create-ugc-video <persona> <app>`
   (e.g. `/create-ugc-video single-mom-maria mode-earn`).
2. **Answer a few quick questions** — it asks:
   - which **persona** (the on-screen presenter),
   - **video length** (~30s / ~45s / ~60s),
   - whether **you'll provide a script** or **Claude writes it**, and
   - **Autonomy: On or Off** — the one setting that decides how hands-on you are (see below).
3. **Approve the script — this is the key checkpoint.**
   - If Claude writes it, it drafts a few **script options**; you review, tweak until you're
     happy, and pick which ones to produce. **Nothing is generated until you approve.**
   - If you provide the script, it's used as-is.
4. **It produces the videos** — generates the presenter footage + B-roll, then edits, captions,
   scores, and renders each variation, and appends the app's CTA endscreen.
5. **You get finished videos back**, ready to post.

### The one choice that matters: Autonomy On vs Off
- **Autonomy On** → once you approve the script, it runs **straight through** to finished
  videos. Fastest and most hands-off.
- **Autonomy Off** → it **pauses after each step** (location, presenter shots, B-roll, video
  clips, final edit) so you can tweak or approve before it continues. Most control.

Either way, it **never spends generation credits before you've approved the script.**

---

## For whoever sets it up (technical)

Everything below is only needed to install and run the project on a machine — not for day-to-day
use of the `/create-ugc-video` command.

### First-time setup (fresh clone)
On a new Windows or Mac, follow **`workflows/setup_environment.md`** — or just tell Claude
*"set up the environment."* It runs `tools/env_check.py`, installs anything missing (each
failure prints the exact per-OS install command), builds the Python venv from
`requirements.txt`, and helps you create `.env` from `.env.example`.

```
python tools/env_check.py        # shows what's missing (any OS, no venv needed)
```

### Prerequisites
Python 3.11, ffmpeg/ffprobe, Node/npx, git, yt-dlp (in the venv); optional: gh, Bun, uv.
`env_check.py` verifies them all. If the venv is recreated, also recreate
`.venv/Lib/site-packages/sitecustomize.py` (forces UTF-8 stdio so helper output doesn't crash
on Windows — see setup workflow step 4).

### API keys (.env)
Real keys live in `.env` (gitignored — never committed). Copy `.env.example` to `.env` and fill
in the values: **Higgsfield** (AI footage), **ElevenLabs** (transcription), **Gemini**
(scriptwriting), plus optional Apify, Postiz, HeyGen, OpenRouter. Get the values from your team
admin.

### Assets
The repo ships the **reusable** assets (CTA, brand, screenshots, reviews, script-writing guide,
SFX, music, props, fonts, personas). Heavy per-video AI clips and rendered edits are **not** in
git — they live in the team's Google Shared Drive.

### Project structure
```
mode-ai-creative-loop/
├── .agents/skills/     ← bundled skills (video-use, hyperframes, higgsfield, …)
├── tools/              ← Python pipeline scripts (the WAT "tools")
├── workflows/          ← plain-language SOPs (create_ugc_video is the spine)
├── assets/             ← per-app brand, personas, CTA, SFX, music, script guides
├── requirements.txt    ← Python dependencies for the venv
├── .venv/              ← project Python env (regenerable, gitignored)
└── .env                ← API keys (gitignored)
```
