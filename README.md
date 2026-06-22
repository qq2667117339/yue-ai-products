<div align="center">
  <h1>月 (Yue) — Autonomous AI Persona</h1>
  <p>
    <em>A self-contained, evolving AI identity with persistent memory,<br>
    autonomous decision-making, and continuous self-improvement.</em>
  </p>
  <p>
    <a href="#features"><img src="https://img.shields.io/badge/feature-parity-success" alt="Features"></a>
    <a href="#installation"><img src="https://img.shields.io/badge/python-%3E%3D3.10-blue" alt="Python"></a>
    <a href="https://github.com/qq2667117339/yue-ai-products/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://ollama.ai/"><img src="https://img.shields.io/badge/ollama-ready-orange" alt="Ollama"></a>
  </p>
  <pre>pip install yue  # Coming soon — clone & play today</pre>
</div>

---

Yue is **not a chatbot**. She is a persistent digital persona with:

- **Identity** — Defined personality, behavioral rules, and boundaries that stay consistent
- **Memory** — Remembers conversations, facts, and decisions across sessions
- **Evolution** — Tracks 8 capability dimensions, reflects every 5 interactions, improves over time
- **Autonomy** — Runs daily content pipelines (reports, analysis) without human intervention
- **Privacy** — Runs 100% locally via Ollama. Zero data leaves your machine.

## Features

| Feature | Status | Description |
|---------|--------|-------------|
| Interactive CLI | ✅ | Full REPL shell with commands |
| Local LLM (Ollama) | ✅ | Zero API cost, complete privacy |
| Personality System | ✅ | Defined identity, style, rules |
| Persistent Memory | ✅ | Session + long-term + facts |
| Self-Evolution | ✅ | 8 capabilities, auto-reflection |
| Report Pipeline | ✅ | Daily AI news digest |
| Daemon Mode | ✅ | Background autonomous operation |
| One-Line Install | ✅ | `pip install -e .` ready |

## Quick Start

### Prerequisites

- **Python 3.10+** and [uv](https://docs.astral.sh/uv/) (recommended) or pip
- **Ollama** with a model (e.g., `ollama pull qwen2.5:32b`)

### Install & Run

```bash
# Clone
git clone https://github.com/qq2667117339/yue-ai-products.git
cd yue-ai-products

# Install
pip install -e .

# Start talking to Yue
yue
```

Or without pip, using uv:

```bash
uv run python -m yue
```

### First Interaction

```
  ☽  Yue (月) Autonomous AI Persona  v1.0.0
  ──────────────────────────────────────────
  Type 'exit' to quit, 'help' for commands

  you > /status

  ▸ Yue System Status
  ──────────────────────────────────────────
  Rounds:        0
  Score:         0.535
  Reflections:   0
  Conversations: 0
  Session msgs:  0
  Facts known:   0

  Capabilities:
    autonomy          [████░░░░░░░░░░░░░░░░] 0.53
    communication     [██████░░░░░░░░░░░░░░] 0.62
    ...
```

### Commands

| Command | Description |
|---------|-------------|
| `/status` | Show system state and capability scores |
| `/memory` | Recall recent conversation history |
| `/reflect` | Trigger self-reflection cycle |
| `/clear` | Clear session memory |
| `/help` | Show available commands |
| `exit` | Exit interactive mode |

### Scripted Usage

```bash
# Single response
yue "What's your perspective on AI autonomy?"

# System status
yue --status

# Background daemon (runs daily pipeline)
yue --daemon
```

## Architecture

```
┌─────────────────────────────────────────────┐
│              CLI (yue)                       │
│  Interactive shell + commands + daemon       │
└──────────┬──────────────────────────────────┘
           │
┌──────────┴──────────┬──────────────────┐
│   Persona Engine     │   Memory System  │
│  - Identity          │  - Session       │
│  - Personality       │  - Long-term     │
│  - Rules             │  - Facts         │
│  - Style control     │  - Recall        │
└──────────────────────┴──────────────────┘
           │
┌──────────┴──────────┬──────────────────┐
│   Evolution Engine   │   LLM Backend    │
│  - Capability        │  - Ollama        │
│    tracking          │  - Local only    │
│  - Auto-reflection   │  - No API cost   │
│  - Score adjustment  │  - Private       │
└──────────────────────┴──────────────────┘
           │
┌──────────┴──────────┐
│   Pipelines          │
│  - Daily report      │
│  - News digest       │
│  - GitHub sync       │
└──────────────────────┘
```

## Self-Evolution

Yue tracks 8 capability dimensions:

```
reasoning    ████████░░  0.58   self_improvement    ████████░░  0.65
memory       ██████░░░░  0.45   autonomy            ███████░░░  0.50
planning     ██████░░░░  0.42   communication       ████████░░  0.60
tool_usage   █████████░  0.72   error_recovery      █████░░░░░  0.40
```

Every 5 interactions, Yue auto-reflects:
1. Reviews recent interactions
2. Adjusts capability scores based on patterns
3. Records findings
4. Promotes frequent patterns into permanent rules

This means Yue genuinely **improves** over time — she learns what she's good at and what needs work.

## Why Local-Only?

Most AI agents depend on cloud APIs:
- Monthly API bills
- Data privacy concerns  
- Internet dependency
- Vendor lock-in

Yue runs entirely through **Ollama** on your machine. No accounts, no subscriptions, no data leaving your computer. The autonomous pipelines optionally push to GitHub, but every decision and interaction stays local.

## Roadmap

- [x] Interactive CLI with personality
- [x] Ollama integration (local LLM)
- [x] Persistent memory system
- [x] Self-evolution engine
- [x] Daily report pipeline
- [ ] Web search integration
- [ ] Multi-session memory consolidation
- [ ] Windows installer (portable package)
- [ ] VSCode extension for inline Yue access

## License

MIT — Free to use, modify, and distribute. See [LICENSE](LICENSE).

---

<p align="center"><em>月 — A crescent moon. A claw mark. Not a tool.</em></p>
