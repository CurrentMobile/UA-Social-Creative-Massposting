"""fix_editable_timeline_audio.py — patch legacy editable-timeline HTML for Studio audio.

One-off maintenance fix (see build_editable_timeline.py's header for the full story): every
editable-timeline project built before 2026-07-10 carries A-roll/endscreen dialogue on an UNMUTED
`<video data-has-audio="true">` with no separate `<audio>` element. Per the HyperFrames media
contract (hyperframes-core skill, variables-and-media.md), Studio's interactive scrubber only
drives sound through `<audio>` elements — so these projects preview silently even though
`hyperframes render` (which reads `data-has-audio` as a render-time hint) still baked audio into
the delivered MP4s. This patches the ALREADY-GENERATED index.html in place: mute the video, flip
data-has-audio to false, and insert a sibling <audio> at the identical timing on a fresh,
never-colliding track. Idempotent — a video already `muted` is left untouched.

Usage:
    .venv\\Scripts\\python.exe tools\\fix_editable_timeline_audio.py                 # scan assets/
    .venv\\Scripts\\python.exe tools\\fix_editable_timeline_audio.py <path-to-index.html>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Matches a self-contained <video ...></video> tag (single line, as emitted by
# build_editable_timeline.py) that still carries its own audio unmuted.
VIDEO_RE = re.compile(
    r'<video\b(?P<attrs>[^>]*\bdata-has-audio="true"[^>]*)></video>',
)
TRACK_RE = re.compile(r'data-track-index="(\d+)"')


def get_attr(attrs: str, name: str) -> str | None:
    # (?<=\s) rather than \b: a bare \b also matches inside Studio-injected `data-hf-id="..."`
    # (the '-' before 'id' is a word boundary too), stealing the plain `id=` lookup.
    m = re.search(rf'(?<=\s){name}="([^"]*)"', attrs)
    return m.group(1) if m else None


def fix_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    existing_tracks = [int(n) for n in TRACK_RE.findall(text)]
    next_track = (max(existing_tracks) + 1) if existing_tracks else 0

    fixed = 0

    def repl(m: re.Match) -> str:
        nonlocal next_track, fixed
        attrs = m.group("attrs")
        if re.search(r'(^|\s)muted(\s|=|$)', attrs):
            return m.group(0)  # already muted -> already fixed (or intentionally silent), skip
        clip_id = get_attr(attrs, "id") or f"video{fixed}"
        start = get_attr(attrs, "data-start") or "0"
        media_start = get_attr(attrs, "data-media-start")
        duration = get_attr(attrs, "data-duration") or "0"
        src = get_attr(attrs, "src")
        if not src:
            return m.group(0)  # can't pair audio without a source

        new_attrs = attrs.replace('data-has-audio="true"', 'data-has-audio="false"')
        new_attrs = new_attrs.rstrip() + " muted"
        new_video = f"<video{new_attrs}></video>"

        media_start_attr = f' data-media-start="{media_start}"' if media_start is not None else ""
        audio_tag = (
            f'\n      <audio class="clip" id="dlg-{clip_id}" data-start="{start}"'
            f'{media_start_attr} data-duration="{duration}" data-track-index="{next_track}" '
            f'src="{src}" data-volume="1"></audio>'
        )
        next_track += 1
        fixed += 1
        return new_video + audio_tag

    new_text = VIDEO_RE.sub(repl, text)
    if fixed:
        path.write_text(new_text, encoding="utf-8")
    return fixed


def main() -> int:
    args = sys.argv[1:]
    if args:
        targets = [Path(a) for a in args]
    else:
        targets = sorted((PROJECT_ROOT / "assets").glob("**/editable-timeline*/index.html"))

    if not targets:
        print("no editable-timeline index.html files found")
        return 0

    total = 0
    for t in targets:
        if not t.exists():
            print(f"[skip] not found: {t}")
            continue
        n = fix_file(t)
        rel = t.relative_to(PROJECT_ROOT) if t.is_relative_to(PROJECT_ROOT) else t
        print(f"{'[fixed]' if n else '[ok]   '} {rel}  ({n} video(s) muted + paired with audio)")
        total += n

    print(f"\n{total} video element(s) fixed across {len(targets)} project(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
