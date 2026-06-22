"""
CLI — Yue's interactive and autonomous command-line interface.
"""
import sys, os, time, json, subprocess
from pathlib import Path

from .persona import Memory, EvolutionEngine, OllamaClient, PERSONA, HOME

def print_banner():
    """Print startup banner."""
    version = "1.0.0"
    print()
    print("  \u263d  Yue (\u6708) Autonomous AI Persona  v" + version)
    print("  " + "\u2500" * 42)
    print("  Type 'exit' to quit, 'help' for commands")
    print()

def cmd_status(memory, evolution):
    """Show system status."""
    stats = memory.get_stats()
    evo = evolution.get_status()
    print()
    print("  \u25b8 Yue System Status")
    print("  " + "\u2500" * 42)
    print(f"  Rounds:        {evo['rounds']}")
    print(f"  Score:         {evo['score']:.3f}")
    print(f"  Reflections:   {evo['reflections']}")
    print(f"  Conversations: {stats['conversations']}")
    print(f"  Session msgs:  {stats['session_messages']}")
    print(f"  Facts known:   {stats['facts_known']}")
    print()
    print("  Capabilities:")
    for name, score in sorted(evo['capabilities'].items(), key=lambda x: -x[1]):
        bar = "\u2588" * int(score * 20) + "\u2591" * (20 - int(score * 20))
        print(f"    {name:<18} [{bar}] {score:.2f}")
    print()

def cmd_evolve(evolution, cycles: int = 5):
    """Run autonomous evolution cycles."""
    print(f"\n  Running {cycles} autonomous evolution cycles...")
    evo_before = evolution.get_status()
    result = evolution.self_evolve(cycles=cycles)
    evo_after = evolution.get_status()
    delta = evo_after["score"] - evo_before["score"]
    print(f"  Score: {evo_before['score']:.3f} \u2192 {evo_after['score']:.3f} ({delta:+.4f})")
    print(f"  Reflections triggered: {evo_after['reflections'] - evo_before['reflections']}")
    print()
    return result

def cmd_help():
    """Show available commands."""
    print("""
  Commands:
    /status     - Show system status and capabilities
    /evolve [n] - Run n autonomous evolution cycles (default 5)
    /memory     - Recall recent conversation history
    /reflect    - Force a reflection cycle
    /clear      - Clear session memory
    /help       - Show this help
    exit        - Exit interactive mode

  Usage:
    yue                    - Interactive shell
    yue <message>          - Single response
    yue --status           - Show status and exit
    yue --evolve [cycles]  - Run autonomous evolution and exit
    yue --daemon           - Background mode
""")

def interactive_mode():
    """Interactive REPL shell where you talk to Yue."""
    mem = Memory()
    evo = EvolutionEngine()
    llm = OllamaClient()

    print_banner()

    if not llm.check_available():
        print("  [WARN] Ollama not detected. Yue will run in offline mode.")
        print("  Start Ollama with: ollama run qwen2.5:32b")
        print()

    while True:
        try:
            user_input = input("  you > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            cmd = user_input.lower()
            args_list = cmd.split()
            cmd_base = args_list[0]

            if cmd_base == "/status":
                cmd_status(mem, evo)
            elif cmd_base == "/evolve":
                cycles = int(args_list[1]) if len(args_list) > 1 else 5
                cmd_evolve(evo, cycles)
            elif cmd_base == "/memory":
                history = mem.recall()
                print(f"\n  Recent ({len(history)} messages):")
                for m in history[-6:]:
                    role = "you" if m["role"] == "user" else "yue"
                    print(f"  [{role}] {m['content'][:100]}")
                print()
            elif cmd_base == "/reflect":
                evo.record_interaction(caps_used=["communication", "reasoning"])
                print(f"\n  Reflection triggered. Score: {evo.get_status()['score']:.3f}\n")
            elif cmd_base == "/clear":
                mem.session = []
                print("\n  Session cleared.\n")
            elif cmd_base in ("/help", "/?"):
                cmd_help()
            elif cmd_base == "exit":
                break
            else:
                print(f"\n  Unknown command: {cmd_base}\n")
            continue

        if user_input.lower() == "exit":
            break

        # Record user input
        mem.add("user", user_input)

        # Generate response
        print("  yue > ", end="", flush=True)
        response = llm.generate(user_input, mem.session[-10:])
        print(response)
        print()

        # Record response
        mem.add("assistant", response)
        evo.record_interaction(caps_used=["communication", "reasoning"])


def single_response(prompt: str):
    """Single-turn response."""
    mem = Memory()
    llm = OllamaClient()
    response = llm.generate(prompt)
    print(response)


def daemon_mode():
    """Background autonomous mode - runs daily pipeline."""
    print("[Yue] Starting background daemon...")
    # Run the daily report pipeline
    from .pipelines.report import generate
    try:
        path = generate()
        print(f"[Yue] Report generated: {path}")
    except Exception as e:
        print(f"[Yue] Error: {e}")


def main():
    """Main entry point."""
    args = sys.argv[1:]

    if not args:
        interactive_mode()
    elif args[0] == "--status":
        mem = Memory()
        evo = EvolutionEngine()
        cmd_status(mem, evo)
    elif args[0] == "--evolve":
        evo = EvolutionEngine()
        cycles = int(args[1]) if len(args) > 1 and args[1].isdigit() else 5
        cmd_evolve(evo, cycles)
    elif args[0] == "--server":
        from .server import start_server
        start_server()
    elif args[0] == "--daemon":
        daemon_mode()
    elif args[0] in ("--help", "-h"):
        cmd_help()
    else:
        single_response(" ".join(args))

if __name__ == "__main__":
    main()
