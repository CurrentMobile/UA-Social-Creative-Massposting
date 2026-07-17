"""Chunk a VO script into Kling-sized dialogue beats for asset generation.

Step 4 of the asset-generation SOP (see workflows/generate_assets.md). Splits the
spoken VO into 10-20 word chunks that NEVER cut a sentence, then recommends a Kling
clip duration per chunk from its word count. Each chunk becomes one extracted first-
frame image (img-<n>) and one A-roll clip (Clip <n>).

Section labels (all-caps lines like HOOK / PROBLEM / SOLUTION / HOW IT WORKS / RESULT
/ CTA) are treated as beat boundaries and carried as metadata, not spoken. Chunking
never merges across sections, so the narrative beats stay intact.

FORMAT ANATOMIES (--anatomy formats/_shared/anatomies/<id>.yaml) extend this beyond
the classic six-beat UGC script. Four chunking modes:
  - sections (default, no --anatomy needed): the behavior described above.
  - turns:    speaker-tagged lines ("INTERVIEWER: ...", "PERSON1: ..."); each turn is
              a beat boundary and chunks carry a `speaker` field. A bare marker line
              (e.g. PAUSE) becomes an edit event, not VO.
  - items:    ranked-list labels ("RANK 5:" ... "RANK 1:"); chunks carry `item_index`.
  - none:     no VO at all (lo-fi / statics) — emits an overlay-plan.json of on-screen
              text cards with reading-speed durations instead of chunks.

Duration heuristic: recommended_duration_s = clamp(ceil(words / wps), 3, 15) with
wps from the anatomy (default 2.7 — grandmotherly "slow, deliberate pacing").

Every chunked plan also carries `broll_slots` — the B-roll quota plan (standing rule
1b in generate_assets.md): which chunks REQUIRE a pattern-interrupt cutaway.

Usage:
    python tools/chunk_script.py <script.md|.txt>
    python tools/chunk_script.py scripts/source.md --out edit/chunks.json \
        --vo-script scripts/vo-script.md --title "ExtraIncomeForRetirees"
    python tools/chunk_script.py scripts/source.md \
        --anatomy formats/_shared/anatomies/interview-turns.yaml --out edit/chunks.json

With no --out the plan JSON is printed to stdout.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DUR_MIN, DUR_MAX = 3, 15

DEFAULT_ANATOMY = {
    "id": "hook-problem-solution",
    "vo": True,
    "chunking": {"mode": "sections", "wps": 2.7, "min_words": 10, "max_words": 20},
}

# Sentence-final punctuation, but NOT ellipsis, which the scripts use mid-line.
# Ellipses are swapped for sentinels before splitting, then restored, so a mid-line
# "scam... but" or "extra ... you" stays one sentence.
_ELL3 = "\x00ELL3\x00"
_ELL1 = "\x00ELL1\x00"
_ELLIPSIS_UNICODE = "…"
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
_SPEAKER_RE = re.compile(r"^([A-Z][A-Z0-9_]{1,15}):\s+(\S.*)$")


def load_anatomy(path: Path | None) -> dict:
    if not path:
        return DEFAULT_ANATOMY
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        sys.exit("--anatomy needs pyyaml: .venv\\Scripts\\python.exe -m pip install pyyaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data.setdefault("chunking", {})
    for k, v in DEFAULT_ANATOMY["chunking"].items():
        data["chunking"].setdefault(k, v)
    return data


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


def iter_script_lines(text: str):
    """Yield cleaned dialogue-relevant lines (markdown noise stripped)."""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#") or line.startswith(">"):
            continue
        low = line.lower()
        if low.startswith("title:") or low in {"script dialogue", "script", "vo", "voiceover"}:
            continue
        yield line


def strip_quotes(line: str) -> str:
    return line.strip().strip('"').strip("“”").strip()


def parse_sections(text: str) -> list[tuple[str, str]]:
    """Return [(section_name, body_text), ...] for sections mode."""
    sections: list[tuple[str, str]] = []
    current = ""
    buf: list[str] = []

    def flush():
        if buf:
            sections.append((current, " ".join(buf)))

    for line in iter_script_lines(text):
        if is_section_label(line):
            flush()
            current = line.strip().strip(":").strip()
            buf = []
            continue
        line = strip_quotes(line)
        if line:
            buf.append(line)
    flush()
    return [(name, body) for name, body in sections if body.strip()]


def pack_chunks(sentences: list[str], max_words: int) -> list[str]:
    """Greedily pack whole sentences up to max_words; never split a sentence."""
    chunks: list[str] = []
    cur: list[str] = []
    cur_words = 0
    for sent in sentences:
        w = word_count(sent)
        if cur and cur_words + w > max_words:
            chunks.append(" ".join(cur))
            cur, cur_words = [], 0
        cur.append(sent)
        cur_words += w
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def recommend_duration(words: int, wps: float) -> int:
    return max(DUR_MIN, min(DUR_MAX, math.ceil(words / wps)))


def make_chunk(cid: int, section: str, text: str, wps: float, **extra) -> dict:
    words = word_count(text)
    return {
        "id": cid,
        "section": section,
        "text": text,
        "word_count": words,
        "recommended_duration_s": recommend_duration(words, wps),
        "shot_type": "",   # fill in when authoring the clip prompt
        "pose": "",
        "b_roll": "",      # e.g. "grandson OTSS", "phone-ui", "music"
        **extra,
    }


def build_broll_slots(chunks: list[dict]) -> list[dict]:
    """Mark which chunks REQUIRE a B-roll cutaway (the pattern-interruption quota).

    Standing rule (workflows/generate_assets.md, rule 1b): minimum 1 B-roll per script
    beat/section, target a cutaway every 3-5s of A-roll:
        required >= max(n_sections, ceil(total_duration / 5) - n_chunks, n_chunks - 1)
    capped at n_chunks. Required chunks are chosen as: first chunk of each section
    first, then the longest remaining chunks (long clips need interruption most).
    """
    n_chunks = len(chunks)
    if not n_chunks:
        return []
    sections: list[str] = []
    for c in chunks:
        if c["section"] not in sections:
            sections.append(c["section"])
    total_dur = sum(c["recommended_duration_s"] for c in chunks)
    target = max(len(sections), math.ceil(total_dur / 5) - n_chunks, n_chunks - 1)
    target = min(target, n_chunks)

    required_ids: list[int] = []
    for s in sections:
        required_ids.append(next(c["id"] for c in chunks if c["section"] == s))
    for c in sorted((c for c in chunks if c["id"] not in required_ids),
                    key=lambda c: -c["recommended_duration_s"]):
        if len(required_ids) >= target:
            break
        required_ids.append(c["id"])

    return [{
        "slot": i + 1,
        "chunk_id": c["id"],
        "section": c["section"],
        "window_s": [0, c["recommended_duration_s"]],
        "required": c["id"] in required_ids,
        "idea": "",  # fill with the chosen concept (mirror it into the chunk's b_roll)
    } for i, c in enumerate(chunks)]


# --------------------------------------------------------------------------- #
# Mode builders
# --------------------------------------------------------------------------- #
def build_sections(text: str, cfg: dict) -> tuple[list[dict], list[dict]]:
    chunks: list[dict] = []
    cid = 0
    for section, body in parse_sections(text):
        for chunk_text in pack_chunks(split_sentences(body), cfg["max_words"]):
            cid += 1
            chunks.append(make_chunk(cid, section, chunk_text, cfg["wps"]))
    return chunks, []


def build_turns(text: str, anatomy: dict) -> tuple[list[dict], list[dict]]:
    cfg = anatomy["chunking"]
    markers = {m["label"]: m.get("event", m["label"].lower())
               for m in anatomy.get("markers", [])}
    known_speakers = set(anatomy.get("speakers", []))
    chunks: list[dict] = []
    events: list[dict] = []
    section = ""
    cid = 0
    cur_speaker: str | None = None
    cur_text: list[str] = []

    def flush_turn():
        nonlocal cid, cur_speaker, cur_text
        if cur_speaker and cur_text:
            for chunk_text in pack_chunks(split_sentences(" ".join(cur_text)), cfg["max_words"]):
                cid += 1
                chunks.append(make_chunk(cid, section, chunk_text, cfg["wps"],
                                         speaker=cur_speaker))
        cur_speaker, cur_text = None, []

    for line in iter_script_lines(text):
        bare = line.strip().strip(":").strip()
        if bare in markers:
            flush_turn()
            events.append({"after_chunk": cid, "event": markers[bare]})
            continue
        m = _SPEAKER_RE.match(line)
        if m and (not known_speakers or m.group(1) in known_speakers or
                  re.fullmatch(r"(PERSON|GUEST|SPEAKER)\d*", m.group(1))):
            flush_turn()
            cur_speaker = m.group(1)
            cur_text = [strip_quotes(m.group(2))]
            continue
        if is_section_label(line):
            flush_turn()
            section = bare
            continue
        # continuation of the current turn (or unattributed narration)
        if cur_speaker:
            cur_text.append(strip_quotes(line))
        else:
            cur_speaker = anatomy.get("speakers", ["HOST"])[0]
            cur_text = [strip_quotes(line)]
    flush_turn()
    return chunks, events


def build_items(text: str, anatomy: dict) -> tuple[list[dict], list[dict]]:
    cfg = anatomy["chunking"]
    item_re = re.compile(anatomy.get("item_pattern", r"^(?:RANK|ITEM|#)\s*(\d+)"), re.IGNORECASE)
    chunks: list[dict] = []
    section = ""
    item_index: int | None = None
    buf: list[str] = []
    cid = 0

    def flush():
        nonlocal cid, buf
        if buf:
            extra = {"item_index": item_index} if item_index is not None else {}
            for chunk_text in pack_chunks(split_sentences(" ".join(buf)), cfg["max_words"]):
                cid += 1
                chunks.append(make_chunk(cid, section, chunk_text, cfg["wps"], **extra))
        buf = []

    for line in iter_script_lines(text):
        m = item_re.match(line)
        if m:
            flush()
            item_index = int(m.group(1))
            section = f"RANK {item_index}"
            rest = strip_quotes(line[m.end():].lstrip(":").strip())
            if rest:
                buf.append(rest)
            continue
        if is_section_label(line):
            flush()
            item_index = None
            section = line.strip().strip(":").strip()
            continue
        buf.append(strip_quotes(line))
    flush()
    return chunks, []


def build_overlay_plan(text: str, anatomy: dict, title: str, source: str) -> dict:
    """No-VO mode: every dialogue line becomes an on-screen text card."""
    cfg = anatomy["chunking"]
    wps = float(cfg.get("reading_wps", 3.3))
    lo = float(cfg.get("min_card_s", 2.0))
    hi = float(cfg.get("max_card_s", 7.0))
    cards: list[dict] = []
    section = ""
    for line in iter_script_lines(text):
        if is_section_label(line):
            section = line.strip().strip(":").strip()
            continue
        card_text = strip_quotes(line)
        if not card_text:
            continue
        dur = round(max(lo, min(hi, word_count(card_text) / wps + 1.0)), 1)
        cards.append({"id": len(cards) + 1, "section": section,
                      "text": card_text, "duration_s": dur})
    return {
        "title": title,
        "source": source,
        "anatomy": anatomy.get("id", "no-vo-overlay"),
        "vo": False,
        "total_cards": len(cards),
        "total_duration_s": round(sum(c["duration_s"] for c in cards), 1),
        "cards": cards,
    }


def build_plan(text: str, title: str, source: str, anatomy: dict) -> dict:
    mode = anatomy["chunking"]["mode"]
    if mode == "none":
        return build_overlay_plan(text, anatomy, title, source)
    if mode == "turns":
        chunks, events = build_turns(text, anatomy)
    elif mode == "items":
        chunks, events = build_items(text, anatomy)
    else:
        chunks, events = build_sections(text, anatomy["chunking"])
    broll_slots = build_broll_slots(chunks)
    plan = {
        "title": title,
        "source": source,
        "anatomy": anatomy.get("id", "hook-problem-solution"),
        "vo": anatomy.get("vo", True),
        "total_chunks": len(chunks),
        "total_words": sum(c["word_count"] for c in chunks),
        "total_duration_s": sum(c["recommended_duration_s"] for c in chunks),
        "broll_required": sum(1 for s in broll_slots if s["required"]),
        "chunks": chunks,
        "broll_slots": broll_slots,
    }
    if events:
        plan["edit_events"] = events
    return plan


def render_vo_script(plan: dict) -> str:
    if not plan.get("vo", True):
        lines = [f"# {plan['title']} - Overlay Plan (no VO)", ""]
        lines.append(f"> {plan['total_cards']} cards - ~{plan['total_duration_s']}s. "
                     "Generated by tools/chunk_script.py (anatomy: no-vo).")
        lines.append("")
        lines.append("| # | Section | On-screen text | Dur (s) |")
        lines.append("|---|---------|----------------|---------|")
        for c in plan["cards"]:
            lines.append(f"| {c['id']} | {c['section']} | {c['text'].replace('|', chr(92) + '|')} "
                         f"| {c['duration_s']} |")
        lines.append("")
        return "\n".join(lines)

    lines = [f"# {plan['title']} - VO Script (chunked for asset generation)", ""]
    lines.append(f"> {plan['total_chunks']} chunks - {plan['total_words']} words - "
                 f"~{plan['total_duration_s']}s of A-roll. Generated by tools/chunk_script.py.")
    lines.append("> One chunk = one extracted first-frame image (img-N) + one A-roll Clip N.")
    lines.append("")
    required = {s["chunk_id"] for s in plan.get("broll_slots", []) if s.get("required")}
    has_speaker = any(c.get("speaker") for c in plan["chunks"])
    spk_col = " Speaker |" if has_speaker else ""
    lines.append(f"| # | Section |{spk_col} Dialogue | Words | Dur (s) | B-roll cue |")
    lines.append(f"|---|---------|{'---------|' if has_speaker else ''}----------|-------|---------|------------|")
    for c in plan["chunks"]:
        dialogue = c["text"].replace("|", "\\|")
        broll = c["b_roll"] or ("**REQUIRED — fill me**" if c["id"] in required else "-")
        spk = f" {c.get('speaker', '')} |" if has_speaker else ""
        lines.append(f"| {c['id']} | {c['section']} |{spk} {dialogue} | {c['word_count']} | "
                     f"{c['recommended_duration_s']} | {broll} |")
    lines.append("")
    lines.append("## VO (numbered, in order)")
    for c in plan["chunks"]:
        cue = f"  -> **B-roll: {c['b_roll']}**" if c["b_roll"] else ""
        spk = f"[{c['speaker']}] " if c.get("speaker") else ""
        lines.append(f"{c['id']}. {spk}{c['text']}{cue}")
    for e in plan.get("edit_events", []):
        lines.append(f"    ⏸ edit event '{e['event']}' after chunk {e['after_chunk']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Chunk a VO script into Kling-sized beats")
    ap.add_argument("script", type=Path, help="script file (.md/.txt) with the VO dialogue")
    ap.add_argument("--anatomy", type=Path,
                    help="script-anatomy YAML (formats/_shared/anatomies/*.yaml); "
                         "default = the classic six-beat sections anatomy")
    ap.add_argument("--out", type=Path, help="write the plan JSON here (else stdout)")
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

    anatomy = load_anatomy(args.anatomy)
    plan = build_plan(text, title, source, anatomy)
    empty = not plan.get("chunks") and not plan.get("cards")
    if empty:
        sys.exit("no dialogue found - is the script empty or all section labels?")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
        n = plan.get("total_chunks", plan.get("total_cards", 0))
        kind = "chunks" if plan.get("vo", True) else "overlay cards"
        print(f"wrote {n} {kind} -> {args.out}")
    else:
        print(json.dumps(plan, indent=2, ensure_ascii=False))

    if args.vo_script:
        args.vo_script.parent.mkdir(parents=True, exist_ok=True)
        args.vo_script.write_text(render_vo_script(plan), encoding="utf-8")
        print(f"wrote vo-script -> {args.vo_script}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
