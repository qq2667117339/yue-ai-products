# Yue API Server — Quick Start Guide

> Turn your local AI persona into a service. REST API, web dashboard, zero dependencies.

## Overview

The Yue API Server is a **zero-dependency REST API** built into the `yue` package. It uses only Python's built-in `http.server`, `json`, and `urllib` — no installation required beyond basic Python.

- **Port**: 18792 (configurable via `--port`)
- **Dashboard**: SPA web UI served at `http://127.0.0.1:18792/`
- **API**: REST endpoints for chat, memory, evolution, status

## Quick Start

```bash
# Method 1: CLI command (if installed via pip)
yue-server

# Method 2: Python module
python -m yue.server

# Method 3: With custom port
yue-server --port 8080

# Method 4: Start yue interactive CLI with server
yue --server
```

Open `http://127.0.0.1:18792/` in your browser.

## API Reference

### `GET /api/status`

Returns real-time system status:
```json
{
  "version": "1.0.0",
  "rounds": 42,
  "overall_score": 0.685,
  "capabilities": { "reasoning": 0.72, "communication": 0.68, ... },
  "memory_count": 15,
  "reflections": 8
}
```

### `POST /api/chat`

Send a message and receive a response:
```json
{
  "message": "What's AI-powered short video generation?",
  "model": "ollama"
}
```

### `GET /api/memory`

View Yue's long-term memory:
```json
{
  "facts": ["User prefers local-first tools", "..."]
}
```

### `POST /api/remember`

Save a new memory:
```json
{
  "key": "project_preference",
  "value": "User emphasized GitHub quality over language"
}
```

### `POST /api/reflect`

Trigger a reflection cycle. Returns updated capability scores.

### `GET /api/history`

Returns recent conversation history.

## Use Cases

**Embedded AI Assistant**
```python
import requests, json
r = requests.post("http://127.0.0.1:18792/api/chat",
    json={"message": "Summarize today's AI news"})
print(r.json()["response"])
```

**CI/CD Integration**
```bash
# In your CI pipeline
curl -s http://127.0.0.1:18792/api/status | jq .
```

**Home Automation**
```bash
# Trigger reflection on schedule
curl -X POST http://127.0.0.1:18792/api/reflect
```

## Architecture

```
Browser / Client
      |
      v
 HTTP Server (:18792)
      |
      +-- /api/status   → EvolutionEngine.get_status()
      +-- /api/chat     → Ollama + Memory + Evolution
      +-- /api/memory   → MemoryStore
      +-- /api/reflect  → EvolutionEngine.reflect()
      +-- /api/remember → MemoryStore.save()
      +-- /             → Embedded SPA (static HTML/CSS/JS)
      |
      +-- EvolutionEngine
      |     +-- 8-dimension capability tracking
      |     +-- Real performance metrics
      |     +-- Auto-reflection every 5 interactions
      |
      +-- MemoryStore
      |     +-- Session memory
      |     +-- Long-term facts
      |     +-- Learning journal
      |
      +-- Ollama (optional)
            +-- qwen2.5:32b (default)
            +-- Zero API cost
```

## Security Notes

- **Default**: binds to `127.0.0.1` (localhost only)
- **No authentication by default** — wrap with nginx for production
- **All data stays local** — no external API calls
- **CORS**: enabled for localhost development

## Production Deployment

```bash
# Run as background service (Windows)
start /B python -m yue.server

# With nginx reverse proxy
server {
    listen 443 ssl;
    server_name yue.example.com;
    location / {
        proxy_pass http://127.0.0.1:18792;
    }
}
```

## Roadmap

- [ ] API key authentication
- [ ] Cloud backup option
- [ ] Multi-persona support
- [ ] WebSocket streaming
- [ ] Docker container
- [ ] Stripe integration for paid API access
