# Learnings — ugc-single (append-only)

The ONLY file under `formats/ugc-single/` agents may write. Append dated entries when
a run teaches something; never edit the recipes/SOP directly. Entries that contradict
a LOCKED rule are logged here but NOT applied. Promotion into the recipes is a human
act (bumps `version` in format.md and clears the promoted entries).

Format: `- YYYY-MM-DD: <what was learned> → <how to apply it>`

- 2026-07-08: (seed) Phone shots prompted as bare "holding a phone" produce
  back-to-viewer defects → phone visibility grammar is now a LOCKED rule; QA Gate B
  catches regressions (verified on backinthe-80s-era img-5).
- 2026-07-08: (seed) GPT Image 2 grid extractions at busy multi-surface areas produce
  "pinned between two tables" spatial hallucinations → grounding clause + prefer
  single-surface cells (guardrail GR-004).
