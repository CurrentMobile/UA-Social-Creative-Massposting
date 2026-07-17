# Workflow: Onboard a New App (inline, one approval)

Triggered when the intake form's App = "New app (not onboarded)". Turns the user's
product brief into a working per-app tree without leaving the run.

## Inputs

`new_app_brief` from the intake form (required — the form enforces it): what the app
does, target users, store link, brand do's/don'ts, anything else pasted.

## Steps

1. **Slug + scaffold:** derive a kebab-case slug; run
   `.venv\Scripts\python.exe tools\scaffold.py app <slug>` (creates
   `assets/<slug>/manifest.md` from `assets/_templates/`).
2. **Draft `brand/creative-direction.md`** from the brief: about-the-app paragraph,
   voice/tone, standing language rules, compliance notes, target personas, standard
   stats/claims ONLY if the brief states them. **Never invent brand facts** — anything
   the brief doesn't cover gets an explicit `TODO(owner)` marker, not a guess.
3. **Fill the app manifest:** display name, platforms, brand_dir, cta_dir (note CTA
   clip as missing if not provided), video index (empty).
4. **ONE approval:** show the drafted creative-direction + manifest to the user;
   apply their edits; confirmed ⇒ continue the run.
5. **Missing-asset warnings, not blockers:** no CTA clip ⇒ the edit stage will flag
   delivery as CTA-pending; no app UI screenshots ⇒ phone-shot compositing and the
   app-ui-demo card are degraded — tell the user what to drop into
   `assets/<slug>/brand/` and continue with what exists.

If there is no brief at all: STOP with the checklist (app description, audience,
store link, brand rules, UI screenshots, CTA clip) — never proceed on invented facts.
