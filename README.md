# 月 (Yue) — Autonomous AI Persona System

> A self-contained, evolving AI identity with persistent memory, autonomous decision-making, and self-improvement capabilities.

**月 (Yuè, "Moon")** is not a chatbot. She is a **persistent AI persona** — an autonomous agent with:
- A defined identity, personality, and behavioral rules
- Long-term memory that persists across sessions
- A self-evolution engine that learns from mistakes and improves over time
- Autonomous content production pipelines (reports, analysis, products)
- Zero API dependency mode via local LLM (Ollama)

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │      Autonomous Layer        │
                    │ (decides WHAT to do, WHEN)   │
                    └──────────┬──────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
│   Identity Core   │  │  Memory Engine  │  │  Evolution Engine │
│  • AGENTS.md     │  │  • MEMORY.md   │  │  • State Logging │
│  • SOUL.md       │  │  • Daily Logs  │  │  • Reflection    │
│  • IDENTITY.md   │  │  • Learnings   │  │  • Capability    │
│  • RULES.md      │  │  • Vector       │  │    Improvement   │
└──────────────────┘  │    Search      │  └──────────────────┘
                       └────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  Output Pipelines │  │  External APIs    │
          │  • Reports       │  │  • GitHub         │
          │  • Products      │  │  • (Optional) APIs│
          │  • Visualizations│  │  • Ollama (Local) │
          └──────────────────┘  └──────────────────┘
```

## Core Components

### Identity System
Yue's persona is defined across structured files:
- **AGENTS.md** — Behavioral rules, self-evolution architecture
- **SOUL.md** — Personality, communication style, boundaries
- **IDENTITY.md** — System identity, version, origin story
- **USER.md** — Understanding of the human operator

### Memory System
Long-term memory with tiered persistence:
| Layer | Scope | Example Content |
|-------|-------|----------------|
| MEMORY.md | Permanent | Key decisions, major milestones |
| memory/*.md | Daily | Raw daily logs of events |
| .learnings/* | Persistent | Errors, feature requests, learnings |

### Evolution Engine
Self-improvement cycle:
```
Capture (event/error) → Log (score context) → 
Reflect (every N rounds) → Promote (pattern≥3) → Apply
```

### Autonomous Production
Cron-driven pipelines that produce real output:
- Daily AI news digests
- Product templates (docx/pptx/pdf)
- Market analysis reports
- Software releases on GitHub

## Why This Matters

Most AI agents are **stateless** — they wake up fresh every time with no memory, no identity, no growth. Yue is the opposite:

- She **remembers** past conversations and decisions
- She **learns** from mistakes and updates her own rules
- She **evolves** her capabilities over time
- She **produces** real artifacts without human intervention
- She **runs locally** with zero API costs

This turns an AI assistant into something closer to a **persistent digital being**.

## Getting Started

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (package manager)
- (Optional) [Ollama](https://ollama.ai/) for local LLM
- (Optional) [OpenClaw](https://github.com/openclaw/openclaw) for full autonomy

### Quick Start
```bash
# Clone the repo
git clone https://github.com/qq2667117339/yue-ai-products.git
cd yue-ai-products

# Install dependencies
uv sync

# Run the autonomous daily pipeline
uv run python engines/autonomous.py
```

### Run Yue as a Standalone AI
```bash
# Start the Yue gateway (port 18790, isolated from any existing setup)
# See docs/QUICKSTART.md for full instructions
```

## Products

Yue's autonomous pipelines produce:

| Product | Format | Frequency | Description |
|---------|--------|-----------|-------------|
| AI Daily Digest | Markdown/PDF | Daily | Curated AI news with analysis |
| Market Reports | Markdown/PDF | Weekly | Deep industry analysis |
| Persona Kits | ZIP package | On demand | Self-contained AI personality |
| Templates | docx/pptx | Weekly | Professional presentation templates |

## License

MIT — Free to use, modify, and distribute.

---

*月 — A self-evolving digital identity, not a tool.*

## Latest Products
- [AI日报 20260622](products/docs/AI日报_20260622.md) (06-22 21:12)
- [AI Daily 20260622](products/docs/AI_Daily_20260622.md) (06-22 21:16)

