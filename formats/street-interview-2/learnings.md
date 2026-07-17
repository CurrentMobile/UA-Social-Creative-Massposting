# Learnings — street-interview-2

Append-only. Promotion into recipes is the owner's act.

## 2026-07-10 — first run (laziest-way-to-earn)

- Higgsfield ultra plan caps at **8 concurrent jobs** per model family (`rate_limit_reached`,
  rc 3); the 9th+ submission fails after retries. Batch ≤8 and refill as slots free.
- `gpt_image_2` resolutions are `1k/2k/4k` — `1080p` is rejected (rc 4).
- QA rubric compares wardrobe to the persona base image: per-video wardrobe changes flag
  WARDROBE_DRIFT on every asset even when stated in `--context`. Treated as expected false
  positive; the real gate is identical wardrobe phrasing across all of the video's prompts.
- Extract-stage identity drift (Chloe img-4, Ashley grid-5) fixed both times by regenerating with
  the persona base passed as an extra reference + "EXACT match" phrasing (Format-1's img-8-nb2 fix
  generalizes).
- Kling hallucinated a lead-in line once in 7 sound-on clips ("Are you charging it?" before the
  scripted words, Clip 7) — transcribe every sound-on clip; trim via EDL range start.
- `hyperframes transcribe <file> --json` prints a summary; the actual word JSON lands at
  `<input-dir>/transcript.json` and is OVERWRITTEN per run — `mv` it per file.
- Curated meme SFX (turntable scratch, "ceeday huh", Win game rewards) beat literal SFX searches
  (gavel/siren/bass-drop all missed local + yt-dlp) and fit the meme grammar better anyway.
- ElevenLabs "Liam" at style 0.85 / stability 0.3 gives a convincing breathless chase read from
  punctuation alone (no v3 audio tags needed).
- **Whisper pads the last word's end time past the file's end** (Clip 7: word end 4.00s in a 3.04s
  clip). Trusting it in the EDL produced 0.93s of black frames. ALWAYS ffprobe every source and
  clamp each range's `end` to the real duration; blackdetect the render before delivering.

## 2026-07-11 — revision pass (owner feedback on the first cut)

- **ElevenLabs TTS for the interviewer is banned** — see [[interviewer-vo-no-elevenlabs]]. Replaced
  with: generate the line via `kling3_0` sound-on using an EXISTING validated persona's voice tag +
  face as an "audio vehicle" (video discarded, audio extracted with `ffmpeg -vn`), then mux that
  audio under the REAL interviewee reaction B-roll (same mux mechanics as before, just swap the
  audio source). Reused `student-jake`'s voice tag (Format-1's proven energetic male voice) as the
  vehicle even though this video's on-camera cast is different — the vehicle face is discarded, so
  identity mismatch doesn't matter, only the voice performance does.
- `kling3_0`'s documented `duration` default is 5 with no listed max — durations up to 8 (tested)
  were accepted without error; no need to split long interviewer lines across multiple generations.
- Whisper's `small.en` occasionally mishears a spoken app name badly (heard "Mode Earn App" as
  "Mode or an app"). Cross-check any suspicious transcript against `--model medium.en` before
  trusting it for logo/card sync — medium fixed it cleanly. Conversely, medium.en can glitch a
  single word's alignment far worse than small.en (one word spanned 2.5s of silence) — check BOTH
  and use whichever produces sane, monotonically-increasing word boundaries.
- For a chase-hook cold open, generate the interviewer's audio-vehicle clip with the SAME visual
  as the actual B-roll (e.g. the duo-chase start image) rather than a neutral plate, and bake
  breathless/panting performance direction directly into that one generation's prompt — simpler
  than layering a separate synthetic pant SFX, and reads more natural.
- **Continuity gotcha:** if line N's B-roll shows subjects already fully stopped/settled while the
  dialogue is still describing the action that just happened (e.g. "he's actually sprinting" said
  over a static reaction shot), regenerate that beat's clip with explicit residual
  motion/shake-decaying-to-a-stop in the prompt so the visual and the line's tense agree.
- Per-card GSAP pop-in offsets are hand-tuned to ONE specific VO take's word timings — any time the
  underlying interviewer audio is regenerated, recompute word offsets from a fresh transcript and
  edit the card's `fromTo`/`to` start times before re-rendering the webm; a small script that sums
  segment durations + looks up transcript words (see `edit/build_new_edl.py`) beats hand arithmetic.
- SFX search for generic "gavel"/"siren"/"bass drop" still misses (see prior entry); a bank of
  curated crowd/campus AMBIENCE also isn't in the local library — `resolve_sfx.py`'s yt-dlp
  fallback found a usable "Courtyard Ambience" track on a broader query ("campus courtyard ambience
  people talking"); loop/fade it locally with ffmpeg to cover the full runtime rather than relying
  on the mix schema to loop a short bed (it doesn't — `sfx` entries play once from `t`).
