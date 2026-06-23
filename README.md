# Mode Marketing UA Skills

Mode Marketing's AI creative toolkit for Claude Code — a one-click plugin that turns a plain-English brief into a finished marketing video using the [HyperFrames](https://github.com/heygen-com/hyperframes) framework. Install it once, then just describe the video you want and Claude takes over.

## Quick Start (non-technical — start here)

You need [Claude Code](https://claude.com/claude-code) installed. Then it's three steps, once.

### 1. Install the plugin

In Claude Code, run these two commands:

```
/plugin marketplace add currentmobile/mode-marketing-ua-skills
/plugin install mode-marketing-ua@mode-marketing
```

That's it — all 15 video skills are now loaded. You don't clone anything or touch the code.

### 2. Set your API keys (once)

The skills use a few services (for AI images, voiceover, scraping, publishing). Get the keys from the **team vault** — ask the owner. **Never paste a key into a file you commit, or into Slack.**

Pick whichever is easier for you:

**Option A — set them globally (recommended).** Add these lines to your `~/.zshrc` (or `~/.bashrc`), then open a new terminal:

```bash
export HIGGSFIELD_API_ID="..."
export HIGGSFIELD_API_KEY="..."
export GEMINI_API_KEY="..."
export APIFY_API_KEY="..."
export POSTIZ_API_KEY="..."
export HEYGEN_API_KEY="..."
# Optional, only if you use ElevenLabs voiceover:
# export ELEVENLABS_API_KEY="..."
```

**Option B — per project.** Copy `.env.example` to a file named `.env` in the folder you're working in and fill in the values. The HyperFrames CLI auto-loads `.env` from your current folder.

You only do this once. See `.env.example` for the full list.

### 3. Describe the video — Claude takes over

Open Claude Code in any folder and just say what you want, in plain English. For example:

> *"Make a 15-second vertical ad from getmode.com — punchy, upbeat, with a voiceover. Caption it and get it ready to post."*

Claude picks the right skills, captures the site, writes the script, generates the voiceover, animates the scenes, renders the video, and hands you the file. Ask for changes the same way — *"make the intro snappier"*, *"swap the music"* — and it iterates.

### Getting the latest version

When the team ships new or improved skills, update with:

```
/plugin marketplace update mode-marketing
```

You'll have everyone's latest skills. That's it.

## What's inside (the 15 skills)

### Core Authoring
| Skill | Description |
|-------|-------------|
| **hyperframes** | Create video compositions, animations, title cards, captions, and audio-reactive visuals in HTML |
| **hyperframes-cli** | Dev loop commands: scaffold, lint, preview, render |
| **hyperframes-media** | Asset preprocessing: TTS (Kokoro), transcription (Whisper), background removal |
| **hyperframes-registry** | Install reusable blocks and components from the registry |

### Animation Adapters
| Skill | Description |
|-------|-------------|
| **gsap** | GSAP tweens, timelines, stagger patterns |
| **css-animations** | CSS keyframe animations (shimmer, glow, etc.) |
| **waapi** | Web Animations API patterns |
| **animejs** | Anime.js adapter for seek-driven playback |
| **lottie** | Lottie / dotLottie deterministic playback |

### 3D / GPU
| Skill | Description |
|-------|-------------|
| **three** | Three.js / WebGL scenes and AnimationMixer sync |
| **typegpu** | WebGPU shaders, particle systems, liquid glass |

### Conversion & Ingestion
| Skill | Description |
|-------|-------------|
| **website-to-hyperframes** | Capture a website URL and produce a HyperFrames video (7-step workflow) |
| **remotion-to-hyperframes** | Port Remotion (React) video projects to HyperFrames |

### Supporting
| Skill | Description |
|-------|-------------|
| **tailwind** | Tailwind CSS v4 patterns for compositions |
| **contribute-catalog** | Guide for authoring new registry entries |

## Integrations

| Service | Purpose |
|---------|---------|
| Higgsfield | AI image & video generation |
| Gemini | Google AI models (image descriptions, scripting) |
| Apify | Web scraping |
| Postiz | Social media scheduling/publishing (via MCP) |
| HeyGen | AI avatar video |
| ElevenLabs | Optional voiceover (alternative to built-in Kokoro TTS) |

---

## For developers / contributors

If you're working *on* the skills themselves (rather than just using them), you can run this repo directly.

### Clone + run

```bash
git clone https://github.com/currentmobile/mode-marketing-ua-skills.git
cd mode-marketing-ua-skills
cp .env.example .env   # fill in keys from the team vault
./run.sh               # launches Claude Code with .env loaded
```

`run.sh` sources `.env` so that `${VAR}` references in `.mcp.json` (e.g. `${POSTIZ_API_KEY}`) resolve before launching Claude Code.

### Project structure

```
.
├── .claude-plugin/
│   ├── plugin.json            # Plugin manifest (points skills → .agents/skills)
│   └── marketplace.json       # Marketplace manifest (mode-marketing)
├── CLAUDE.md                  # Agent instructions (WAT framework)
├── .agents/skills/            # All 15 HyperFrames skills (referenced in place)
├── .claude/                   # Claude Code config (settings, skill symlinks)
├── .mcp.json                  # MCP server config (gitignored)
├── .env.example               # API key template
├── run.sh                     # Launch script (sources .env, runs claude)
├── skills-lock.json           # Skill version lock file
├── src/                       # Source code (future use)
└── outputs/                   # Generated outputs (future use)
```

### Architecture

This project follows the **WAT framework** (Workflows, Agents, Tools):
- **Workflows** — Markdown SOPs defining objectives and procedures
- **Agents** — Claude Code as the decision-maker and orchestrator
- **Tools** — Deterministic scripts for execution

See `CLAUDE.md` for full agent instructions.

### Using & contributing — read me first

This repo is the team's shared source of truth for our Claude Code skills. Treat `main` as read-only: you pull from it, you don't push straight to it.

**Suggesting an improvement.** Found a better prompt, a fix, or a new skill? Don't edit `main` directly. In Claude Code, just say: *"Create a branch, commit these changes, and open a pull request."* Claude Code handles the git for you. The owner reviews it; if it's good, it gets merged and everyone gets it on their next `/plugin marketplace update mode-marketing`.

**Want a personal tweak just for you?** Keep personal experiments in your own user-level skills folder (`~/.claude/skills`), NOT by editing the shared files here. That way your version survives every update and never collides with the team's.

**Please don't.**
- ❌ Put API keys (or any passwords) in any committed file.
- ❌ Push directly to `main` — it's protected; use a pull request.
- ❌ Edit `CLAUDE.md`, `run.sh`, `skills-lock.json`, or `.claude/` unless you know what they do.

**Who owns this.** @Prodart is the admin and reviewer. Changes get announced in #ad-creatives Slack channel with a link to the GitHub release notes.

## Credits

Skills sourced from [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes).
