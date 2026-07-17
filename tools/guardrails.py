"""Guardrails ledger — turn generation errors into reusable prompt rules.

Every recurring hallucination/defect becomes a short, positively-phrased prompt rule
that gets INJECTED into future generation prompts. QA failures (tools/qa_image.py)
feed candidates in automatically; a human promotes them to active. This is the
error -> guardrail -> better-prompt loop from the self-improvement SOP.

Store: guardrails/index.json is the single machine truth. The per-model markdown
files (guardrails/<model>.md) are HUMAN VIEWS regenerated from the index on every
change — never hand-edit them; edit via this tool.

Lifecycle: candidate -> active -> retired.
  - Only ACTIVE rules inject. Candidates wait for review (`report` lists them).
  - Anti-bloat: <=7 active rules per (model x shot-type); `inject --budget` caps
    output tokens; rules that stop hitting go stale (report flags 60d+).
  - A rule that applies ALWAYS belongs in the prompt template (asset_prompts.md),
    not the ledger — fold it in and retire the rule (the pressure valve).

Usage:
    guardrails.py inject --model gpt_image_2 --shot-type phone-shot [--budget 600]
    guardrails.py add --from-verdict .tmp/qa/img-5.verdict.json --model gpt_image_2
    guardrails.py promote GR-003   |   guardrails.py retire GR-002
    guardrails.py report
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GUARD_DIR = PROJECT_ROOT / "guardrails"
INDEX = GUARD_DIR / "index.json"
MAX_ACTIVE_PER_BUCKET = 7


def today() -> str:
    return time.strftime("%Y-%m-%d")


def load_index() -> dict:
    if INDEX.exists():
        return json.loads(INDEX.read_text(encoding="utf-8"))
    return {"next_id": 1, "rules": []}


def save_index(idx: dict) -> None:
    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding="utf-8")
    render_markdown(idx)


def shot_match(rule_shots: list[str], shot_type: str) -> bool:
    return any(fnmatch.fnmatch(shot_type, pat) for pat in rule_shots)


def render_markdown(idx: dict) -> None:
    """Regenerate guardrails/<model>.md human views from the index."""
    by_model: dict[str, list[dict]] = {}
    for r in idx["rules"]:
        by_model.setdefault(r["model"], []).append(r)
    for model, rules in by_model.items():
        lines = [f"# Guardrails — {model}", "",
                 "> GENERATED from index.json by tools/guardrails.py — do not hand-edit.",
                 "> Only `active` rules inject into prompts. Review candidates with "
                 "`guardrails.py report`.", ""]
        for status in ("active", "candidate", "retired"):
            group = [r for r in rules if r["status"] == status]
            if not group:
                continue
            lines.append(f"## {status} ({len(group)})")
            lines.append("")
            for r in sorted(group, key=lambda r: -r.get("hits", 0)):
                shots = ", ".join(r["shot_types"])
                lines.append(f"### {r['id']} · {shots} · {r['defect']} · {status} · "
                             f"hits:{r.get('hits', 0)} · added:{r['added']}")
                if r.get("description"):
                    lines.append(f"- **Defect:** {r['description']}")
                if r.get("failed_fragment"):
                    lines.append(f"- **Failed fragment:** \"{r['failed_fragment']}\"")
                lines.append(f"- **Rule (inject):** {r['rule']}")
                lines.append("")
        (GUARD_DIR / f"{model}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_inject(args) -> int:
    idx = load_index()
    rules = [r for r in idx["rules"]
             if r["status"] == "active" and r["model"] == args.model
             and shot_match(r["shot_types"], args.shot_type)]
    rules.sort(key=lambda r: -r.get("hits", 0))
    if not rules:
        print(f"(no active guardrails for {args.model} x {args.shot_type})")
        return 0
    budget_chars = args.budget * 4  # ~4 chars/token
    out, used = [], 0
    for r in rules:
        line = f"- [{r['id']}] {r['rule']}"
        if used + len(line) > budget_chars:
            print(f"(budget reached — {len(rules) - len(out)} lower-priority rule(s) omitted)")
            break
        out.append(line)
        used += len(line)
    print(f"GUARDRAILS for {args.model} x {args.shot_type} — honor every rule when authoring the prompt:")
    print("\n".join(out))
    return 0


def cmd_add(args) -> int:
    idx = load_index()
    verdict = json.loads(Path(args.from_verdict).read_text(encoding="utf-8"))
    shot_type = verdict.get("shot_type", args.shot_type or "extract")
    candidates = verdict.get("guardrail_candidates") or []
    # also derive bare candidates from fail defects that proposed no rule
    proposed = {c["defect"] for c in candidates}
    for d in verdict.get("defects", []):
        if d.get("severity") == "fail" and d["code"] not in proposed:
            candidates.append({"shot_type": shot_type, "defect": d["code"],
                               "rule": verdict.get("regenerate_hint") or d.get("description", ""),
                               "description": d.get("description", "")})
    if not candidates:
        print("verdict has no guardrail candidates (pass or warn-only) — nothing added.")
        return 0
    added, bumped = 0, 0
    for c in candidates:
        key = (args.model, c["defect"])
        existing = next((r for r in idx["rules"]
                         if (r["model"], r["defect"]) == key
                         and shot_match(r["shot_types"], c.get("shot_type", shot_type))), None)
        if existing:
            existing["hits"] = existing.get("hits", 0) + 1
            existing["last_hit"] = today()
            bumped += 1
            print(f"  bumped {existing['id']} ({existing['defect']}) -> hits:{existing['hits']}")
        else:
            rid = f"GR-{idx['next_id']:03d}"
            idx["next_id"] += 1
            idx["rules"].append({
                "id": rid, "model": args.model,
                "shot_types": [c.get("shot_type", shot_type)],
                "defect": c["defect"], "status": "candidate",
                "hits": 1, "added": today(), "last_hit": today(),
                "rule": (c.get("rule") or "").strip(),
                "failed_fragment": args.failed_fragment or "",
                "description": c.get("description", ""),
                "source_asset": verdict.get("asset", ""),
            })
            added += 1
            print(f"  added {rid} ({c['defect']}) as candidate")
    save_index(idx)
    print(f"done: {added} candidate(s) added, {bumped} hit(s) bumped -> guardrails/index.json")
    return 0


def _set_status(rule_id: str, status: str) -> int:
    idx = load_index()
    rule = next((r for r in idx["rules"] if r["id"] == rule_id), None)
    if not rule:
        sys.exit(f"no rule {rule_id}")
    if status == "active":
        bucket = [r for r in idx["rules"] if r["status"] == "active" and r["model"] == rule["model"]
                  and set(r["shot_types"]) & set(rule["shot_types"])]
        if len(bucket) >= MAX_ACTIVE_PER_BUCKET:
            sys.exit(f"cap reached: {len(bucket)} active rules for {rule['model']} x "
                     f"{rule['shot_types']} — retire or consolidate one first "
                     f"(or fold a universal rule into asset_prompts.md).")
    rule["status"] = status
    save_index(idx)
    print(f"{rule_id} -> {status}")
    return 0


def cmd_report(args) -> int:
    idx = load_index()
    cands = [r for r in idx["rules"] if r["status"] == "candidate"]
    actives = [r for r in idx["rules"] if r["status"] == "active"]
    stale_cut = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    stale = [r for r in actives if (r.get("last_hit") or r["added"]) < stale_cut]
    print(f"guardrails: {len(actives)} active, {len(cands)} candidate(s) awaiting review, "
          f"{len(stale)} stale active(s) (no hits 60d+)")
    for r in cands:
        print(f"  [candidate] {r['id']} {r['model']} x {r['shot_types']} {r['defect']} "
              f"hits:{r.get('hits', 0)} — {r['rule'][:80]}")
    for r in stale:
        print(f"  [stale]     {r['id']} {r['model']} x {r['shot_types']} {r['defect']} "
              f"last_hit:{r.get('last_hit', '?')} — consider retiring or folding into the template")
    if not cands and not stale:
        print("  nothing awaiting action.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Guardrails ledger (error -> prompt-rule loop)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("inject", help="print active rules for a model x shot-type")
    p.add_argument("--model", required=True)
    p.add_argument("--shot-type", dest="shot_type", required=True)
    p.add_argument("--budget", type=int, default=600, help="max tokens of rules to emit (default 600)")
    p.set_defaults(fn=cmd_inject)

    p = sub.add_parser("add", help="add candidates from a qa_image.py verdict")
    p.add_argument("--from-verdict", required=True)
    p.add_argument("--model", required=True, help="the GENERATION model that produced the asset")
    p.add_argument("--shot-type", dest="shot_type", help="override if verdict lacks shot_type")
    p.add_argument("--failed-fragment", dest="failed_fragment",
                   help="the prompt fragment that produced the defect (for the ledger)")
    p.set_defaults(fn=cmd_add)

    p = sub.add_parser("promote", help="candidate -> active")
    p.add_argument("rule_id")
    p.set_defaults(fn=lambda a: _set_status(a.rule_id, "active"))

    p = sub.add_parser("retire", help="-> retired (kept for history)")
    p.add_argument("rule_id")
    p.set_defaults(fn=lambda a: _set_status(a.rule_id, "retired"))

    p = sub.add_parser("report", help="candidates awaiting review + stale actives")
    p.set_defaults(fn=cmd_report)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
