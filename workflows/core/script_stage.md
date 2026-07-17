# Core: Script Stage (format-aware)

Generalizes `workflows/generate_scripts.md` — read that file for the drafting
mechanics (novelty scan, hooks/body/CTAs structure, iteration, verbatim saving); this
file adds the format parameterization.

## Format plug-ins

- **Anatomy** comes from the format's `anatomy:` (e.g. six-beat sections, interview
  turns with `SPEAKER:` lines + PAUSE markers, ranked `RANK N:` items, or no-VO
  overlay copy). Draft the script IN that anatomy's shape — the sample in the format's
  `sop.md` §2 is the reference.
- **No-VO formats** (lofi-text, static-ad): the "script" is the on-screen overlay copy
  / static copy variants. It still goes through drafting → iteration → approval → the
  script library, exactly like VO scripts.
- **Multi-speaker formats:** draft each speaker's lines tagged (`INTERVIEWER:` /
  `PERSON1:`); hooks and CTAs belong to the speaker the format's SOP assigns.

## Rules (unchanged from generate_scripts.md)

1. **Novelty scan first** — read `assets/<app>/script-library/index.md` + `approved/`,
   **filtered by this format's tag**; never repeat a hook/angle within a format.
2. Draft N variations per the intake form; iterate in chat until the user approves.
   NOTHING is saved or generated before approval.
3. On approval, save verbatim:
   `save_approved_script.py <file> --format <slug>` (registers the format tag in the
   library index), then scaffold the video folder(s) and write per-variation scripts.
4. Chunk with the format's anatomy:
   `chunk_script.py scripts\source.md --anatomy <format's anatomy yaml> --out
   edit\chunks.json --vo-script scripts\vo-script.md`
   (no `--anatomy` for ugc formats = the classic default).
