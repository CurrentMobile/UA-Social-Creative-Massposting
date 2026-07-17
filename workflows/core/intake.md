# Core: Intake (Phase 1 — ONE form round)

The single form that replaces multi-round questioning. Deterministic tool; the agent
just launches it and reads the JSON.

```
.venv\Scripts\python.exe tools\intake_form.py --family video ^
    [--prefill format=ugc-single --prefill persona=retiree-female-poc --prefill app=mode-earn] ^
    [--timeout 900]
```

The tool scans the repo live (registry formats + posters, app manifests, persona
library with thumbnails), serves a one-page form on localhost, opens the browser,
blocks until submit, writes `.tmp/intake/intake-<ts>.json`, prints its path as the
LAST stdout line, and shuts down.

**Read the JSON** — schema:
```json
{"family": "video", "app": "mode-earn", "new_app_brief": null,
 "format": "ugc-single", "sub_format": null, "personas": ["retiree-female-poc"],
 "duration": 45, "variations": 2, "script_source": "claude", "script_text": null,
 "autonomy": "on", "reference_source": null, "reference_mode": null,
 "brief": "", "notes": "", "submitted_at": "..."}
```

Rules:
- Record the intake JSON path in the video manifest once scaffolded.
- `script_source: "provide"` with empty `script_text` ⇒ ask for the paste in chat
  (long text is the one thing that may follow the form).
- `app: "__new__"` ⇒ `new_app_brief` is required by the form; run
  `workflows/onboard_app.md` before anything else.
- `reference_source` non-null (a URL or local file path) ⇒ run
  `workflows/analyze_video.md` on it BEFORE the script stage (its dry-run cost gate
  still applies); record the resulting `blueprint.md` path in the video manifest.
  `reference_mode` says how downstream uses it: `recreate` = the blueprint's scene
  table is the structural contract for the edit stage; `inspiration` = style/pacing
  cues only.
- **Fallback (no browser / headless / form timeout):** ask the same fields via at most
  TWO AskUserQuestion rounds built from the same registry/format metadata — Round 1:
  format + app; Round 2: the format's `form_fields` (max 4). Same JSON contract.
