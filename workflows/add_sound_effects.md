# Workflow: Add & Sync Sound Effects

Download sound effects into `assets/sfx/` and place them at exact timestamps in an edit.
Called by `edit_video.md` step 6, or run standalone.

## Tools
- `tools/fetch_sfx.py` — `yt-dlp` wrapper tuned for short clips (default `--max-duration 60`).
- `tools/mix_audio.py` — places each SFX at a timestamp via `--sfx "path@time[:gain]"`.

## Steps

1. **List the beats that need a sound.** From the cut, note timestamps (in OUTPUT time, i.e.
   seconds into the finished video) where an effect lands: a whoosh on a hard cut, a ding on a
   text pop, an impact on a logo reveal.

2. **Fetch effects** (project root, venv python):
   ```
   .venv\Scripts\python.exe tools\fetch_sfx.py "whoosh transition sound effect" --count 3 --tags whoosh,transition
   .venv\Scripts\python.exe tools\fetch_sfx.py "ui pop click sound" --count 2 --tags ui,pop
   ```
   - Files land in `assets/sfx/`; metadata appends to `assets/sfx/library.json`.
   - Raise `--max-duration` if searches get filtered out; pass a direct URL for a known clip.

3. **Find precise timestamps.** Use `timeline_view.py` on the rendered video around each beat
   to read the exact second, or read it off the EDL / master.srt. SFX time is in output time.

4. **Place them** with one `--sfx` per effect (repeatable). Optional per-clip gain after a colon:
   ```
   .venv\Scripts\python.exe tools\mix_audio.py <rendered.mp4> -o <out.mp4> ^
       --music assets\music\<track>.mp3 ^
       --sfx "assets\sfx\whoosh.mp3@2.50" ^
       --sfx "assets\sfx\ding.mp3@7.00:0.8" ^
       --sfx "assets\sfx\impact.mp3@11.25"
   ```
   `mix_audio.py` delays each effect to its timestamp, mixes with music + dialogue, and
   re-normalizes the whole bed to −14 LUFS.

5. **Verify sync.** Re-run `timeline_view.py` on the mixed output at each SFX time and check the
   waveform spike lands on the visual beat. Nudge the `@time` value and re-mix if off.

## STANDING RULES (2026-06-16)
- **Curated-first:** `resolve_sfx.py` searches `assets/sfx/curated/` recursively (incl. the user's
  primary `Sound effects and documentation/` library) and prefers it; yt-dlp only when nothing
  matches locally. The ding = `Ting.MP3`, cha-ching = `Cash register.MP3`.
- **Synced number pop-ups:** build the pop-up as an alpha-WebM card via HyperFrames
  (`edit/animations/<name>/` → `render.webm`), place it as an `overlays` card in the EDL at the
  SFX timestamp, add a `caption_blackouts` window so captions don't clash, and put the SFX in
  `mix.json` at the same `t`. (Mode Earn examples: "+1,200 POINTS" on "the points add up" with a
  ding; "+$70" on the gift-cards line with a cha-ching.)

## Tips
- Sync to the visual, not the spoken word: a whoosh should peak on the cut frame.
- Keep SFX subtle — gain 0.6–0.9 usually sits right under dialogue + music.
- One `mix_audio.py` call handles music AND all SFX together, so levels balance in a single
  normalization pass. Don't chain multiple mix passes.
