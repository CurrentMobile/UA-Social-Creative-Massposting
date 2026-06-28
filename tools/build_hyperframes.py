"""Port a jump-cut edit_spec.json into a HyperFrames composition for browser preview.

Produces a HyperFrames project (index.html + media/) where every piece of the edit lives
on the timeline as a clip with data-start / data-duration / data-track-index:

  track 0  A-roll segments  (muted <video>, trimmed via data-media-start, CSS/GSAP zoom)
  track 1  B-roll cutaways  (muted <video>, full-frame cover, z-index above A-roll)
  track 2  logo             (alpha WebM, converted from the .mov)
  track 3  captions         (text divs, <=4 words, centered narrow)
  track 9  VO audio         (single <audio>, extracted from the assembled backbone)

Then `npx hyperframes preview .` serves it on localhost so you can scrub and rearrange
(move a clip = change its data-start / data-duration and the preview hot-reloads).

Usage:
    python tools/build_hyperframes.py <edit_spec.json> <project_dir> --backbone <backbone.mp4>
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BRAND_FIXES = {"ModeEarn": "Mode Earn", "Mode earn": "Mode Earn", "modeearn": "Mode Earn"}


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"cmd failed ({r.returncode}): {' '.join(cmd[:6])}...\n{r.stderr[-400:]}")


def sanitize(name: str) -> str:
    stem = Path(name).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return stem + Path(name).suffix.lower()


def load_words(transcripts_dir: Path, src: str) -> list[dict]:
    p = transcripts_dir / f"{Path(src).stem}.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for w in d.get("words", []):
        if w.get("type") in ("spacing", "audio_event"):
            continue
        t = (w.get("text") or "").strip()
        if t and "start" in w and "end" in w:
            out.append({"text": t, "start": float(w["start"]), "end": float(w["end"])})
    return out


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_caption_chunks(spec: dict, segs: list[dict]) -> list[dict]:
    tdir = Path(spec["transcripts_dir"])
    timed: list[dict] = []
    cur_out = 0.0
    for s in segs:
        seg_dur = s["end"] - s["start"]
        for w in load_words(tdir, s["src"]):
            if w["start"] >= s["start"] - 0.02 and w["end"] <= s["end"] + 0.25:
                timed.append({
                    "s": cur_out + max(0.0, w["start"] - s["start"]),
                    "e": cur_out + min(seg_dur, w["end"] - s["start"]),
                    "text": w["text"],
                })
        cur_out += seg_dur

    chunks: list[dict] = []
    cur: list[dict] = []
    for w in timed:
        cur.append(w)
        if len(cur) >= 4 or w["text"].rstrip()[-1:] in ".!?":
            chunks.append({"s": cur[0]["s"], "e": cur[-1]["e"],
                           "text": " ".join(x["text"] for x in cur)})
            cur = []
    if cur:
        chunks.append({"s": cur[0]["s"], "e": cur[-1]["e"],
                       "text": " ".join(x["text"] for x in cur)})
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1]["s"] if i + 1 < len(chunks) else c["e"] + 0.4
        c["e"] = min(c["e"] + 0.35, nxt - 0.02)
        if c["e"] <= c["s"]:
            c["e"] = c["s"] + 0.3
        txt = c["text"]
        for k, v in BRAND_FIXES.items():
            txt = txt.replace(k, v)
        c["text"] = txt
    return chunks


def map_src_to_out(segs: list[dict], over_src: str, at_src: float) -> float:
    cur = 0.0
    stem = Path(over_src).stem
    for s in segs:
        d = s["end"] - s["start"]
        if Path(s["src"]).stem == stem and s["start"] - 0.05 <= at_src <= s["end"] + 0.05:
            return cur + max(0.0, min(d, at_src - s["start"]))
        cur += d
    cur = 0.0
    for s in segs:
        if Path(s["src"]).stem == stem:
            return cur
        cur += s["end"] - s["start"]
    return 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description="Build a HyperFrames composition from an edit spec")
    ap.add_argument("spec", type=Path)
    ap.add_argument("project_dir", type=Path)
    ap.add_argument("--backbone", type=Path, required=True, help="assembled backbone.mp4 (for VO audio)")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    W, H, FPS = spec.get("width", 1080), spec.get("height", 1920), spec.get("fps", 30)
    segs = spec["segments"]
    overlays = spec.get("overlays", [])

    proj = args.project_dir
    media = proj / "media"
    media.mkdir(parents=True, exist_ok=True)

    # --- copy + convert media ---
    name_map: dict[str, str] = {}  # original abs path -> media/<file>

    def stage(src: str, *, logo: bool = False) -> str:
        if src in name_map:
            return name_map[src]
        if logo:
            dst = media / "logo.webm"
            print(f"  convert logo -> {dst.name}")
            run(["ffmpeg", "-y", "-i", src, "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p",
                 "-b:v", "2M", "-an", str(dst)])
        else:
            dst = media / sanitize(Path(src).name)
            if not dst.exists():
                shutil.copyfile(src, dst)
        rel = f"media/{dst.name}"
        name_map[src] = rel
        return rel

    for s in segs:
        stage(s["src"])
    for ov in overlays:
        stage(ov["src"], logo=(ov.get("kind") == "logo"))

    # VO audio from backbone
    vo = media / "vo.m4a"
    print(f"  extract VO -> {vo.name}")
    run(["ffmpeg", "-y", "-i", str(args.backbone), "-vn", "-c:a", "aac", "-b:a", "192k", str(vo)])

    # --- timeline: derive starts as rounded cumulative, durations as exact diffs of
    #     rounded starts so contiguous clips touch precisely (no FP overlap on track 0).
    starts: list[float] = []
    cum = 0.0
    for s in segs:
        starts.append(round(cum, 3))
        cum += s["end"] - s["start"]
    total = round(cum, 3)

    def seg_dur(i: int) -> float:
        nxt = starts[i + 1] if i + 1 < len(starts) else total
        return round(nxt - starts[i], 3)

    # --- build HTML pieces ---
    aroll_html: list[str] = []
    tweens: list[str] = []
    for i, s in enumerate(segs):
        dur = seg_dur(i)
        o = starts[i]
        z = float(s.get("zoom", 1.0))
        rel = name_map[s["src"]]
        # Alternate A-roll across two tracks so contiguous clips never share a track
        # (avoids float-addition "overlap" while keeping full frame coverage — both
        # tracks sit below B-roll via CSS z-index, so visual layering is unaffected).
        trk = 0 if i % 2 == 0 else 4
        vid = (f'<video id="aroll_{i}" class="clip aroll" data-start="{o}" data-duration="{dur}" '
               f'data-media-start="{round(s["start"],3)}" data-track-index="{trk}" muted playsinline '
               f'src="{rel}" style="transform:scale({z if not s.get("smooth") else 1.0});"></video>')
        aroll_html.append(f'<div class="vwrap">{vid}</div>')
        if s.get("smooth") and z > 1.0:
            tweens.append(f'tl.fromTo("#aroll_{i}",{{scale:1.0}},{{scale:{z},duration:{dur},'
                          f'ease:"power1.inOut",transformOrigin:"50% 50%"}},{o});')

    ov_html: list[str] = []
    for k, ov in enumerate(overlays):
        o = round(map_src_to_out(segs, ov["over_src"], float(ov["at_src"])), 3)
        dur = round(float(ov["dur"]), 3)
        rel = name_map[ov["src"]]
        if ov.get("kind") == "logo":
            ov_html.append(f'<video id="logo_{k}" class="clip logo" data-start="{o}" data-duration="{dur}" '
                           f'data-track-index="2" muted playsinline src="{rel}"></video>')
        else:
            ov_html.append(f'<video id="broll_{k}" class="clip broll" data-start="{o}" data-duration="{dur}" '
                           f'data-media-start="0" data-track-index="1" muted playsinline src="{rel}"></video>')

    cap_html: list[str] = []
    for n, c in enumerate(build_caption_chunks(spec, segs)):
        o = round(c["s"], 3); dur = round(c["e"] - c["s"], 3)
        cap_html.append(f'<div id="cap_{n}" class="clip cap" data-start="{o}" data-duration="{dur}" '
                        f'data-track-index="3">{esc(c["text"])}</div>')

    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ width:{W}px; height:{H}px; overflow:hidden; background:#000;
                    font-family: Arial, Helvetica, sans-serif; }}
      .vwrap {{ position:absolute; inset:0; }}
      video.aroll, video.broll {{ position:absolute; inset:0; width:{W}px; height:{H}px;
                                  object-fit:cover; transform-origin:50% 50%; }}
      video.broll {{ z-index:10; }}
      video.logo  {{ position:absolute; inset:0; width:{W}px; height:{H}px;
                     object-fit:contain; z-index:30; }}
      .cap {{ position:absolute; left:50%; bottom:540px; transform:translateX(-50%);
              width:760px; text-align:center; z-index:40;
              color:#fff; font-size:60px; font-weight:800; line-height:1.1;
              text-shadow: 0 0 6px #000, 3px 3px 0 #000, -3px -3px 0 #000,
                           3px -3px 0 #000, -3px 3px 0 #000; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}"
         data-width="{W}" data-height="{H}">

      <!-- A-roll segments (track 0) -->
      {chr(10) + "      " + (chr(10) + "      ").join(aroll_html)}

      <!-- B-roll + logo cutaways (tracks 1-2) -->
      {(chr(10) + "      ").join(ov_html)}

      <!-- Captions (track 3) -->
      {(chr(10) + "      ").join(cap_html)}

      <!-- VO audio (track 9) -->
      <audio id="vo" data-start="0" data-duration="{total}" data-track-index="9" src="media/vo.m4a"></audio>
    </div>

    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {(chr(10) + "      ").join(tweens) if tweens else "// (no smooth-zoom tweens)"}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (proj / "index.html").write_text(html, encoding="utf-8")
    print(f"\nwrote {proj / 'index.html'}")
    print(f"  segments={len(segs)}  overlays={len(overlays)}  captions={len(cap_html)}  total={total}s")


if __name__ == "__main__":
    main()
