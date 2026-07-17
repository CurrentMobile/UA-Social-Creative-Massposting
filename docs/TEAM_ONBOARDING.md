# Mode AI Creative Loop — Team Setup & Video Guide

*A plain-English guide to setting up the project and making your first finished video.
No coding required.*

---

## The 30-second mental model

> **Think of this project as a robot video studio.** You talk to it in plain English
> inside **Claude Code**. You describe the video you want; the robot writes the script,
> generates the AI actor and clips, edits everything, adds captions/music/sound, shows you
> a preview to tweak, then delivers the finished vertical video to the team Google Drive.
> **You never write code** — you give instructions and approve along the way.

Under the hood it follows a simple idea called **WAT**:

- **W — Workflows**: the recipes (step-by-step instructions the robot follows)
- **A — Agent**: Claude (the brain that reads the recipe and does the work)
- **T — Tools**: small programs that do the heavy lifting (transcribe, cut, render…)

There are only **two phases** to learn:

1. **Set up once** — per computer, ~15–20 minutes. You do this a single time.
2. **Make a video** — the fun loop you'll repeat for every video.

---

## PHASE 1 — Set up once (do this on each computer — Windows)

> **Goal:** reach the point where Claude says *"All required checks passed. Studio is ready."*

### Step 1 — Install Claude Code and sign in
Download **Claude Code** (the desktop app) from Anthropic and sign in with your own
Anthropic account. *(Everyone needs their own login — ask your team lead (Osasenaga) for
access.)* This is the window where everything else happens.

### Step 2 — Let Claude set up the whole machine
In Claude Code, paste this ONE sentence (Claude does the rest — installs the helper
programs, downloads the project, builds the Python environment, applies the Windows
text-encoding fix, and checks everything):

> **"Set up https://github.com/CurrentMobile/UA-Social-Creative-Massposting — follow the
> repo's onboarding."**

*(Already have the project open? Just type `/setup`.)* Under the hood this runs
`workflows/onboard.md` → `tools/bootstrap.py`, which is idempotent and resumable — if it
stops, just say "continue the setup" and it picks up where it left off.

### Step 3 — The 3 human steps ("the 10 human minutes")
Claude can do almost everything, but three things need you (it can't, by design):
1. **Secret keys** — your team lead (Osasenaga) shares them via the team password vault.
   Open `.env` in Notepad and paste them into the empty lines Claude points out
   (`HIGGSFIELD_API_ID`/`HIGGSFIELD_API_KEY`, `GEMINI_API_KEY`, `ELEVENLABS_API_KEY`).
   ⚠️ **Never paste keys into the Claude chat** and never upload `.env` anywhere.
2. **Higgsfield login** — run `higgsfield auth login` in a terminal and finish the
   browser sign-in.
3. **Google Drive** — install Google Drive for desktop and sign in so the `G:` drive
   mounts (that's where finished videos + heavy media live).

### Step 4 — Verify it's ready
Claude finishes by running the environment check. When it prints **"All required checks
passed. Studio is ready."** — setup is done for good on this machine.

---

## PHASE 2 — Make a video (repeat every time)

The whole thing is **one command and a few approvals.**

### 1. Open the project in Claude Code
Open the `mode-ai-creative-loop` folder.

### 2. Start the pipeline
Type one of the two commands:
```
/create-videos     ← any video format (UGC, ranking, interview, lo-fi, clone, split-screen…)
/create-statics    ← image ad creatives
```
You can pre-fill and skip the picker: `/create-videos ugc-single retiree-female-poc mode-earn`.
*(The old `/create-ugc-video <persona> <app>` still works — it's a shortcut for the UGC
format.)*

### 3. Claude runs silent safety checks
It confirms the environment, the video engine, and the AI account credits. If something's
off, it stops and tells you how to fix it.

### 4. Fill ONE form (opens in your browser)
A single form pops up with **everything** on one page — no more back-and-forth questions:
- **App** (or "➕ New app" — paste a product brief and Claude onboards it inline)
- **Format** — pick from cards, each showing a **preview poster + example-video link** so
  you can see what it looks like before choosing; a badge flags "not yet validated" formats
- **Sub-format, Persona(s), Length, Variations**
- **Script** — "I'll paste my own" or "Claude writes it"
- **Autonomy** — On (run through after you approve the script) / Off (pause each stage)
- **Extra notes**

Every dropdown also lets you type a custom value. Submit once and Claude takes it from
there. *(No browser? Claude falls back to a couple of quick in-chat questions.)*

### 5. ⭐ Approve the script
If Claude writes it, it drafts a few angles, each with hooks + calls-to-action. You pick
the ones you like, tweak the wording, and approve. *Nothing is saved until you approve, and
approved scripts are remembered so future videos never repeat them.*

### 6. AI generates the assets
Claude creates the location, the actor poses, then the talking **A-roll** clips and
**B-roll** cutaways using Higgsfield AI. *(AI video costs credits — for big jobs Claude
shows the cost first.)*

### 7. Claude edits the video
It transcribes the clips, cuts filler, and adds captions, motion-graphics cards (app demo,
reviews, balance counter, "FREE" stamp, logo pop), background music, and sound effects —
all automatically, in the house style.

### 8. ⭐ Review the editable preview (your moment to tweak)
Claude opens an **interactive timeline** in your browser (a link like
`http://localhost:3017`). Every clip, caption, overlay, and music track is a **separate,
editable layer** — not one flattened video. Watch it, then tell Claude what to change
("move the balance card 1 second earlier", "brighten the FREE stamp"). It updates and
re-shows. **Claude always waits for your approval here before the final render.**

### 9. Final render + delivery
Once you approve, Claude renders the final, appends the app's call-to-action end-screen,
and **copies it to the team Google Shared Drive**
(`G:\Shared drives\Mode AI Creative Loop\Videos`).

### 10. Grab it and post 🎉
The finished 9:16 video is in the project's `outputs/` folder **and** on the shared drive.
Ready to post to TikTok / Instagram / etc.

---

## Cheat sheet — handy phrases to say to Claude

| Say this… | …and Claude will |
|-----------|------------------|
| "Set up <github-url> — follow the repo's onboarding" (or `/setup`) | set up the whole machine |
| "run the environment check" | confirm everything's ready |
| `/create-videos` | make a video in any format (opens the one-shot form) |
| `/create-statics` | make image ad creatives |
| `/create-ugc-video <persona> <app>` | shortcut for a UGC talking-head video |
| "show me the formats" | open the formats gallery (poster + description per format) |
| "edit these clips in `<folder>`, cut filler, add captions and lofi music, vertical" | edit existing footage without the full pipeline |
| "show me the editable timeline" | reopen the tweakable preview |
| "sync the finals to the shared drive" | push the outputs to Google Drive |

---

## Troubleshooting — the 5 most common snags

| Problem | Fix |
|---------|-----|
| "command not found" right after installing | Close and reopen the terminal (it needs to refresh). |
| Claude says a key is missing | Open `.env`, paste the key from your team lead, save, retry. |
| Weird symbol crash on Windows | Tell Claude "reapply the UTF-8 fix". |
| "Persona not found" | Check the slug exists in `assets/_shared/personas/`. |
| Setup check fails | Read each `[FAIL]` line — it prints the exact command to fix it. |

---

## What each teammate needs

- ✅ **Their own Claude Code / Anthropic login** (each person, individually).
- ✅ **The shared API keys** from your team lead (Higgsfield, Gemini, ElevenLabs), pasted
  into `.env`. You do **not** create your own AI-service accounts.
- ✅ **Access to the Google Shared Drive** "Mode AI Creative Loop" (where delivered videos
  and the heavy media live — that media is **not** stored in GitHub).

---

*Questions? Ask in the team channel or ping Osasenaga.*
