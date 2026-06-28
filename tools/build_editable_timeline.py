"""build_editable_timeline.py — generate an EDITABLE HyperFrames timeline from an EDL.

Reads <edit-dir>/edl.json and <edit-dir>/master.srt (+ optional <edit-dir>/mix.json) and emits a
HyperFrames project at <edit-dir>/editable-timeline/ where EVERY A-roll segment, B-roll cutaway,
overlay card, and caption is its own tweakable track/clip — NOT one flattened video. This is the
review/edit surface the user scrubs BEFORE the final render (workflows/edit_video.md step 8).

Track layout (data-track-index keeps same-track clips from overlapping; CSS z-index stacks them):
  0      A-roll segments      video, full-frame (data-media-start trims the source)
  1      B-roll cutaways      video, full-frame, on top of A-roll
  2      overlay cards        alpha video (WebM) / image, floats over the video
  3      captions             text divs, one per SRT cue
  10     dialogue             audio, one per A-roll segment (video is muted per HF rules)
  11     music                audio, looped under the whole edit (no ducking in preview)
  12+    SFX                  audio, one track each (so they never collide)

Source media is hardlinked (copy fallback) into the project with browser-safe names. The alpha card
is served as WebM, not ProRes MOV — browsers can't decode ProRes.

Serve with:  npx --yes hyperframes preview <edit-dir>/editable-timeline --port 3017
Then report:  http://localhost:3017/#project/editable-timeline

Usage:
    .venv\\Scripts\\python.exe tools\\build_editable_timeline.py assets\\<app>\\<video>\\edit
    .venv\\Scripts\\python.exe tools\\build_editable_timeline.py <edit-dir> --out <dir> --mix <mix.json>
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_NAME = "editable-timeline"


# ---------- helpers ----------------------------------------------------------

def srt_time_to_s(ts: str) -> float:
    ts = ts.strip().replace(".", ",")
    hms, ms = ts.split(",")
    h, m, s = hms.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    if not path.exists():
        return []
    cues: list[tuple[float, float, str]] = []
    blocks = re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip())
    for b in blocks:
        lines = [ln for ln in b.splitlines() if ln.strip() != ""]
        if len(lines) < 2:
            continue
        time_line = lines[1] if "-->" in lines[1] else (lines[0] if "-->" in lines[0] else None)
        if not time_line:
            continue
        start_s, end_s = (p.strip() for p in time_line.split("-->"))
        text = " ".join(lines[2:]) if "-->" in lines[1] else " ".join(lines[1:])
        cues.append((srt_time_to_s(start_s), srt_time_to_s(end_s), text.strip()))
    return cues


def safe(stem: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", stem.lower()) or "x"


def titlecase(text: str) -> str:
    """First letter of each word capitalized, rest lowercase. 'I'M RETIRED.' -> 'I'm Retired.'"""
    return " ".join((w[:1].upper() + w[1:].lower()) if w else w for w in text.split(" "))


def balance_lines(text: str, max_per: int = 4) -> list[str]:
    """Split text into balanced lines (never all on one line). >=2 lines; ~max_per words/line,
    distributed evenly. 5 words -> ['3 words','2 words']."""
    words = text.split()
    n = len(words)
    if n <= 1:
        return [text]
    lines_n = max(2, -(-n // max_per))  # ceil(n/max_per), at least 2
    base, extra = divmod(n, lines_n)
    out, i = [], 0
    for k in range(lines_n):
        take = base + (1 if k < extra else 0)
        out.append(" ".join(words[i:i + take]))
        i += take
    return out


def in_blackout(cs: float, ce: float, windows: list) -> bool:
    """True if cue [cs,ce) overlaps any [start,end] blackout window (e.g. a pop-up)."""
    for w in windows:
        if len(w) >= 2 and cs < float(w[1]) and ce > float(w[0]):
            return True
    return False


def link_media(src: Path, dst: Path) -> None:
    """Hardlink src -> dst (copy fallback). Overwrites an existing dst."""
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[warn] cmd failed ({r.returncode}): {' '.join(str(c) for c in cmd[:6])}…\n{r.stderr[-300:]}")


def ffprobe_dur(path: Path) -> float:
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nokey=1:noprint_wrappers=1", str(path)],
            capture_output=True, text=True)
        return float(out.stdout.strip())
    except Exception:  # noqa: BLE001
        return 0.0


def stage_broll(src: Path, dst: Path, span: float, trim_start: float = 0.0) -> None:
    """Stage a B-roll into the project with AUDIO STRIPPED, sized to exactly `span` seconds so it
    ends precisely with its A-roll segment (no trailing gap). `trim_start` drops the first N seconds
    of the source. After trimming, if the remaining footage is shorter than the span it is slowed
    (setpts) to fill; otherwise the first `span`s (from `trim_start`) is taken."""
    if dst.exists():
        dst.unlink()
    nat = ffprobe_dur(src)
    eff = (nat - trim_start) if nat else 0.0
    if eff and eff < span - 0.05:
        factor = span / eff
        run(["ffmpeg", "-y", "-ss", f"{trim_start}", "-i", str(src),
             "-vf", f"setpts={factor:.6f}*PTS", "-an", "-t", f"{span}", "-r", "30",
             "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", str(dst)])
    elif trim_start > 0:
        run(["ffmpeg", "-y", "-ss", f"{trim_start}", "-i", str(src), "-an", "-t", f"{span}",
             "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", str(dst)])
    else:
        run(["ffmpeg", "-y", "-i", str(src), "-c:v", "copy", "-an", str(dst)])
        if not dst.exists():  # codec not mp4-copy-safe → re-encode
            run(["ffmpeg", "-y", "-i", str(src), "-an",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p", str(dst)])


def ensure_project(project_dir: Path) -> None:
    """Make sure project_dir is a HyperFrames project (best-effort `init`)."""
    if (project_dir / "meta.json").exists():
        return
    project_dir.parent.mkdir(parents=True, exist_ok=True)
    npx = shutil.which("npx") or "npx"
    cmd = [npx, "--yes", "hyperframes", "init", str(project_dir),
           "--example", "blank", "--non-interactive", "--skip-skills"]
    try:
        subprocess.run(cmd, check=True, shell=(os.name == "nt"))
    except Exception as e:  # noqa: BLE001
        print(f"[warn] could not auto-init HyperFrames project ({e}).")
        print(f"       run first:  npx --yes hyperframes init {project_dir} "
              f"--example blank --non-interactive --skip-skills")


# ---------- HTML emit --------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Generate an editable HyperFrames timeline from an EDL")
    ap.add_argument("edit_dir", type=Path, help="the video's edit/ dir (holds edl.json, master.srt)")
    ap.add_argument("--out", type=Path, default=None, help="project dir (default <edit-dir>/editable-timeline)")
    ap.add_argument("--mix", type=Path, default=None, help="mix.json (default <edit-dir>/mix.json if present)")
    ap.add_argument("--edl", type=Path, default=None, help="EDL path (default <edit-dir>/edl.json)")
    args = ap.parse_args()

    edit_dir = args.edit_dir.resolve()
    edl_path = (args.edl or (edit_dir / "edl.json")).resolve()
    if not edl_path.exists():
        sys.exit(f"edl not found: {edl_path}")
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    srt = parse_srt(edit_dir / "master.srt")
    mix_path = args.mix or (edit_dir / "mix.json")
    mix = json.loads(Path(mix_path).read_text(encoding="utf-8")) if Path(mix_path).exists() else {}

    project_dir = (args.out or (edit_dir / PROJECT_NAME)).resolve()
    ensure_project(project_dir)
    media_dir = project_dir
    project_dir.mkdir(parents=True, exist_ok=True)

    W = int(edl.get("width", 1080))
    H = int(edl.get("height", 1920))

    # ---- link sources + build A-roll segments + dialogue ----
    sources = edl.get("sources", {})
    src_safe: dict[str, str] = {}
    for key, p in sources.items():
        sp = Path(p)
        if not sp.is_absolute():
            sp = (edit_dir / p)
        name = f"src_{safe(key)}{sp.suffix.lower() or '.mp4'}"
        if sp.exists():
            link_media(sp, media_dir / name)
        src_safe[key] = name

    # A-roll: each segment's VIDEO carries its own VO (data-has-audio="true", NOT muted) so there
    # is exactly ONE audio source per moment — no separate dialogue track (that duplicate is what
    # caused the echo / phase-cancellation on hyperframes render). Zoom = per-segment scale,
    # alternating within a source clip (cut via inline transform; "smooth" via a GSAP tween).
    fps = float(edl.get("fps", 30) or 30)
    def _snap(t: float) -> float:
        # Snap an output time to the integer frame grid. Consecutive A-roll clips must abut on
        # exact frame boundaries; sub-frame cumulative drift (e.g. 7.54s = 226.2 frames @30fps)
        # leaves one render frame uncovered -> a 1-frame BLACK flash at the cut.
        return round(round(t * fps) / fps, 6)

    video_clips: list[str] = []
    smooth_tweens: list[str] = []
    offset = 0.0  # RAW cumulative time; snapped only at use so per-clip rounding can't accumulate
    seg_index = 0
    auto_i = 0
    prev_key = None
    hook_end = 0.0  # cumulative end of the last HOOK-beat range (hook sticker leaves here)
    for r in edl.get("ranges", []):
        key = r["source"]
        start = float(r["start"]); end = float(r["end"])
        raw_dur = end - start
        out = _snap(offset)
        # each clip fills exactly to the NEXT clip's snapped start -> contiguous, no black gap
        dur = round(_snap(offset + raw_dur) - out, 6)
        beat = html.escape(str(r.get("beat", "")))
        name = src_safe.get(key, "missing.mp4")
        if key != prev_key:
            auto_i = 0; prev_key = key
        z = float(r.get("zoom", 1.0 if auto_i % 2 == 0 else 1.1))
        smooth = bool(r.get("smooth", False))
        auto_i += 1
        style = "transform-origin:50% 50%;"
        if z != 1.0 and not smooth:
            style += f"transform:scale({z});"
        # alternate tracks 0/4 so contiguous segments never share a track (float-add boundary
        # equality otherwise trips the overlap linter); z-index is class-based so look is unchanged.
        seg_trk = 0 if seg_index % 2 == 0 else 4
        video_clips.append(
            f'      <video class="clip seg" id="seg{seg_index}" title="{beat}: {key}" '
            f'data-start="{out}" data-media-start="{start}" data-duration="{dur}" data-track-index="{seg_trk}" '
            f'data-has-audio="true" src="{name}" playsinline style="{style}"></video>'
        )
        if smooth and z != 1.0:
            smooth_tweens.append(
                f'tl.fromTo("#seg{seg_index}",{{scale:1.0}},{{scale:{z},duration:{dur},'
                f'ease:"power1.inOut",transformOrigin:"50% 50%"}},{out});'
            )
        offset += raw_dur
        if str(r.get("beat", "")).strip().upper() == "HOOK":
            hook_end = _snap(offset)
        seg_index += 1
    # total spans the body, any overlay that extends past it, and the endscreen (which is
    # overlaid on the last clip at full length and runs past the body).
    total = _snap(offset)
    for _ov in edl.get("overlays", []):
        total = max(total, float(_ov["start_in_output"]) + float(_ov["duration"]))
    _es = edl.get("endscreen")
    if _es:
        total = max(total, float(_es["start_in_output"]) + float(_es["duration"]))
    total = round(max(total, float(edl.get("total_duration_s", 0) or 0)), 3)

    # ---- overlays: classify B-roll (opaque, full-frame) vs cards (alpha) ----
    broll_clips: list[str] = []
    card_clips: list[str] = []
    broll_n = 0
    card_n = 0
    for i, ov in enumerate(edl.get("overlays", [])):
        f = ov["file"]
        op = Path(f)
        if not op.is_absolute():
            op = (edit_dir / f).resolve()
        fl = f.lower()
        is_broll = "broll" in fl or "b-roll" in fl or "b_roll" in fl
        # browsers can't decode ProRes — prefer a .webm sibling for cards
        if not is_broll and op.suffix.lower() == ".mov":
            webm = op.with_suffix(".webm")
            if webm.exists():
                op = webm
        ext = op.suffix.lower() or ".mp4"
        kind = "broll" if is_broll else "card"
        name = f"{kind}{i}{ext}"
        st = _snap(float(ov["start_in_output"]))
        du = _snap(float(ov["duration"]))
        note = html.escape(str(ov.get("note", "")))
        if is_broll:
            # B-roll is ALWAYS muted (audio stripped at stage) and stretched/sized to fill its
            # A-roll segment exactly (no end gap).
            if op.exists():
                stage_broll(op, media_dir / name, du, float(ov.get("trim_start", 0.0)))
            broll_trk = 1 if broll_n % 2 == 0 else 5  # alternate so tiled B-rolls don't share a track
            broll_n += 1
            broll_clips.append(
                f'      <video class="clip broll" id="broll{i}" title="{note}" '
                f'data-start="{st}" data-duration="{du}" data-track-index="{broll_trk}" '
                f'data-has-audio="false" src="{name}" muted playsinline></video>'
            )
        else:
            # cards (logo / pop-ups): keep audio only when the overlay asks (e.g. the logo pop).
            keep = bool(ov.get("keep_audio"))
            if op.exists():
                link_media(op, media_dir / name)
            mute_attr = "" if keep else "muted "
            # alternate cards across tracks 2/10 so adjacent cards never share a track (a tiny gap
            # between two cards on one track makes HF's per-track player drop the second one).
            card_trk = 2 if card_n % 2 == 0 else 10
            card_n += 1
            card_clips.append(
                f'      <video class="clip card" id="card{i}" title="{note}" '
                f'data-start="{st}" data-duration="{du}" data-track-index="{card_trk}" '
                f'data-has-audio="{"true" if keep else "false"}" src="{name}" {mute_attr}playsinline></video>'
            )

    # ---- captions: one div per SRT cue (Title Case; skipped during pop-up blackout windows) ----
    blackouts = edl.get("caption_blackouts", [])
    caption_clips: list[str] = []
    for i, (cs, ce, text) in enumerate(srt):
        if in_blackout(cs, ce, blackouts):
            continue
        du = round(max(0.1, ce - cs), 3)
        caption_clips.append(
            f'      <div class="clip cap" id="cap{i}" data-start="{round(cs,3)}" '
            f'data-duration="{du}" data-track-index="3"><span>{html.escape(text)}</span></div>'
        )

    # ---- audio FX from mix.json (music + SFX, each on its own track) ----
    fx_clips: list[str] = []
    music = mix.get("music")
    if music:
        mp = Path(music)
        if not mp.is_absolute():
            mp = (Path.cwd() / music)
        if mp.exists():
            mname = f"music{mp.suffix.lower() or '.mp3'}"
            link_media(mp, media_dir / mname)
            vol = float(mix.get("music_volume", 0.15))
            fx_clips.append(
                f'      <audio class="clip" id="music" data-start="0" data-duration="{total}" '
                f'data-track-index="11" src="{mname}" data-volume="{vol}"></audio>'
            )
    # Dedupe: link each distinct SFX source ONCE and reuse its filename across all its <audio>
    # instances. Copying the same file many times (e.g. a shutter reused 12x) creates duplicate
    # media nodes that HF flags ("duplicate_media_discovery_risk") and can drop a sibling clip.
    sfx_link_cache: dict[str, str] = {}
    for i, s in enumerate(mix.get("sfx", [])):
        sp = Path(s["file"])
        if not sp.is_absolute():
            sp = (Path.cwd() / s["file"])
        if not sp.exists():
            continue
        cache_key = str(sp.resolve())
        sname = sfx_link_cache.get(cache_key)
        if sname is None:
            sname = f"sfx{i}{sp.suffix.lower() or '.mp3'}"
            link_media(sp, media_dir / sname)
            sfx_link_cache[cache_key] = sname
        fx_clips.append(
            f'      <audio class="clip" id="sfx{i}" data-start="{round(float(s["t"]),3)}" '
            f'data-track-index="{12 + i}" src="{sname}" data-volume="{float(s.get("gain",1.0))}"></audio>'
        )

    # ---- endscreen: full-frame CTA overlaid on the last clip, full length (extends total) ----
    endscreen_clips: list[str] = []
    es = edl.get("endscreen")
    if es:
        esp = Path(es["file"])
        if not esp.is_absolute():
            esp = (edit_dir / es["file"])
        if esp.exists():
            ename = f"endscreen{esp.suffix.lower() or '.mp4'}"
            link_media(esp, media_dir / ename)
            est = round(float(es["start_in_output"]), 3)
            esd = round(float(es["duration"]), 3)
            # CTA video carries its own audio (keep_audio default True) — single source, so NO
            # separate track-60 audio (that duplicate would echo on render).
            keep = es.get("keep_audio", True)
            mute_attr = "" if keep else "muted "
            endscreen_clips.append(
                f'      <video class="clip endscreen" id="endscreen" data-start="{est}" '
                f'data-duration="{esd}" data-track-index="8" data-has-audio="{"true" if keep else "false"}" '
                f'src="{ename}" {mute_attr}playsinline></video>'
            )

    # ---- hook sticker (top, balanced multi-line, leaves when the hook clip ends) ----
    sticker_clips: list[str] = []
    hs = edl.get("hook_sticker")
    if hs and hs.get("text"):
        h_end = round(float(hs.get("end", hook_end or 3.0)), 3)
        h_lines = balance_lines(str(hs["text"]), int(hs.get("max_words_per_line", 4)))
        # ONE merged sticker box wrapping all lines (opaque white, curved edges, dark text)
        h_html = "<br>".join(html.escape(ln) for ln in h_lines)
        sticker_clips.append(
            f'      <div class="clip hooksticker" id="hooksticker" data-start="0" '
            f'data-duration="{h_end}" data-track-index="6"><span>{h_html}</span></div>'
        )
    # ---- persistent disclaimer (tiny, bottom, centered multi-line, full duration) ----
    dc = edl.get("disclaimer")
    if dc:
        d_lines = dc.get("lines") or [str(dc.get("text", ""))]
        d_html = "<br>".join(html.escape(str(ln)) for ln in d_lines)
        sticker_clips.append(
            f'      <div class="clip disclaimer" id="disclaimer" data-start="0" '
            f'data-duration="{total}" data-track-index="7"><span>{d_html}</span></div>'
        )

    # ---- flicker transitions: quick white flash at selected cuts (camera-shutter SFX synced in
    # mix.json). EDL key flicker_cuts: [output_time, ...]; optional flicker_duration (default 0.16). ----
    flicker_clips: list[str] = []
    flicker_tweens: list[str] = []
    for i, ft in enumerate(edl.get("flicker_cuts", [])):
        t = float(ft)
        fdur = float(edl.get("flicker_duration", 0.16))
        fst = round(max(0.0, t - fdur / 2), 3)
        flicker_clips.append(
            f'      <div class="clip flicker" id="flicker{i}" data-start="{fst}" '
            f'data-duration="{round(fdur, 3)}" data-track-index="9"></div>'
        )
        flicker_tweens.append(
            f'tl.fromTo("#flicker{i}",{{opacity:0}},{{opacity:0.92,duration:{round(fdur/2, 3)},'
            f'yoyo:true,repeat:1,ease:"power1.inOut"}},{fst});'
        )

    body = "\n".join(video_clips + broll_clips + card_clips + endscreen_clips
                     + caption_clips + flicker_clips + sticker_clips + fx_clips)
    all_tweens = smooth_tweens + flicker_tweens
    tween_js = ("\n      ".join(all_tweens)) if all_tweens else "// (no tweens)"

    doc = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      .seg, .broll, .card {{ position: absolute; inset: 0; width: {W}px; height: {H}px; }}
      .seg  {{ object-fit: cover; z-index: 0; }}
      .broll {{ object-fit: cover; z-index: 10; }}
      .card  {{ object-fit: contain; z-index: 20; }}
      .endscreen {{ position: absolute; inset: 0; width: {W}px; height: {H}px; object-fit: cover; z-index: 25; }}
      /* caption style — matches the earlier "Back in the 80s" look: Arial bold, lower-third,
         narrow & centered, natural case, white with a heavy black outline. */
      .cap {{
        position: absolute; left: 50%; bottom: 540px; transform: translateX(-50%); z-index: 30;
        width: 800px; text-align: center;
        font-family: Arial, Helvetica, sans-serif; font-weight: 800;
        font-size: 60px; line-height: 1.1; color: #fff;
        text-shadow: 0 0 6px #000, 3px 3px 0 #000, -3px -3px 0 #000,
                     3px -3px 0 #000, -3px 3px 0 #000;
      }}
      /* hook sticker — centered band BETWEEN the head and the lower-third captions (was top:14%,
         which covered the presenter's head in tighter shots). bottom:740px sits ~145px above the
         caption block (caption bottom:540px) and below the chin; leaves when the hook clip ends. */
      .hooksticker {{ position: absolute; left: 0; right: 0; bottom: 740px; text-align: center;
                      z-index: 40; padding: 0 40px; }}
      .hooksticker span {{
        display: inline-block; text-align: center;
        background: #ffffff; color: #141414;
        font-family: Arial, Helvetica, sans-serif; font-weight: 900; font-size: 60px; line-height: 1.32;
        padding: 26px 50px; border-radius: 46px; box-shadow: 0 12px 34px rgba(0,0,0,.4);
      }}
      /* light-flicker transition — quick full-frame white flash at selected cuts */
      .flicker {{ position: absolute; inset: 0; width: {W}px; height: {H}px;
                  background: #fff; z-index: 48; opacity: 0; pointer-events: none; }}
      /* persistent AI/rewards disclaimer — tiny, bottom, centered, above everything incl. CTA */
      .disclaimer {{ position: absolute; left: 0; right: 0; bottom: 34px; text-align: center;
                     z-index: 50; padding: 0 70px; }}
      .disclaimer span {{
        display: inline-block; color: rgba(255,255,255,0.92);
        font-family: Arial, Helvetica, sans-serif; font-weight: 600; font-size: 22px; line-height: 1.32;
        text-shadow: 0 1px 3px rgba(0,0,0,.95), 0 0 2px rgba(0,0,0,.95);
      }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}"
         data-width="{W}" data-height="{H}">
{body}
    </div>
    <script>
      // Editable timeline: every clip/B-roll/card/caption is its own track element.
      // The player drives media playback + seeking; the root timeline is registered (empty)
      // per the HyperFrames timeline contract.
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      {tween_js}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (project_dir / "index.html").write_text(doc, encoding="utf-8")

    print(f"editable timeline -> {project_dir / 'index.html'}")
    print(f"  duration   : {total}s")
    print(f"  A-roll segs: {len(video_clips)} (track 0, carry own VO; {len(smooth_tweens)} smooth-zoom)")
    print(f"  B-roll     : {len(broll_clips)} (track 1)")
    print(f"  cards      : {len(card_clips)} (track 2)")
    print(f"  captions   : {len(caption_clips)} (track 3)")
    print(f"  audio fx   : music={'yes' if music else 'no'}, sfx={len(mix.get('sfx', []))} (tracks 11+)")
    print(f"\n  preview:  npx --yes hyperframes preview \"{project_dir}\" --port 3017")
    print(f"  url:      http://localhost:3017/#project/{PROJECT_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
