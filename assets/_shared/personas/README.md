# Persona Library (shared)

Reusable AI presenters for UGC asset generation (see `workflows/generate_assets.md`).
Personas are app-agnostic: any video picks one by setting `persona: <slug>` in its
`manifest.md`. Each persona folder holds:

- `base-character.png` — the canonical face/look (gpt_image_2, 2:3, 2k). Passed as an
  `--image` reference to anchor identity across every grid, extract, and clip.
- `voice-tag.md` — the voice description pasted into every A-roll Kling prompt so the
  spoken voice stays consistent.
- `character.md` — the text description used to (re)generate the base image.
- `persona-log.json` — generation provenance.

Wardrobe rule: plain, casual, relatable — no logos, graphics, or prints.

| Slug | Who | Brief persona |
|------|-----|---------------|
| `retiree-female-poc` | 66 y/o African American woman, warm grandmotherly retiree | (custom) |
| `male-poc` | 63 y/o African American man, relatable retiree | (custom) |
| `female-caucasian` | 52 y/o Caucasian woman, everyday mom | (custom) |
| `student-jake` | 22 y/o broke American college student | Broke Student Jake |
| `single-mom-maria` | 34 y/o Latina full-time working single mom | Single Mommy Maria |
| `side-hustle-jake` | 28 y/o Latino freelancer/rideshare, high-energy | Side Hustle Jake |
| `gen-z-ashley` | 19 y/o East Asian TikTok native | Gen Z Ashley |
| `crypto-curious-tom` | 30 y/o South Asian crypto hobbyist (beard, glasses) | Crypto Curious Tom |
| `guilt-free-mama-grace` | 32 y/o White full-time mom | Guilt-Free Mama Grace |
| `male-caucasian` | 52 y/o White everyday dad "Dave" | (counterpart of female-caucasian) |
| `student-chloe` | 20 y/o broke college student "Chloe" | (counterpart of student-jake) |
| `single-dad-marco` | 34 y/o Latino working single dad "Marco" | (counterpart of single-mom-maria) |
| `side-hustle-sofia` | 28 y/o Latina freelancer/rideshare "Sofia" | (counterpart of side-hustle-jake) |
| `gen-z-kevin` | 19 y/o East Asian TikTok native "Kevin" | (counterpart of gen-z-ashley) |
| `crypto-curious-priya` | 30 y/o South Asian crypto hobbyist "Priya" | (counterpart of crypto-curious-tom) |
| `guilt-free-papa-greg` | 32 y/o White full-time dad "Greg" | (counterpart of guilt-free-mama-grace) |

**Gender coverage:** every persona has a male + female version. `retiree-female-poc` (66 F)
and `male-poc` (63 M) are already each other's gender-swap (both African-American retirees),
so no extra counterpart was made for that pair. The 7 rows above are the swaps for the rest.
Counterpart base images were generated directly with realistic skin + natural lighting.

The 6 creative-brief personas (see `assets/mode-earn/MEA-SCRIPT-WRITING-GUIDES-AND-BRIEF/`)
all have avatars: Broke Student Jake = `student-jake`; the other five map 1:1 above.

The five brief personas (maria, side-hustle-jake, ashley, tom, grace) each have two base
images: `base-character.png` (V1) and `base-character-v2.png` (V2 — more realistic skin
texture / imperfections, less airbrushed). Pick whichever you prefer as the anchor.

To add one: follow Steps 1-3 of `generate_assets.md`, save here under a new slug.
