# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

> **First time on this machine (fresh clone)?** Run `tools/env_check.py` to see what's missing,
> then follow `workflows/setup_environment.md` to install dependencies, build the venv from
> `requirements.txt`, and create `.env` from `.env.example`. Heavy media is not in git — it
> lives in the Google Shared Drive.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Slides, etc.) where I can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
.env            # API keys and environment variables (NEVER store secrets anywhere else)
credentials.json, token.json  # Google OAuth (gitignored)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Asset organization (UGC pipeline)

Assets for the multi-app UGC video pipeline (Mode Earn, AppLock, NGL, Gallery, Cleaner, Trimbox)
live under `assets/` in a per-app tree. **Before doing any work on an app's video, read
`assets/<app>/manifest.md` then the specific `assets/<app>/<video-title>/manifest.md` first** —
they are the single source of truth (brand, CTA, screen recordings, asset choices). The full
layout and rules are in `assets/ASSETS.md` and `workflows/asset_organization.md`. Standing rules:
SFX local-first via `tools/resolve_sfx.py` (yt-dlp fallback), background music always downloaded,
and every final gets the per-app CTA appended via `tools/append_cta.py`. **Always give me an editable
HyperFrames timeline preview before the final render** — each A-roll clip, B-roll cutaway, overlay,
and caption as a separate, tweakable track (never one flattened video). Build it with
`tools/build_editable_timeline.py` and serve via `npx hyperframes preview`, then wait for my edits
before rendering the final (see `workflows/edit_video.md` step 8). **Final deliverables always go to
the team Google Shared Drive at `G:\Shared drives\Mode AI Creative Loop\Videos`** — sync `outputs\*.mp4`
there on every delivery via `robocopy` (see `workflows/edit_video.md` step 9).

## Content formats (multi-format engine)

Content formats are **data, not code**: each lives in `formats/<slug>/` (manifest
`format.md`, step-by-step `sop.md`, recipes, prompt templates, poster) and is listed in
`formats/REGISTRY.md` — the single source of truth. Runs start with `/create-videos`
or `/create-statics`, which launch ONE browser intake form (`tools/intake_form.py`)
capturing everything up front, then drive `workflows/create.md` → `workflows/core/*`
with the chosen format's recipes plugged in. `/create-ugc-video` remains as the
backward-compat alias for `ugc-single`.

**Standing rules:**
- **Image generation ALWAYS defaults to GPT Image 2 (`gpt_image_2`)** — never another
  image model unless I explicitly ask (applies to every format, including clone
  composites; documented content-filter fallback only, visually confirmed).
- **Formats are LOCKED.** Never modify files under `formats/` except appending to
  `formats/<slug>/learnings.md`. `tools/check_formats_lock.py` runs in preflight and
  stops the run on drift. Promoting a learning into a recipe is MY act (version bump).
- **QA gates + guardrails on every asset run:** `tools/qa_image.py` (rubric
  `qa/rubrics.json`) gates every image before paid clips; failures feed
  `tools/guardrails.py add`; inject active guardrails before authoring prompts. A
  `fail` asset never seeds a paid Kling job.
- **Phone visibility grammar** (`formats/_shared/prompts/phone-visibility-grammar.md`):
  every phone-holding shot shows the screen to the viewer with the real app UI/logo;
  bare "holding a phone" is banned.
- **B-roll quota:** minimum 1 B-roll per script beat, cutaway every 3-5s — the
  `broll_slots` plan in `chunks.json` is mandatory; brainstorm from
  `assets/_shared/b-roll-bank/bank.md` and append shipped concepts to its registry.
- **Reference recreation (Step 3b):** a competitor winner approved for recreation — or any
  video/image the user drops in — gets a deep Gemini blueprint first via
  `workflows/analyze_video.md` (`/analyze-video`, tool `tools/analyze_video.py`) →
  `assets/<app>/reference-analysis/`. The intake form's Reference field triggers it
  automatically inside `/create-videos` runs.

## Public-fork sync (OS-Content Studio)

A sanitized, Mode-free duplicate of this pipeline lives at
`C:\Users\ADMIN\Projects\os-content-studio`. `tools/sync_to_studio.py` mirrors the
whitelisted trees there, replacing every Mode-specific term via its sanitization map and
failing on any forbidden-term leak. It runs automatically via a Stop hook in
`.claude/settings.local.json`, and can be run manually
(`.venv\Scripts\python.exe tools\sync_to_studio.py`, `--dry-run`, `--sweep`).
README.md / CLAUDE.md / .gitignore / .env.example / assets/ASSETS.md are MANUAL-tier:
the fork owns its own versions and the sync only reports drift — when it does, hand-port
the change (sanitized) into the fork. Mode app asset trees and screen recordings never
sync. Keep the fork private until the owner explicitly says otherwise.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
