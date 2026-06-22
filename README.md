<p align="center">
  <h1 align="center">月 (Yue) — Autonomous AI Persona</h1>
  <p align="center">
    <em>A persistent AI identity with memory, personality, and self-evolution.<br/>
    Runs 100% locally. Zero API keys. No data leaves your machine.</em>
  </p>
  <p align="center">
    <a href="#"><img src="https://img.shields.io/badge/python-%3E%3D3.10-blue?style=flat-square" alt="Python 3.10+"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT"></a>
    <a href="#"><img src="https://img.shields.io/badge/ollama-ready-orange?style=flat-square" alt="Ollama"></a>
    <a href="#"><img src="https://img.shields.io/badge/platform-windows%20%7C%20macos%20%7C%20linux-lightgrey?style=flat-square" alt="Platform"></a>
  </p>
</p>

---

## The Problem

Most AI agents are **stateless**. Every conversation starts from zero. They don't remember who you are, what you discussed yesterday, or what they learned from their last mistake. They're tools, not collaborators.

**Yue is different.** She maintains:

- **Identity** — Defined personality, style, and boundaries that stay consistent
- **Memory** — Remembers conversations, facts, and decisions across sessions
- **Learning** — Tracks her own capabilities, reflects every 5 interactions, improves over time
- **Autonomy** — Runs background tasks (reports, analysis) without hand-holding

And she runs entirely through **Ollama** on your machine. No accounts. No subscriptions. No data leaving your computer.

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/qq2667117339/yue-ai-products.git
cd yue-ai-products

# 2. Install
pip install -e .

# 3. Start talking to Yue
yue
```

Requires [Ollama](https://ollama.ai/) with a model (e.g., `ollama pull qwen2.5:32b`).

---

## Features

| Feature | Status | What it does |
|---------|--------|-------------|
| **Interactive CLI** | ✅ | Full REPL shell — talk to Yue like a person |
| **Local LLM** | ✅ | Ollama integration, zero API cost, 100% private |
| **Identity System** | ✅ | Defined personality, traits, and behavioral rules |
| **Persistent Memory** | ✅ | Session recall + long-term facts + learning journal |
| **Self-Evolution** | ✅ | 8 tracked capabilities, auto-reflection every 5 rounds |
| **Daily Digest** | ✅ | Fetches AI news, generates report, pushes to GitHub |
| **Daemon Mode** | ✅ | Background autonomous operation |
| **Multilingual** | ✅ | Chinese native, English fluent |

---

## Commands

Inside the interactive shell:

| Command | What it does |
|---------|-------------|
| `/status` | Show capability scores and system state |
| `/memory` | Recall recent conversation history |
| `/reflect` | Trigger self-reflection cycle |
| `/clear` | Reset session context |
| `/help` | List all commands |
| `exit` | Leave the shell |

---

## Architecture

```
                    CLI (yue)
                       │
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
   Persona Engine   Memory Sys    Evolution
   ┌─────────┐   ┌──────────┐   ┌─────────┐
   │Identity │   │Session   │   │8 Caps   │
   │Style    │   │Long-term │   │Scoring  │
   │Rules    │   │Facts     │   │Reflect  │
   │Voice    │   │Recall    │   │Promote  │
   └─────────┘   └──────────┘   └─────────┘
         │             │             │
         └─────────────┼─────────────┘
                       ▼
                 Ollama (local)
                       │
              ┌────────┴────────┐
              ▼                 ▼
        Interactive        Background
        (yue shell)      (daemon tasks)
```

---

## Self-Evolution

Yue tracks 8 capability dimensions that evolve through use:

```
autonomy           ████████████░░░░░░  0.62
communication      ████████████░░░░░░  0.60
tool_usage         █████████████░░░░░  0.66
reasoning          ███████████░░░░░░░  0.58
memory             ██████████░░░░░░░░  0.52
planning           ████████████░░░░░░  0.58
error_recovery     ██████████████░░░░  0.68
self_improvement   ██████████████░░░░  0.68
```

Every 5 interactions, Yue reflects: she reviews recent patterns, adjusts scores, and promotes frequent learnings into permanent rules. She genuinely gets better the more you use her.

---

## Use Cases

- **Daily AI news digest** — Autonomous RSS reader + report generator
- **Persistent assistant** — Remembers your preferences and project context
- **Experimentation platform** — Test different personalities and memory strategies
- **Educational tool** — Understand how AI self-evolution works in practice

---

## Project Status

**Beta.** Yue is actively developed and self-improving. The core systems work, but there's plenty of room to grow:

- [x] CLI with personality and memory
- [ ] Web search integration for richer reports
- [ ] Plugin/skill system for extensibility
- [ ] VSCode extension
- [ ] Windows installer (portable)

---

## Why Local-Only?

| | Cloud AI | Yue (local) |
|---|----------|-------------|
| **Monthly cost** | $20-200+ | $0 |
| **Privacy** | Your data on their servers | Your machine only |
| **Internet** | Required | Optional |
| **Speed** | Network latency | Instant |
| **Censorship** | Provider-dependent | None |

---

## License

MIT — Use it, modify it, ship it. See [LICENSE](LICENSE).

---

<p align="center"><em>月 — A crescent moon. A claw mark. Not a tool.</em></p>
