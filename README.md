# Mode AI Creative Loop

**An AI creative studio that turns a short brief into finished, ready-to-post social content.**
You pick a content style, fill in one form, and approve a script — the studio writes the script,
generates the AI actors and footage, edits everything with captions, motion graphics, music, and
sound, checks every frame for mistakes, and hands you finished videos (or image ads), usually in
several variations. **You never touch code.**

It can make **videos in 11 different styles** and **static image ads** — see [the full list](#the-content-styles-you-can-make) below.

---

## 🚀 Quick start (already set up?)

Type one of these in Claude and follow the form:

| Type this | To make… |
|-----------|----------|
| **`/create-videos`** | a video in any style (UGC, ranking, interview, lo-fi, clone, split-screen, reaction, play/pause, yap…) |
| **`/create-statics`** | image ad creatives |

That's it. The rest of this page walks you through exactly what happens, step by step.

*(First time on this computer? Jump to [Setting up](#-first-time-setup-once-per-computer) first.)*

---

## 🎬 Making a video — the full journey, step by step

### Step 1 — Start it
In Claude, type **`/create-videos`** and press enter.

*(Power-user shortcut: you can pre-fill choices, e.g. `/create-videos ugc-single retiree-female-poc mode-earn` — but you never have to. Just typing `/create-videos` is enough.)*

### Step 2 — Claude runs quick safety checks (automatic, ~5 seconds)
Behind the scenes it confirms the video engine works and the AI account has credits. If something
is off, it stops and tells you exactly what to fix. You don't do anything here.

### Step 3 — Fill in ONE form (opens in your web browser)
A single page pops up in your browser with **everything on it** — no more answering questions one
at a time. Here's each box:

| Box | What to pick | Notes |
|-----|--------------|-------|
| **App** | Which app the content is for (Mode Earn, AppLock, etc.) | Pick **"➕ New app"** if it's not listed yet — a box appears where you paste a short description and Claude sets the app up for you. |
| **Format** | The content style — shown as **cards with a preview picture** | Each card has a poster, a one-line description, and a **"see example videos"** link so you know what you're choosing. A badge marks styles that are brand-new / not yet battle-tested. |
| **Sub-format** | A variation of the style, if the style has any | e.g. Interview → "off-camera interviewer". Hidden if the style has none. |
| **Persona(s)** | The on-screen actor(s) — shown with face thumbnails | Some styles use more than one; the form tells you how many to pick. |
| **Length** | ~15s / ~30s / ~45s / ~60s (depends on the style) | |
| **Variations** | How many versions to make (1–4) | More variations = more options to test. |
| **Script** | **"Claude writes it"** or **"I'll paste my own"** | If you paste your own, a text box appears. |
| **Autonomy** | **On** or **Off** — the one setting that decides how hands-on you are | See the box below. |
| **Extra notes** | Anything else you want Claude to know | Optional. |

**Every dropdown also lets you type your own answer** if the option you want isn't listed.
When you're done, click **"Start creating"** and go back to Claude.

> **💡 The one choice that matters: Autonomy On vs Off**
> - **On** → after you approve the script, it runs **all the way to finished videos** without
>   stopping. Fastest, most hands-off.
> - **Off** → it **pauses after each stage** (locations, actor shots, B-roll, video clips, final
>   edit) so you can look and tweak before it continues. Most control.
>
> Either way, **it never spends generation credits before you approve the script.**

*(No web browser available? Claude automatically falls back to asking you a couple of quick
questions in the chat instead — same result.)*

### Step 4 — ⭐ Approve the script (your key checkpoint)
- If **Claude writes it**: it drafts a few script options (with different hooks and calls-to-action).
  You read them, ask for any changes ("make the hook punchier", "swap CTA 2"), and pick the ones to
  produce. **Nothing is generated until you say yes.**
- If **you pasted your own**: it's used as-is.

Approved scripts are remembered, so future videos never accidentally repeat one.

### Step 5 — Claude generates the assets (automatic)
It creates the location, the actor poses, then the talking **A-roll** clips and the **B-roll**
cutaways using AI. **Every image is automatically checked for mistakes** — wrong phone, warped text,
extra fingers, the actor floating or clipping into furniture, outfit changing between shots — and
bad ones are regenerated *before* any expensive video is made. (AI video costs credits; for big jobs
Claude shows the estimated cost first.)

### Step 6 — Claude edits the video (automatic)
It transcribes the clips, cuts out the filler, and adds captions, motion-graphic cards (app demo,
reviews, balance counter, "FREE" stamp, logo pop), background music, and sound effects — all in the
house style for that format.

### Step 7 — ⭐ Review the editable preview (your moment to tweak)
Claude opens an **interactive timeline** in your browser (a link like `http://localhost:3017`).
Every clip, caption, overlay, and music track is a **separate, editable layer** — not one flattened
video. Watch it, then tell Claude what to change in plain English:
> *"Move the balance card one second earlier."* · *"Brighten the FREE stamp."* · *"Cut the third clip."*

It updates and re-shows. **Claude always waits for your OK here before the final render.**

### Step 8 — Final video + delivery (automatic)
Once you approve, Claude renders the final video, adds the app's call-to-action end-screen, and
**copies it to the team Google Shared Drive** (`G:\Shared drives\Mode AI Creative Loop\Videos`).

### Step 9 — Grab it and post 🎉
The finished 9:16 video is in the project's `outputs/` folder **and** on the shared drive. Ready for
TikTok, Instagram, Reels, wherever.

---

## 🖼️ Making image ads (statics)

Same idea, shorter journey. Type **`/create-statics`**, fill the form (App, style, copy), approve the
wording, and Claude generates the image ads and exports them in every size (9:16, 1:1, 4:5). There's
no editing step — you get finished PNGs.

---

## The content styles you can make

Type **"show me the formats"** in Claude to open a visual gallery, or browse
[`docs/formats-gallery.html`](docs/formats-gallery.html). The styles:

| Style | What it is |
|-------|-----------|
| **UGC — single location** | One relatable creator talking to camera about the app (the classic UGC ad). |
| **UGC — multi-location** | The same creator across a whole day — couch, street, coffee shop. |
| **Clone (double/triple)** | One creator appears 2–3 times in one frame, arguing with themselves. |
| **Street interview** | Off-camera interviewer asks real people for hot takes (vox-pop). |
| **Lo-fi text loop** | Dreamy ambient clips + text cards over a lo-fi beat, no presenter. |
| **Video reaction** | A creator reacts to and talks over footage. |
| **Ranking** | A countdown ("Top 5…") building to the app at #1. |
| **Split screen** | Presenter in one lane, live app demo in the other. |
| **Play/Pause** | Someone reacts to app footage that pauses mid-moment. |
| **Yap** | Fast, raw, selfie-cam rant with big captions. |
| **Static ads** | Image creatives (lifestyle, meme, feature-callout, review-proof…). |

New styles get added over time — the gallery always shows the current list.

---

## 🧰 First-time setup (once per computer)

**The easy way:** in Claude, paste this one sentence —

> *"Set up https://github.com/CurrentMobile/UA-Social-Creative-Massposting — follow the repo's onboarding."*

Claude installs the helper programs, downloads the project, builds everything, and checks it. Then it
walks you through the only **3 things a human must do**:

1. **Paste the secret keys** into the `.env` file (your team lead shares them via the password vault —
   ⚠️ never paste keys into the Claude chat).
2. **Sign in to Higgsfield** — run `higgsfield auth login` and finish the browser login.
3. **Sign in to Google Drive for desktop** so the `G:` drive appears.

When Claude prints **"All required checks passed. Studio is ready."**, you're done for good on this
machine. Full walkthrough: [`docs/TEAM_ONBOARDING.md`](docs/TEAM_ONBOARDING.md).

*(Already have the project open and just want to (re)run setup? Type `/setup`.)*

---

## 💬 Handy phrases to say to Claude

| Say this… | …and Claude will |
|-----------|------------------|
| `/create-videos` | make a video in any style (opens the one-shot form) |
| `/create-statics` | make image ad creatives |
| `/create-ugc-video <persona> <app>` | shortcut straight to a UGC talking-head video |
| "show me the formats" | open the styles gallery |
| "Set up <github-url> — follow the repo's onboarding" (or `/setup`) | set up a fresh computer |
| "run the environment check" | confirm everything's ready |
| "show me the editable timeline" | reopen the tweakable preview |
| "sync the finals to the shared drive" | push finished videos to Google Drive |

---

## 🆘 Common snags

| Problem | Fix |
|---------|-----|
| "command not found" right after installing | Close and reopen the terminal so it refreshes. |
| Claude says a key is missing | Open `.env`, paste the key from your team lead, save, retry. |
| The form didn't open in the browser | Tell Claude "the form didn't open" — it switches to asking in chat. |
| Weird symbol crash on Windows | Tell Claude "reapply the UTF-8 fix". |
| "Persona not found" | Pick a persona from the form's list (faces are shown). |
| A brand-new format looks off | Those are marked "not yet validated" — expect a retry or two; tell Claude what looked wrong. |

---

## For whoever maintains it (technical)

Day-to-day users can ignore this section.

- **How it's built — the WAT framework:** plain-language playbooks (`workflows/`) guide the AI, which
  runs reliable tools (`tools/`). Content **formats are data** — each lives in `formats/<slug>/`
  (a manifest, a step-by-step SOP, recipes, prompt templates, a poster) and is listed in
  `formats/REGISTRY.md`. Adding a style = adding a folder, not changing code.
- **Entry points:** `/create-videos` and `/create-statics` → `workflows/create.md` → the shared
  stages in `workflows/core/*`, with the chosen format's recipes plugged in. `/create-ugc-video`
  remains as a backward-compatible alias.
- **Quality gates:** `tools/qa_image.py` (rubric `qa/rubrics.json`) checks every image with Gemini
  vision before any paid clip; failures feed the guardrail ledger (`tools/guardrails.py`,
  `guardrails/`) whose rules are injected into future prompts.
- **Setup / ops tools:** `tools/bootstrap.py` (idempotent machine setup, driven by `/setup` →
  `workflows/onboard.md`), `tools/sync_assets.py` (pull/push media to the Google Shared Drive),
  `tools/cost_report.py` (credit/cost rollup), `tools/build_formats_gallery.py` (regenerates the
  gallery). Periodic upkeep is documented in [`docs/MAINTENANCE.md`](docs/MAINTENANCE.md).
- **Prerequisites:** Python 3.11, ffmpeg/ffprobe, Node/npx, git, plus venv packages from
  `requirements.txt`. `tools/env_check.py --strict` verifies everything.
- **API keys (`.env`, gitignored):** Higgsfield (AI footage), Gemini (QA + research), ElevenLabs
  (transcription); optional Apify, Postiz, HeyGen, OpenRouter.
- **Assets:** the repo ships reusable assets (personas, brand, CTA, props, SFX/music catalogs,
  posters). Heavy per-video media lives on the Google Shared Drive and is restored with
  `tools/sync_assets.py pull`.

### Project structure
```
mode-ai-creative-loop/
├── .claude/commands/    ← /create-videos, /create-statics, /create-ugc-video, /setup
├── formats/             ← one folder per content style (data, not code) + REGISTRY.md
│   ├── _shared/         ← shared anatomies, prompt rules, motion-graphic cards
│   └── <style>/         ← format.md, sop.md, recipes/, prompts/, learnings.md, preview/
├── workflows/           ← plain-language playbooks (create.md + core/ stages + onboard)
├── tools/               ← Python pipeline + QA + guardrails + setup/ops scripts
├── qa/rubrics.json      ← the image-QA checklist
├── guardrails/          ← the learned prompt-rule ledger
├── assets/              ← per-app brand, personas, props, SFX, music
├── docs/                ← TEAM_ONBOARDING, MAINTENANCE, formats-gallery
├── requirements.txt     ← Python dependencies
├── .venv/               ← project Python env (regenerable, gitignored)
└── .env                 ← API keys (gitignored)
```
