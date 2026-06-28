"""Mix background music + sound effects onto a finished video.

- Background music is looped/trimmed to the video length, lowered in level, and
  (by default) sidechain-ducked under the dialogue so speech stays intelligible.
- Sound effects are placed at explicit timestamps.
- The final mix is loudness-normalized to broadcast/social target (-14 LUFS, -1 dBTP).

The video stream is copied untouched (-c:v copy); only audio is rebuilt. This is the
audio companion to video-use's render.py — run it AFTER render.py has produced the
cut+captioned video.

Usage:
    # music ducked under dialogue, normalized
    python tools/mix_audio.py edit/final.mp4 -o edit/final_mixed.mp4 \
        --music assets/music/track.mp3

    # add two SFX at timestamps (seconds), with optional per-clip gain
    python tools/mix_audio.py edit/final.mp4 -o out.mp4 \
        --music assets/music/track.mp3 \
        --sfx "assets/sfx/whoosh.mp3@2.5" --sfx "assets/sfx/ding.mp3@7.0:0.8"

    # SFX only, no music
    python tools/mix_audio.py in.mp4 -o out.mp4 --sfx "assets/sfx/pop.mp3@1.0"
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def probe_duration(video: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(video)],
        capture_output=True, text=True,
    )
    try:
        return float(json.loads(out.stdout)["format"]["duration"])
    except Exception:  # noqa: BLE001
        sys.exit(f"could not probe duration of {video}")


def has_audio_stream(video: Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=index", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True,
    )
    return bool(out.stdout.strip())


def parse_sfx(spec: str) -> tuple[Path, float, float]:
    """'path@time[:gain]' -> (path, time_s, gain)."""
    if "@" not in spec:
        sys.exit(f"--sfx must be 'path@time[:gain]', got: {spec}")
    path_part, time_part = spec.rsplit("@", 1)
    gain = 1.0
    if ":" in time_part:
        time_part, gain_str = time_part.split(":", 1)
        gain = float(gain_str)
    return Path(path_part), float(time_part), gain


def main() -> None:
    ap = argparse.ArgumentParser(description="Mix music + SFX onto a video")
    ap.add_argument("video", type=Path, help="input video (with dialogue audio)")
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--music", type=Path, default=None, help="background music file")
    ap.add_argument("--music-volume", type=float, default=0.18,
                    help="linear gain applied to music before ducking (default 0.18 ~= -15 dB)")
    ap.add_argument("--no-duck", action="store_true",
                    help="do not sidechain-duck music under dialogue")
    ap.add_argument("--sfx", action="append", default=[],
                    help="sound effect as 'path@time[:gain]' (repeatable)")
    ap.add_argument("--lufs", type=float, default=-14.0, help="integrated loudness target")
    ap.add_argument("--no-normalize", action="store_true", help="skip loudnorm pass")
    args = ap.parse_args()

    if not args.video.exists():
        sys.exit(f"video not found: {args.video}")
    duration = probe_duration(args.video)
    has_audio = has_audio_stream(args.video)
    duck = args.music and (not args.no_duck) and has_audio

    sfx_specs = [parse_sfx(s) for s in args.sfx]
    for p, _, _ in sfx_specs:
        if not p.exists():
            sys.exit(f"sfx not found: {p}")
    if args.music and not args.music.exists():
        sys.exit(f"music not found: {args.music}")

    # --- build input list (track ffmpeg stream indices) ---
    inputs: list[list[str]] = [["-i", str(args.video)]]   # index 0
    music_idx = None
    if args.music:
        music_idx = len(inputs)
        inputs.append(["-stream_loop", "-1", "-i", str(args.music)])  # loop music
    sfx_idx: list[int] = []
    for p, _, _ in sfx_specs:
        sfx_idx.append(len(inputs))
        inputs.append(["-i", str(p)])

    # --- build filter graph ---
    parts: list[str] = []
    mix_inputs: list[str] = []

    dia_key = None
    if has_audio:
        if duck:
            parts.append("[0:a]asplit=2[dia_main][dia_key]")
            mix_inputs.append("[dia_main]")
            dia_key = "[dia_key]"
        else:
            mix_inputs.append("[0:a]")

    if args.music:
        parts.append(f"[{music_idx}:a]volume={args.music_volume}[mvol]")
        music_label = "[mvol]"
        if duck:
            parts.append(
                f"[mvol]{dia_key}sidechaincompress="
                f"threshold=0.03:ratio=8:attack=20:release=300:makeup=1[mduck]"
            )
            music_label = "[mduck]"
        mix_inputs.append(music_label)

    for n, (idx, (_, t, gain)) in enumerate(zip(sfx_idx, sfx_specs)):
        delay_ms = max(0, int(round(t * 1000)))
        parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms},volume={gain}[sfx{n}]")
        mix_inputs.append(f"[sfx{n}]")

    if not mix_inputs:
        sys.exit("nothing to mix: input has no audio and no --music/--sfx given")

    if len(mix_inputs) > 1:
        parts.append(
            f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:"
            f"normalize=0:dropout_transition=0[premix]"
        )
        final_a = "[premix]"
    else:
        # single source — copy through a trivial filter so it gets a label
        parts.append(f"{mix_inputs[0]}anull[premix]")
        final_a = "[premix]"

    if not args.no_normalize:
        parts.append(f"{final_a}loudnorm=I={args.lufs}:TP=-1.0:LRA=11[outa]")
        final_a = "[outa]"

    filtergraph = ";".join(parts)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y"]
    for grp in inputs:
        cmd += grp
    cmd += [
        "-filter_complex", filtergraph,
        "-map", "0:v", "-map", final_a,
        "-t", f"{duration:.3f}",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(args.output),
    ]

    print("Mixing audio:")
    print(f"  duration : {duration:.2f}s   dialogue audio: {has_audio}   duck: {bool(duck)}")
    if args.music:
        print(f"  music    : {args.music}  (vol {args.music_volume})")
    for p, t, g in sfx_specs:
        print(f"  sfx      : {p.name} @ {t}s (gain {g})")
    print(f"  filter   : {filtergraph}\n")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed ({result.returncode})")
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
