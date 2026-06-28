# Workflow: Script Generation (Step 5)

Write fresh, on-brand UGC scripts for an app, get them approved, and bank the approved ones so we
never repeat ourselves. This is **Step 5** of the mass-posting workflow. It consumes the brief from
Step 1 and feeds Step 6 (AI Asset Generation).

## Objective
For one chosen persona, draft one or more **angles**. Each angle is a **shared body** plus a *menu* of
**hooks** (each with its own 0–3s sticker overlay) and a *menu* of **CTAs**. The user iterates on the
wording, then selects which hooks + CTAs to ship. Selected hooks and CTAs **pair index-wise** into
final video **variations** that all share the angle's body. Only approved variations are saved
**verbatim** into the app's script library.

## Model (read this carefully)
- **Angle / script** = one shared `body` (PROBLEM → SOLUTION → HOW IT WORKS → RESULT) + a hook menu + a CTA menu.
- **Hook** = the opening line + its own sticker overlay (first ~3s on screen).
- **CTA** = the closing line (no sticker).
- **Variation** (a final video) = `HOOK_i + BODY + CTA_i` using hook *i*'s sticker. The HOOK and CTA
  are the swappable ends; the body is constant.
- **Pairing is index-wise:** selected hook 1 + CTA 1 = V1, hook 2 + CTA 2 = V2, … If the user selects
  fewer CTAs than hooks, reuse the last selected CTA for the remaining hooks (confirm if ambiguous).

## Inputs
- `assets/<app>/brand/creative-direction.md` — voice, language rules, triggers, personas. **Read first.**
- The chosen **persona** (confirmed with the user) and its avatar in `assets/_shared/personas/<slug>/`.
- `assets/<app>/script-library/index.md` + `approved/*.md` — what's already been used (novelty check).
- Sample scripts in the brief folder — **for tone/style only, never to copy**.
- **FUTURE (after Steps 2–4):** competitor winning-video references. When available, read them here as
  an extra inspiration input and note which competitor angle inspired each variation. Until then this
  input is empty — do not block on it.

## Runtime gates (ask every run)
1. **Confirm the persona.** Ask which persona this batch targets, then select the matching presenter
   avatar slug from the creative-direction persona table. If the persona has no avatar yet, flag that
   one must be created in Step 6 (don't block script writing).
2. **Ask how many angles** (distinct bodies) to draft. Each angle gets a hook menu + a CTA menu
   (default 3 hooks + 3 CTAs) that the user mixes into variations.

## Hard rules
- **Don't copycat.** Use samples to absorb tone, rhythm, and structure — never reproduce their lines.
- **Novelty.** Before writing, scan `script-library/index.md` + `approved/*.md`. Don't repeat a prior
  hook angle or body for the same persona; deliberately go somewhere new.
- **Brand language.** *Reward* not *pay*; *gift cards/real rewards* not *cash/money*; Android only;
  no get-rich-quick. Standard stats: 10M+ downloads, 4.5★, 3M+ reviews.
- **Section labels are sacred.** Body uses `HOOK / PROBLEM / SOLUTION / HOW IT WORKS / RESULT / CTA`
  verbatim — `tools/chunk_script.py` depends on them downstream.
- **Length:** ~110–160 words total (≈30–60s). Conversational fragments, persona-true voice.
- **Approval gates everything.** Only scripts the user approves are saved and proceed to video.

## Output structure (per angle)
```
## Angle N — <Angle name>
Persona: <persona> (<avatar-slug>) | Angle: <one line>

### Hooks (each has its own sticker)
- Hook A (spoken): "<line>"   Sticker (0–3s): "<overlay>"
- Hook B (spoken): "<line>"   Sticker (0–3s): "<overlay>"
- Hook C (spoken): "<line>"   Sticker (0–3s): "<overlay>"

### Body (shared by every variation of this angle)
PROBLEM
"<line(s)>"
SOLUTION
"<line(s)>"
HOW IT WORKS
"<line(s)>"
RESULT
"<line(s)>"

### CTAs (paired with hooks index-wise)
- CTA 1 (spoken): "<line>"
- CTA 2 (spoken): "<line>"
- CTA 3 (spoken): "<line>"
```
Note the body holds only PROBLEM→RESULT. The chosen hook becomes the final `HOOK` and the chosen CTA
the final `CTA` when a variation is assembled — so every shipped variation still has all six sacred
section labels in order.

## Steps
1. Read the brief + the script library (novelty check). Confirm persona; ask how many angles.
2. Draft each angle (shared body + hook menu w/ stickers + CTA menu) in the structure above.
   Present **all** of them in chat.
3. **Iterate — nothing is saved yet.** The user points out edits to any hook, body, or CTA and
   selects which hooks + CTAs to ship per angle. Revise and re-present until they're happy.
4. **Approval gate.** Once the user approves, assemble each selected hook+CTA pairing into a final
   variation: `HOOK_i + BODY + CTA_i`, carrying hook *i*'s sticker.
5. **Save each approved variation verbatim** (below), then **hand off to Step 6** (below).

## Saving approved variations
Save **one file per angle**, enumerating its shipped variations (shared body, one block per
hook+CTA pairing). Then register it:
- File: `assets/<app>/script-library/approved/<YYYY-MM-DD>_<persona-slug>_<angle-slug>.md`
  Front-matter: `id, app, persona, avatar, angle, date, variations, status, video_folder`
  (`chosen_hook`/`sticker` hold V1's for the index row). Body: the shared PROBLEM→RESULT, then a
  `### V1`, `### V2`, … block each listing its hook + sticker + CTA verbatim.
- Register + index: `.venv\Scripts\python.exe tools/save_approved_script.py <file>`.

## Handing off to Step 6
One **video project per angle** (its variations share body A-roll; only hook + CTA clips differ —
Step 6 generates the body once and swaps the ends):
1. `.venv\Scripts\python.exe tools/scaffold.py video <app> "<Angle Title>"`.
2. Write one complete source per variation into the video folder, e.g.
   `scripts/source-v1.md`, `scripts/source-v2.md` — each = `HOOK` (that variation's hook) +
   shared body + `CTA` (that variation's CTA), all six labels in order, ready for `chunk_script.py`.
3. Set `persona:` in the video manifest; record each variation's sticker text (→ first-3s overlay in
   Step 7) and its hook/CTA in the manifest/edit notes.
4. Update the approved file's `video_folder`/`status` so the library links scripts to the video.

## Outputs
- Approved variations saved verbatim (one file per angle) in `assets/<app>/script-library/approved/`
  + a current `index.md`.
- One scaffolded video project per angle, with a complete `scripts/source-v<n>.md` per variation
  ready for Step 6.

## Edge cases
- **Iterate before approving.** Default expectation: present → user edits hooks/body/CTAs and picks
  pairings → revise → only then approve. Never save on the first pass.
- **Approve with edits.** Apply the edits, then save the edited version verbatim (that's the record).
- **No approvals.** Save nothing; offer to iterate with new angles.
- **Hook/CTA count mismatch.** Pair index-wise; reuse the last selected CTA if fewer CTAs than hooks.
- **Persona has no avatar.** Save the script; note the avatar gap so Step 6 creates it first.
