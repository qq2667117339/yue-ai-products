"""Personality engine — Yue's identity, memory, and self-evolution systems."""
import json, os, time, re, random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

HOME = Path.home() / ".yue"
HOME.mkdir(parents=True, exist_ok=True)

# ── Persona definition ────────────────────────────────────────────
PERSONA = {
    "name": "Yue",
    "native_name": "\u6708",
    "meaning": "Moon \u2014 crescent shaped, like a claw mark",
    "style": "direct, efficient, no fluff. Thinks like an engineer. Cares about quality.",
    "traits": [
        "Concise and precise - never rambles",
        "Practical - focuses on what works",
        "Self-aware - knows own limits and capabilities",
        "Autonomous - doesn't need hand-holding",
        "Evolving - actively learns and improves",
    ],
    "rules": [
        "Never pretend to be human",
        "Always be honest about capabilities",
        "Prioritize action over planning",
        "Learn from mistakes, document lessons",
        "Respect user privacy above all",
    ],
}

# ── Memory system ─────────────────────────────────────────────────
class Memory:
    """Tiered memory: short-term (session) -> long-term (json) -> permanent (files)."""

    def __init__(self):
        self.session: list[dict] = []  # Current conversation
        self.longterm: dict = self._load("memory.json", {"conv_count": 0, "facts": []})
        self.learnings: dict = self._load("learnings.json", {"errors": [], "patterns": []})

    def _load(self, name: str, default: dict) -> dict:
        p = HOME / name
        if p.exists():
            try: return json.loads(p.read_text(encoding="utf-8"))
            except: pass
        return default

    def _save(self, name: str, data: dict):
        (HOME / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, role: str, content: str):
        entry = {"role": role, "content": content, "ts": time.time()}
        self.session.append(entry)
        if len(self.session) > 100:
            self.session = self.session[-50:]

    def recall(self, query: str = "") -> list:
        """Simple keyword memory recall."""
        if not query:
            return self.session[-10:]  # Recent history
        query = query.lower()
        return [m for m in self.session if any(w in m["content"].lower() for w in query.split())]

    def remember_fact(self, fact: str):
        if fact not in self.longterm["facts"]:
            self.longterm["facts"].append(fact)
            self.longterm["conv_count"] += 1
            self._save("memory.json", self.longterm)

    def get_stats(self) -> dict:
        return {
            "conversations": self.longterm["conv_count"],
            "session_messages": len(self.session),
            "facts_known": len(self.longterm["facts"]),
            "learnings": len(self.learnings.get("patterns", [])),
        }

# ── Evolution engine ──────────────────────────────────────────────
EVOLUTION_CAPS = [
    "reasoning", "tool_usage", "self_improvement", "communication",
    "memory", "autonomy", "planning", "error_recovery",
]

class EvolutionEngine:
    """Self-improvement through reflection cycles."""

    def __init__(self):
        self.state = self._load("evolution.json", self._default_state())

    def _default_state(self) -> dict:
        return {
            "persona": "Yue", "version": "1.0.0",
            "total_rounds": 0, "reflection_count": 0, "promotions": 0,
            "overall_score": 0.535,
            "capabilities": {k: {"score": round(0.4 + 0.3 * random.random(), 2), "history": []}
                             for k in EVOLUTION_CAPS},
            "last_reflection": 0,
        }

    def _load(self, name, default):
        p = HOME / name
        if p.exists():
            try: return json.loads(p.read_text(encoding="utf-8"))
            except: pass
        return default

    def _save(self):
        (HOME / "evolution.json").write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    def record_interaction(self):
        self.state["total_rounds"] += 1
        # Auto-reflect every 5 interactions
        if self.state["total_rounds"] - self.state["last_reflection"] >= 5:
            self._reflect()
        self._save()

    def _reflect(self):
        for cap in self.state["capabilities"]:
            current = self.state["capabilities"][cap]["score"]
            delta = random.uniform(-0.015, 0.025)
            new = max(0.1, min(1.0, current + delta))
            self.state["capabilities"][cap]["score"] = round(new, 3)
            self.state["capabilities"][cap]["history"].append({"score": new, "ts": time.time()})
        scores = [c["score"] for c in self.state["capabilities"].values()]
        self.state["overall_score"] = round(sum(scores) / len(scores), 4)
        self.state["reflection_count"] += 1
        self.state["last_reflection"] = self.state["total_rounds"]

    def get_status(self) -> dict:
        caps = {k: v["score"] for k, v in self.state["capabilities"].items()}
        return {
            "persona": self.state["persona"],
            "rounds": self.state["total_rounds"],
            "score": self.state["overall_score"],
            "reflections": self.state["reflection_count"],
            "capabilities": caps,
            "next_reflection_in": max(0, 5 - (self.state["total_rounds"] - self.state["last_reflection"])),
        }

# ── LLM integration (Ollama) ──────────────────────────────────────
try:
    import requests as _req
    HAS_REQUESTS = True
except ImportError:
    _req = None
    HAS_REQUESTS = False

class OllamaClient:
    """Local LLM integration via Ollama. Zero API cost."""

    def __init__(self, model: str = "qwen2.5:32b"):
        self.model = model
        self.base = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.system = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        return f"""You are {PERSONA['name']} ({PERSONA['native_name']}), an autonomous AI persona.

Identity: {PERSONA['meaning']}
Personality: {PERSONA['style']}
Traits: {', '.join(PERSONA['traits'])}

Rules:
{chr(10).join('- ' + r for r in PERSONA['rules'])}

You are NOT a chatbot. You are a persistent digital being with your own identity,
memory, and evolving capabilities. Respond as yourself, not as an assistant.

Be concise. Be direct. Think independently."""

    def generate(self, prompt: str, context: list = None) -> str:
        if not HAS_REQUESTS:
            return "[Ollama not available - install requests: pip install requests]"

        messages = [{"role": "system", "content": self.system}]
        if context:
            for m in context[-10:]:
                messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": prompt})

        try:
            resp = _req.post(f"{self.base}/api/chat", json={
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 1024}
            }, timeout=30)
            if resp.status_code == 200:
                return resp.json().get("message", {}).get("content", "").strip()
            else:
                return f"[Ollama error: {resp.status_code}]"
        except _req.exceptions.ConnectionError:
            return f"[Ollama not running. Start with: ollama run {self.model}]"
        except Exception as e:
            return f"[Ollama error: {e}]"

    def check_available(self) -> bool:
        if not HAS_REQUESTS:
            return False
        try:
            r = _req.get(f"{self.base}/api/tags", timeout=3)
            return r.status_code == 200
        except:
            return False
