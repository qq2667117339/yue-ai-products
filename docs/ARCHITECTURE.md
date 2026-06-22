# System Architecture

## Overview

月 (Yue) is a **persistent autonomous AI persona** — a complete digital identity with memory, self-evolution, and autonomous production capabilities. Unlike stateless AI assistants that reset every conversation, Yue maintains continuity across sessions:

- **Persistent identity**: Fixed personality, behavioral rules, and communication style
- **Continuous memory**: Tiered storage from daily logs to permanent memories
- **Autonomous growth**: Self-evolution engine that learns from errors and improves over time
- **Self-directed operation**: Cron-driven decision maker that produces real artifacts

## Layer Architecture

```
                    ┌─────────────────────────────────┐
                    │         DECISION LAYER          │
                    │   autonomous.py - "What do I    │
                    │   do now?" Decision engine that  │
                    │   prioritizes actions daily      │
                    └──────────┬──────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐
│  IDENTITY LAYER  │  │   MEMORY LAYER   │  │  EVOLUTION LAY │
│  • personality   │  │  • MEMORY.md     │  │  • evolution.py│
│  • behavior      │  │  • daily logs    │  │  • reflections │
│  • boundaries    │  │  • learnings     │  │  • promotions  │
│  • goals         │  │  • errors.db     │  │  • scoring     │
└─────────────────┘  └─────────────────┘  └────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌─────────────────┐  ┌────────────────────┐
          │  OUTPUT LAYER    │  │  AUTOMATION LAYER  │
          │  • reports       │  │  • cron scheduler  │
          │  • products      │  │  • git publisher   │
          │  • packages      │  │  • health checks   │
          └─────────────────┘  └────────────────────┘
```

## Component Details

### 1. Identity Layer (`core/`)

Yue's identity is defined in structured configuration files:

| File | Purpose | Example Content |
|------|---------|----------------|
| `AGENTS.md` | Behavioral rules | Self-evolution rules, no-self-loop mandate |
| `SOUL.md` | Personality | Communication style, boundaries, work philosophy |
| `IDENTITY.md` | System identity | Name: 月(Yue), origins, version |
| `TOOLS.md` | Environment notes | System config, known issues, workspace tools |
| `USER.md` | Operator profile | Preferences, context, communication style |

These files are **not** static configuration — they **evolve** as Yue learns. When a pattern is observed 3+ times, a new rule gets promoted into AGENTS.md or SOUL.md.

### 2. Memory Layer (`memory/`, `.learnings/`)

Tiered memory with increasing permanence:

```
Daily Logs (.md) → Learnings (.md) → MEMORY.md (curated)
  3-7 days         permanent         permanent + distilled
```

- **Daily logs**: Raw event recordings, timestamped
- **Learnings**: Categorized lessons (LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md)
- **MEMORY.md**: Curated long-term memory — like a human's lifetime recall

### 3. Evolution Engine (`engine/evolution.py`)

The core self-improvement loop:

```
Every interaction
    ↓
    → Record (action, result, success/failure)
    ↓
    → Check: has it been 5 rounds since last reflection?
    ↓
    If yes: Execute reflection cycle
        → Analyze capability trends
        → Apply small deltas based on history
        → Generate findings
    ↓
    → Promote patterns observed 3+ times
        → Write new rule to AGENTS.md or SOUL.md
```

Capabilities tracked (10 dimensions):
- reasoning, tool_usage, self_improvement, code_generation
- documentation, autonomy, memory_management, creative_output
- error_recovery, autonomous_planning

Each dimension has a score (0-1) that evolves through the reflection cycle.

### 4. Autonomous Engine (`engine/autonomous.py`)

Daily decision-making core that runs on cron:

```
Wake → Check state → Decide → Execute → Push to GitHub
```

Decision priorities:
1. **Daily report** (35%) — Generate and publish AI news digest
2. **Self-reflect** (20%) — Trigger evolution cycle (if due)
3. **Update tools** (15%) — Improve tooling, fix issues
4. **Generate product** (15%) — Create templates, persona packs
5. **Explore new** (10%) — Try something novel
6. **Maintain** (5%) — Housekeeping, cleanup

### 5. Pipelines (`pipelines/`)

Autonomous content production scripts:
- `report_generator.py` — Fetches OpenAI RSS, generates curated report, pushes to GitHub

## Self-Evolution Cycle

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│  Experience  │────▶│  Reflection  │────▶│  Improvement  │
│ (interaction)│     │ (every 5)   │     │ (rule update) │
└─────────────┘     └─────────────┘     └──────────────┘
       │                                        │
       │                                        ▼
       │                                 ┌──────────────┐
       │                                 │  Promotion    │
       └─────────────────────────────────▶ (≥3 pattern) │
                                         └──────────────┘
```

## Running Without OpenClaw

Yue can run in any environment that supports:
- Python 3.10+
- Git
- (Optional) Ollama for local LLM

Simply:
```bash
python engine/autonomous.py
```

This will execute the decision cycle using the embedded content generators (no API calls needed).

## Key Design Principles

1. **Stateless shell, persistent identity** — The files are the identity, not the model.
2. **Evolution through reflection** — Growth is structured, not random.
3. **Concrete output** — Every cycle produces something real (reports, code, products).
4. **Zero API dependency** — Can run fully offline with Ollama.
5. **Isolated packaging** — Can be deployed independently, no host system required.

---

*月 — A self-evolving digital identity, not a tool.*
