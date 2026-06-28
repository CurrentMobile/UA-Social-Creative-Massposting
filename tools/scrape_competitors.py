"""Step 2 — Competitor Research. Find winning organic content (and competitor ads)
across TikTok, Instagram, and the Facebook Ad Library via Apify, then normalize and
rank them into a reviewable winners list.

Reads APIFY_API_KEY from root .env. One Apify run per platform (batched seeds, capped
by --results-per-query) to keep cost down. Nothing is spent under --dry-run.

Usage:
    # See exactly what would run, spend nothing:
    .venv\\Scripts\\python.exe tools/scrape_competitors.py --platform all --dry-run

    # Small live run (recommended first):
    .venv\\Scripts\\python.exe tools/scrape_competitors.py --platform tiktok \\
        --queries "rewards app" --results-per-query 10 --top 10

    # Full default run (Mode Earn seeds baked in):
    .venv\\Scripts\\python.exe tools/scrape_competitors.py --platform all --days 180

Outputs (under assets/<app>/competitor-research/<date>/):
    winners.json   normalized + ranked records (consumed by Step 3 breakdown_videos.py)
    winners.md     human review table (per platform), clickable URLs
Raw per-platform dumps go to .tmp/<app>/competitor-research/<date>/raw_<platform>.json
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus

import _research_lib as rl

ACTORS_OK = rl.ACTORS  # platform -> Apify actor id

# --- Mode Earn default seeds (rewards-app niche) ---------------------------- #
DEFAULT_KEYWORDS = ["earn money app", "rewards app", "make money on your phone", "passive income app"]
DEFAULT_HASHTAGS = ["makemoneyonline", "rewardsapp", "sidehustle", "appsthatpay", "passiveincome"]
DEFAULT_PROFILES = ["sweatcoin", "mistplay", "swagbucks"]          # known competitors
DEFAULT_MENTIONS = ["mode earn", "mode earn app", "modeearn"]      # the brand itself

ALL_PLATFORMS = ["tiktok", "instagram", "facebook-ads"]


def _split(values: list[str] | None) -> list[str]:
    """Flatten repeated --flag values and split each on commas."""
    out: list[str] = []
    for v in values or []:
        out.extend(p.strip() for p in v.split(",") if p.strip())
    return out


def _days_ago(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")


def _slug(s: str) -> str:
    return s.lower().replace("#", "").replace(" ", "")


# --- per-platform actor input builders -------------------------------------- #
def build_tiktok_input(keywords, hashtags, profiles, rpp, days) -> dict:
    inp: dict = {
        "resultsPerPage": rpp,
        "shouldDownloadVideos": False,
        "shouldDownloadCovers": False,
        "shouldDownloadSubtitles": False,
    }
    if keywords:
        inp["searchQueries"] = keywords
    if hashtags:
        inp["hashtags"] = [h.lstrip("#") for h in hashtags]
    if profiles:
        inp["profiles"] = [p.lstrip("@") for p in profiles]
    if days:
        inp["oldestPostDate"] = _days_ago(days)
    return inp


def build_instagram_input(keywords, hashtags, profiles, rpp, days) -> dict:
    # IG has no strong free-text search; drive it by hashtag + profile URLs.
    tags = list(dict.fromkeys([*(h.lstrip("#") for h in hashtags), *(_slug(k) for k in keywords)]))
    urls = [{"url": f"https://www.instagram.com/explore/tags/{t}/"} for t in tags if t]
    urls += [{"url": f"https://www.instagram.com/{p.lstrip('@')}/"} for p in profiles]
    inp: dict = {
        "directUrls": urls,
        "resultsType": "posts",
        "resultsLimit": rpp,
        "addParentData": False,
    }
    if days:
        inp["onlyPostsNewerThan"] = _days_ago(days)
    return inp


def build_facebook_ads_input(terms, rpp, country) -> dict:
    urls = []
    for t in terms:
        q = quote_plus(t)
        urls.append({
            "url": (
                "https://www.facebook.com/ads/library/?active_status=all&ad_type=all"
                f"&country={country}&q={q}&search_type=keyword_unordered&media_type=all"
            )
        })
    return {"urls": urls, "count": rpp, "activeStatus": "all", "scrapePageAds": False}


def build_input(platform, keywords, hashtags, profiles, rpp, days, country) -> dict:
    if platform == "tiktok":
        return build_tiktok_input(keywords, hashtags, profiles, rpp, days)
    if platform == "instagram":
        return build_instagram_input(keywords, hashtags, profiles, rpp, days)
    if platform == "facebook-ads":
        terms = list(dict.fromkeys([*keywords, *profiles]))
        return build_facebook_ads_input(terms, rpp, country)
    raise ValueError(platform)


# --- winners.md rendering --------------------------------------------------- #
def _fmt_int(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "—"
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def render_winners_md(app: str, date: str, rank_by: str, winners: list[dict]) -> str:
    lines = [
        f"# {app} — Competitor Research winners ({date})",
        "",
        f"Ranked by **{rank_by}** (Facebook ads by run-duration). Review these, then run Step 3 "
        f"(`tools/breakdown_videos.py`) on the strongest organic picks.",
        "",
    ]
    titles = {"tiktok": "TikTok", "instagram": "Instagram", "facebook-ads": "Facebook Ad Library (paid creative)"}
    for platform in ALL_PLATFORMS:
        recs = [w for w in winners if w["platform"] == platform]
        if not recs:
            continue
        lines.append(f"## {titles[platform]}  ({len(recs)})")
        lines.append("")
        if platform == "facebook-ads":
            lines.append("| # | Page | Active (days) | Hook / ad copy | Link |")
            lines.append("|--:|------|--------------:|----------------|------|")
            for w in recs:
                hook = (w.get("hook_text") or "").replace("|", "\\|")
                link = f"[ad]({w['url']})" if w.get("url") else "—"
                lines.append(
                    f"| {w['rank']} | {w.get('author') or '—'} | {w.get('ad_active_days') if w.get('ad_active_days') is not None else '—'} | {hook} | {link} |"
                )
        else:
            lines.append("| # | Author | Views | Likes | ER | Hook | Link |")
            lines.append("|--:|--------|------:|------:|---:|------|------|")
            for w in recs:
                hook = (w.get("hook_text") or "").replace("|", "\\|")
                er = w.get("engagement_rate")
                er_s = f"{er*100:.1f}%" if isinstance(er, (int, float)) else "—"
                link = f"[watch]({w['url']})" if w.get("url") else "—"
                lines.append(
                    f"| {w['rank']} | {w.get('author') or '—'} | {_fmt_int(w.get('views'))} | {_fmt_int(w.get('likes'))} | {er_s} | {hook} | {link} |"
                )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Step 2 — scrape + rank winning competitor content via Apify")
    ap.add_argument("--platform", default="all", help="tiktok | instagram | facebook-ads | all")
    ap.add_argument("--app", default="mode-earn")
    ap.add_argument("--queries", action="append", help="keyword search terms (repeatable / comma-sep)")
    ap.add_argument("--hashtags", action="append", help="hashtags without # (repeatable / comma-sep)")
    ap.add_argument("--profiles", action="append", help="competitor handles (repeatable / comma-sep)")
    ap.add_argument("--results-per-query", type=int, default=30, help="cap per search unit (default 30)")
    ap.add_argument("--min-views", type=int, default=0, help="drop organic posts under N views")
    ap.add_argument("--days", type=int, default=None, help="only posts newer than N days")
    ap.add_argument("--rank-by", default="blended", choices=["views", "engagement", "blended", "recency"])
    ap.add_argument("--top", type=int, default=25, help="winners kept per platform (default 25)")
    ap.add_argument("--country", default="US", help="Facebook Ad Library country (default US)")
    ap.add_argument("--timeout", type=int, default=300, help="seconds to wait per Apify run")
    ap.add_argument("--dry-run", action="store_true", help="print actor inputs + plan; spend nothing")
    args = ap.parse_args()

    platforms = ALL_PLATFORMS if args.platform == "all" else [args.platform]
    for p in platforms:
        if p not in ACTORS_OK:
            sys.exit(f"Unknown platform '{p}'. Choose from: {', '.join(ALL_PLATFORMS)} | all")

    keywords = _split(args.queries) or (DEFAULT_KEYWORDS + DEFAULT_MENTIONS)
    hashtags = _split(args.hashtags) or DEFAULT_HASHTAGS
    profiles = _split(args.profiles) or DEFAULT_PROFILES
    rpp = args.results_per_query
    date = rl.today_str()
    persistent, tmp = rl.research_dirs(args.app, date)

    print("=" * 64)
    print(f"STEP 2 — COMPETITOR RESEARCH  ({args.app}, {date})")
    print(f"platforms : {', '.join(platforms)}")
    print(f"keywords  : {keywords}")
    print(f"hashtags  : {hashtags}")
    print(f"profiles  : {profiles}")
    print(f"rpp={rpp} top={args.top}/platform rank_by={args.rank_by} days={args.days} min_views={args.min_views}")
    print("=" * 64)

    # Build inputs up front so --dry-run shows exactly what each run would receive.
    inputs = {
        p: build_input(p, keywords, hashtags, profiles, rpp, args.days, args.country)
        for p in platforms
    }

    if args.dry_run:
        import json
        for p in platforms:
            print(f"\n## {p}  ->  actor {ACTORS_OK[p]}")
            print(json.dumps(inputs[p], indent=2, ensure_ascii=False))
        est = rpp * sum(
            len(inputs[p].get("searchQueries", [])) + len(inputs[p].get("hashtags", []))
            + len(inputs[p].get("profiles", [])) + len(inputs[p].get("directUrls", []))
            + len(inputs[p].get("urls", []))
            for p in platforms
        )
        print(f"\n[dry-run] ~{est} results max across {len(platforms)} run(s). No credits spent.")
        print(f"[dry-run] would write -> {rl.rel_to_root(persistent / 'winners.json')}")
        return

    env = rl.load_env()
    token = env.get("APIFY_API_KEY", "")
    if not token:
        sys.exit("APIFY_API_KEY not found in .env")
    ok, detail = rl.apify_check_token(token)
    if not ok:
        sys.exit(f"Apify token check failed: {detail}")
    print(f"Apify token OK ({detail}). Masked: {rl.mask(token)}\n")

    all_records: list[dict] = []
    for p in platforms:
        actor = ACTORS_OK[p]
        label = f"{p}: " + ", ".join(keywords[:3]) + ("…" if len(keywords) > 3 else "")
        print(f"-> {p} via {actor}")
        try:
            items = rl.apify_run_actor(actor, inputs[p], token, timeout=args.timeout)
        except Exception as e:  # noqa: BLE001
            print(f"   !! {p} run failed: {str(e)[:240]}")
            continue
        rl.write_json(tmp / f"raw_{p}.json", items)
        recs = rl.normalize(p, items, query=label)
        print(f"   normalized {len(recs)} record(s).")
        all_records.extend(recs)

    if not all_records:
        print("\nNo records scraped. Check the --dry-run input against each actor's Apify README "
              "(field names drift between actor versions).")
        sys.exit(1)

    records = rl.dedupe(all_records)
    records = rl.filter_records(records, min_views=args.min_views, days=args.days)
    records = rl.rank_records(records, rank_by=args.rank_by)
    winners = [r for r in records if r.get("rank", 999) <= args.top]

    payload = {
        "app": args.app,
        "date": date,
        "generated_at": rl.now_iso(),
        "rank_by": args.rank_by,
        "platforms": platforms,
        "seeds": {"keywords": keywords, "hashtags": hashtags, "profiles": profiles},
        "counts": {"scraped": len(all_records), "deduped": len(records), "winners": len(winners)},
        "winners": winners,
    }
    winners_json = persistent / "winners.json"
    rl.write_json(winners_json, payload)
    (persistent / "winners.md").write_text(
        render_winners_md(args.app, date, args.rank_by, winners), encoding="utf-8"
    )

    print(f"\nScraped {len(all_records)} -> {len(records)} unique -> {len(winners)} winners (top {args.top}/platform).")
    print(f"Review: {rl.rel_to_root(persistent / 'winners.md')}")
    print(rl.rel_to_root(winners_json))  # last line = machine-readable path for callers


if __name__ == "__main__":
    main()
