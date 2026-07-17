# Core: Asset Stage (recipe executor)

Generalizes `workflows/generate_assets.md` — read that file for the mechanics
(Higgsfield conventions, QA gates A-D, guardrail loop, B-roll quota, cost discipline,
edge cases). This file adds the format parameterization.

## How to execute a format's asset recipe

1. Read `formats/<slug>/recipes/assets.md`. Its YAML `assets:` inventory declares
   each asset id with `kind`, `model`, `per` (cardinality), `refs`, `prompt` template
   pointer, and `qa` gate.
2. **Expand cardinality against `edit/chunks.json`:**
   - `per: run` → one asset for the video
   - `per: persona_env` → one per (persona × environment) — multi-persona/multi-
     location formats expand here
   - `per: chunk` → one per chunk (filtered by `speaker` when the chunk carries one —
     each speaker's clips seed from THAT character's stills)
   - `per: section` → one per script beat (B-roll quota: honor `broll_slots`)
3. For each expanded asset: inject guardrails (`guardrails.py inject --model <m>
   --shot-type <qa.shot_type>`) → author the prompt from the format's template +
   `formats/_shared/prompts/*` rules → generate via `higgsfield_gen.py` → run the
   declared QA gate → on fail follow the gate's regen policy (Gate B: max 2, then
   stop for the owner).
4. **Models:** the format's `models:` block. Image gen is ALWAYS `gpt_image_2`
   (standing owner rule) unless the user explicitly overrides.
5. **Cost:** print the format's `cost_estimate` and `--dry-run` the clip batch before
   spending (Autonomy On pre-authorizes after script approval).
6. Special asset kinds:
   - `kind: import` (e.g. play-pause overlay clip, reaction source): the user supplies
     the file OR the SOP defines how to generate a stand-in; never scrape copyrighted
     content without the owner's explicit say-so.
   - `kind: composite` (clone formats): multi-instance still built with GPT Image 2
     from the persona reference before animating.
7. Finish: Gate-D batch QA + `check_assets.py --update-manifest` + append shipped
   B-roll concepts to the bank registry.
