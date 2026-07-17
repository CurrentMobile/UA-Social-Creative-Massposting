# SOP — Street Interview, POV interviewer (`interview` v0.1.0)

Locked step-by-step guide. Learnings → `learnings.md`. <!-- LOCKED --> sections
non-negotiable. `status: draft`, `feasibility: experimental` — expect retries; keep
turns short and QA every interviewee.

---

## 1. Format overview

Man-on-the-street vox pop. <!-- LOCKED --> v1 = `pov-interviewer`: the interviewer is
OFF camera — their voice (and optionally a handheld mic / arm entering frame) leads;
only the interviewee(s) face the camera. <!-- /LOCKED --> Handheld run-and-gun energy,
outdoor/public settings, 1-2 interviewees. `on-camera-interviewer` is an experimental
sub-style (needs a second consistent face) — only attempt if the owner asks and QA holds.

**Personas:** 1-3 (interviewer voice + 1-2 interviewee faces). The interviewer needs no
base image in POV v1 (never seen). **Props:** a handheld mic in frame sells it — add
`assets/_shared/props/handheld-mic.png` (create it; see `_shared/prompts/props.md`).

## 2. Script anatomy

Anatomy: `formats/_shared/anatomies/interview-turns.yaml` (turns mode; speakers
INTERVIEWER / PERSON1 / PERSON2). Chunk:
```
chunk_script.py scripts\source.md --anatomy formats\_shared\anatomies\interview-turns.yaml ^
  --out edit\chunks.json --vo-script scripts\vo-script.md
```
INTERVIEWER turns are heard (POV, off-camera); PERSON turns are the on-camera answers.

**Worked sample (45s, one interviewee + a cameo second):**
```
HOOK
INTERVIEWER: "Quick question — would you let your phone earn money while you scroll?"
PERSON1: "I mean… yeah? Is that a real thing?"
INTERVIEWER: "It's called Mode Earn. Music, games, charging — it all earns points."
PERSON1: "Wait, so I'd get paid for stuff I already do all day?"
INTERVIEWER: "Gift cards. A guy earned twenty-five bucks his first week."
PERSON2: "Okay I'm downloading that right now, hold on."
CTA
INTERVIEWER: "Mode Earn App, Google Play. Go ask your phone for a raise."
```

## 3. Asset generation — step by step (worked prompt per step)

Recipe: `recipes/assets.md`. Stills ALWAYS `gpt_image_2`; A-roll `kling3_0` sound ON.
Inject guardrails. <!-- LOCKED --> Each interviewee has their OWN base reference +
named wardrobe; the interviewer is never rendered in POV v1. <!-- /LOCKED -->

**3.1 Outdoor environment (1-2).** A public street/plaza/campus plate, no crowd faces in
focus (blurred background people are fine).

**3.2 Interviewee base + grids/extracts (per interviewee, per their turns).** If the
interviewee is a library persona, use it; else generate a base first (approve it). Grids
are framed as if shot by a handheld interviewer at arm's length — the mic may intrude
from the bottom/side.

**Worked grid example (PERSON1):**
> A 3x3 grid of the exact same `<PERSON1: age + look>` from the reference, same face +
> `<their exact wardrobe>`, standing on `<the street plate>`, being interviewed —
> reacting to an off-camera question with candid expressions (curious, surprised,
> laughing), a handheld microphone from the reference just entering the lower frame in
> some tiles. Looking toward the off-camera interviewer / into the lens, handheld
> street framing, blurred passersby behind. Identity + wardrobe consistent across all
> nine. Photorealistic, candid, documentary feel.

**3.3 A-roll clips (per PERSON turn).** From that interviewee's extract; they answer the
off-camera question. Handheld street energy (a bit more drift than ugc). Voice tag
verbatim per interviewee. INTERVIEWER lines are audio-only (generate as a voiced clip
over a mic-in-frame / cutaway, or add as a VO track in the edit). Phone shots (an
interviewee pulling out their phone showing the app) follow the phone grammar.

**Worked clip example (PERSON1 answers):**
> Begin on the handheld street shot of `<PERSON1>` from the reference, a mic just in the
> lower frame, reacting to an off-camera question in `<their voice tag verbatim>`,
> genuinely surprised: "Wait, so I'd get paid for stuff I already do all day?" A candid
> laugh and a "no way" head-tilt, glancing to the off-camera interviewer. Handheld drift,
> blurred passersby, wardrobe + lighting consistent — a seamless single take.

**3.4 B-roll (quota per beat).** Street cutaways: a wide establishing shot, a phone
reveal (interviewee showing the app, real UI), a reaction insert. Bank + registry.

**3.5 QC.** <!-- LOCKED --> Gate-D QA checks EACH interviewee's identity + wardrobe
across their turns (per-face drift is the core risk). <!-- /LOCKED --> `check_assets.py`.

## 4. Edit recipe — per scene

Recipe: `recipes/edit.md`.
- Cut between the off-camera question (mic-in-frame / establishing cutaway) and the
  interviewee answer; fast, documentary rhythm.
- Captions label who's talking implicitly via framing; big captions optional for the
  punchy answers.
- ugc polish adapted: hook sticker on the opening question, logo-pop on the app name,
  app-ui-demo / phone reveal on the "it earns points" beat, endscreen CTA on the spoken
  CTA line, music 20% no duck, punch zooms on reactions.

## 5. QA + guardrails hooks

Shot-types: `environment`, `grid`, `extract`, `aroll-clip`, `phone-shot`,
`broll-still`. Critical codes: IDENTITY_DRIFT / WARDROBE_DRIFT PER interviewee across
their turns (the core risk), FLOATING_CHARACTER / SPATIAL_INTERSECTION in busy street
scenes, PHONE_* on reveals. Inject guardrails; fails feed the ledger. If a second
interviewee won't hold consistency, cut to a single interviewee (log it).

## 6. Delivery

Same as ugc-single: `outputs/<APP-CODE>/…_9x16.mp4`, shared-drive sync, seed
`format-examples/interview/`, manifest `format: interview@0.1.0` + sub_format + intake
ref, `check_manifest.py`, propose `draft → beta` after the first validated POV output.
