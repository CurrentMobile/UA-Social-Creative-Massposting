# Card: pause-freeze

**What:** the play/pause moment — the overlaid watched clip freezes abruptly with a
pause-UI flash (⏸ icon + slight dim + vignette), then the presenter reacts.
**Fires at:** every `pause` edit event (from the interview-turns anatomy's PAUSE
markers → `edit_events` in chunks.json).
**Build:** alpha-WebM card (pause icon + dim layer) + the overlaid clip's video track
freeze-frames at the event time (hold last frame). One tape-stop / record-scratch SFX
on the freeze; a soft "play" SFX when it resumes.
**EDL:** freeze the PiP overlay track at the event time + `overlays` entry for the
pause card + SFX in `mix.json`.
