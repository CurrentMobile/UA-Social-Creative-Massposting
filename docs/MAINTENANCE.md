# Maintenance

Periodic upkeep for the pipeline. None of this is needed for a normal video run.

## Git repo size (free GitHub) — DEFERRED history rewrite

**Current strategy (keep it):** selective tracking. The repo holds the knowledge layer
(workflows, tools, formats, personas, brand, manifests, curated SFX catalogs, posters);
heavy regenerable media (`ai-videos/`, `ai-images/`, `edit/`, `outputs/`, `vendor/`,
`.venv/`) is gitignored and lives on the Google Shared Drive, restored by
`tools/sync_assets.py pull`. **Do NOT adopt Git LFS** — its free tier (1 GB storage +
1 GB/month bandwidth) would be exhausted by the first teammate's clone of the tracked
persona/brand media.

**The pack is ~280 MB**, mostly history blobs of media that was later gitignored. This
is under GitHub's limits and fine for now. When you want to slim it (a quiet moment,
before onboarding many teammates):

1. Announce a freeze; make sure everyone has pushed.
2. Install `git-filter-repo`.
3. Strip the since-removed media paths from history, e.g.:
   ```
   git filter-repo --invert-paths \
     --path-glob 'assets/*/*/ai-videos/*' \
     --path-glob 'assets/*/*/ai-images/*' \
     --path-glob 'assets/*/*/edit/*' \
     --path-glob 'outputs/*'
   ```
4. Force-push the rewritten history.
5. **Every teammate deletes their clone and re-clones** (history hashes changed).

This is disruptive (a coordinated re-clone) but a one-time cost; hence deferred, not
automated.

**Escape hatch if TRACKED media ever nears 1 GB:** move the persona/CTA/brand media
into a GitHub Release asset (assets up to 2 GB each, don't count toward repo size) and
have `tools/bootstrap.py` download it. Designed, not built — add a bootstrap step when
needed.

## Guardrails ledger consolidation (monthly)

Run `tools/guardrails.py report`. Then:
- Promote reviewed candidates (`promote GR-###`) or leave them.
- Retire rules with no hits in 60 days (`retire GR-###`) — they stay in the index for
  history.
- Fold any rule that is UNIVERSALLY true into the prompt template itself
  (`workflows/asset_prompts.md` / the relevant `formats/<slug>/prompts/`), then retire
  the ledger entry. This is the pressure valve that keeps the ledger small.
- Watch for rules whose `hits` keep RISING after going active — suspect the phrasing.

## Format template versioning (promote-learnings)

Format templates are LOCKED; runs append to `formats/<slug>/learnings.md`. To fold
accepted learnings into a format's recipes (a HUMAN act):
1. Read `formats/<slug>/learnings.md`; decide what to promote.
2. Edit the recipe/prompt/SOP with the improvement.
3. Bump `version` in `formats/<slug>/format.md` (patch = prompt tweak, minor = recipe
   step, major = anatomy/form change).
4. Clear the promoted entries from `learnings.md` (leave a note pointing to the version).
5. Tag the repo `templates-vYYYY.MM.DD` when `formats/` or `guardrails/` change
   materially, so a video's `template_tag` in its generation-log is reproducible.

## Regenerate the formats gallery

After adding/changing a format:
`.venv\Scripts\python.exe tools\build_formats_gallery.py` → `docs/formats-gallery.html`.

## Deferred / noted optimizations (not built)

- `tools/higgsfield_batch.py` — bounded-concurrency clip submission (concurrency 2,
  jittered, per-job retries, `account status` re-check between jobs with pause-and-
  instruct). Halves wall-clock on 12-clip videos. Build after QA gates are exercised.
- Hash-keyed transcription/analysis cache in `_media_lib.py` (`.tmp/cache/`) to stop
  ElevenLabs/Gemini re-billing across edit iterations.
- Per-seat Higgsfield accounts as the team grows (one shared account will hit session/
  credit contention) — a pricing decision, not code.
