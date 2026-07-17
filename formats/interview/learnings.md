# Learnings — interview (append-only)

The ONLY file under `formats/interview/` agents may write. Append dated entries when a
run teaches something; never edit the recipes/SOP directly. Entries contradicting a
LOCKED rule are logged but NOT applied. Promotion into recipes is a human act.

Format: `- YYYY-MM-DD: <what was learned> → <how to apply it>`

- 2026-07-08: (seed) `experimental` — the hardest format. v1 is POV-interviewer
  (interviewer never on camera) to avoid a second consistent face. Per-interviewee drift
  across turns is the main risk; if a 2nd interviewee won't hold, cut to one. On-camera
  interviewer stays experimental until multi-character consistency is reliable.
- 2026-07-08: (seed) needs `assets/_shared/props/handheld-mic.png` — create it before
  the first run (see `formats/_shared/prompts/props.md`).
- 2026-07-09: created `assets/_shared/props/handheld-mic.png` (gpt_image_2, clean prop reference) for the first interview run — props.md is LOCKED, so its planned table row awaits the owner promote-learnings pass.
- 2026-07-09: Higgsfield gpt_image_2 img2img pathway can fail server-side (status "failed", no result_url) for ALL reference-image jobs while text-only jobs succeed — looks like a model-side outage, not prompt/filter. Detect by A/B: trivial no-ref prompt vs trivial ref prompt. Remedy: documented fallback nano_banana_flash with the persona base passed as an extra identity reference (without it Nano Banana drifts the face — QA caught IDENTITY_DRIFT), visually confirm each output.
- 2026-07-09 (OWNER RULE): for interview-format videos do NOT composite app UI onto a phone held by interviewer/interviewee. The held phone shows only a bright glowing screen (still screen-to-viewer, never the back panel). All app UI arrives at EDIT time as pop-up graphic cards — UI screenshots / screen recordings / app logo / review cards — popping over the footage while the interviewee blurs out behind the pop-up. Also: the interviewee must never hold the mic or its cable (the unseen interviewer holds it).
- 2026-07-09: first real interview output shipped (MEA_V1_askYourPhoneForARaise). Worked: VO-muxed interviewer clips (TTS over muted B-roll, stretch/tile to VO length, blur baked for popup windows) slot cleanly into the ugc edit pipeline as normal ranges. Kling can hallucinate EXTRA unscripted dialogue in sound-on clips — always read the transcript and trim via range start. check_assets.py reports popup-covered b-roll slots as "missing" (ugc-shaped heuristic) — expected for this format. render.py --build-subtitles truncates master.srt; build with tools/build_srt.py and render without the flag.
