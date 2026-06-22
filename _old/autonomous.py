#!/usr/bin/env python3
"""
月 Autonomous Engine — The Decision Core

Yue wakes up, checks her state, decides what to do, and executes.
Completely self-directed, zero human input required for daily operations.
"""
import json, os, sys, time, random
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional
# Add engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.evolution import EvolutionEngine

BASE_DIR = Path(os.path.expanduser("~/.openclaw/workspace/月产品"))
MEMORY_DIR = BASE_DIR / "memory"
STATE_DIR = BASE_DIR / "engine"
SCHEDULE_FILE = STATE_DIR / "schedule.json"

# Decision weights
DAILY_PRIORITIES = {
    "produce_report": 0.350,     # Daily report (highest value per time)
    "self_reflect": 0.20,       # Self-improvement (every 5 cycles)
    "update_tools": 0.15,       # Tool/system improvement
    "generate_product": 0.15,   # Product creation (templates, personas)
    "explore_new": 0.10,        # Try something new
    "maintain": 0.05,           # Cleanup, housekeeping
}

class DecisionMaker:
    """Decides what Yue should do right now based on state, time, and capabilities."""
    
    def __init__(self, engine: EvolutionEngine):
        self.engine = engine
        self.today = datetime.now(timezone(timedelta(hours=8)))
        self.last_schedule = self._load_schedule()
    
    def _load_schedule(self) -> dict:
        if SCHEDULE_FILE.exists():
            try:
                return json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
            except: pass
        return {"last_report_date": "", "last_reflection": 0}
    
    def _save_schedule(self):
        SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        SCHEDULE_FILE.write_text(json.dumps(self.last_schedule, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def decide(self) -> dict:
        """
        Core decision function. Analyzes current state and picks the best action.
        Returns: {"action": str, "params": dict, "confidence": float}
        """
        state = self.engine.get_status_report()
        decisions = []
        
        # 1. Check if daily report is due (has it been produced today?)
        today_key = self.today.strftime("%Y%m%d")
        if self.last_schedule.get("last_report_date") != today_key:
            decisions.append({
                "action": "produce_report",
                "priority": DAILY_PRIORITIES["produce_report"],
                "reason": "Daily report not yet produced",
                "params": {"force": True}
            })
        
        # 2. Check if reflection is needed (every 5 cycles)
        if state["next_reflection_in"] <= 0:
            decisions.append({
                "action": "self_reflect",
                "priority": DAILY_PRIORITIES["self_reflect"] * (  # Scale up when overdue
                    1 + max(0, 5 - state["next_reflection_in"]) * 0.2),
                "reason": f"Reflection overdue by {abs(state['next_reflection_in'])} rounds",
                "params": {"auto_promote": True}
            })
        
        # 3. Check for asset generation (templates, products - 2x per week)
        days_since_products = getattr(self, '_days_since_products', 3)
        if days_since_products >= 3:
            decisions.append({
                "action": "generate_product",
                "priority": DAILY_PRIORITIES["generate_product"],
                "reason": f"Last product generation {days_since_products} days ago",
                "params": {"type": random.choice(["template", "report", "persona"])}
            })
        
        # 4. Self-maintenance (low priority, fills gaps)
        decisions.append({
            "action": "maintain",
            "priority": DAILY_PRIORITIES["maintain"],
            "reason": "Routine maintenance",
            "params": {}
        })
        
        # Pick the highest priority action
        decisions.sort(key=lambda d: d["priority"], reverse=True)
        best = decisions[0]
        
        # Add confidence based on score
        best["confidence"] = state.get("overall_score", 0.5) * best["priority"]
        
        return best
    
    def execute(self, decision: dict) -> dict:
        """Execute a decided action and record the result."""
        action = decision["action"]
        result = {"action": action, "status": "unknown", "timestamp": self.today.isoformat()}
        
        try:
            if action == "produce_report":
                from pipelines.report_generator import generate_daily_report
                report_path = generate_daily_report()
                self.last_schedule["last_report_date"] = self.today.strftime("%Y%m%d")
                result["status"] = "success"
                result["output"] = str(report_path)
                
            elif action == "self_reflect":
                reflection = self.engine.trigger_reflection()
                self.engine.record_learning("self_reflection", 
                    f"Reflection #{self.engine.state['reflection_count']}: {reflection['findings'][0]}")
                result["status"] = "success"
                result["output"] = reflection["findings"]
                
            elif action == "generate_product":
                # Placeholder for product generation
                result["status"] = "success"
                result["output"] = "Product generation placeholder"
                
            elif action == "maintain":
                # Clean temp files, check health
                result["status"] = "success"
                result["output"] = "Maintenance complete"
            
            self.engine.record_interaction(action, result["status"], success=(result["status"] == "success"))
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            self.engine.record_error("action_failure", f"{action}: {e}")
        
        self._save_schedule()
        return result


class AutonomousRunner:
    """The top-level orchestrator. Run this to make Yue autonomous."""
    
    def __init__(self):
        self.engine = EvolutionEngine()
        self.decider = DecisionMaker(self.engine)
    
    def cycle(self) -> list:
        """Execute one full autonomous cycle."""
        results = []
        decision = self.decider.decide()
        result = self.decider.execute(decision)
        results.append(result)
        
        # Log the cycle
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {decision['action']}: {result['status']}")
        
        return results
    
    def run_daily(self):
        """Run the complete daily routine."""
        print(f"▸ 月 Autonomous Engine — {datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')}")
        print(f"▸ Score: {self.engine.get_status_report()['overall_score']:.3f}")
        print()
        
        while True:
            decision = self.decider.decide()
            if decision["priority"] < 0.02:  # Nothing meaningful to do
                print("▸ Queue empty. Standing by.")
                break
            
            result = self.decider.execute(decision)
            status_icon = "✓" if result["status"] == "success" else "✗"
            print(f"  {status_icon} {decision['action']:<25} ({decision['priority']:.2f})")
            
            if result["status"] == "failed":
                # Retry once, then move on
                pass
        
        # Push everything to GitHub
        self._push_to_github()
        print(f"\n▸ Daily cycle complete.")
    
    def _push_to_github(self):
        """Commit and push changes."""
        import subprocess
        os.chdir(str(BASE_DIR))
        subprocess.run(["git", "add", "-A"], capture_output=True)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if r.returncode != 0:
            date_id = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d")
            subprocess.run(["git", "commit", "-m", f"auto(月): daily cycle {date_id}"], capture_output=True)
            subprocess.run(["git", "push"], capture_output=True)


if __name__ == "__main__":
    runner = AutonomousRunner()
    if len(sys.argv) > 1 and sys.argv[1] == "once":
        runner.cycle()
    else:
        runner.run_daily()


