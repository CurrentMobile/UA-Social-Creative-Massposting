"""QC the asset set for a video, then optionally flip its manifest status to 'assets'.

The final gate of the asset-generation SOP (see workflows/generate_assets.md). Reads
the chunk plan (edit/chunks.json from chunk_script.py) and checks that the generated
assets are complete and consistent before the editing module consumes them:

  - per-app persona present  (assets/<app>/persona/base-character.* + voice-tag.md)
  - every chunk N has an extracted first-frame image (img-N.*) and a voiced A-roll
    clip (Clip N.mp4)
  - B-roll clips follow naming (<scene>_b-roll.mp4) and, where a chunk declares a
    b_roll cue, a B-roll clip exists and its duration is <= the A-roll it overlays
  - generation-log.json exists

With --update-manifest and zero missing-required items, flips the manifest frontmatter
status to 'assets'.

Usage:
    python tools/check_assets.py assets/mode-earn/extraincomeforretirees
    python tools/check_assets.py assets/mode-earn/extraincomeforretirees --update-manifest
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMG_EXTS = (".png", ".jpg", ".jpeg", ".webp")
DUR_TOLERANCE = 0.75  # seconds of slack when comparing B-roll vs A-roll length


def probe_duration(path: Path) -> float | None:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True,
        )
        return float(r.stdout.strip())
    except Exception:  # noqa: BLE001
        return None


def first_existing(directory: Path, stem: str, exts: tuple[str, ...]) -> Path | None:
    for ext in exts:
        cand = directory / f"{stem}{ext}"
        if cand.exists():
            return cand
    return None


def load_chunks(videodir: Path, override: Path | None) -> list[dict]:
    path = override or (videodir / "edit" / "chunks.json")
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("chunks", [])
    except Exception:  # noqa: BLE001
        return []


def read_frontmatter_value(manifest: Path, key: str) -> str | None:
    if not manifest.exists():
        return None
    m = re.search(rf"(?m)^{key}:\s*(\S+)", manifest.read_text(encoding="utf-8"))
    return m.group(1).strip() if m else None


def flip_status(manifest: Path, new_status: str) -> bool:
    text = manifest.read_text(encoding="utf-8")
    new = re.sub(r"(?m)^(status:\s*)\S+(.*)$", rf"\g<1>{new_status}\g<2>", text, count=1)
    if new != text:
        manifest.write_text(new, encoding="utf-8")
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="QC a video's generated asset set")
    ap.add_argument("videodir", type=Path, help="assets/<app>/<video> directory")
    ap.add_argument("--chunks", type=Path, help="chunk plan JSON (default: <videodir>/edit/chunks.json)")
    ap.add_argument("--persona", help="persona slug override (default: manifest `persona:` field)")
    ap.add_argument("--update-manifest", action="store_true",
                    help="flip manifest status to 'assets' if nothing required is missing")
    args = ap.parse_args()

    videodir = args.videodir.resolve()
    if not videodir.is_dir():
        sys.exit(f"not a directory: {videodir}")
    app = videodir.parent.name
    manifest = videodir / "manifest.md"
    ai_images = videodir / "ai-images"
    ai_videos = videodir / "ai-videos"

    chunks = load_chunks(videodir, args.chunks)
    missing = 0
    warnings = 0
    print(f"\nQC: {videodir.relative_to(PROJECT_ROOT).as_posix()}  (app: {app})")

    # 1. persona (resolved from the manifest's `persona:` slug -> shared library)
    print("\n[persona]")
    persona_slug = args.persona or read_frontmatter_value(manifest, "persona")
    if not persona_slug:
        print("  [warn] no `persona:` set in manifest (and no --persona) - skipping persona check")
        warnings += 1
    else:
        persona = PROJECT_ROOT / "assets" / "_shared" / "personas" / persona_slug
        base = first_existing(persona, "base-character", IMG_EXTS)
        vtag = persona / "voice-tag.md"
        print(f"  persona: {persona_slug}")
        print(f"  {'[ OK ]' if base else '[MISS]'}   base-character image")
        print(f"  {'[ OK ]' if vtag.exists() else '[MISS]'}   voice-tag.md")
        missing += (base is None) + (not vtag.exists())

    # 2. per-chunk image + clip
    if not chunks:
        print("\n[chunks] no chunk plan found - run chunk_script.py --out edit/chunks.json first")
        warnings += 1
    else:
        print(f"\n[chunks] {len(chunks)} expected")
        clip_dur: dict[int, float | None] = {}
        for c in chunks:
            cid = c["id"]
            img = first_existing(ai_images, f"img-{cid}", IMG_EXTS)
            clip = ai_videos / f"Clip {cid}.mp4"
            has_clip = clip.exists()
            dur = probe_duration(clip) if has_clip else None
            clip_dur[cid] = dur
            durtxt = f"{dur:.1f}s" if dur else "?"
            rec = c.get("recommended_duration_s")
            print(f"  chunk {cid:>2} [{c.get('section','')[:12]:<12}] "
                  f"img:{'OK ' if img else 'MISS'}  clip:{'OK ' if has_clip else 'MISS'} "
                  f"({durtxt} / rec {rec}s)")
            missing += (img is None) + (not has_clip)

        # 3. B-roll cues
        cued = [c for c in chunks if (c.get("b_roll") or "").strip()]
        brolls = sorted(p for p in ai_videos.glob("*_b-roll.*")) if ai_videos.exists() else []
        print(f"\n[b-roll] {len(brolls)} file(s) found; {len(cued)} chunk(s) cue B-roll")
        for p in brolls:
            d = probe_duration(p)
            print(f"  - {p.name}  ({f'{d:.1f}s' if d else '?'})")
        for c in cued:
            cid = c["id"]
            adur = clip_dur.get(cid)
            # heuristic match: a b-roll whose name shares a token with the cue
            cue = (c["b_roll"] or "").lower()
            match = next((p for p in brolls
                          if any(tok in p.name.lower() for tok in re.findall(r"[a-z]+", cue))), None)
            if not match:
                print(f"  [warn] chunk {cid} cues B-roll '{c['b_roll']}' but no matching file")
                warnings += 1
                continue
            bdur = probe_duration(match)
            if adur and bdur and bdur > adur + DUR_TOLERANCE:
                print(f"  [warn] {match.name} ({bdur:.1f}s) longer than Clip {cid} ({adur:.1f}s)")
                warnings += 1

    # 4. log
    log = videodir / "generation-log.json"
    print(f"\n[log] {'[ OK ]' if log.exists() else '[MISS]'}   generation-log.json")
    if not log.exists():
        warnings += 1

    print(f"\nsummary: {missing} required missing, {warnings} warning(s)")
    if args.update_manifest:
        if missing:
            print("not flipping status - required assets are missing.")
        elif manifest.exists() and flip_status(manifest, "assets"):
            print("manifest status -> assets")
        else:
            print("manifest status unchanged.")

    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
