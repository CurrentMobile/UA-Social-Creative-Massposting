"""Shared helpers for competitor research (Steps 2-3 of the mass-posting workflow).

Used by scrape_competitors.py (Step 2) and breakdown_videos.py (Step 3). Not a CLI.

Provides:
  - .env loading (manual parse, matches tools/test_api_keys.py — no python-dotenv)
  - Apify REST transport: start an actor run, poll to completion, fetch dataset items
    (no apify-client package needed; uses `requests`, already in the venv)
  - Per-platform normalization (TikTok / Instagram / Facebook Ad Library) to ONE schema
  - Ranking (views / engagement / blended / recency), computed per platform
  - Video download (yt-dlp for TikTok/IG, direct stream for Facebook ad media)
  - Small path / JSON / date helpers

No secrets ever land on disk here — keys stay in root .env.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# Reuse the venv-aware yt-dlp resolver from the audio helper (tools/ is on sys.path).
from _media_lib import find_ytdlp, rel_to_root  # noqa: F401  (rel_to_root re-exported)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APIFY_BASE = "https://api.apify.com/v2"

# Apify actor ids per platform (URL path uses '~' instead of '/').
ACTORS = {
    "tiktok": "clockworks/tiktok-scraper",
    "instagram": "apify/instagram-scraper",
    "facebook-ads": "apify/facebook-ads-scraper",
}

# Terminal Apify run statuses.
_TERMINAL = {"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT", "TIMING-OUT"}

VIDEO_EXTS = {".mp4", ".mov", ".webm", ".mkv", ".m4v"}

# Engagement rate from a tiny view count is statistical noise (a 150-view post can
# show 25% ER). For the blended score we only fully trust ER once a post clears this
# reach floor, so low-reach/high-ratio posts don't outrank genuinely viral ones.
ER_CONFIDENCE_VIEWS = 5000


# --------------------------------------------------------------------------- #
# env / small helpers
# --------------------------------------------------------------------------- #
def load_env() -> dict[str, str]:
    """Parse root .env into a dict (same pattern as tools/test_api_keys.py)."""
    d: dict[str, str] = {}
    p = PROJECT_ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def mask(v: str) -> str:
    if not v:
        return "(empty)"
    return (v[:4] + "…" + v[-4:]) if len(v) > 10 else "***"


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path, default=None):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return default
    return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def research_dirs(app: str, date: str | None = None) -> tuple[Path, Path]:
    """Return (persistent_dir, tmp_dir) for an app's research run.

    persistent: assets/<app>/competitor-research/<date>/   (synced, reviewable)
    tmp:        .tmp/<app>/competitor-research/<date>/      (disposable: raw dumps, videos)
    """
    date = date or today_str()
    persistent = PROJECT_ROOT / "assets" / app / "competitor-research" / date
    tmp = PROJECT_ROOT / ".tmp" / app / "competitor-research" / date
    return persistent, tmp


# --------------------------------------------------------------------------- #
# Apify transport
# --------------------------------------------------------------------------- #
def _actor_path(actor_id: str) -> str:
    return actor_id.replace("/", "~")


def apify_run_actor(
    actor_id: str,
    run_input: dict,
    token: str,
    timeout: int = 300,
    poll_interval: int = 5,
    log=print,
) -> list[dict]:
    """Start an Apify actor run, poll until terminal, return dataset items.

    Raises RuntimeError on a failed start or a non-SUCCEEDED terminal status, and
    TimeoutError if the run does not finish within `timeout` seconds.
    """
    actor = _actor_path(actor_id)
    start = requests.post(
        f"{APIFY_BASE}/acts/{actor}/runs",
        params={"token": token},
        json=run_input,
        timeout=60,
    )
    if start.status_code not in (200, 201):
        raise RuntimeError(
            f"Apify run start failed for {actor_id}: HTTP {start.status_code} — {start.text[:300]}"
        )
    data = start.json().get("data", {})
    run_id = data.get("id")
    dataset_id = data.get("defaultDatasetId")
    if not run_id:
        raise RuntimeError(f"Apify run start returned no run id for {actor_id}: {start.text[:300]}")

    log(f"    apify run {run_id} started ({actor_id}); polling…")
    deadline = time.monotonic() + timeout
    status = data.get("status", "READY")
    while status not in _TERMINAL:
        if time.monotonic() > deadline:
            raise TimeoutError(
                f"Apify run {run_id} ({actor_id}) did not finish within {timeout}s (last status {status})."
            )
        time.sleep(poll_interval)
        r = requests.get(f"{APIFY_BASE}/actor-runs/{run_id}", params={"token": token}, timeout=60)
        if r.status_code != 200:
            log(f"    poll HTTP {r.status_code}; retrying…")
            continue
        rd = r.json().get("data", {})
        status = rd.get("status", status)
        dataset_id = rd.get("defaultDatasetId", dataset_id)

    if status != "SUCCEEDED":
        raise RuntimeError(f"Apify run {run_id} ({actor_id}) ended {status}.")

    items = requests.get(
        f"{APIFY_BASE}/datasets/{dataset_id}/items",
        params={"token": token, "clean": "true", "format": "json"},
        timeout=120,
    )
    items.raise_for_status()
    out = items.json()
    log(f"    apify run {run_id} SUCCEEDED — {len(out)} item(s).")
    return out


def apify_check_token(token: str) -> tuple[bool, str]:
    """Validate the Apify token (read-only). Returns (ok, detail)."""
    try:
        r = requests.get(f"{APIFY_BASE}/users/me", params={"token": token}, timeout=20)
        if r.status_code == 200:
            d = r.json().get("data", {})
            plan = d.get("plan", {})
            plan_id = plan.get("id") if isinstance(plan, dict) else plan
            return True, f"user={d.get('username')} plan={plan_id}"
        return False, f"HTTP {r.status_code} — {r.text[:160]}"
    except Exception as e:  # noqa: BLE001
        return False, str(e)[:160]


# --------------------------------------------------------------------------- #
# normalization — every platform -> ONE record schema
# --------------------------------------------------------------------------- #
def _dig(d: dict, *keys, default=None):
    """First non-None value among several top-level keys."""
    for k in keys:
        v = d.get(k)
        if v is not None:
            return v
    return default


def _hashtags(raw) -> list[str]:
    out: list[str] = []
    if isinstance(raw, list):
        for h in raw:
            if isinstance(h, dict):
                name = h.get("name") or h.get("title")
                if name:
                    out.append(str(name))
            elif isinstance(h, str):
                out.append(h.lstrip("#"))
    return out


def _hook_text(caption: str | None, words: int = 12) -> str:
    if not caption:
        return ""
    flat = " ".join(str(caption).split())
    parts = flat.split(" ")
    return " ".join(parts[:words]) + ("…" if len(parts) > words else "")


def _record(**kw) -> dict:
    """Build a normalized record with every field present (defaults filled)."""
    base = {
        "platform": None, "url": None, "author": None, "caption": None, "hook_text": None,
        "views": None, "likes": None, "comments": None, "shares": None, "saves": None,
        "engagement_rate": None, "posted_date": None, "duration_s": None,
        "hashtags": [], "music": None, "thumbnail_url": None, "video_url": None,
        "is_ad": False, "ad_active_days": None, "query": None, "scraped_at": now_iso(),
    }
    base.update(kw)
    return base


def normalize_tiktok(item: dict, query: str) -> dict:
    caption = _dig(item, "text", "desc", default="")
    author = item.get("authorMeta", {}) if isinstance(item.get("authorMeta"), dict) else {}
    video = item.get("videoMeta", {}) if isinstance(item.get("videoMeta"), dict) else {}
    music = item.get("musicMeta", {}) if isinstance(item.get("musicMeta"), dict) else {}
    return _record(
        platform="tiktok",
        url=_dig(item, "webVideoUrl", "videoUrl"),
        author=author.get("name") or author.get("nickName"),
        caption=caption,
        hook_text=_hook_text(caption),
        views=_dig(item, "playCount", default=0),
        likes=_dig(item, "diggCount", default=0),
        comments=_dig(item, "commentCount", default=0),
        shares=_dig(item, "shareCount", default=0),
        saves=_dig(item, "collectCount", default=0),
        posted_date=(_dig(item, "createTimeISO") or "")[:10] or None,
        duration_s=video.get("duration"),
        hashtags=_hashtags(item.get("hashtags")),
        music=music.get("musicName"),
        thumbnail_url=video.get("coverUrl") or video.get("originalCoverUrl"),
        video_url=_dig(item, "webVideoUrl"),  # yt-dlp resolves the playable stream
        query=query,
    )


def normalize_instagram(item: dict, query: str) -> dict:
    caption = _dig(item, "caption", default="")
    return _record(
        platform="instagram",
        url=_dig(item, "url", "inputUrl"),
        author=_dig(item, "ownerUsername", "ownerFullName"),
        caption=caption,
        hook_text=_hook_text(caption),
        views=_dig(item, "videoViewCount", "videoPlayCount", default=0),
        likes=_dig(item, "likesCount", default=0),
        comments=_dig(item, "commentsCount", default=0),
        shares=None,   # IG does not expose shares
        saves=None,    # IG does not expose saves
        posted_date=(_dig(item, "timestamp") or "")[:10] or None,
        duration_s=_dig(item, "videoDuration"),
        hashtags=_hashtags(item.get("hashtags")),
        music=None,
        thumbnail_url=_dig(item, "displayUrl"),
        video_url=_dig(item, "videoUrl", "url"),
        query=query,
    )


def normalize_facebook_ad(item: dict, query: str) -> dict:
    """Facebook Ad Library has no engagement metrics. Capture creative text, page,
    media, CTA, and how long the ad has been running (a performance proxy)."""
    snap = item.get("snapshot", {}) if isinstance(item.get("snapshot"), dict) else {}
    body = snap.get("body", {})
    body_text = body.get("text") if isinstance(body, dict) else (body if isinstance(body, str) else None)
    if not body_text:
        bodies = snap.get("bodies") or item.get("bodies")
        if isinstance(bodies, list) and bodies:
            first = bodies[0]
            body_text = first.get("text") if isinstance(first, dict) else str(first)

    # media: first video HD/SD url, else first image
    video_url = None
    vids = snap.get("videos") or []
    if isinstance(vids, list) and vids and isinstance(vids[0], dict):
        video_url = _dig(vids[0], "videoHdUrl", "videoSdUrl")
    thumb = None
    if isinstance(vids, list) and vids and isinstance(vids[0], dict):
        thumb = vids[0].get("videoPreviewImageUrl")
    if not thumb:
        imgs = snap.get("images") or []
        if isinstance(imgs, list) and imgs and isinstance(imgs[0], dict):
            thumb = _dig(imgs[0], "originalImageUrl", "resizedImageUrl")

    start = _dig(item, "startDate", "adDeliveryStartTime", "startDateFormatted")
    start_date = str(start)[:10] if start else None
    active_days = None
    if isinstance(start, (int, float)):  # epoch seconds
        try:
            d0 = datetime.fromtimestamp(float(start), tz=timezone.utc)
            active_days = (datetime.now(timezone.utc) - d0).days
            start_date = d0.strftime("%Y-%m-%d")
        except Exception:  # noqa: BLE001
            pass
    elif start_date:
        try:
            d0 = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            active_days = (datetime.now(timezone.utc) - d0).days
        except Exception:  # noqa: BLE001
            pass

    return _record(
        platform="facebook-ads",
        url=_dig(item, "url", "adLibraryUrl") or snap.get("linkUrl"),
        author=_dig(item, "pageName") or snap.get("pageName"),
        caption=body_text,
        hook_text=_hook_text(body_text),
        posted_date=start_date,
        hashtags=[],
        music=None,
        thumbnail_url=thumb,
        video_url=video_url,
        is_ad=True,
        ad_active_days=active_days,
        query=query,
    )


NORMALIZERS = {
    "tiktok": normalize_tiktok,
    "instagram": normalize_instagram,
    "facebook-ads": normalize_facebook_ad,
}


def normalize(platform: str, items: list[dict], query: str) -> list[dict]:
    fn = NORMALIZERS[platform]
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        try:
            out.append(fn(it, query))
        except Exception:  # noqa: BLE001 — never let one bad item kill the batch
            continue
    return out


# --------------------------------------------------------------------------- #
# metrics + ranking
# --------------------------------------------------------------------------- #
def _num(v) -> float:
    try:
        return float(v) if v is not None else 0.0
    except (TypeError, ValueError):
        return 0.0


def compute_engagement(rec: dict) -> float | None:
    views = _num(rec.get("views"))
    if views <= 0:
        return None
    eng = _num(rec.get("likes")) + _num(rec.get("comments")) + _num(rec.get("shares")) + _num(rec.get("saves"))
    return round(eng / views, 5)


def dedupe(records: list[dict]) -> list[dict]:
    """Drop duplicate posts (same url) that surface under multiple queries."""
    seen: set[str] = set()
    out = []
    for r in records:
        key = (r.get("url") or "") + "|" + (r.get("hook_text") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def rank_records(records: list[dict], rank_by: str = "blended") -> list[dict]:
    """Fill engagement_rate + a `score`, then rank WITHIN each platform (1-based `rank`).

    Facebook ads have no engagement data, so they are always ranked by recency
    (ad_active_days, longer-running = higher) regardless of `rank_by`.
    """
    for r in records:
        r["engagement_rate"] = compute_engagement(r)

    by_platform: dict[str, list[dict]] = {}
    for r in records:
        by_platform.setdefault(r["platform"], []).append(r)

    ranked: list[dict] = []
    for platform, recs in by_platform.items():
        mode = "recency" if platform == "facebook-ads" else rank_by
        max_views = max((_num(r.get("views")) for r in recs), default=0.0) or 1.0

        def score(r: dict) -> float:
            er = r.get("engagement_rate") or 0.0
            if mode == "views":
                return _num(r.get("views"))
            if mode == "engagement":
                return er
            if mode == "recency":
                if platform == "facebook-ads":
                    return _num(r.get("ad_active_days"))
                # newer posts score higher
                pd = r.get("posted_date") or "0000-00-00"
                return float(pd.replace("-", "") or 0)
            # blended (default): half (linear) normalized reach + half engagement, but
            # trust ER only once a post clears the reach floor so tiny-view/noisy-ratio
            # posts don't dominate the winners list.
            v = _num(r.get("views"))
            cred = min(1.0, v / ER_CONFIDENCE_VIEWS) if ER_CONFIDENCE_VIEWS else 1.0
            return 0.5 * (v / max_views) + 0.5 * min(er, 1.0) * cred

        recs.sort(key=score, reverse=True)
        for i, r in enumerate(recs, 1):
            r["score"] = round(score(r), 5)
            r["rank"] = i
        ranked.extend(recs)

    # stable platform order for output
    order = {"tiktok": 0, "instagram": 1, "facebook-ads": 2}
    ranked.sort(key=lambda r: (order.get(r["platform"], 9), r["rank"]))
    return ranked


def filter_records(records: list[dict], min_views: int = 0, days: int | None = None) -> list[dict]:
    out = records
    if min_views:
        out = [r for r in out if r["platform"] == "facebook-ads" or _num(r.get("views")) >= min_views]
    if days:
        cutoff = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        cutoff_dt = datetime.now(timezone.utc)
        keep = []
        for r in out:
            pd = r.get("posted_date")
            if not pd:
                keep.append(r)  # don't drop FB ads / undated items here
                continue
            try:
                d0 = datetime.strptime(pd, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                if (cutoff_dt - d0).days <= days:
                    keep.append(r)
            except Exception:  # noqa: BLE001
                keep.append(r)
        out = keep
        _ = cutoff
    return out


# --------------------------------------------------------------------------- #
# video download (Step 3)
# --------------------------------------------------------------------------- #
def download_video(url: str, out_stem: Path, direct: bool = False, log=print) -> Path | None:
    """Download a video to out_stem.<ext>. Returns the file path, or None on failure.

    direct=True streams the URL straight to disk (Facebook ad media URLs).
    Otherwise uses yt-dlp (TikTok / Instagram page URLs).
    """
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    if direct:
        try:
            dst = out_stem.with_suffix(".mp4")
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(dst, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1 << 16):
                        f.write(chunk)
            return dst if dst.stat().st_size > 0 else None
        except Exception as e:  # noqa: BLE001
            log(f"    direct download failed: {str(e)[:160]}")
            return None

    ytdlp = find_ytdlp()
    if not ytdlp:
        log("    yt-dlp not found in venv; cannot download.")
        return None
    template = str(out_stem) + ".%(ext)s"
    cmd = [ytdlp, "--no-playlist", "--no-warnings", "-o", template, url]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        log("    yt-dlp timed out.")
        return None
    if res.returncode != 0:
        log(f"    yt-dlp exited {res.returncode}: {(res.stderr or '')[:200]}")
    for ext in (".mp4", ".mov", ".webm", ".mkv", ".m4v"):
        cand = out_stem.with_suffix(ext)
        if cand.exists() and cand.stat().st_size > 0:
            return cand
    # yt-dlp may produce an unexpected ext sharing the stem
    for p in out_stem.parent.glob(out_stem.name + ".*"):
        if p.suffix.lower() in VIDEO_EXTS and p.stat().st_size > 0:
            return p
    return None
