# Workflow: Source Royalty-Free Background Music

Download royalty-free music into `assets/music/` and pick a track for an edit. Called by
`edit_video.md` step 6, or run standalone.

## Tool
`tools/fetch_music.py` — wraps `yt-dlp`. Source priority: YouTube Audio Library and
creator-cleared "No Copyright Music" channels. Provide either a **direct URL/playlist**
(most reliable) or a **search query**.

## Steps

1. **Decide the mood.** From the edit's tone: e.g. "upbeat corporate", "lofi calm",
   "cinematic tension", "energetic trap no copyright".

2. **Fetch** (run from project root with the venv python):
   ```
   .venv\Scripts\python.exe tools\fetch_music.py "lofi chill no copyright" --count 3 --tags lofi,calm
   ```
   - `--count N` for a search (fetches N results). A single URL ignores `--count`.
   - Files land in `assets/music/`; metadata appends to `assets/music/library.json`
     (title, duration, source URL, tags, `license_note`).

3. **Audit the license.** `library.json` carries a `license_note` reminder — the license is
   NOT auto-verified. Before any commercial publish, confirm the track is cleared
   (YouTube Audio Library / CC0 / explicitly royalty-free). Prefer direct URLs from sources
   you trust over blind search hits.

4. **Pick & preview.** Listen / check duration vs. the edit length. A track shorter than the
   video is fine — `mix_audio.py` loops it.

5. **Mix it in** (see `edit_video.md` step 6):
   ```
   .venv\Scripts\python.exe tools\mix_audio.py <rendered.mp4> -o <out.mp4> --music assets\music\<track>.mp3
   ```
   Music is auto-ducked under dialogue. Tune level with `--music-volume` (default 0.18).
   Use `--no-duck` only for music-only videos with no speech.

## STANDING RULE — music level (2026-06-16)
**Music sits at 20% of the A-roll/voice level, with NO ducking.** On the HyperFrames-render path
set `mix.json` `"music_volume": 0.20` (A-roll plays at 1.0). On the `mix_audio.py` path, do not
sidechain-duck — keep music at a constant ~0.20 of the dialogue. (Ducking is off by default now.)

## Notes
- Downloaded audio is gitignored (`assets/music/*` except `.gitkeep`) but `library.json`
  is tracked so the catalog is shareable.
- The official YouTube Audio Library catalog needs a logged-in browser session, so this
  tool works from URLs/queries rather than scraping that catalog directly.
