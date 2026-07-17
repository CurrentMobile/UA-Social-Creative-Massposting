# Core: Deliver

Same for every format (statics deliver PNGs instead of MP4s).

1. **Naming:** `outputs/<APP-CODE>/<videoTitleCamel>/<APP-CODE>_V<n>_<videoTitleCamel>_<dim>.mp4`
   (statics: `_<aspect>.png` per declared aspect). mode-earn → MEA.
2. **CTA:** video formats append/overlay the per-app CTA per the format's edit recipe
   (`append_cta.py` / EDL `endscreen`). Statics carry the CTA text in the layout.
3. **Sync:** robocopy `outputs\` → `G:\Shared drives\Mode AI Creative Loop\Videos`
   (exit 0-7 = success; use `tools/sync_assets.py push` once built).
4. **Format examples seeding:** the FIRST production-quality output of a format also
   copies to `G:\…\format-examples\<slug>\` — this powers the intake form's "see
   example" links. Check if the folder is empty; if so, copy.
5. **Manifest:** status → review/posted, output paths, `format: <slug>@<version>`,
   intake JSON reference; append a session entry to `edit/project.md`; validate with
   `check_manifest.py`.
6. **Registry promotion:** a format's first validated real output ⇒ propose promoting
   its REGISTRY.md row `draft → beta` (owner confirms).
7. **Learnings:** anything this run taught → append to `formats/<slug>/learnings.md`
   (the one writable file under formats/).
