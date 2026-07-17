"""Aggregate generation-log.json across videos into a credit/cost rollup.

Per-video `generation-log.json` records every generated asset (model, label, created)
and — since the QA layer — every QA check (type:"qa"). This tool rolls those up so the
owner can see spend per video / app / week, QA overhead, and retry waste. Feeds the
private pitch-audit skill's cost-per-video math.

Credit costs are ESTIMATES (Higgsfield pricing varies by model/mode); override via
--credits or edit CREDIT_ESTIMATES. Gemini QA is priced in tiny $ (per-image), not
credits.

Usage:
    .venv\\Scripts\\python.exe tools\\cost_report.py                     # all videos
    .venv\\Scripts\\python.exe tools\\cost_report.py --app mode-earn
    .venv\\Scripts\\python.exe tools\\cost_report.py --since 2026-06-01
    .venv\\Scripts\\python.exe tools\\cost_report.py --json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS = PROJECT_ROOT / "assets"

# Rough per-generation credit estimates (override with --credits model=NN).
CREDIT_ESTIMATES = {
    "gpt_image_2": 2.0,
    "nano_banana_flash": 2.0,
    "kling3_0": 75.0,        # a pro clip is the big cost; tune to your plan
    "kling3_0_turbo": 7.5,   # verified in project memory
    "seedance_2_0": 40.0,
}
GEMINI_QA_USD = 0.002       # ~per image on gemini-2.5-flash
GEMINI_ANALYSIS_USD = 0.30  # fallback per reference-video analysis (analyze_video.py logs real est_usd)


def logs(app: str | None) -> list[Path]:
    base = (ASSETS / app) if app else ASSETS
    return sorted(base.glob("**/generation-log.json")) if base.exists() else []


def video_key(log: Path) -> tuple[str, str]:
    # assets/<app>/<video>/generation-log.json  (some logs live in edit/)
    parts = log.relative_to(ASSETS).parts
    app = parts[0]
    video = parts[1] if len(parts) > 2 else "(app-level)"
    return app, video


def main() -> int:
    ap = argparse.ArgumentParser(description="Credit/cost rollup from generation logs")
    ap.add_argument("--app", help="limit to one app")
    ap.add_argument("--since", help="ISO date (YYYY-MM-DD); count entries created on/after")
    ap.add_argument("--credits", action="append", default=[], metavar="model=NN",
                    help="override a model's credit estimate (repeatable)")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    credits = dict(CREDIT_ESTIMATES)
    for ov in args.credits:
        if "=" in ov:
            k, v = ov.split("=", 1)
            credits[k] = float(v)

    per_video: dict[tuple, dict] = defaultdict(lambda: {
        "gens": 0, "qa_checks": 0, "qa_fails": 0, "by_model": defaultdict(int), "credits": 0.0,
        "analyses": 0, "analysis_usd": 0.0})
    for log in logs(args.app):
        try:
            entries = json.loads(log.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(entries, list):
            continue
        key = video_key(log)
        v = per_video[key]
        for e in entries:
            created = str(e.get("created") or e.get("checked_at") or "")
            if args.since and created and created[:10] < args.since:
                continue
            if e.get("type") == "qa":
                v["qa_checks"] += 1
                if e.get("verdict") == "fail":
                    v["qa_fails"] += 1
                continue
            if e.get("type") == "video_analysis":
                v["analyses"] += 1
                v["analysis_usd"] += float(e.get("est_usd") or GEMINI_ANALYSIS_USD)
                continue
            model = e.get("model", "unknown")
            v["gens"] += 1
            v["by_model"][model] += 1
            v["credits"] += credits.get(model, 0.0)

    # rollups
    apps: dict[str, dict] = defaultdict(lambda: {"videos": 0, "gens": 0, "credits": 0.0,
                                                 "qa_checks": 0, "qa_fails": 0,
                                                 "analyses": 0, "analysis_usd": 0.0})
    total = {"videos": 0, "gens": 0, "credits": 0.0, "qa_checks": 0, "qa_fails": 0,
             "analyses": 0, "analysis_usd": 0.0}
    rows = []
    for (app, video), v in sorted(per_video.items()):
        qa_usd = v["qa_checks"] * GEMINI_QA_USD
        rows.append({"app": app, "video": video, "gens": v["gens"],
                     "credits": round(v["credits"], 1), "qa_checks": v["qa_checks"],
                     "qa_fails": v["qa_fails"], "qa_usd": round(qa_usd, 3),
                     "analyses": v["analyses"], "analysis_usd": round(v["analysis_usd"], 3),
                     "by_model": dict(v["by_model"])})
        a = apps[app]
        a["videos"] += 1; a["gens"] += v["gens"]; a["credits"] += v["credits"]
        a["qa_checks"] += v["qa_checks"]; a["qa_fails"] += v["qa_fails"]
        a["analyses"] += v["analyses"]; a["analysis_usd"] += v["analysis_usd"]
        total["videos"] += 1; total["gens"] += v["gens"]; total["credits"] += v["credits"]
        total["qa_checks"] += v["qa_checks"]; total["qa_fails"] += v["qa_fails"]
        total["analyses"] += v["analyses"]; total["analysis_usd"] += v["analysis_usd"]

    if args.json:
        print(json.dumps({"videos": rows,
              "by_app": {k: {**v, "credits": round(v["credits"], 1),
                             "analysis_usd": round(v["analysis_usd"], 3)} for k, v in apps.items()},
              "total": {**total, "credits": round(total["credits"], 1),
                        "analysis_usd": round(total["analysis_usd"], 3)}},
              indent=2))
        return 0

    print(f"\nCOST REPORT{f'  (since {args.since})' if args.since else ''}"
          f"{f'  app={args.app}' if args.app else ''}")
    print(f"{'video':<40} {'gens':>5} {'~credits':>9} {'QA':>4} {'QAfail':>7} {'anlys':>6}")
    print("-" * 77)
    for r in rows:
        print(f"{(r['app']+'/'+r['video'])[:40]:<40} {r['gens']:>5} {r['credits']:>9.1f} "
              f"{r['qa_checks']:>4} {r['qa_fails']:>7} {r['analyses']:>6}")
    print("-" * 77)
    for app, a in sorted(apps.items()):
        print(f"{app+' (total)':<40} {a['gens']:>5} {a['credits']:>9.1f} "
              f"{a['qa_checks']:>4} {a['qa_fails']:>7} {a['analyses']:>6}  ({a['videos']} videos)")
    avg = (total["credits"] / total["videos"]) if total["videos"] else 0
    print(f"\nTOTAL: {total['videos']} videos, {total['gens']} generations, "
          f"~{total['credits']:.0f} credits, {total['qa_checks']} QA checks "
          f"(~${total['qa_checks']*GEMINI_QA_USD:.2f}), {total['analyses']} video analyses "
          f"(~${total['analysis_usd']:.2f}). Avg ~{avg:.0f} credits/video.")
    print("(credit numbers are estimates — override with --credits model=NN)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
