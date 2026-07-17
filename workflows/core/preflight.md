# Core: Preflight (Phase 0 — silent, hard stops only)

Run before the intake form. Fix or stop; never ask what a tool can answer.

1. **Environment:** `.venv\Scripts\python.exe tools\env_check.py --strict` — must exit
   clean. If ffmpeg/deps/keys are missing, print the exact remediation and STOP.
2. **Higgsfield session (video formats):** `higgsfield account status` — needs an
   authenticated account with credits. `Session expired` ⇒ tell the owner to run
   `higgsfield auth login` (interactive; Claude cannot) and STOP.
3. **Formats lock:** `.venv\Scripts\python.exe tools\check_formats_lock.py` — stop on
   unexpected modifications under `formats/` (someone edited a locked template).
4. **Registry:** read `formats/REGISTRY.md`. Only `production`/`beta`/`draft` formats
   are offerable (draft shows a "not yet validated" flag); `deprecated` is hidden.
5. **Prefills:** validate any command args (format slug in registry? persona exists in
   `assets/_shared/personas/`? app has `assets/<app>/manifest.md`?). Invalid prefill ⇒
   drop it and let the form ask.
6. **Shared drive (soft):** `Test-Path 'G:\Shared drives\Mode AI Creative Loop'` — if
   absent, warn that delivery sync + format example previews will be skipped; don't stop.
