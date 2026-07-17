# Workflow: Competitor Research (Step 2)

Find **winning organic content** (and competitor **ads**) in the app's niche across TikTok, Instagram,
and the Facebook Ad Library, then rank it into a short, reviewable list. This is **Step 2** of the
mass-posting workflow. Its output feeds **Step 3 (Winning Video Breakdown)** and ultimately grounds
**Step 5 (Script Generation)** in what's actually performing.

## Objective
Produce one dated, reviewable winners list per app — `assets/<app>/competitor-research/<date>/winners.{json,md}`
— containing the top-performing posts/ads for the niche, normalized to one schema and ranked, so a human
can scan them and the strongest organic picks can be handed to Step 3.

## Inputs
- `assets/<app>/brand/creative-direction.md` — for the niche, named competitors, and language rules.
  For Mode Earn: competitors **Sweatcoin / Mistplay / Swagbucks**; niche = "earn rewards for everyday
  phone activity" (`creative-direction.md` "Competitive edge").
- **Search seeds** (confirmed with the user before a live run): keywords, hashtags, competitor handles.
  Sensible Mode Earn defaults are baked into the tool — override per run as needed.
- `APIFY_API_KEY` in root `.env` (already present; validated by `tools/test_api_keys.py`).

## Tools
- `tools/test_api_keys.py` — confirm the Apify key is live first.
  `.venv\Scripts\python.exe tools/test_api_keys.py`
- `tools/scrape_competitors.py` — the scraper. One Apify run per platform (batched seeds, capped by
  `--results-per-query`). **`--dry-run` spends nothing** and prints the exact actor input JSON.
  ```
  # 1) see exactly what would run (no spend):
  .venv\Scripts\python.exe tools/scrape_competitors.py --platform all --dry-run --days 180
  # 2) small live run first (recommended):
  .venv\Scripts\python.exe tools/scrape_competitors.py --platform tiktok --queries "rewards app" --results-per-query 10 --top 10
  # 3) full default run:
  .venv\Scripts\python.exe tools/scrape_competitors.py --platform all --days 180
  ```
  Key flags: `--platform tiktok|instagram|facebook-ads|all`, `--queries`/`--hashtags`/`--profiles`
  (repeatable, comma-ok), `--results-per-query N` (default 30), `--min-views N`, `--days N`,
  `--rank-by views|engagement|blended|recency` (default `blended`), `--top N` (per platform, default 25),
  `--country` (FB Ad Library, default US).

## Steps
0. **Preflight.** Read the app brand brief for competitors + niche. Run `test_api_keys.py` and confirm
   Apify shows **WORKS**. Then run `scrape_competitors.py --dry-run` and read back the actor inputs.
1. **Assemble seeds from the brief.** Keywords/hashtags for the niche, the named competitor handles, and
   the brand's own name (to see what's already working for it). The tool's defaults already encode the
   Mode Earn set; adjust if the brief names new competitors or angles.
2. **Confirm scope + budget with the user.** Apify bills per result — show the dry-run estimate and the
   seed list, and agree on `--platform`, `--results-per-query`, and `--days` before any live run.
   **Start small** (one platform, low `--results-per-query`) to sanity-check the data, then scale.
3. **Run the scrape** for the agreed platforms. Raw per-platform dumps land in
   `.tmp/<app>/competitor-research/<date>/raw_<platform>.json`.
4. **Normalize + rank** (the tool does this): every record maps to one schema (views, likes, comments,
   shares, saves, engagement_rate, hook_text, hashtags, url, …); ranked `blended` by default. Facebook
   ads have no engagement data, so they're ranked by **run-duration** (`ad_active_days`) and flagged.
5. **Write winners.** `winners.json` (machine-readable, for Step 3) + `winners.md` (per-platform review
   tables with clickable links).
6. **Present the top picks** to the user from `winners.md` and confirm which to break down. Hand the
   `winners.json` to **Step 3** (`workflows/winning_video_breakdown.md`). A winner **approved for
   recreation** additionally goes to **Step 3b** (`workflows/analyze_video.md`, `/analyze-video <rank>`)
   for a recreation-grade blueprint.

## Outputs
- `assets/<app>/competitor-research/<date>/winners.json` — normalized + ranked winners (Step 3 input).
- `assets/<app>/competitor-research/<date>/winners.md` — human review tables, per platform.
- `.tmp/<app>/competitor-research/<date>/raw_<platform>.json` — raw Apify dumps (disposable).

## Edge cases & notes
- **Cost gate (project rule).** Anything that spends credits is dry-run-first and confirmed with the
  owner. Default caps are conservative (30/query); scale only after a small run looks right.
- **Actor input fields drift between actor versions.** The `--dry-run` JSON is the checkpoint. If a live
  run returns **0 items**, open the actor's Apify README and confirm field names:
  - TikTok `clockworks/tiktok-scraper` (`searchQueries`/`hashtags`/`profiles`/`resultsPerPage`)
  - Instagram `apify/instagram-scraper` (`directUrls`/`resultsType`/`resultsLimit`)
  - Facebook Ad Library `apify/facebook-ads-scraper` (`urls`/`count`) — Ad Library search URL form.
- **Facebook Ad Library = paid creative, not organic, and has no like/view counts.** Use it to see what
  ad *angles* competitors run; it's ranked by how long the ad has been live, never blended with organic ER.
- **Instagram has weak free-text search** — the tool drives IG by hashtag + profile URLs (keywords are
  slugified into tag URLs). Expect partial coverage; lean on hashtags + competitor profiles.
- **Rate limits / partial results.** These scrapers proxy around login-gating but can return fewer items
  than requested; `--days` + `--min-views` keep the set tight and relevant.
- **Never paste secrets** into files under `assets/` (it syncs to the Shared Drive). Keys stay in `.env`.
- **Downstream wiring (live):** `generate_scripts.md`'s Inputs section reads
  `assets/<app>/competitor-research/<date>/breakdown.md` (Step 3) and
  `assets/<app>/reference-analysis/**/blueprint.md` (Step 3b) as inspiration when present.
