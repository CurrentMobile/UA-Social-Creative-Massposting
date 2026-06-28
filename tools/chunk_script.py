"""Chunk a VO script into Kling-sized dialogue beats for asset generation.

Step 4 of the asset-generation SOP (see workflows/generate_assets.md). Splits the
spoken VO into 10-20 word chunks that NEVER cut a sentence, then recommends a Kling
clip duration per chunk from its word count. Each chunk becomes one extracted first-
frame image (img-<n>) and one A-roll clip (Clip <n>).

Section labels (all-caps lines like HOOK / PROBLEM / SOLUTION / HOW IT WORKS / RESULT
/ CTA) are treated as beat boundaries and carried as metadata, not spoken. Chunking
never merges across sections, so the narrative beats stay intact.

Duration heuristic: recommended_duration_s = clamp(ceil(words / 2.7), 3, 15).
Grandmotherly "slow, deliberate pacing" runs ~2.7 words/sec; tune per clip if needed.

Usage:
    python tools/chunk_script.py <script.md|.txt>
    python tools/chunk_script.py assets/mode-earn/extraincomeforretirees/scripts/source.md \
        --out  assets/mode-earn/extraincomeforretirees/edit/chunks.json \
        --vo-script assets/mode-earn/extraincomeforretirees/scripts/vo-script.md \
        --title "ExtraIncomeForRetirees"

With no --out the chunk plan JSON is printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MIN_WORDS = 10
MAX_WORDS = 20
WORDS_PER_SEC = 2.7
DUR_MIN, DUR_MAX = 3, 15

# Sentence-final punctuation, but NOT ellipsis, which the scripts use mid-line.
# Ellipses are swapped for sentinels before splitting, then restored, so a mid-line
# "scam... but" or "extra ... you" stays one sentence.
_ELL3 = "\x00ELL3\x00"
_ELL1 = "\x00ELL1\x00"
_ELLIPSIS_UNICODE = "…"
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def is_section_label(line: str) -> bool:
    """A short all-caps line (e.g. HOOK, HOW IT WORKS) — a beat marker, not dialogue."""
    s = line.strip().strip(":").strip()
    if not s or len(s) > 24:
        return False
    if len(s.split()) > 4:
        return False
    letters = [c for c in s if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def word_count(text: str) -> int:
    return len([t for t in re.split(r"\s+", text.strip()) if re.search(r"\w", t)])


def split_sentences(text: str) -> list[str]:
    """Split into sentences on . ! ? — protecting ellipses first."""
    guard = text.replace("...", _ELL3).replace(_ELLIPSIS_UNICODE, _ELL1)
    parts = _SENT_SPLIT.split(guard)
    out = []
    for p in parts:
        s = p.replace(_ELL3, "...").replace(_ELL1, _ELLIPSIS_UNICODE).strip()
        if s:
            out.append(s)
    return out


def parse_sections(text: str) -> list[tuple[str, str]]:
    """Return [(section_name, body_text), ...]. Body is dialogue with quotes stripped.

    Lines before the first label go under section ''. Markdown headings (#, >) and the
    common 'Script dialogue' preamble line are ignored.
    """
    sections: list[tuple[str, list[str]]] = []
    current = ""
    buf: list[str] = []

    def flush():
        if buf:
            sections.append((current, " ".join(buf)))

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith(">"):
            continue
        low = line.lower()
        if low.startswith("title:") or low in {"script dialogue", "script", "vo", "voiceover"}:
            continue
        if is_section_label(line):
            flush()
            current = line.strip().strip(":").strip()
            buf = []
            continue
        # strip wrapping quotes (straight or smart) from dialogue lines
        line = line.strip().strip('"').strip("“”").strip()
        if line:
            buf.append(line)
    flush()
    return [(name, body) for name, body in sections if body.strip()]


def pack_chunks(sentences: list[str]) -> list[str]:
    """Greedily pack whole sentences up to MAX_WORDS; never split a sentence.

    A lone sentence longer than MAX_WORDS becomes its own chunk.
    """
    chunks: list[str] = []
    cur: list[str] = []
    cur_words = 0
    for sent in sentences:
        w = word_count(sent)
        if cur and cur_words + w > MAX_WORDS:
            chunks.append(" ".join(cur))
            cur, cur_words = [], 0
        cur.append(sent)
        cur_words += w
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def recommend_duration(words: int) -> int:
    return max(DUR_MIN, min(DUR_MAX, math.ceil(words / WORDS_PER_SEC)))


def build_plan(text: str, title: str, source: str) -> dict:
    chunks_out = []
    cid = 0
    for section, body in parse_sections(text):
        for chunk_text in pack_chunks(split_sentences(body)):
            cid += 1
            words = word_count(chunk_text)
            chunks_out.append({
                "id": cid,
                "section": section,
                "text": chunk_text,
                "word_count": words,
                "recommended_duration_s": recommend_duration(words),
                "shot_type": "",   # fill in when authoring the clip prompt
                "pose": "",
                "b_roll": "",      # e.g. "grandson OTSS", "phone-ui", "music"
            })
    return {
        "title": title,
        "source": source,
        "total_chunks": len(chunks_out),
        "total_words": sum(c["word_count"] for c in chunks_out),
        "total_duration_s": sum(c["recommended_duration_s"] for c in chunks_out),
        "chunks": chunks_out,
    }


def render_vo_script(plan: dict) -> str:
    lines = [f"# {plan['title']} - VO Script (chunked for asset generation)", ""]
    lines.append(f"> {plan['total_chunks']} chunks - {plan['total_words']} words - "
                 f"~{plan['total_duration_s']}s of A-roll. Generated by tools/chunk_script.py.")
    lines.append("> One chunk = one extracted first-frame image (img-N) + one A-roll Clip N.")
    lines.append("")
    lines.append("| # | Section | Dialogue | Words | Dur (s) | B-roll cue |")
    lines.append("|---|---------|----------|-------|---------|------------|")
    for c in plan["chunks"]:
        dialogue = c["text"].replace("|", "\\|")
        broll = c["b_roll"] or "-"
        lines.append(f"| {c['id']} | {c['section']} | {dialogue} | {c['word_count']} | "
                     f"{c['recommended_duration_s']} | {broll} |")
    lines.append("")
    lines.append("## VO (numbered, in order)")
    for c in plan["chunks"]:
        cue = f"  -> **B-roll: {c['b_roll']}**" if c["b_roll"] else ""
        lines.append(f"{c['id']}. {c['text']}{cue}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Chunk a VO script into Kling-sized beats")
    ap.add_argument("script", type=Path, help="script file (.md/.txt) with the VO dialogue")
    ap.add_argument("--out", type=Path, help="write the chunk plan JSON here (else stdout)")
    ap.add_argument("--vo-script", type=Path, dest="vo_script",
                    help="also write a human vo-script.md chunk table here")
    ap.add_argument("--title", help="video title (default: derived from the filename)")
    args = ap.parse_args()

    if not args.script.exists():
        sys.exit(f"script not found: {args.script}")
    text = args.script.read_text(encoding="utf-8")
    title = args.title or args.script.stem.replace("-", " ").replace("_", " ").title()
    try:
        source = str(args.script.resolve().relative_to(PROJECT_ROOT).as_posix())
    except ValueError:
        source = str(args.script.resolve())

    plan = build_plan(text, title, source)
    if not plan["chunks"]:
        sys.exit("no dialogue found - is the script empty or all section labels?")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {plan['total_chunks']} chunks -> {args.out}")
    else:
        print(json.dumps(plan, indent=2, ensure_ascii=False))

    if args.vo_script:
        args.vo_script.parent.mkdir(parents=True, exist_ok=True)
        args.vo_script.write_text(render_vo_script(plan), encoding="utf-8")
        print(f"wrote vo-script -> {args.vo_script}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
