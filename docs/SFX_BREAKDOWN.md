# SFX Breakdown: Analyzing, Trimming, and Classifying Sound Effects

Reference notes on how to programmatically analyze SFX/audio files — for cleaning up
dead air and multi-effect files, and for telling apart same-named SFX that are
actually different in character. Written for this repo's pipeline (`tools/resolve_sfx.py`,
`tools/mix_audio.py`) but the concepts apply to any sound library.

## Section 1 — Detecting silence & splitting multi-SFX files

### What's assessable in an audio file

| Data | What it tells you | How you get it |
|---|---|---|
| Amplitude / RMS energy | Loudness over time (windowed, e.g. 20–50ms hops) | `librosa.feature.rms`, or raw sample math |
| Peak vs RMS (crest factor) | Punchy/transient sound vs sustained tone | max(abs(samples)) vs RMS in a window |
| dBFS | Log-scaled loudness — the natural unit for a silence threshold | `20*log10(rms / full_scale)` |
| Integrated loudness (LUFS) | Perceptual loudness standard, used for normalizing level, not detecting silence | ffmpeg `loudnorm` filter (already used in `tools/mix_audio.py`) |
| Zero-crossing rate | Near-zero + low RMS = strong silence signal (vs. low hum) | `librosa.feature.zero_crossing_rate` |
| Onsets/transients | Where a new sound starts — key signal for "multiple SFX in one file" | `librosa.onset.onset_detect` |
| Spectral centroid/rolloff/flatness | Timbre — useful for tagging, not needed for silence/splitting | `librosa.feature.spectral_*` |
| Duration/sample rate/channels | Metadata to convert time↔samples for cutting | `ffprobe` |

### How silence detection works

1. Slice the waveform into short windows (20–50ms, overlapping).
2. Compute RMS per window, convert to dB.
3. Threshold: anything below, say, -40dBFS is "silent."
4. Require the silent run to last a minimum gap (e.g. 150–300ms) before calling it a
   real gap — a single quiet window mid-decay isn't a cut point, it's just reverb
   tail.

Two ways to run this, both available in this repo's stack:

- **Python**: `librosa.effects.trim(y, top_db=40)` — one call, trims leading/trailing
  silence and hands back the sample indices it cut.
- **No-code CLI**: `ffmpeg -i in.mp3 -af silencedetect=noise=-40dB:d=0.2 -f null -` —
  prints `silence_start`/`silence_end` timestamps to stderr.

### Approach: leading dead air + multiple SFX stitched into one file

1. **Detect** — run RMS/dB windowing (or ffmpeg `silencedetect`) across the whole
   file to get a list of `(start, end, silent?)` segments.
2. **Trim edges** — drop leading/trailing silent segments, leaving a small pad
   (~20–50ms) so the effect doesn't sound clipped at the front.
3. **Split interior** — if there are ≥2 non-silent segments separated by a silence
   run past the gap threshold, that's a multi-SFX file. Cut at the gap midpoint (or
   gap-start + small pad) and export each chunk separately.
4. **Filter false positives** — require each segment to be longer than some minimum
   (e.g. 50ms) and, ideally, have a detected onset near its start. This stops a
   click or noise-floor blip from becoming a spurious split.
5. **Normalize after cutting** — once segments are isolated, loudness-normalize each
   one so they're consistent in level before placement (ffmpeg `loudnorm`).
6. **Threshold isn't universal** — clean library SFX behave fine at a fixed
   -40dBFS; noisy downloads may need a relative threshold (N dB below that file's
   own peak) instead of an absolute one.

### Where this plugs into this repo's pipeline

`tools/resolve_sfx.py` resolves a query to a file path with zero trimming, and
`tools/mix_audio.py` places whole SFX files at timestamps and normalizes the final
mix, but never inspects an SFX file's internal silence. A trim/split preprocessing
step would sit between the two: resolve → trim/split → mix.

## Section 2 — Distinguishing same-named SFX by character (professional sound design)

Two files both named `impact.wav` are trivially distinguishable once the waveform is
measured — the filename tells you almost nothing; the signal tells you nearly
everything.

### Tier 1: DSP features (librosa/numpy — already installed here)

| Feature | What it encodes | Deep cinematic impact | Fast dry thud |
|---|---|---|---|
| Sub-band energy ratio (energy below ~120–200Hz ÷ total) | "Depth" — sub-bass body | High (0.4+) — chest-punch trailer boom at 30–80Hz | Low — energy sits in low-mids (200–800Hz) |
| Spectral centroid | Brightness / perceived weight | Low centroid (dark) | Mid/high centroid |
| Attack time (silence → peak) | Punch vs swell | Near-instant, or preceded by a riser | Near-instant |
| Decay / tail length (peak → -40dB) | Cinematic "size" — reverb/sub tail | Long: 1.5–4s tail | Short: <300ms, dry |
| Duration | Overall gesture size | 2–5s | 0.2–0.8s |
| Crest factor (peak − RMS) | Transient sharpness | Moderate (tail raises RMS) | High (all transient) |

Whooshes separate the same way, plus:

- **Envelope shape**: a whoosh is a rise-then-fall RMS curve (crescendo into a peak,
  often ending on a hit); an impact is a spike-then-decay. This also tells you the
  **sync point** — a cinematic whoosh syncs at its peak, not its start, which is why
  untrimmed whooshes land late when placed naively.
- **Spectral flux over time**: a "deep cinematic whoosh" shows a slow upward
  pitch/energy sweep with heavy low-frequency content and a long airy tail; a
  "simple UI whoosh" is a short broadband noise burst with a high centroid and no
  sub content.
- **Spectral flatness**: distinguishes noisy whooshes (air, flat spectrum) from
  tonal ones (braams, risers with a pitch).

A heuristic profile like `{sub_ratio: 0.47, centroid_hz: 380, attack_ms: 8,
tail_ms: 2600, duration_s: 3.1, envelope: "spike-decay"}` is "deep cinematic impact,
trailer-grade" regardless of filename.

### Tier 2: ML / embedding approaches (external installs)

- **CLAP** (`pip install laion-clap`) — embeds audio and text into the same vector
  space. Score any SFX against prompts like `"deep cinematic sub-bass impact with
  long reverb tail"` vs `"short dry percussive thud"`; cosine similarity picks the
  winner. Can auto-tag an entire library with genre-relevant descriptors ("trailer
  riser," "soft emotional swell," "comedic pop").
- **PANNs / YAMNet** (`pip install panns-inference`, or TF Hub) — general-purpose
  AudioSet tagging (527 classes). Coarser than CLAP for sound-design nuance, good
  for sanity-checking category.
- **Embedding nearest-neighbor search** — embed a hand-picked reference set ("this
  is my canonical deep trailer impact," "this is my canonical fast thud"), then
  classify new files by nearest neighbor. Matches your taste, not a generic
  taxonomy.
- **Essentia** (`pip install essentia`) — industrial DSP feature extraction with
  prebuilt high-level mood/timbre models. Heavier install, covers Tier 1 plus
  learned descriptors in one library.
- **pyloudnorm + soundfile** — proper LUFS measurement per file so descriptors
  include true perceived loudness, for matching SFX energy to scene intensity
  consistently.

### Tier 3: Multimodal LLM listening (fits this pipeline with zero new infra)

Gemini accepts raw audio input natively, and this repo already has
`GEMINI_API_KEY` wired in and uses Gemini multimodally elsewhere (video breakdowns
in `breakdown_videos.py`, image QA in `qa_image.py`). Send an SFX file with a prompt
like:

> "Describe this sound effect for a sound designer: attack character, low-end
> depth, tail length, emotional register, and which contexts it suits (cinematic
> trailer / motion graphics UI / comedic UGC / emotional film). Return JSON."

This gives human-quality semantic tags ("ominous sub-heavy braam impact, 3s tail,
suits trailer stings, too heavy for UI motion graphics") with no new
infrastructure. For a library of hundreds of files, this runs once per file.

### Recommended architecture: profile once, match deterministically forever

1. **Profiling pass** — when an SFX enters the library (curated or downloaded), run
   it through: silence trim/split (Section 1) → Tier-1 DSP descriptor → CLAP scores
   against a fixed vocabulary of design terms (deep/bright, fast/slow, dry/tailed,
   cinematic/UI/comedic) → optionally a Gemini semantic description. Store all of it
   alongside the file — `tools/resolve_sfx.py` already maintains a `library.json`
   index; these descriptors belong in exactly that index.
2. **Genre grammar** — a small mapping from project style to required sound
   character: *cinematic trailer* → sub_ratio high, tail long, sync-on-peak;
   *motion-graphics UI* → bright centroid, <400ms, dry, sync-on-attack; *emotional
   film* → soft attack, tonal, low flatness; *UGC ad* → punchy crest factor, short,
   loud. "Give me an impact" then resolves against the grammar, not the filename.
3. **Selection** — a query like "whoosh for a title reveal in a cinematic trailer"
   ranks candidates by descriptor match + CLAP text similarity, and the winner comes
   with its measured sync point so it's placed frame-accurately on the cut.
4. **Verification loop** — after a render, the mixed section can be re-analyzed (did
   the impact's sub actually read over the music? was crest factor preserved after
   loudnorm?) — the audio equivalent of this repo's existing image QA gate
   (`tools/qa_image.py`).

## Status

This is a reference doc only — no pipeline code has been changed. `tools/resolve_sfx.py`
and `tools/mix_audio.py` are referenced above as the natural integration points if
this is ever built, but neither has been modified.
