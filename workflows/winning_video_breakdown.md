# Workflow: Winning Video Breakdown (Step 3)

Take the top winners from Step 2, **watch the actual videos**, and break each one down into structured
creative anatomy — hook, beat structure, on-screen text, CTA, pacing, why it works, and how to adapt it
on-brand. This is **Step 3** of the mass-posting workflow. It consumes `winners.json` from Step 2 and
produces the inspiration artifact Step 5 (Script Generation) will read.

## Objective
For the strongest organic winners (and a few competitor ads), produce
`assets/<app>/competitor-research/<date>/breakdowns.json` — one structured breakdown per video — then
**synthesize** `breakdown.md`: the recurring winning patterns and the **whitespace angles** the app can
own. The breakdown schema mirrors the sacred beats (`HOOK / PROBLEM / SOLUTION / HOW IT WORKS / RESULT /
CTA`) so findings drop straight into Step 5.

## Inputs
- `assets/<app>/competitor-research/<date>/winners.json` (from Step 2). The tool reads its `winners`.
- `GEMINI_API_KEY` in root `.env` (Gemini multimodal — watches the clips). Already present.
- `assets/<app>/brand/creative-direction.md` — the brand context for "transferable angle" is also baked
  into the tool's prompt (`BRAND_CONTEXT`), keep it in sync if the brief changes materially.

## Tools
- `tools/breakdown_videos.py` — downloads the top organic videos (yt-dlp), uploads each to Gemini, and
  returns a structured breakdown per video; Facebook ads are analyzed **text-only** from ad copy.
  **`--dry-run` spends nothing.**
  ```
  # 1) list what would be analyzed (no spend):
  .venv\Scripts\python.exe tools/breakdown_videos.py --app mode-earn --dry-run
  # 2) small first (3 videos) to confirm the schema + quality:
  .venv\Scripts\python.exe tools/breakdown_videos.py --app mode-earn --top 3
  # 3) full breakdown:
  .venv\Scripts\python.exe tools/breakdown_videos.py --app mode-earn --top 12
  ```
  Key flags: `--top N` (organic videos, default 12), `--ads N` (FB ads text-only, default 5),
  `--no-ads`, `--model <gemini-id>` (default `gemini-2.5-flash`), `--date`, `--winners <path>`.

## Steps
0. **Preflight.** Confirm `winners.json` exists for the date. Run `breakdown_videos.py --dry-run` and
   read back the target list + model. Confirm Gemini shows **WORKS** (`test_api_keys.py`).
1. **Confirm top-N + budget with the user.** Gemini bills per video/token. Start with `--top 3`,
   inspect `breakdowns.json` quality, then scale to `--top 12`.
2. **Download** the chosen videos → `.tmp/<app>/competitor-research/<date>/videos/` (disposable).
3. **Break down** each clip with Gemini (structured JSON enforced by `responseSchema`): hook + hook type,
   opening visual, beat-by-beat map, on-screen text, CTA, pacing, visual style, audio, why it works, and
   a Mode-Earn-specific transferable angle. FB ads get a text-only breakdown from their copy.
4. **Agent synthesizes `breakdown.md`** from `breakdowns.json` — this part is *your* reasoning, not the
   tool's:
   - **Recurring winning hooks** (group by hook_type; quote the strongest).
   - **Common CTA patterns** and pacing/edit norms across winners.
   - **Whitespace / gap angles** the app can own — for Mode Earn, lean on the methods rivals don't cover
     (music / charging / reading news; `creative-direction.md` "Competitive edge").
   - A shortlist of **3–6 concrete angle ideas** for Step 5, each tagged with the competitor video that
     inspired it (rank + url) and the on-brand adaptation.

## Outputs
- `assets/<app>/competitor-research/<date>/breakdowns.json` — one structured breakdown per analyzed item.
- `assets/<app>/competitor-research/<date>/breakdown.md` — agent-synthesized patterns + whitespace +
  angle shortlist. **This is the artifact Step 5 reads** (fills the "FUTURE competitor references" hook
  in `generate_scripts.md`).
- `.tmp/<app>/competitor-research/<date>/videos/` — downloaded clips (disposable).

**Next:** `breakdowns.json` is *triage across many* winners. For a recreation-grade, scene-by-scene
blueprint of ONE winner (camera mechanics, transitions/animations, B-roll trigger rules, tagged
transcript), run **Step 3b** — `workflows/analyze_video.md` (`/analyze-video <rank>`).

## Edge cases & notes
- **Cost gate.** Dry-run first, start at `--top 3`, scale only after the output looks right.
- **Gemini model id / availability.** Default `gemini-2.5-flash`. The tool lists available models on the
  key and errors with the valid list if the chosen id isn't present — pass a working id via `--model`.
- **Video must finish processing.** Gemini's Files API marks a video `PROCESSING` then `ACTIVE`; the tool
  polls before analyzing. Long/large clips may time out (`--timeout`) — they're skipped with a note.
- **yt-dlp download failures** (geo-block, format, login wall) skip that video and continue the batch;
  re-run later or drop the item. TikTok/IG short clips are usually fine.
- **Facebook ads are text-only** here (often image creative, no playable video) — visual fields stay thin
  by design; the value is the messaging/hook angle.
- **Keep `BRAND_CONTEXT` in the tool aligned** with `creative-direction.md` so transferable angles stay
  on-brand (reward-not-pay, Android-only, no get-rich-quick).
