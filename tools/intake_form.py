"""One-shot intake form — captures EVERYTHING for a content run in a single round.

Launched by workflows/core/intake.md (the /create-videos and /create-statics
commands). Scans the repo live (format registry, app manifests, persona library),
serves a one-page form on localhost, opens the default browser, blocks until the user
submits, writes the intake JSON, prints its path as the LAST stdout line, and exits.

This replaces multi-round in-chat questioning: the user fills ONE form with dropdowns
(every dropdown also accepts custom typed values) and free-text fields. Format options
show poster thumbnails, feasibility badges, and "see example" links to the shared
drive so users can PREVIEW a format before selecting it.

Usage:
    .venv\\Scripts\\python.exe tools\\intake_form.py --family video
    .venv\\Scripts\\python.exe tools\\intake_form.py --family video ^
        --prefill format=ugc-single --prefill persona=retiree-female-poc --prefill app=mode-earn
    .venv\\Scripts\\python.exe tools\\intake_form.py --family static --timeout 900

Exit codes: 0 = submitted (path on last stdout line), 3 = timeout / cancelled.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORMATS_DIR = PROJECT_ROOT / "formats"
PERSONAS_DIR = PROJECT_ROOT / "assets" / "_shared" / "personas"
INTAKE_DIR = PROJECT_ROOT / ".tmp" / "intake"
IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp")

# only these roots may be served as images (thumbnails)
SERVE_ROOTS = (FORMATS_DIR, PERSONAS_DIR)


# --------------------------------------------------------------------------- #
# Repo scanning
# --------------------------------------------------------------------------- #
def read_frontmatter(md: Path) -> dict:
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        sys.exit("intake_form needs pyyaml: .venv\\Scripts\\python.exe -m pip install pyyaml")
    text = md.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    data = yaml.safe_load(m.group(1)) or {}
    one = re.search(r"\*\*One-liner for the intake form:\*\*\s*\"(.+?)\"", text, re.DOTALL)
    if one:
        data["one_liner"] = re.sub(r"\s+", " ", one.group(1))
    return data


def scan_formats(family: str) -> list[dict]:
    out = []
    if not FORMATS_DIR.exists():
        return out
    for d in sorted(FORMATS_DIR.iterdir()):
        fm = d / "format.md"
        if not d.is_dir() or d.name.startswith("_") or not fm.exists():
            continue
        meta = read_frontmatter(fm)
        if not meta or meta.get("family") != family:
            continue
        if meta.get("status") == "deprecated":
            continue
        poster = d / "preview" / "poster.jpg"
        out.append({
            "id": meta.get("id", d.name),
            "name": meta.get("name", d.name),
            "status": meta.get("status", "draft"),
            "feasibility": meta.get("feasibility", "experimental"),
            "one_liner": meta.get("one_liner", ""),
            "sub_formats": meta.get("sub_formats") or [],
            "durations": meta.get("durations") or [30, 45, 60],
            "personas": meta.get("personas") or {"min": 1, "max": 1, "roles": ["presenter"]},
            "vo": meta.get("vo", True),
            "form_fields": meta.get("form_fields") or
                           ["persona", "duration", "variations", "script_source", "autonomy", "extra_notes"],
            "poster": str(poster.relative_to(PROJECT_ROOT).as_posix()) if poster.exists() else "",
            "examples": (meta.get("preview") or {}).get("examples", ""),
            "cost_note": ((meta.get("cost_estimate") or {}).get("per_video") or {}),
        })
    # production first, then beta, then draft
    order = {"production": 0, "beta": 1, "draft": 2}
    out.sort(key=lambda f: (order.get(f["status"], 3), f["id"]))
    return out


def scan_apps() -> list[dict]:
    out = []
    assets = PROJECT_ROOT / "assets"
    for d in sorted(assets.iterdir()) if assets.exists() else []:
        if not d.is_dir() or d.name.startswith(("_", ".")) or d.name in ("sfx", "music", "fonts"):
            continue
        mf = d / "manifest.md"
        if not mf.exists():
            continue
        text = mf.read_text(encoding="utf-8", errors="replace")
        disp = re.search(r"(?m)^display_name:\s*(.+)$", text)
        out.append({"slug": d.name, "name": (disp.group(1).strip() if disp else d.name)})
    return out


def scan_personas() -> list[dict]:
    out = []
    for d in sorted(PERSONAS_DIR.iterdir()) if PERSONAS_DIR.exists() else []:
        if not d.is_dir():
            continue
        base = next((d / f"base-character{e}" for e in IMG_EXTS if (d / f"base-character{e}").exists()), None)
        if base:
            out.append({"slug": d.name,
                        "img": str(base.relative_to(PROJECT_ROOT).as_posix())})
    return out


# --------------------------------------------------------------------------- #
# HTML
# --------------------------------------------------------------------------- #
def build_html(family: str, formats: list[dict], apps: list[dict],
               personas: list[dict], prefill: dict) -> str:
    data = json.dumps({"family": family, "formats": formats, "apps": apps,
                       "personas": personas, "prefill": prefill}, ensure_ascii=False)
    # NOTE: doubled braces {{ }} are literal braces in this f-string.
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Create {'Video' if family == 'video' else 'Static'} — Mode AI Creative Loop</title>
<style>
 body{{font-family:Segoe UI,system-ui,sans-serif;background:#0f1115;color:#e8eaed;margin:0;padding:24px}}
 .wrap{{max-width:880px;margin:0 auto}}
 h1{{font-size:22px;margin:0 0 4px}} .sub{{color:#9aa0a6;margin:0 0 20px;font-size:14px}}
 fieldset{{border:1px solid #2a2f3a;border-radius:10px;margin:0 0 16px;padding:14px 16px}}
 legend{{padding:0 8px;color:#8ab4f8;font-weight:600;font-size:13px;text-transform:uppercase;letter-spacing:.06em}}
 label{{display:block;font-size:13px;color:#bdc1c6;margin:10px 0 4px}}
 select,input[type=text],input[type=number],textarea{{width:100%;box-sizing:border-box;background:#1a1e26;color:#e8eaed;border:1px solid #333a47;border-radius:8px;padding:9px 10px;font-size:14px}}
 textarea{{min-height:74px;resize:vertical}}
 .cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(255px,1fr));gap:10px}}
 .card{{border:1px solid #333a47;border-radius:10px;padding:10px;cursor:pointer;background:#161a22}}
 .card.sel{{border-color:#8ab4f8;background:#1c2433;box-shadow:0 0 0 1px #8ab4f8}}
 .card img{{width:100%;height:120px;object-fit:cover;border-radius:6px;background:#0a0c10}}
 .card .noimg{{width:100%;height:120px;border-radius:6px;background:#0a0c10;display:flex;align-items:center;justify-content:center;color:#5f6368;font-size:12px}}
 .card h3{{font-size:14px;margin:8px 0 2px}} .card p{{font-size:12px;color:#9aa0a6;margin:2px 0}}
 .badge{{display:inline-block;font-size:10px;border-radius:99px;padding:2px 8px;margin-right:4px;font-weight:600}}
 .b-proven{{background:#12351c;color:#81c995}} .b-feasible{{background:#33301a;color:#fdd663}}
 .b-experimental{{background:#3a1d1d;color:#f28b82}} .b-draft{{background:#2a2f3a;color:#9aa0a6}}
 .b-production{{background:#1a2c47;color:#8ab4f8}} .b-beta{{background:#2d2440;color:#c58af9}}
 .ex{{font-size:11px;color:#8ab4f8;text-decoration:none}} .ex:hover{{text-decoration:underline}}
 .personas{{display:grid;grid-template-columns:repeat(auto-fill,minmax(108px,1fr));gap:8px}}
 .pcard{{border:1px solid #333a47;border-radius:10px;padding:6px;text-align:center;cursor:pointer;background:#161a22}}
 .pcard.sel{{border-color:#81c995;box-shadow:0 0 0 1px #81c995}}
 .pcard img{{width:100%;height:100px;object-fit:cover;border-radius:6px}}
 .pcard div{{font-size:10.5px;color:#bdc1c6;margin-top:4px;word-break:break-word}}
 .row{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
 .hidden{{display:none!important}}
 button{{background:#8ab4f8;color:#0f1115;font-weight:700;font-size:15px;border:0;border-radius:10px;padding:12px 26px;cursor:pointer;margin-top:6px}}
 button:hover{{background:#aecbfa}}
 .hint{{font-size:11.5px;color:#5f6368;margin-top:3px}}
</style></head><body><div class="wrap">
<h1>Create {'a Video' if family == 'video' else 'Statics'}</h1>
<p class="sub">One form, everything Claude needs. Every dropdown also accepts a custom typed value.</p>
<form id="f" onsubmit="return submitForm(event)">

<fieldset><legend>App</legend>
 <select id="app"></select>
 <div id="newappwrap" class="hidden">
   <label>Product brief (required for a new app — what it does, target users, store link, brand do's/don'ts)</label>
   <textarea id="new_app_brief"></textarea>
 </div>
</fieldset>

<fieldset><legend>Format <span class="hint">(click a card — links preview real examples)</span></legend>
 <div class="cards" id="fmtcards"></div>
 <div id="subwrap" class="hidden"><label>Sub-format</label><select id="sub_format"></select></div>
</fieldset>

<fieldset id="personaset"><legend>Persona</legend>
 <div class="personas" id="pcards"></div>
 <label>Or type a custom persona note</label>
 <input type="text" id="persona_custom" placeholder="e.g. new persona: 40s gym-bro Dave (will be created)">
</fieldset>

<fieldset><legend>Options</legend>
 <div class="row">
  <div id="durwrap"><label>Duration</label><select id="duration"></select></div>
  <div><label>Variations</label><select id="variations"><option>1</option><option selected>2</option><option>3</option><option>4</option></select></div>
 </div>
 <div class="row">
  <div><label>Script</label><select id="script_source">
    <option value="claude">Claude writes it</option><option value="provide">I'll provide the script</option></select></div>
  <div><label>Autonomy</label><select id="autonomy">
    <option value="on">On — run straight through after script approval</option>
    <option value="off">Off — pause after each stage for my review</option></select></div>
 </div>
 <div id="scriptwrap" class="hidden"><label>Paste your script</label><textarea id="script_text"></textarea></div>
</fieldset>

<fieldset><legend>Reference (optional)</legend>
 <label>Reference video/image to recreate or draw from — URL or local file path</label>
 <input type="text" id="reference_source" placeholder="e.g. https://www.tiktok.com/@user/video/123  or  C:\\refs\\ad.mp4">
 <div class="hint">Claude runs a deep Gemini analysis on it (workflows/analyze_video.md) before scripting.</div>
 <div id="refmodewrap" class="hidden"><label>How closely to follow it</label><select id="reference_mode">
   <option value="recreate">Recreate — 1:1 structural recreation (its scene table is the edit contract)</option>
   <option value="inspiration">Inspiration — style/pacing cues only</option></select></div>
</fieldset>

<fieldset><legend>Extra</legend>
 <label>Product/creative brief (optional)</label><textarea id="brief"></textarea>
 <label>Extra notes for Claude (optional)</label><textarea id="notes"></textarea>
</fieldset>

<button type="submit">Start creating →</button>
</form></div>
<script>
const D = {data};
const $ = id => document.getElementById(id);
let selFormat = null, selPersonas = [];

function opt(sel, val, txt, selq) {{ const o = document.createElement('option');
  o.value = val; o.textContent = txt || val; if (selq) o.selected = true; sel.appendChild(o); }}

// apps
const appSel = $('app');
D.apps.forEach(a => opt(appSel, a.slug, a.name + ' (' + a.slug + ')', D.prefill.app === a.slug));
opt(appSel, '__new__', '➕ New app (not onboarded yet)');
appSel.onchange = () => $('newappwrap').classList.toggle('hidden', appSel.value !== '__new__');

// formats
const fc = $('fmtcards');
D.formats.forEach(f => {{
  const c = document.createElement('div'); c.className = 'card'; c.id = 'fmt-' + f.id;
  const img = f.poster ? '<img src="/img?p=' + encodeURIComponent(f.poster) + '">'
                       : '<div class="noimg">no poster yet</div>';
  const badges = '<span class="badge b-' + f.status + '">' + (f.status === 'draft' ? 'not yet validated' : f.status) + '</span>'
               + '<span class="badge b-' + f.feasibility + '">' + f.feasibility + '</span>';
  const ex = f.examples ? '<a class="ex" href="file:///' + f.examples.replace(/\\\\/g, '/') + '" target="_blank" onclick="event.stopPropagation()">▶ see examples</a>' : '';
  c.innerHTML = img + '<h3>' + f.name + '</h3><p>' + badges + '</p><p>' + (f.one_liner || '') + '</p>' + ex;
  c.onclick = () => pickFormat(f);
  fc.appendChild(c);
}});

function pickFormat(f) {{
  selFormat = f;
  document.querySelectorAll('.card').forEach(c => c.classList.remove('sel'));
  $('fmt-' + f.id).classList.add('sel');
  // sub-formats
  const sw = $('subwrap'), ss = $('sub_format'); ss.innerHTML = '';
  if (f.sub_formats.length) {{ sw.classList.remove('hidden');
    f.sub_formats.forEach(s => opt(ss, typeof s === 'string' ? s : s.id));
    opt(ss, '__custom__', 'custom… (describe in notes)'); }}
  else sw.classList.add('hidden');
  // durations
  const ds = $('duration'); ds.innerHTML = '';
  f.durations.forEach(d => opt(ds, d, '~' + d + 's'));
  opt(ds, '__custom__', 'custom… (say in notes)');
  $('durwrap').classList.toggle('hidden', !f.vo && f.id !== 'lofi-text');
  // personas visibility + limits
  $('personaset').classList.toggle('hidden', !f.form_fields.includes('persona'));
  const maxP = (f.personas && f.personas.max) || 1;
  $('personaset').querySelector('legend').textContent =
    'Persona' + (maxP > 1 ? 's (pick up to ' + maxP + ' — roles: ' + (f.personas.roles || []).join(', ') + ')' : '');
}}

// personas
const pc = $('pcards');
D.personas.forEach(p => {{
  const c = document.createElement('div'); c.className = 'pcard'; c.id = 'p-' + p.slug;
  c.innerHTML = '<img src="/img?p=' + encodeURIComponent(p.img) + '"><div>' + p.slug + '</div>';
  c.onclick = () => {{
    const maxP = (selFormat && selFormat.personas && selFormat.personas.max) || 1;
    const i = selPersonas.indexOf(p.slug);
    if (i >= 0) selPersonas.splice(i, 1);
    else {{ if (selPersonas.length >= maxP) selPersonas.shift(); selPersonas.push(p.slug); }}
    document.querySelectorAll('.pcard').forEach(x => x.classList.remove('sel'));
    selPersonas.forEach(s => $('p-' + s).classList.add('sel'));
  }};
  pc.appendChild(c);
}});

$('script_source').onchange = e => $('scriptwrap').classList.toggle('hidden', e.target.value !== 'provide');
$('reference_source').oninput = e => $('refmodewrap').classList.toggle('hidden', !e.target.value.trim());

// prefills
if (D.prefill.format) {{ const f = D.formats.find(x => x.id === D.prefill.format); if (f) pickFormat(f); }}
if (D.prefill.persona) {{ const el = $('p-' + D.prefill.persona);
  if (el) {{ selPersonas = [D.prefill.persona]; el.classList.add('sel'); }} }}
if (D.prefill.app) $('newappwrap').classList.toggle('hidden', appSel.value !== '__new__');
if (D.prefill.reference) {{ $('reference_source').value = D.prefill.reference;
  $('refmodewrap').classList.remove('hidden'); }}

function submitForm(ev) {{
  ev.preventDefault();
  if (!selFormat) {{ alert('Pick a format.'); return false; }}
  if (appSel.value === '__new__' && !$('new_app_brief').value.trim()) {{
    alert('A new app needs a product brief.'); return false; }}
  if (!$('personaset').classList.contains('hidden') &&
      selPersonas.length === 0 && !$('persona_custom').value.trim() &&
      selFormat.form_fields.includes('persona')) {{
    alert('Pick at least one persona (or describe a custom one).'); return false; }}
  const payload = {{
    family: D.family, app: appSel.value,
    new_app_brief: appSel.value === '__new__' ? $('new_app_brief').value.trim() : null,
    format: selFormat.id,
    sub_format: $('subwrap').classList.contains('hidden') ? null : $('sub_format').value,
    personas: selPersonas, persona_custom: $('persona_custom').value.trim() || null,
    duration: $('durwrap').classList.contains('hidden') ? null : $('duration').value,
    variations: parseInt($('variations').value, 10),
    script_source: $('script_source').value,
    script_text: $('script_source').value === 'provide' ? $('script_text').value : null,
    autonomy: $('autonomy').value,
    reference_source: $('reference_source').value.trim() || null,
    reference_mode: $('reference_source').value.trim() ? $('reference_mode').value : null,
    brief: $('brief').value.trim(), notes: $('notes').value.trim(),
    submitted_at: new Date().toISOString()
  }};
  fetch('/submit', {{method: 'POST', headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(payload)}})
    .then(() => document.body.innerHTML =
      '<div style="text-align:center;padding-top:120px;font-family:sans-serif;color:#e8eaed">' +
      '<h1>✅ Got it!</h1><p>Head back to Claude — the run is starting. You can close this tab.</p></div>');
  return false;
}}
</script></body></html>"""


# --------------------------------------------------------------------------- #
# Server
# --------------------------------------------------------------------------- #
class Handler(BaseHTTPRequestHandler):
    html: str = ""
    result: dict | None = None
    done = threading.Event()

    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            body = Handler.html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif url.path == "/img":
            rel = parse_qs(url.query).get("p", [""])[0]
            p = (PROJECT_ROOT / rel).resolve()
            ok = p.exists() and any(str(p).startswith(str(r.resolve())) for r in SERVE_ROOTS) \
                 and p.suffix.lower() in IMG_EXTS
            if not ok:
                self.send_response(404); self.end_headers(); return
            body = p.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", f"image/{'jpeg' if p.suffix.lower() in ('.jpg', '.jpeg') else p.suffix[1:]}")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if urlparse(self.path).path != "/submit":
            self.send_response(404); self.end_headers(); return
        n = int(self.headers.get("Content-Length", 0))
        Handler.result = json.loads(self.rfile.read(n).decode("utf-8"))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')
        Handler.done.set()


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main() -> int:
    ap = argparse.ArgumentParser(description="One-shot intake form (browser)")
    ap.add_argument("--family", choices=["video", "static"], required=True)
    ap.add_argument("--prefill", action="append", default=[], metavar="key=value",
                    help="prefill a field: format=, persona=, app=, reference= (repeatable)")
    ap.add_argument("--timeout", type=int, default=900, help="seconds to wait (default 900)")
    ap.add_argument("--port", type=int, default=0, help="fixed port (default: auto)")
    ap.add_argument("--no-browser", action="store_true", help="don't auto-open the browser")
    args = ap.parse_args()

    prefill = dict(p.split("=", 1) for p in args.prefill if "=" in p)
    formats = scan_formats(args.family)
    if not formats:
        sys.exit(f"no {args.family} formats found in formats/ — check formats/REGISTRY.md")
    apps = scan_apps()
    personas = scan_personas()
    Handler.html = build_html(args.family, formats, apps, personas, prefill)

    port = args.port or free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    url = f"http://127.0.0.1:{port}/"
    print(f"[intake] form ready at {url}  ({len(formats)} formats, {len(apps)} apps, "
          f"{len(personas)} personas)")
    if not args.no_browser:
        webbrowser.open(url)

    got = Handler.done.wait(timeout=args.timeout)
    server.shutdown()
    if not got or Handler.result is None:
        print("[intake] timed out / cancelled — fall back to AskUserQuestion rounds "
              "(see workflows/core/intake.md)")
        return 3

    INTAKE_DIR.mkdir(parents=True, exist_ok=True)
    out = INTAKE_DIR / f"intake-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.write_text(json.dumps(Handler.result, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        rel = out.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        rel = str(out)
    print(rel)  # LAST line = machine-readable path
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
