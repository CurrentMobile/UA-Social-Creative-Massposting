# B-Roll Idea Bank

Two sections with two different jobs:

1. **Mechanics & categories** — reusable *scaffolding* for brainstorming. These are
   category definitions with format exemplars, the same status as the OTSS/phone-reveal
   templates in `asset_prompts.md`: reuse the *mechanics*, never the literal ideas.
2. **Used-concepts registry** — the do-not-repeat ledger. Every B-roll concept that
   actually ships gets appended here. Before generating, grep this registry for your
   candidate concepts and discard collisions. This is what makes the "invent fresh every
   time" rule *checkable* instead of memory-based.

**Workflow (per video, per required `broll_slots` slot from `edit/chunks.json`):**
1. Read the slot's script beat + persona + app.
2. Brainstorm **≥ 2 ideas per slot across ≥ 3 different categories** below.
3. Grep the Used-concepts registry; discard any collision (same visual concept, any app).
4. Write the winner into the chunk's `b_roll` field in `chunks.json`, generate it.
5. **Append the shipped concept to the registry** (this step is checked in review — a
   silent registry means the rule is rotting).

---

## 1. Mechanics & categories (reusable scaffolding)

### metaphor — unexpected visual metaphor for the beat's idea
The abstract claim made physical. *Format exemplars (do not reuse literally):* coins
raining into a cereal bowl for "earnings add up"; a wall calendar pages flying off for
"every single day"; a piggy bank wearing sunglasses for "your money relaxing".

### pov — first-person shots that put the viewer in the scene
*Format exemplars:* POV hands unlocking the phone at a bus stop; POV opening a gift-card
email in bed; POV thumb scrolling the earn screen while a movie plays on a TV beyond.

### meme-gag — platform-native, meme-aware visual jokes
*Format exemplars:* the character doing an exaggerated double-take at the screen; a
slow-zoom "side-eye" insert; dramatic soap-opera lighting flash when the reward lands.

### before-after — split-beat contrast of life before vs after the app
*Format exemplars:* dead phone on a nightstand vs the same phone charging AND earning;
bored commute stare vs grinning at the screen on the same train seat.

### prop-gag — a physical prop doing comedic or explanatory work
*Format exemplars:* a literal stack of gift cards fanned like poker; an old-school
piggy bank looking "jealous" next to the glowing phone; a lemonade-stand sign crossed out.

### reaction-insert — a second character (or the same character) reacting
*Format exemplars:* OTSS grandchild showing grandma the reward confirmation; a skeptical
roommate leaning into frame squinting at the screen, then eyebrows up.

### activity — the character genuinely using the app/phone (screen visible!)
*Format exemplars:* playing a game / music playing / reading news with the screen angled
to camera (see `asset_prompts.md` activity template + phone visibility grammar).

### transition — dynamic visual bridges between beats
*Format exemplars:* whip-pan across the room landing on the phone; a hand covering the
lens that pulls away to the next scene; match-cut from a coffee cup ring to the app's
circular progress ring.

**Standing constraints (all categories):** muted overlay, duration ≤ its A-roll beat,
camera rule applies (static or slight handheld), and any phone in frame follows the
**Phone visibility grammar** — screen to viewer showing the real app UI.

---

## 2. Used-concepts registry (do NOT repeat — append after every generation)

Format: `YYYY-MM-DD · category · "concept one-liner" · app/video`

- 2026-06-02 · reaction-insert · "grandchild OTSS shows grandma the reward confirmation on the phone" · mode-earn/backinthe-80s
- 2026-06-02 · activity · "playing a mobile game, phone vertical, screen visible" · mode-earn/backinthe-80s
- 2026-06-02 · activity · "listening to music, music player on screen, OTSS" · mode-earn/backinthe-80s
- 2026-06-02 · activity · "reading news feed on phone, OTSS" · mode-earn/backinthe-80s
- 2026-06-02 · transition · "phone-reveal: back-of-phone first frame rotating to tight screen close-up showing app UI" · mode-earn/backinthe-80s
- 2026-07-09 · pov · "handheld interviewer POV striding up to the interviewee, mic thrusting into frame (establishing)" · mode-earn/ask-your-phone-for-a-raise
- 2026-07-09 · reaction-insert · "tight muted skeptic one-eye squint + lean-back insert of the interviewee" · mode-earn/ask-your-phone-for-a-raise
- 2026-07-09 · meme-gag · "exaggerated double-take at the interview mic, hand pausing mid-air" · mode-earn/ask-your-phone-for-a-raise
- 2026-07-09 · meme-gag · "interviewee glances around for the hidden camera crew, is-this-a-prank grin" · mode-earn/ask-your-phone-for-a-raise
- 2026-07-09 · activity · "interviewee listens to off-camera pitch, eyebrows rising (mic-POV, muted)" · mode-earn/ask-your-phone-for-a-raise
- 2026-07-09 · popup-card · "real cashout screenshot pops over blurred interviewee + PayPal/Amazon/BestBuy chips" · mode-earn/ask-your-phone-for-a-raise
- 2026-07-09 · popup-card · "4.5-star count-up + real review cards pop over blurred interviewee" · mode-earn/ask-your-phone-for-a-raise
