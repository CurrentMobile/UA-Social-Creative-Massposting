"""build_srt.py — generate master.srt from an EDL + cached word-level transcripts.

Maps each EDL range's spoken words (from edit/transcripts/<source-stem>.json) onto the
output timeline (cumulative segment durations), chunks them into <=N words (breaking on
sentence punctuation), applies brand-name fixes, and writes <edit-dir>/master.srt.

Usage:
    .venv\\Scripts\\python.exe tools\\build_srt.py assets\\<app>\\<video>\\edit [--max-words 4]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

BRAND_FIXES = {"ModeEarn": "Mode Earn", "Mode earn": "Mode Earn", "modeearn": "Mode Earn"}


def load_words(transcripts_dir: Path, stem: str) -> list[dict]:
    p = transcripts_dir / f"{stem}.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for w in d.get("words", []):
        if w.get("type") != "word":
            continue
        t = (w.get("text") or "").strip()
        if t and "start" in w and "end" in w:
            out.append({"text": t, "start": float(w["start"]), "end": float(w["end"])})
    return out


def fmt(t: float) -> str:
    if t < 0:
        t = 0.0
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate master.srt from edl.json + transcripts")
    ap.add_argument("edit_dir", type=Path)
    ap.add_argument("--max-words", type=int, default=4)
    args = ap.parse_args()

    edit_dir = args.edit_dir.resolve()
    edl = json.loads((edit_dir / "edl.json").read_text(encoding="utf-8"))
    tdir = edit_dir / "transcripts"
    sources = edl.get("sources", {})

    # words mapped to output timeline
    timed: list[dict] = []
    cur = 0.0
    for r in edl.get("ranges", []):
        key = r["source"]; start = float(r["start"]); end = float(r["end"])
        seg_dur = end - start
        stem = Path(sources.get(key, key)).stem
        for w in load_words(tdir, stem):
            if w["start"] >= start - 0.02 and w["end"] <= end + 0.25:
                timed.append({
                    "s": cur + max(0.0, w["start"] - start),
                    "e": cur + min(seg_dur, w["end"] - start),
                    "text": w["text"],
                })
        cur += seg_dur

    # chunk <= max-words, break after sentence-ending punctuation
    chunks: list[dict] = []
    grp: list[dict] = []
    for w in timed:
        grp.append(w)
        if len(grp) >= args.max_words or w["text"].rstrip()[-1:] in ".!?":
            chunks.append({"s": grp[0]["s"], "e": grp[-1]["e"],
                           "text": " ".join(x["text"] for x in grp)})
            grp = []
    if grp:
        chunks.append({"s": grp[0]["s"], "e": grp[-1]["e"],
                       "text": " ".join(x["text"] for x in grp)})

    for i, c in enumerate(chunks):
        nxt = chunks[i + 1]["s"] if i + 1 < len(chunks) else c["e"] + 0.4
        c["e"] = min(c["e"] + 0.35, nxt - 0.02)
        if c["e"] <= c["s"]:
            c["e"] = c["s"] + 0.3
        txt = c["text"]
        for k, v in BRAND_FIXES.items():
            txt = txt.replace(k, v)
        c["text"] = txt

    lines = []
    for i, c in enumerate(chunks, 1):
        lines.append(str(i))
        lines.append(f"{fmt(c['s'])} --> {fmt(c['e'])}")
        lines.append(c["text"])
        lines.append("")
    (edit_dir / "master.srt").write_text("\n".join(lines), encoding="utf-8")
    print(f"master.srt -> {edit_dir / 'master.srt'}  ({len(chunks)} cues)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
