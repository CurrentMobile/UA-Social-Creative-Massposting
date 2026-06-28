"""Assemble a talking-head edit with jump-cut zooms, B-roll/logo cutaways, and captions.

Reads a JSON spec describing ordered A-roll segments (each a phrase span with a zoom level),
overlay cutaways (B-roll / alpha logo) addressed by source time, and a transcripts dir.
Produces a composed video (jump-cut backbone + overlays + burned captions) with the original
VO audio. Background music and the CTA are added afterward by mix_audio.py / append_cta.py.

Pipeline:
  Stage A: per-segment accurate-seek extract + scale-to-cover + alternating zoom -> concat (VO kept)
  Stage B: overlay B-roll (scaled, muted, PTS-shifted, gated) + alpha logo, then burn ASS captions
Captions are generated from the word-level transcripts, remapped to the output timeline,
chunked to <=4 words, centered and narrow.

Spec JSON:
{
  "transcripts_dir": "<abs>",
  "width":1080,"height":1920,"fps":30,
  "segments":[{"src":"<abs>","start":0.94,"end":4.26,"zoom":1.0,"smooth":false}, ...],
  "overlays":[{"src":"<abs>","over_src":"Clip 3.mp4","at_src":5.58,"dur":5.0,"kind":"broll|logo"}, ...],
  "work_dir":"<abs edit/_build>",
  "out":"<abs composed.mp4>"
}

Usage:
    python tools/assemble_jumpcut.py <spec.json> [--stage-a-only] [--no-captions]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> None:
    print("  $ ffmpeg ...", cmd[-1] if cmd else "")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed ({r.returncode})")


def even(n: float) -> int:
    return int(round(n / 2.0)) * 2


def vfilter_zoom(W: int, H: int, fps: int, zoom: float, smooth: bool, dur: float) -> str:
    cover = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if smooth and zoom > 1.0:
        step = (zoom - 1.0) / max(dur * fps, 1)
        zp = (f"zoompan=z='min(zoom+{step:.6f},{zoom})':d=1:"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps}")
        return f"{cover},{zp},setsar=1,format=yuv420p"
    if zoom > 1.0:
        zw, zh = even(W * zoom), even(H * zoom)
        return f"{cover},scale={zw}:{zh},crop={W}:{H},setsar=1,fps={fps},format=yuv420p"
    return f"{cover},setsar=1,fps={fps},format=yuv420p"


def build_backbone(spec: dict, segs: list[dict]) -> Path:
    W, H, fps = spec["width"], spec["height"], spec["fps"]
    work = Path(spec["work_dir"]); work.mkdir(parents=True, exist_ok=True)
    backbone = work / "backbone.mp4"

    inputs: list[str] = []
    fparts: list[str] = []
    cat = ""
    for i, s in enumerate(segs):
        dur = s["end"] - s["start"]
        inputs += ["-ss", f"{s['start']:.3f}", "-to", f"{s['end']:.3f}", "-i", s["src"]]
        vf = vfilter_zoom(W, H, fps, float(s.get("zoom", 1.0)), bool(s.get("smooth")), dur)
        fparts.append(f"[{i}:v]{vf}[v{i}]")
        fparts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
        cat += f"[v{i}][a{i}]"
    fparts.append(f"{cat}concat=n={len(segs)}:v=1:a=1[vout][aout]")
    fg = ";".join(fparts)

    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", fg,
           "-map", "[vout]", "-map", "[aout]",
           "-r", str(fps), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2",
           str(backbone)]
    print(f"Stage A: {len(segs)} segments -> backbone")
    run(cmd)
    return backbone


def load_words(transcripts_dir: Path, src: str) -> list[dict]:
    stem = Path(src).stem
    p = transcripts_dir / f"{stem}.json"
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


def _ts(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


BRAND_FIXES = {"ModeEarn": "Mode Earn", "Mode earn": "Mode Earn", "modeearn": "Mode Earn"}


def build_captions(spec: dict, segs: list[dict]) -> Path:
    """Map words to the output timeline, chunk <=4 words, write ASS."""
    W, H = spec["width"], spec["height"]
    tdir = Path(spec["transcripts_dir"])
    work = Path(spec["work_dir"])
    ass = work / "captions.ass"

    timed: list[dict] = []  # {out_start,out_end,text}
    out_cursor = 0.0
    for s in segs:
        seg_dur = s["end"] - s["start"]
        for w in load_words(tdir, s["src"]):
            if w["start"] >= s["start"] - 0.02 and w["end"] <= s["end"] + 0.25:
                os_ = out_cursor + max(0.0, w["start"] - s["start"])
                oe_ = out_cursor + min(seg_dur, w["end"] - s["start"])
                timed.append({"s": os_, "e": oe_, "text": w["text"]})
        out_cursor += seg_dur

    # chunk <=4 words, break after sentence-ending punctuation
    chunks: list[dict] = []
    cur: list[dict] = []
    for w in timed:
        cur.append(w)
        ends_sentence = w["text"].rstrip()[-1:] in ".!?"
        if len(cur) >= 4 or ends_sentence:
            chunks.append({"s": cur[0]["s"], "e": cur[-1]["e"],
                           "text": " ".join(x["text"] for x in cur)})
            cur = []
    if cur:
        chunks.append({"s": cur[0]["s"], "e": cur[-1]["e"],
                       "text": " ".join(x["text"] for x in cur)})

    # extend each caption slightly but not into the next
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1]["s"] if i + 1 < len(chunks) else c["e"] + 0.4
        c["e"] = min(c["e"] + 0.35, nxt - 0.02)
        if c["e"] <= c["s"]:
            c["e"] = c["s"] + 0.3

    style = (
        "Style: Default,Arial,60,&H00FFFFFF,&H000000FF,&H00000000,&H64000000,"
        "-1,0,0,0,100,100,0,0,1,3,0,2,140,140,560,1"
    )
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: %d\nPlayResY: %d\nWrapStyle: 2\n\n"
        "[V4+ Styles]\n"
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,"
        "Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding\n%s\n\n"
        "[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    ) % (W, H, style)

    lines = [header]
    for c in chunks:
        txt = c["text"].replace("\n", " ").strip()
        for k, v in BRAND_FIXES.items():
            txt = txt.replace(k, v)
        lines.append(f"Dialogue: 0,{_ts(c['s'])},{_ts(c['e'])},Default,,0,0,0,,{txt}")
    ass.write_text("\n".join(lines), encoding="utf-8")
    print(f"  captions: {len(chunks)} cues -> {ass.name}")
    return ass


def map_src_to_out(segs: list[dict], over_src: str, at_src: float) -> float:
    """Map a (source file, source time) to output time on the concatenated backbone."""
    out_cursor = 0.0
    stem = Path(over_src).stem
    for s in segs:
        seg_dur = s["end"] - s["start"]
        if Path(s["src"]).stem == stem and s["start"] - 0.05 <= at_src <= s["end"] + 0.05:
            return out_cursor + max(0.0, min(seg_dur, at_src - s["start"]))
        out_cursor += seg_dur
    # fallback: start of the first segment of that source
    out_cursor = 0.0
    for s in segs:
        if Path(s["src"]).stem == stem:
            return out_cursor
        out_cursor += s["end"] - s["start"]
    return 0.0


def compose(spec: dict, segs: list[dict], backbone: Path, ass: Path | None) -> Path:
    W, H, fps = spec["width"], spec["height"], spec["fps"]
    out = Path(spec["out"])
    overlays = spec.get("overlays", [])

    inputs = ["-i", str(backbone)]
    for ov in overlays:
        inputs += ["-i", ov["src"]]

    fparts: list[str] = []
    prev = "[0:v]"
    for k, ov in enumerate(overlays):
        idx = k + 1
        o_start = map_src_to_out(segs, ov["over_src"], float(ov["at_src"]))
        o_end = o_start + float(ov["dur"])
        if ov.get("kind") == "logo":
            pre = f"[{idx}:v]setpts=PTS-STARTPTS+{o_start:.3f}/TB[ov{k}]"
        else:  # broll: scale to cover, drop audio implicitly (we never map it)
            pre = (f"[{idx}:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
                   f"crop={W}:{H},setsar=1,fps={fps},setpts=PTS-STARTPTS+{o_start:.3f}/TB[ov{k}]")
        fparts.append(pre)
        lbl = f"[t{k}]"
        fparts.append(f"{prev}[ov{k}]overlay=enable='between(t,{o_start:.3f},{o_end:.3f})':eof_action=pass{lbl}")
        prev = lbl

    if ass is not None:
        ass_esc = str(ass).replace("\\", "/").replace(":", "\\:")
        fparts.append(f"{prev}subtitles='{ass_esc}'[vfin]")
        vmap = "[vfin]"
    else:
        # need a label for the final video; if no overlays and no captions, just copy backbone
        if prev == "[0:v]":
            vmap = "0:v"
        else:
            vmap = prev

    cmd = ["ffmpeg", "-y", *inputs]
    if fparts:
        cmd += ["-filter_complex", ";".join(fparts)]
    cmd += ["-map", vmap, "-map", "0:a",
            "-r", str(fps), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-ac", "2",
            str(out)]
    print(f"Stage B: {len(overlays)} overlays + captions -> {out.name}")
    run(cmd)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Assemble jump-cut zoom edit with overlays + captions")
    ap.add_argument("spec", type=Path)
    ap.add_argument("--stage-a-only", action="store_true")
    ap.add_argument("--no-captions", action="store_true")
    args = ap.parse_args()

    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    spec.setdefault("width", 1080); spec.setdefault("height", 1920); spec.setdefault("fps", 30)
    segs = spec["segments"]

    backbone = build_backbone(spec, segs)
    if args.stage_a_only:
        print(f"backbone: {backbone}")
        return
    ass = None if args.no_captions else build_captions(spec, segs)
    out = compose(spec, segs, backbone, ass)
    print(f"\ncomposed: {out}")


if __name__ == "__main__":
    main()
