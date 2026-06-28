"""Live-test every API key in .env against its provider and report status.

Read-only / non-destructive: only hits GET (or auth-validation) endpoints — never
submits a generation or spends generation credits. Prints a results table with the
HTTP status and a parsed detail per service. Keys are masked in output.

Usage:
    python tools/test_api_keys.py
"""

from __future__ import annotations

from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TIMEOUT = 20


def load_env() -> dict[str, str]:
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


def show(service: str, key_disp: str, endpoint: str, status, verdict: str, detail: str) -> None:
    print(f"\n## {service}")
    print(f"   key      : {key_disp}")
    print(f"   endpoint : {endpoint}")
    print(f"   status   : {status}")
    print(f"   verdict  : {verdict}")
    if detail:
        print(f"   detail   : {detail}")


def short(r: requests.Response, n: int = 240) -> str:
    try:
        return r.text[:n].replace("\n", " ")
    except Exception:  # noqa: BLE001
        return ""


def test_gemini(env):
    key = env.get("GEMINI_API_KEY", "")
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    if not key:
        return show("Gemini", "(empty)", url, "-", "SKIP (no key)", "")
    # try ?key= (API key style)
    try:
        r = requests.get(url, params={"key": key}, timeout=TIMEOUT)
        if r.status_code == 200:
            models = [m.get("name", "") for m in r.json().get("models", [])]
            gem = [m for m in models if "gemini" in m]
            return show("Gemini", mask(key), url + "?key=…", r.status_code,
                        "WORKS (api-key style)", f"{len(models)} models; e.g. {', '.join(gem[:3])}")
    except Exception as e:  # noqa: BLE001
        return show("Gemini", mask(key), url, "ERR", "ERROR", str(e)[:160])
    # try Bearer (OAuth access-token style)
    try:
        r2 = requests.get(url, headers={"Authorization": f"Bearer {key}"}, timeout=TIMEOUT)
        if r2.status_code == 200:
            return show("Gemini", mask(key), url + " (Bearer)", r2.status_code,
                        "WORKS (OAuth Bearer token)", "token accepted as Bearer")
        return show("Gemini", mask(key), url, f"{r.status_code}/{r2.status_code}",
                    "FAILS (key rejected both ways)", short(r))
    except Exception as e:  # noqa: BLE001
        return show("Gemini", mask(key), url, "ERR", "ERROR", str(e)[:160])


def test_apify(env):
    key = env.get("APIFY_API_KEY", "")
    url = "https://api.apify.com/v2/users/me"
    if not key:
        return show("Apify", "(empty)", url, "-", "SKIP (no key)", "")
    try:
        r = requests.get(url, params={"token": key}, timeout=TIMEOUT)
        if r.status_code == 200:
            d = r.json().get("data", {})
            return show("Apify", mask(key), url, r.status_code, "WORKS",
                        f"user={d.get('username')}  plan={d.get('plan',{}).get('id','?') if isinstance(d.get('plan'),dict) else d.get('plan')}")
        return show("Apify", mask(key), url, r.status_code, "FAILS", short(r))
    except Exception as e:  # noqa: BLE001
        return show("Apify", mask(key), url, "ERR", "ERROR", str(e)[:160])


def test_heygen(env):
    key = env.get("HEYGEN_API_KEY", "")
    url = "https://api.heygen.com/v2/user/remaining_quota"
    if not key:
        return show("HeyGen", "(empty)", url, "-", "SKIP (no key)", "")
    try:
        r = requests.get(url, headers={"X-Api-Key": key}, timeout=TIMEOUT)
        if r.status_code == 200:
            return show("HeyGen", mask(key), url, r.status_code, "WORKS", short(r, 200))
        # fallback endpoint
        r2 = requests.get("https://api.heygen.com/v1/user/remaining_quota",
                          headers={"X-Api-Key": key}, timeout=TIMEOUT)
        if r2.status_code == 200:
            return show("HeyGen", mask(key), "v1/user/remaining_quota", r2.status_code, "WORKS", short(r2, 200))
        return show("HeyGen", mask(key), url, f"{r.status_code}/{r2.status_code}", "FAILS", short(r))
    except Exception as e:  # noqa: BLE001
        return show("HeyGen", mask(key), url, "ERR", "ERROR", str(e)[:160])


def test_elevenlabs(env):
    key = env.get("ELEVENLABS_API_KEY", "")
    url = "https://api.elevenlabs.io/v1/user/subscription"
    if not key:
        return show("ElevenLabs", "(empty)", url, "-", "SKIP (no key)", "")
    try:
        r = requests.get(url, headers={"xi-api-key": key}, timeout=TIMEOUT)
        if r.status_code == 200:
            d = r.json()
            used = d.get("character_count"); lim = d.get("character_limit")
            return show("ElevenLabs", mask(key), url, r.status_code, "WORKS",
                        f"tier={d.get('tier')}  chars {used}/{lim}")
        return show("ElevenLabs", mask(key), url, r.status_code, "FAILS", short(r))
    except Exception as e:  # noqa: BLE001
        return show("ElevenLabs", mask(key), url, "ERR", "ERROR", str(e)[:160])


def test_postiz(env):
    key = env.get("POSTIZ_API_KEY", "")
    url = "https://api.postiz.com/public/v1/integrations"
    if not key:
        return show("Postiz", "(empty)", url, "-", "SKIP (no key)", "")
    try:
        r = requests.get(url, headers={"Authorization": key}, timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            n = len(data) if isinstance(data, list) else len(data.get("integrations", []) if isinstance(data, dict) else [])
            names = [i.get("name") or i.get("identifier") for i in (data if isinstance(data, list) else [])][:6]
            return show("Postiz", mask(key), url, r.status_code, "WORKS",
                        f"{n} channel(s) connected: {names}")
        return show("Postiz", mask(key), url, r.status_code, "FAILS", short(r))
    except Exception as e:  # noqa: BLE001
        return show("Postiz", mask(key), url, "ERR", "ERROR", str(e)[:160])


def test_higgsfield(env):
    kid = env.get("HIGGSFIELD_API_ID", "")
    sec = env.get("HIGGSFIELD_API_KEY", "")
    disp = f"id {mask(kid)} / key {mask(sec)}"
    if not (kid and sec):
        return show("Higgsfield", disp, "platform.higgsfield.ai", "-", "SKIP (missing id or key)", "")
    # SDK scheme: Authorization: Key <ID>:<SECRET>.  Probe a GET that requires auth but
    # does NOT submit a job. A 401/403 => bad creds; 200/400/404/422 => creds accepted.
    attempts = [
        ("GET", "https://platform.higgsfield.ai/v1/generations", {"Authorization": f"Key {kid}:{sec}"}),
        ("GET", "https://platform.higgsfield.ai/v1/models", {"Authorization": f"Key {kid}:{sec}"}),
        ("GET", "https://platform.higgsfield.ai/v1/account", {"Authorization": f"Key {kid}:{sec}"}),
    ]
    last = None
    for method, url, headers in attempts:
        try:
            r = requests.request(method, url, headers=headers, timeout=TIMEOUT)
            last = (url, r)
            if r.status_code in (200, 201):
                return show("Higgsfield", disp, url, r.status_code, "WORKS (creds accepted)", short(r, 200))
            if r.status_code in (400, 404, 405, 422):
                return show("Higgsfield", disp, url, r.status_code,
                            "LIKELY OK (auth passed; endpoint returned non-auth error)", short(r, 200))
            if r.status_code in (401, 403):
                continue  # try next endpoint/scheme
        except Exception as e:  # noqa: BLE001
            last = (url, str(e))
    if last:
        url, r = last
        st = r.status_code if hasattr(r, "status_code") else "ERR"
        body = short(r) if hasattr(r, "text") else str(r)[:160]
        return show("Higgsfield", disp, url, st, "FAILS / inconclusive (401/403 or error)", body)


def main() -> None:
    env = load_env()
    print("=" * 64)
    print("API KEY LIVE TEST  (read-only — no generation credits spent)")
    print("=" * 64)
    test_gemini(env)
    test_apify(env)
    test_heygen(env)
    test_elevenlabs(env)
    test_postiz(env)
    test_higgsfield(env)
    print("\n" + "=" * 64)


if __name__ == "__main__":
    main()
