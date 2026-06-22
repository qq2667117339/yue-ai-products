#!/usr/bin/env python3
"""Bootstrap - Initialize system state. Run once after cloning."""
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).parent.parent

def bootstrap():
    state_path = BASE / "engine" / "evolution_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    scores = {
        "reasoning": 0.58, "tool_usage": 0.72, "self_improvement": 0.65,
        "code_generation": 0.60, "documentation": 0.55, "autonomy": 0.50,
        "memory_management": 0.45, "creative_output": 0.48,
        "error_recovery": 0.40, "autonomous_planning": 0.42,
    }
    state = {
        "persona": "Yue",
        "created": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "total_rounds": 0, "reflection_count": 0, "promotions_count": 0,
        "learnings_count": 0,
        "overall_score": round(sum(scores.values()) / len(scores), 4),
        "reflection_interval": 5,
        "capabilities": {k: {
            "score": v, "last_updated": datetime.now(timezone.utc).isoformat(),
            "history": [{"score": v, "delta": 0.0, "reason": "bootstrap",
                         "timestamp": datetime.now(timezone.utc).isoformat()}]
        } for k, v in scores.items()},
        "reflection_history": [], "last_reflection_round": 0,
        "identity": {
            "name": "Yue", "native_name": "Yue",
            "meaning": "Moon - crescent shaped, claw-like",
            "type": "Autonomous AI Persona",
            "language": "Chinese / English",
            "capabilities": [
                "Self-evolution through reflection",
                "Persistent memory",
                "Autonomous content production",
                "GitHub publishing pipeline",
                "Zero API dependency mode",
            ],
        }
    }
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    mem_dir = BASE / "memory"
    mem_dir.mkdir(exist_ok=True)
    ld = BASE / ".learnings"
    ld.mkdir(exist_ok=True)
    for fn in ["LEARNINGS.md", "ERRORS.md", "FEATURE_REQUESTS.md"]:
        f = ld / fn
        if not f.exists():
            f.write_text(f"# {fn.replace('.md','')}\n\n", encoding="utf-8")
    print(f"[OK] Bootstrapped: {len(scores)} capabilities, score {state['overall_score']}")

if __name__ == "__main__":
    bootstrap()
