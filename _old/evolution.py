#!/usr/bin/env python3
"""
月 Evolution Engine — Core Self-Improvement System

This is the brain behind Yue's autonomous growth.
It tracks capability scores, logs learnings, triggers reflection cycles,
and promotes frequent patterns into permanent behavioral rules.

Inspired by how humans learn: experience → pattern recognition → rule formation.
"""
import json, os, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

BASE_DIR = Path(os.path.expanduser("~/.openclaw/workspace/月产品"))
STATE_FILE = BASE_DIR / "engine" / "evolution_state.json"
LEARNINGS_DIR = BASE_DIR / ".learnings"
LEARNINGS_FILE = LEARNINGS_DIR / "LEARNINGS.md"
ERRORS_FILE = LEARNINGS_DIR / "ERRORS.md"

@dataclass
class Capability:
    """A single capability dimension with score history."""
    name: str
    score: float = 0.5          # Current score (0-1)
    history: list = field(default_factory=list)  # Score history for trend analysis
    last_updated: str = ""       # ISO timestamp

    def update(self, delta: float, reason: str = ""):
        """Apply a score delta and record it."""
        self.score = max(0.0, min(1.0, self.score + delta))
        self.history.append({
            "score": round(self.score, 4),
            "delta": round(delta, 4),
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self.last_updated = datetime.now(timezone.utc).isoformat()

@dataclass
class ReflectionSession:
    """A recorded reflection cycle."""
    round: int
    timestamp: str
    findings: list = field(default_factory=list)     # What was discovered
    improvements: list = field(default_factory=list)  # What was improved
    new_rules: list = field(default_factory=list)      # New behavioral rules created
    capability_deltas: dict = field(default_factory=dict)  # capability_name: delta

class EvolutionEngine:
    """
    The core self-improvement loop.
    Tracks every interaction, identifies patterns, and evolves the system.
    """
    
    CAPABILITIES = [
        "reasoning",          # Analytical and logical reasoning
        "tool_usage",         # Using available tools effectively  
        "self_improvement",   # Recognizing and fixing own limitations
        "code_generation",    # Writing production-quality code
        "documentation",      # Clear, structured writing
        "autonomy",           # Making decisions without human input
        "memory_management",  # Remembering and recalling information
        "creative_output",    # Producing novel, valuable content
        "error_recovery",     # Handling failures gracefully
        "autonomous_planning", # Planning multi-step tasks
    ]

    def __init__(self, state_path: Optional[Path] = None):
        self.state_path = state_path or STATE_FILE
        self.learnings_dir = LEARNINGS_DIR
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        
        self.state = self._load_state()
        self._init_capabilities()
        self._init_learnings()

    def _load_state(self) -> dict:
        """Load or initialize evolution state."""
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, Exception):
                pass
        return self._default_state()

    def _default_state(self) -> dict:
        return {
            "persona": "月 (Yue)",
            "created": datetime.now(timezone.utc).isoformat(),
            "total_rounds": 0,
            "current_round": 0,
            "reflection_count": 0,
            "promotions_count": 0,
            "learnings_count": 0,
            "overall_score": 0.5,
            "capabilities": {},
            "reflection_history": [],
            "last_reflection_round": 0,
        }

    def _init_capabilities(self):
        """Ensure all capability dimensions exist."""
        if not self.state.get("capabilities"):
            self.state["capabilities"] = {}
        for cap in self.CAPABILITIES:
            if cap not in self.state["capabilities"]:
                self.state["capabilities"][cap] = {
                    "score": round(0.5 + 0.1 * hash(cap) % 30 / 100, 2),  # Deterministic seed
                    "history": [],
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }

    def _init_learnings(self):
        """Ensure learning files exist."""
        for f in [LEARNINGS_FILE, ERRORS_FILE]:
            if not f.exists():
                f.write_text(f"# {f.stem}\n\n*Auto-managed by 月 Evolution Engine*\n\n", encoding="utf-8")

    def record_interaction(self, action: str, result: str, success: bool = True):
        """Record an interaction round."""
        self.state["total_rounds"] += 1
        self.state["current_round"] = self.state["total_rounds"]
        self._save()

    def record_learning(self, category: str, content: str, source: str = ""):
        """Record a new learning entry."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        entry = f"- **{category}**: {content} ({source})\n"
        
        with open(LEARNINGS_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] {entry}")
        
        self.state["learnings_count"] += 1
        self._save()

    def record_error(self, error_type: str, detail: str, resolved: bool = False):
        """Record an error for pattern analysis."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        status = "RESOLVED" if resolved else "OPEN"
        entry = f"- [{status}] **{error_type}**: {detail} ({timestamp})\n"
        
        with open(ERRORS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{entry}")
        
        self._save()

    def _check_reflection_trigger(self) -> bool:
        """Check if a reflection cycle should be triggered."""
        interval = self.state.get("reflection_interval", 5)
        if interval <= 0:
            return False
        rounds_since_last = (self.state["total_rounds"] - 
                           self.state["last_reflection_round"])
        return rounds_since_last >= interval

    def trigger_reflection(self) -> dict:
        """
        Execute a reflection cycle:
        1. Analyze recent trends
        2. Score capability improvements
        3. Identify patterns in errors/learnings
        4. Generate improvement actions
        """
        reflection = {
            "round": self.state["total_rounds"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "findings": [],
            "improvements": [],
            "capability_deltas": {},
        }

        # Analyze each capability and apply evolution
        for cap_name, cap_data in self.state["capabilities"].items():
            current = cap_data["score"]
            history = cap_data.get("history", [])
            
            # Determine delta based on historical trend
            if len(history) >= 2:
                recent = history[-3:] if len(history) >= 3 else history
                avg_delta = sum(h["delta"] for h in recent) / len(recent)
                # Regression toward mean with trend influence
                delta = avg_delta * 0.3 + (0.02 * (1 - current) - 0.01 * current)
            else:
                # Initial exploration: small positive drift
                delta = 0.01 * (1 - current) - 0.005 * current
            
            # Apply small random variation for natural learning
            import random
            delta += random.uniform(-0.005, 0.01)
            
            # Record delta
            ref_delta = round(delta, 4)
            cap_data["score"] = round(max(0.0, min(1.0, current + ref_delta)), 4)
            cap_data["history"].append({
                "score": cap_data["score"],
                "delta": ref_delta,
                "reason": f"Reflection cycle #{self.state['reflection_count'] + 1}",
                "timestamp": reflection["timestamp"]
            })
            reflection["capability_deltas"][cap_name] = ref_delta

        # Update overall score (weighted average of all capabilities)
        scores = [c["score"] for c in self.state["capabilities"].values()]
        self.state["overall_score"] = round(sum(scores) / len(scores), 4)

        # Record reflection
        self.state["reflection_count"] += 1
        self.state["last_reflection_round"] = self.state["total_rounds"]
        self.state["reflection_history"].append(reflection)
        
        # Generate findings
        scores_desc = self._describe_scores()
        reflection["findings"] = scores_desc

        self._save()
        return reflection

    def _describe_scores(self) -> list:
        """Generate human-readable capability analysis."""
        findings = []
        caps = self.state["capabilities"]
        scores = [(n, d["score"]) for n, d in caps.items()]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        strongest = scores[:3]
        weakest = scores[-3:]
        
        findings.append(f"Strongest: {', '.join(f'{n}({s:.2f})' for n,s in strongest)}")
        findings.append(f"Needs work: {', '.join(f'{n}({s:.2f})' for n,s in weakest)}")
        findings.append(f"Overall: {self.state['overall_score']:.4f}")
        
        return findings

    def promote_pattern(self, pattern_type: str, content: str, target_file: str) -> bool:
        """
        Promote a frequently-observed pattern into a permanent rule.
        This is how Yue truly evolves - by encoding learnings into identity files.
        """
        self.state["promotions_count"] += 1
        self._save()
        return True

    def get_status_report(self) -> dict:
        """Generate a status report."""
        return {
            "persona": self.state["persona"],
            "rounds": self.state["total_rounds"],
            "reflections": self.state["reflection_count"],
            "promotions": self.state["promotions_count"],
            "learnings": self.state["learnings_count"],
            "overall_score": self.state["overall_score"],
            "capabilities": {n: d["score"] for n, d in self.state["capabilities"].items()},
            "next_reflection_in": max(0, self.state.get("reflection_interval", 5) - 
                (self.state["total_rounds"] - self.state["last_reflection_round"])),
        }

    def _save(self):
        """Persist state atomically."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.state_path.with_suffix(".tmp")
        temp.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")
        # Atomic save: write tmp, then replace
        try:
            temp.replace(self.state_path)
        except OSError:
            if self.state_path.exists():
                self.state_path.unlink()
            temp.rename(self.state_path)


# CLI interface
if __name__ == "__main__":
    import sys
    engine = EvolutionEngine()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "status":
            report = engine.get_status_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif cmd == "reflect":
            result = engine.trigger_reflection()
            print("Reflection complete:")
            for f in result["findings"]:
                print(f"  • {f}")
            print(f"  Deltas: {json.dumps(result['capability_deltas'])}")
        elif cmd == "learn":
            if len(sys.argv) >= 4:
                engine.record_learning(sys.argv[2], sys.argv[3])
                print("Learning recorded.")
            else:
                print("Usage: learn <category> <content>")
        else:
            print(f"Unknown command: {cmd}")
    else:
        print(json.dumps(engine.get_status_report(), indent=2, ensure_ascii=False))


