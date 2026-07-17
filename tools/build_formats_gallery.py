"""Generate docs/formats-gallery.html — a browsable catalog of every content format.

Reads each formats/<slug>/format.md (the single source of truth) and renders a static
gallery: poster + name + status/feasibility badges + one-liner + example-folder link.
Committed to the repo so anyone can open it without a run; the intake form shows the
same info inline. Posters (git) render; example MP4 links point at the shared drive.

Usage:
    .venv\\Scripts\\python.exe tools\\build_formats_gallery.py
    .venv\\Scripts\\python.exe tools\\build_formats_gallery.py --out docs/formats-gallery.html
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORMATS_DIR = PROJECT_ROOT / "formats"


def read_format(fm_path: Path) -> dict | None:
    import yaml  # lazy
    text = fm_path.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None
    meta = yaml.safe_load(m.group(1)) or {}
    one = re.search(r"\*\*One-liner for the intake form:\*\*\s*\"(.+?)\"", text, re.DOTALL)
    meta["one_liner"] = re.sub(r"\s+", " ", one.group(1)) if one else ""
    return meta


def poster_data_uri(slug: str) -> str:
    """Inline the poster as a data URI (self-contained gallery) if it exists."""
    import base64
    for ext in (".jpg", ".jpeg", ".png"):
        p = FORMATS_DIR / slug / "preview" / f"poster{ext}"
        if p.exists():
            mime = "jpeg" if ext in (".jpg", ".jpeg") else "png"
            return f"data:image/{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the formats gallery HTML")
    ap.add_argument("--out", type=Path, default=PROJECT_ROOT / "docs" / "formats-gallery.html")
    args = ap.parse_args()

    formats = []
    for d in sorted(FORMATS_DIR.iterdir()):
        if not d.is_dir() or d.name.startswith("_"):
            continue
        fm = d / "format.md"
        if fm.exists():
            meta = read_format(fm)
            if meta and meta.get("status") != "deprecated":
                meta["_slug"] = d.name
                meta["_poster"] = poster_data_uri(d.name)
                formats.append(meta)

    order = {"production": 0, "beta": 1, "draft": 2}
    formats.sort(key=lambda f: (f.get("family", "video"), order.get(f.get("status"), 3), f["_slug"]))

    def badge(kind, val):
        return f'<span class="badge b-{val}">{html.escape(str(val))}</span>'

    cards = []
    for f in formats:
        slug = f["_slug"]
        status = f.get("status", "draft")
        status_label = "not yet validated" if status == "draft" else status
        img = (f'<img src="{f["_poster"]}" alt="{html.escape(f.get("name",""))}">'
               if f["_poster"] else '<div class="noimg">poster coming soon</div>')
        ex = f.get("preview", {}).get("examples", "")
        ex_link = (f'<a class="ex" href="file:///{html.escape(ex).replace(chr(92), "/")}">▶ example videos</a>'
                   if ex else "")
        subs = f.get("sub_formats") or []
        subs_html = (f'<p class="subs">sub-styles: {html.escape(", ".join(str(s) for s in subs))}</p>'
                     if subs else "")
        cards.append(f"""
        <div class="card">
          {img}
          <div class="body">
            <h3>{html.escape(f.get("name", slug))}</h3>
            <div class="badges">
              <span class="badge b-{status}">{html.escape(status_label)}</span>
              {badge("feas", f.get("feasibility","experimental"))}
              <span class="badge b-fam">{html.escape(f.get("family","video"))}</span>
            </div>
            <p class="one">{html.escape(f.get("one_liner",""))}</p>
            {subs_html}
            <p class="meta">v{html.escape(str(f.get("version","0")))} ·
              {html.escape(str(f.get("aspect","")))} ·
              {"VO" if f.get("vo") else "no VO"} · <code>{html.escape(slug)}</code></p>
            {ex_link}
          </div>
        </div>""")

    html_out = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Content Formats — Mode AI Creative Loop</title>
<style>
 body{{font-family:Segoe UI,system-ui,sans-serif;background:#0f1115;color:#e8eaed;margin:0;padding:32px}}
 h1{{margin:0 0 4px}} .sub{{color:#9aa0a6;margin:0 0 24px}}
 .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
 .card{{border:1px solid #2a2f3a;border-radius:12px;overflow:hidden;background:#161a22}}
 .card img,.noimg{{width:100%;height:180px;object-fit:cover;background:#0a0c10}}
 .noimg{{display:flex;align-items:center;justify-content:center;color:#5f6368;font-size:13px}}
 .body{{padding:14px}} h3{{margin:0 0 8px;font-size:17px}}
 .badges{{margin-bottom:8px}}
 .badge{{display:inline-block;font-size:11px;border-radius:99px;padding:3px 9px;margin:0 4px 4px 0;font-weight:600}}
 .b-production{{background:#1a2c47;color:#8ab4f8}} .b-beta{{background:#2d2440;color:#c58af9}}
 .b-draft{{background:#2a2f3a;color:#9aa0a6}}
 .b-proven{{background:#12351c;color:#81c995}} .b-feasible{{background:#33301a;color:#fdd663}}
 .b-experimental{{background:#3a1d1d;color:#f28b82}} .b-fam{{background:#20262f;color:#9aa0a6}}
 .one{{color:#cdd1d6;font-size:13.5px;line-height:1.5;margin:6px 0}}
 .subs{{color:#9aa0a6;font-size:12px;margin:4px 0}}
 .meta{{color:#5f6368;font-size:11.5px;margin:8px 0 6px}} code{{color:#8ab4f8}}
 .ex{{font-size:12.5px;color:#8ab4f8;text-decoration:none}} .ex:hover{{text-decoration:underline}}
</style></head><body>
<h1>Content Formats</h1>
<p class="sub">Every format the engine can produce. Generated from formats/REGISTRY.md +
each format.md by tools/build_formats_gallery.py — re-run it after adding a format.
Launch a run with <code>/create-videos</code> or <code>/create-statics</code>.</p>
<div class="grid">{"".join(cards)}</div>
</body></html>"""

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html_out, encoding="utf-8")
    print(f"wrote {len(formats)} formats -> {args.out.relative_to(PROJECT_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
