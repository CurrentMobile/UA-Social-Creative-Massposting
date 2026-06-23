# Mode Marketing UA Skills

Skill library for the Mode marketing team — a collection of Claude Code skills for AI-powered creative content production using the [HyperFrames](https://github.com/heygen-com/hyperframes) video framework.

## Overview

This repo provides a Claude Code project wired with 15 HyperFrames skills and integrations for social media creative automation. Skills live under `.agents/skills/` and cover the full pipeline from website capture to rendered video output.

## Skills

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

## Project Structure

```
.
├── CLAUDE.md                  # Agent instructions (WAT framework)
├── .agents/skills/            # All 15 HyperFrames skills
│   ├── hyperframes/           #   Core composition skill
│   ├── website-to-hyperframes/#   URL → video pipeline
│   ├── remotion-to-hyperframes/#  Remotion → HyperFrames migration
│   ├── hyperframes-cli/       #   CLI dev loop
│   ├── hyperframes-media/     #   TTS, transcription, bg removal
│   ├── hyperframes-registry/  #   Block/component registry
│   ├── gsap/                  #   GSAP adapter
│   ├── css-animations/        #   CSS keyframes adapter
│   ├── waapi/                 #   Web Animations API adapter
│   ├── animejs/               #   Anime.js adapter
│   ├── lottie/                #   Lottie adapter
│   ├── three/                 #   Three.js adapter
│   ├── typegpu/               #   WebGPU adapter
│   ├── tailwind/              #   Tailwind CSS patterns
│   └── contribute-catalog/    #   Contribution guide
├── .claude/                   # Claude Code config (settings, skill symlinks)
├── .mcp.json                  # MCP server config (gitignored)
├── .env.example               # API key template
├── run.sh                     # Launch script (sources .env, runs claude)
├── skills-lock.json           # Skill version lock file
├── src/                       # Source code (future use)
└── outputs/                   # Generated outputs (future use)
```

## Setup

1. Clone this repo
2. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```
3. Launch Claude Code with the environment loaded:
   ```bash
   ./run.sh
   ```

## Integrations

| Service | Purpose |
|---------|---------|
| Higgsfield | AI image & video generation |
| Gemini | Google AI models |
| Apify | Web scraping |
| Postiz | Social media scheduling/publishing (via MCP) |
| HeyGen | AI avatar video |

## Architecture

This project follows the **WAT framework** (Workflows, Agents, Tools):
- **Workflows** — Markdown SOPs defining objectives and procedures
- **Agents** — Claude Code as the decision-maker and orchestrator
- **Tools** — Deterministic scripts for execution

See `CLAUDE.md` for full agent instructions.

## Credits

Skills sourced from [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes).

## Codebase Rules

## Using & Contributing (read me first)

This repo is the team's shared source of truth for our Claude Code skills.
Treat `main` as read-only: you pull from it, you don't push straight to it.

### Getting set up
1. Clone the repo and copy `.env.example` → `.env`.
2. Ask the owner for the shared API keys (kept in our password vault — never paste keys into any file or into Slack).
3. Run `./run.sh` to launch Claude Code with the skills loaded.

### Getting the latest version
Run `git pull` before you start working. That's it — you'll have everyone's latest skills.

### Suggesting an improvement
Found a better prompt, a fix, or a new skill? Don't edit `main` directly. Instead:
- In Claude Code, just say: *"Create a branch, commit these changes, and open a pull request."* Claude Code handles the git for you.
- The owner reviews it. If it's good, it gets merged and everyone gets it on their next pull.

### Want a personal tweak just for you?
Keep personal experiments in your own user-level skills folder (`~/.claude/skills`),
NOT by editing the shared files here. That way your version survives every update
and never collides with the team's.

### Please don't
- ❌ Put API keys (or any passwords) in any file.
- ❌ Push directly to `main` — it's protected; use a pull request.
- ❌ Edit `CLAUDE.md`, `run.sh`, `skills-lock.json`, or `.claude/` unless you know what they do.

### Who owns this
@Prodart is the admin and reviewer. Changes get announced in #ad-creatives Slack channel with a link to the GitHub release notes.
