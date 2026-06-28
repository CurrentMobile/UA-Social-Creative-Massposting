"""Append a per-app CTA end-screen clip to a final render.

The CTA clip may be a different resolution / fps / codec (or have no audio), so both
the main video and the CTA are normalized to 1080x1920 @ 30fps before concatenation
via the ffmpeg concat filter. Output loudness is re-normalized to -14 LUFS.

Usage:
    python tools/append_cta.py <final.mp4> --cta assets/mode-earn/cta/<clip>.mp4 -o <out.mp4>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

W, H, FPS = 1080, 1920, 30


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(json.loads(out.stdout)["format"]["duration"])
    except Exception:  # noqa: BLE001
        sys.exit(f"could not probe duration of {path}")


def has_audio(path: Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    return bool(out.stdout.strip())


def _norm_v(label_in: str, label_out: str) -> str:
    return (
        f"[{label_in}]scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps={FPS},"
        f"format=yuv420p[{label_out}]"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description="Append a CTA clip to a final video")
    ap.add_argument("video", type=Path, help="main final render")
    ap.add_argument("--cta", type=Path, required=True, help="CTA end-screen clip")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--no-normalize", action="store_true", help="skip loudnorm")
    args = ap.parse_args()

    for p in (args.video, args.cta):
        if not p.exists():
            sys.exit(f"not found: {p}")

    main_has_a = has_audio(args.video)
    cta_has_a = has_audio(args.cta)
    cta_dur = probe_duration(args.cta)

    # inputs: 0=main, 1=cta, (2=silent for whichever lacks audio)
    inputs = ["-i", str(args.video), "-i", str(args.cta)]
    parts = [_norm_v("0:v", "v0"), _norm_v("1:v", "v1")]

    # audio for main
    silent_idx = 2
    if main_has_a:
        parts.append("[0:a]aresample=async=1[a0]")
        a0 = "[a0]"
    else:
        inputs += ["-f", "lavfi", "-t", f"{probe_duration(args.video):.3f}",
                   "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
        a0 = f"[{silent_idx}:a]"
        silent_idx += 1

    # audio for cta
    if cta_has_a:
        parts.append("[1:a]aresample=async=1[a1]")
        a1 = "[a1]"
    else:
        inputs += ["-f", "lavfi", "-t", f"{cta_dur:.3f}",
                   "-i", "anullsrc=channel_layout=stereo:sample_rate=48000"]
        a1 = f"[{silent_idx}:a]"
        silent_idx += 1

    parts.append(f"[v0]{a0}[v1]{a1}concat=n=2:v=1:a=1[v][aout]")
    final_a = "[aout]"
    if not args.no_normalize:
        parts.append(f"[aout]loudnorm=I={args.lufs}:TP=-1.0:LRA=11[anorm]")
        final_a = "[anorm]"

    filtergraph = ";".join(parts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", *inputs,
           "-filter_complex", filtergraph,
           "-map", "[v]", "-map", final_a,
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "fast",
           "-c:a", "aac", "-b:a", "192k",
           str(args.output)]

    print(f"Appending CTA: {args.cta.name} -> {args.video.name}")
    print(f"  cta audio: {cta_has_a}   main audio: {main_has_a}   cta dur: {cta_dur:.2f}s")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed ({result.returncode})")
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
