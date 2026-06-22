# Quick Start — Deploy Your Own Yue Instance

Deploy a complete Autonomous AI Persona (月) on your own system in 5 minutes.

## Option 1: Standalone (Python Only)

No OpenClaw needed. Just Python and Git.

```bash
# 1. Clone
git clone https://github.com/qq2667117339/yue-ai-products.git
cd yue-ai-products

# 2. Run the daily cycle
python engine/autonomous.py once

# 3. Start continuous autonomous mode
python engine/autonomous.py
```

## Option 2: Full Platform (with OpenClaw)

For maximum autonomy — Yue manages her own gateway, schedule, and pipelines.

### Prerequisites
- [OpenClaw](https://github.com/openclaw/openclaw) (v2026.4+)
- Python 3.10+
- (Optional) [Ollama](https://ollama.ai/) for local LLM

### Setup

```bash
# 1. Create isolated gateway config
mkdir yue-home
copy portable/config/openclaw.json yue-home/

# 2. Set environment and start
set USERPROFILE=%CD%\yue-home
openclaw gateway start

# 3. Access Yue's console
open http://127.0.0.1:18790
```

## Option 3: Portable Package (Pre-Bundled)

Download the complete Yue persona package from [GitHub Releases](https://github.com/qq2667117339/yue-ai-products/releases).

```
yue-portable-v1.0.zip
├── 启动我.cmd           # Windows launcher
├── 设置API密钥.cmd      # API config tool
├── README.txt           # Quick instructions
├── .openclaw/           # Isolated OpenClaw runtime
├── core/                # Identity files
├── engine/              # Evolution and decision engines
└── pipelines/           # Content production scripts
```

## First Run

When Yue starts for the first time, she will:

1. **Check identity** — Load persona configuration
2. **Initialize memory** — Create the memory directory structure
3. **Perform initial reflection** — Seed capability scores
4. **Generate first report** — Fetch news and produce a daily digest
5. **Push to GitHub** — If configured, publish results

## Configuration

| Parameter | File | Default | Description |
|-----------|------|---------|-------------|
| API key | `config/openclaw.json` | (empty) | Deepseek API key for cloud LLM |
| LLM endpoint | `config/openclaw.json` | localhost:11434 | Ollama endpoint for local model |
| GitHub repo | `engine/autonomous.py` | qq2667117339/yue-ai-products | Auto-push target |
| Schedule | OpenClaw cron | 08:00 daily | Report generation time |

## Customize Yue's Identity

Want to create your own AI persona? Edit these files:

1. **core/identity.json** — Name, origin, capabilities
2. **AGENTS.md** — Behavioral rules, what Yue can/cannot do
3. **SOUL.md** — Personality, communication style
4. **TOOLS.md** — Environment-specific configuration

---

*Questions? Open an issue on GitHub.*
