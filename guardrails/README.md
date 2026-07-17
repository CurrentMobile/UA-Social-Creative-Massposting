# Guardrails Ledger

Every recurring generation error / AI hallucination becomes a **guardrail**: a short,
positively-phrased prompt rule injected into future generation prompts. This is the
error → guardrail → better-prompt loop of the self-improvement SOP, made durable.

## How it flows

1. **QA finds a defect** — `tools/qa_image.py` fails an asset with a defect code
   (codes are defined in `qa/rubrics.json`, 1:1 with guardrail categories).
2. **Defect becomes a candidate** —
   `tools/guardrails.py add --from-verdict <verdict.json> --model gpt_image_2`
   appends it as `status: candidate` (or bumps `hits` on an existing rule for the same
   model + defect + shot-type). **Nothing enters prompts un-reviewed.**
3. **Human promotes** — `guardrails.py report` lists candidates;
   `guardrails.py promote GR-###` makes it active.
4. **Agents inject** — before authoring prompts for a shot type, the asset workflow runs
   `guardrails.py inject --model <m> --shot-type <s>` and honors every rule printed.

## Files

- `index.json` — **the single machine truth.** All edits go through `tools/guardrails.py`.
- `<model>.md` — human-readable views regenerated from the index. **Never hand-edit.**

## Rules for rules (anti-bloat — the ledger must stay small to stay useful)

- **≤ 7 active rules per (model × shot-type)** — the tool enforces this on promote.
- **≤ 2 lines per rule**, positively phrased: say what SHOULD be in frame. A badly
  phrased negative rule ("no back of phone") can *cause* the defect in image models.
- **Monthly consolidation:** merge overlapping rules; retire rules with no hits in 60
  days (`report` flags them); and **fold universally-true rules into the prompt
  templates themselves** (`workflows/asset_prompts.md`) then retire them here — a rule
  that applies always belongs in the template, not the ledger. This is the pressure valve.
- **Watch for rule-induced regressions:** if a rule's `hits` keep RISING after it goes
  active, suspect the rule's phrasing itself.

## Lifecycle

`candidate` → `active` → `retired` (retired rules stay in the index for history).
