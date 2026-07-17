# Workflow: Reference Video Analysis (Step 3b)

Take **ONE** reference — a competitor-research winner approved for recreation, a local
file the user drops in, or a URL — and produce a hyper-detailed **recreation blueprint**
with Gemini multimodal on the most capable model available at analysis time. The
analysis persona is an elite Direct Response organic-social + paid-ads Content
Strategist and Creative Director; the output is a technical contract the edit stage can
execute 1:1: scene-by-scene cut table, camera mechanics, framing, transition/animation
behaviors, CTA mechanics, B-roll trigger rules, and a speaker-tagged transcript.

**Positioning:** Step 3 (`winning_video_breakdown.md`) is *wide triage* of many winners
(coarse creative anatomy, pattern synthesis). This step is *deep analysis of one
reference* you actually intend to recreate or draw heavy inspiration from. Statics
(image ads) are supported too (`--static`).

## Objective
Produce `assets/<app>/reference-analysis/<date>/<slug>/blueprint.md` (+ `blueprint.json`)
covering all six sections, nothing missed — especially camera mechanics, VFX, motion
graphics, and animation behaviors:
1. Overview & Creative Direction (format+aspect, color grading, audience, every
   persona, pacing)
2. Scene-by-Scene Breakdown — one row per cut
3. Technical Execution (asset layering/rotoscoping, end-card/CTA mechanics)
4. Production Checklist (A-roll avatar requirements; B-roll & digital assets)
5. B-Roll Generation Template (4–5 trigger keywords → programmatic B-roll standards)
6. Complete Tagged Transcript

## Inputs
- The reference, ONE of:
  - winner rank + research date (`assets/<app>/competitor-research/<date>/winners.json`)
  - a local video/image file path
  - a URL (TikTok/IG page URL via yt-dlp, or a direct media URL)
- `GEMINI_API_KEY` in root `.env` (already a required key).
- App slug — routes the output tree only; the analysis itself is app-agnostic
  (brand adaptation happens downstream, not here).

## Tools
- `tools/analyze_video.py` — resolves/downloads the source, uploads to Gemini's Files
  API, generates the schema-enforced blueprint, self-validates, renders `blueprint.md`,
  and logs cost. **`--dry-run` spends nothing.**
  ```
  # 1) resolve source + auto model + plan (no spend):
  .venv\Scripts\python.exe tools\analyze_video.py --app mode-earn --winner 1 --date 2026-06-24 --dry-run
  # 2) run (examples of the three source modes):
  .venv\Scripts\python.exe tools\analyze_video.py --app mode-earn --winner 1 --date 2026-06-24
  .venv\Scripts\python.exe tools\analyze_video.py --app mode-earn --file "C:\refs\clip.mp4"
  .venv\Scripts\python.exe tools\analyze_video.py --app mode-earn --url "https://www.tiktok.com/@user/video/123"
  ```
  Key flags: `--model auto` (default — newest Pro-tier on the key, e.g. Gemini 3.x Pro
  when available; pass an explicit id to override), `--static` (image mode), `--fps N`
  (denser sampling for fast-cut edits), `--media-resolution low` (long videos),
  `--retry-note "<text>"` (corrective re-run), `--slug`, `--force` (bypass 15-min gate).
  Exit codes: 0 clean, 2 written-with-warnings, 1 hard fail. Last stdout line =
  `blueprint.md` path.

## Steps
0. **Preflight.** Gemini shows WORKS (`tools/test_api_keys.py`). Winner source: the
   rank must be an **organic** entry with a `video_url` (FB text-only ads can't be
   blueprinted — analyze their copy via Step 3 instead). If a blueprint for this source
   already exists under `assets/<app>/reference-analysis/**/`, offer to reuse it
   instead of re-spending.
1. **Dry-run cost gate.** Run with `--dry-run` and read back: resolved source, file
   size/duration, the **auto-selected model**, and the output path. Pro-tier video
   analysis is roughly $0.10–0.50 for a short clip. Confirm the spend with the owner
   before the live call (project rule: check before paid API calls).
2. **Run the analysis.** The tool downloads/copies the source to `.tmp`, uploads,
   waits `ACTIVE`, generates against the blueprint schema, validates (timestamp
   contiguity vs ffprobe duration, thin-detail detection, trigger-count), renders
   `blueprint.md`, and appends the cost entry.
3. **Agent QA (beyond the tool's deterministic checks).** Open `blueprint.md` and
   verify: every scene row has *real* camera-movement and transition detail (not
   generic filler like "standard cut"); end-card mechanics are exact (text, logos,
   SFX, animate-on); the transcript reads word-for-word; the 4–5 B-roll standards are
   programmatic ("when the script says X, cut to Y") — not vibes.
4. **Retry once if thin.** Re-run with `--retry-note` naming the weak sections, and/or
   `--fps 5` for fast-cut edits (default sampling is 1 fps and can miss
   micro-animations). **Max 2 attempts**, then escalate to the owner — same rule as
   asset QA.
5. **Handoff.** Report the blueprint path and how downstream consumes it:
   - **Script stage** (`generate_scripts.md`): `overview` + `transcript` are
     inspiration inputs; tag which reference inspired each variation.
   - **Edit stage** (`edit_video.md` / `core/edit_stage.md`): scene rows map to
     `edit/chunks.json` chunk boundaries; `broll_generation_template` standards seed
     the mandatory `broll_slots` plan; the Transitions & Animations column drives
     timeline animation choices; end-card mechanics drive the CTA/endscreen build.
   - **B-roll checklist** feeds the brainstorm against
     `assets/_shared/b-roll-bank/bank.md` (append shipped concepts to its registry).

## Outputs
- `assets/<app>/reference-analysis/<date>/<slug>/blueprint.md` — the recreation
  contract (human + edit-stage facing).
- `assets/<app>/reference-analysis/<date>/<slug>/blueprint.json` — source metadata,
  model, token usage/est cost, QA warnings, and the raw structured blueprint.
- `assets/<app>/reference-analysis/generation-log.json` — cost entry
  (`type: "video_analysis"`, rolled up by `tools/cost_report.py`).
- `.tmp/<app>/reference-analysis/<date>/<slug>/` — the disposable source copy.
  **Source clips NEVER go under `assets/`** (copyright + Shared-Drive sync).

## Edge cases & notes
- **Files API stuck `PROCESSING`** → the tool times out; re-encode with
  `ffmpeg -i in.mp4 -movflags +faststart out.mp4` and retry once.
- **Model not on the key** → the tool exits with the valid Pro-tier list; pass
  `--model <id>`. `auto` never picks embedding/tts/image/live/flash variants.
- **Video too long/large** → 15-min gate (`--force` to bypass), ~2 GB upload cap.
  Trim to the relevant span, or use `--media-resolution low`.
- **`MAX_TOKENS`** → the error names the fixes (lower `--fps`, low res, trim, raise
  `--max-output-tokens`).
- **Login-walled / geo-blocked URLs** → yt-dlp fails; ask the user for a local file.
- **IP note:** the blueprint recreates *structure and mechanics*. Never copy the
  competitor's brand assets, logos, or footage verbatim into our videos.
