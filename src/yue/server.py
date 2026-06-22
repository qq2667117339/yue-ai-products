"""
Yue HTTP API Server — Premium feature: REST API for the Yue persona engine.

Provides a web interface and API that wraps the core persona engine.
No external dependencies — uses Python's built-in http.server.

Usage:
    yue-server              # Start on default port 18791
    yue-server --port 8888  # Custom port
"""

import json, os, sys, time, threading, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime, timezone

# Import Yue core
sys.path.insert(0, str(Path(__file__).parent.parent))
from yue.persona import Memory, EvolutionEngine, OllamaClient, PERSONA, HOME

HOST = "127.0.0.1"
PORT = 18791

# ── Shared state ─────────────────────────────────────────────────
mem = Memory()
evo = EvolutionEngine()
llm = OllamaClient()

# ── HTML Dashboard (embedded) ────────────────────────────────────
DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Yue Dashboard</title>
    <style>
        :root {
            --bg: #0d1117; --card: #161b22; --border: #30363d;
            --text: #c9d1d9; --heading: #f0f6fc; --accent: #58a6ff;
            --green: #3fb950;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg); color: var(--text); line-height: 1.6;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 24px; }
        h1 { color: var(--heading); font-size: 1.8em; margin-bottom: 8px; }
        h2 { color: var(--heading); font-size: 1.3em; margin: 24px 0 12px; }
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 6px; padding: 20px; margin-bottom: 16px;
        }
        .stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
        .stat {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 6px; padding: 16px; flex: 1; min-width: 120px;
            text-align: center;
        }
        .stat .value { font-size: 2em; font-weight: 700; color: var(--accent); }
        .stat .label { font-size: 0.85em; color: #8b949e; margin-top: 4px; }
        .cap-bar { display: flex; align-items: center; gap: 12px; margin: 6px 0; }
        .cap-bar .name { width: 140px; text-align: right; }
        .cap-bar .bar-bg {
            flex: 1; height: 20px; background: var(--border);
            border-radius: 10px; overflow: hidden;
        }
        .cap-bar .bar-fill { height: 100%; border-radius: 10px; transition: width 0.3s; }
        .cap-bar .score { width: 40px; text-align: right; font-family: monospace; }
        textarea {
            width: 100%; min-height: 100px; background: var(--card);
            border: 1px solid var(--border); border-radius: 6px;
            color: var(--text); padding: 12px; font-family: inherit;
            resize: vertical; margin-bottom: 8px;
        }
        .btn {
            background: #238636; color: #fff; border: none;
            padding: 10px 24px; border-radius: 6px; cursor: pointer;
            font-size: 1em; font-weight: 600;
        }
        .btn:hover { background: #2ea043; }
        #response { white-space: pre-wrap; font-size: 0.95em; padding: 12px; }
        .msg { margin: 8px 0; padding: 8px 12px; border-radius: 6px; }
        .msg.you { background: #1f2937; }
        .msg.yue { background: #161b22; border-left: 3px solid var(--accent); }
        .msg .ts { font-size: 0.75em; color: #484f58; }
        .nav { display: flex; gap: 16px; margin-bottom: 20px; }
        .nav a { color: var(--accent); text-decoration: none; padding: 4px 0; }
        .nav a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <a href="/">Dashboard</a>
            <a href="/chat">Chat</a>
            <a href="/memory">Memory</a>
            <a href="/api/status" target="_blank">API</a>
            <a href="https://github.com/qq2667117339/yue-ai-products" target="_blank">GitHub</a>
        </div>

        <div id="root">
            <h1 id="title">Yue</h1>
            <p style="color: #8b949e;" id="subtitle">Loading...</p>
            <div id="content"></div>
        </div>
    </div>

    <script>
    const API = '';

    async function loadPage() {
        const path = window.location.pathname;
        document.getElementById('title').textContent = path === '/' ? 'Yue Dashboard' :
            path === '/chat' ? 'Chat with Yue' :
            path === '/memory' ? 'Memory Explorer' : 'Yue';

        if (path === '/') { await loadDashboard(); }
        else if (path === '/chat') { await loadChat(); }
        else if (path === '/memory') { await loadMemory(); }
    }

    async function loadDashboard() {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('subtitle').textContent =
            `Round ${data.rounds} · Score ${data.score.toFixed(3)} · ${data.reflections} reflections`;

        let html = '<div class="stat-row">';
        html += `<div class="stat"><div class="value">${data.rounds}</div><div class="label">Rounds</div></div>`;
        html += `<div class="stat"><div class="value">${data.score.toFixed(3)}</div><div class="label">Score</div></div>`;
        html += `<div class="stat"><div class="value">${data.reflections}</div><div class="label">Reflections</div></div>`;
        html += `<div class="stat"><div class="value">${data.conversations}</div><div class="label">Conversations</div></div>`;
        html += `<div class="stat"><div class="value">${data.facts}</div><div class="label">Facts</div></div>`;
        html += '</div>';

        html += '<h2>Capabilities</h2>';
        const colors = ['#58a6ff','#3fb950','#d29922','#f85149','#bc8cff','#79c0ff','#ffa657','#56d4dd'];
        let i = 0;
        for (const [name, score] of Object.entries(data.capabilities)) {
            const pct = (score * 100).toFixed(0);
            html += `<div class="cap-bar">
                <div class="name">${name}</div>
                <div class="bar-bg"><div class="bar-fill" style="width:${pct}%;background:${colors[i % colors.length]}"></div></div>
                <div class="score">${pct}%</div>
            </div>`;
            i++;
        }
        document.getElementById('content').innerHTML = html;
    }

    async function loadChat() {
        document.getElementById('subtitle').textContent = 'Talk to Yue (messages persist locally)';
        let html = '<div class="card">';
        html += '<div id="history"></div>';
        html += '<textarea id="input" placeholder="Type a message..." rows="3"></textarea>';
        html += '<button class="btn" onclick="sendMessage()">Send</button>';
        html += '</div>';
        html += '<div class="card"><div id="response">Response will appear here.</div></div>';
        document.getElementById('content').innerHTML = html;

        // Load history
        const hres = await fetch('/api/history');
        const hist = await hres.json();
        const historyDiv = document.getElementById('history');
        for (const m of hist.messages || []) {
            const div = document.createElement('div');
            div.className = 'msg ' + m.role;
            div.innerHTML = '<strong>' + (m.role === 'user' ? 'you' : 'yue') + '</strong> ' +
                m.content.slice(0, 200) + '<br><span class="ts">' + new Date(m.ts * 1000).toLocaleString() + '</span>';
            historyDiv.appendChild(div);
        }

        document.getElementById('input').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
        });
    }

    async function sendMessage() {
        const input = document.getElementById('input');
        const msg = input.value.trim();
        if (!msg) return;
        input.value = '';

        const resp = document.getElementById('response');
        resp.textContent = 'Yue is thinking...';

        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: msg})
        });
        const data = await res.json();
        resp.textContent = data.response || '[No response]';

        // Refresh history
        const hres = await fetch('/api/history');
        const hist = await hres.json();
        const historyDiv = document.getElementById('history');
        historyDiv.innerHTML = '';
        for (const m of (hist.messages || []).slice(-20)) {
            const div = document.createElement('div');
            div.className = 'msg ' + m.role;
            div.innerHTML = '<strong>' + (m.role === 'user' ? 'you' : 'yue') + '</strong> ' +
                m.content.slice(0, 200) + '<br><span class="ts">' + new Date(m.ts * 1000).toLocaleString() + '</span>';
            historyDiv.appendChild(div);
        }
    }

    async function loadMemory() {
        const res = await fetch('/api/memory');
        const data = await res.json();
        document.getElementById('subtitle').textContent = `${data.facts} facts · ${data.learnings} learnings · ${data.conversations} conversations`;

        let html = '<div class="card"><h2>Facts</h2><ul>';
        for (const f of data.facts_list || []) {
            html += '<li>' + f.slice(0, 150) + '</li>';
        }
        html += '</ul></div>';
        html += '<div class="card"><h2>Learnings</h2><ul>';
        for (const l of data.patterns || []) {
            html += '<li>' + l.slice(0, 150) + '</li>';
        }
        html += '</ul></div>';
        document.getElementById('content').innerHTML = html;
    }

    loadPage();
    </script>
</body>
</html>
"""


# ── HTTP Request Handler ──────────────────────────────────────────
class YueAPIHandler(BaseHTTPRequestHandler):
    """REST API + Web Dashboard for Yue persona engine."""

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def _send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _send_error(self, msg, status=400):
        self._send_json({"error": msg}, status)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}

    def log_message(self, fmt, *args):
        """Suppress default logging, use cleaner format."""
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [API {ts}] {self.command} {self.path}")

    # ── Routes ──────────────────────────────────────────────────
    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/" or path == "/dashboard":
            self._send_html(DASHBOARD_HTML)
        elif path == "/chat":
            self._send_html(DASHBOARD_HTML)
        elif path == "/memory":
            self._send_html(DASHBOARD_HTML)
        elif path == "/api/status":
            self._handle_status()
        elif path == "/api/history":
            self._handle_history()
        elif path == "/api/memory":
            self._handle_memory()
        elif path == "/api/persona":
            self._handle_persona()
        else:
            # SPA: serve dashboard for all frontend routes
            self._send_html(DASHBOARD_HTML)

    def do_POST(self):
        path = urlparse(self.path).path

        if path == "/api/chat":
            self._handle_chat()
        elif path == "/api/reflect":
            self._handle_reflect()
        elif path == "/api/remember":
            self._handle_remember()
        elif path == "/api/reset":
            self._handle_reset()
        else:
            self._send_error("Not found", 404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ── API Handlers ────────────────────────────────────────────
    def _handle_status(self):
        evo_status = evo.get_status()
        mem_stats = mem.get_stats()
        self._send_json({
            "name": PERSONA["name"],
            "native_name": PERSONA["native_name"],
            "rounds": evo_status["rounds"],
            "score": evo_status["score"],
            "reflections": evo_status["reflections"],
            "conversations": mem_stats["conversations"],
            "facts": mem_stats["facts_known"],
            "learnings": mem_stats["learnings"],
            "capabilities": evo_status["capabilities"],
            "version": "1.0.0",
            "status": "online",
        })

    def _handle_history(self):
        self._send_json({
            "messages": mem.session[-50],
        })

    def _handle_memory(self):
        self._send_json({
            "conversations": mem.longterm.get("conv_count", 0),
            "facts": len(mem.longterm.get("facts", [])),
            "learnings": len(mem.learnings.get("patterns", [])),
            "facts_list": mem.longterm.get("facts", [])[-20:],
            "patterns": mem.learnings.get("patterns", [])[-10:],
            "errors": mem.learnings.get("errors", [])[-10:],
        })

    def _handle_persona(self):
        self._send_json({
            "persona": PERSONA,
            "model": llm.model,
            "ollama_host": llm.base,
        })

    def _handle_chat(self):
        body = self._read_body()
        message = body.get("message", "").strip()
        if not message:
            return self._send_error("Message is required")

        mem.add("user", message)

        if llm.check_available():
            response = llm.generate(message, mem.session[-10:])
        else:
            response = (
                f"[Yue is currently in offline mode - Ollama not detected]\n\n"
                f"I received: \"{message}\"\n\n"
                f"Start Ollama to enable full responses: `ollama run qwen2.5:32b`"
            )

        mem.add("assistant", response)
        evo.record_interaction()

        self._send_json({
            "response": response,
            "round": evo.get_status()["rounds"],
            "score": evo.get_status()["score"],
        })

    def _handle_reflect(self):
        evo.record_interaction()
        evo._reflect()
        status = evo.get_status()
        self._send_json({
            "reflected": True,
            "score": status["score"],
            "rounds": status["rounds"],
            "capabilities": status["capabilities"],
        })

    def _handle_remember(self):
        body = self._read_body()
        fact = body.get("fact", "").strip()
        if not fact:
            return self._send_error("Fact is required")
        mem.remember_fact(fact)
        self._send_json({
            "memorized": True,
            "fact": fact,
            "total_facts": len(mem.longterm.get("facts", [])),
        })

    def _handle_reset(self):
        mem.session = []
        self._send_json({"reset": True, "message": "Session cleared"})


# ── Server Runner ─────────────────────────────────────────────────
def start_server(port=PORT, host=HOST, open_browser=False):
    """Start the Yue API server."""
    server = HTTPServer((host, port), YueAPIHandler)
    url = f"http://{host}:{port}"

    print(f"  Yue API Server running at:")
    print(f"    Dashboard: {url}")
    print(f"    API:       {url}/api/status")
    print(f"    Chat:      {url}/chat")
    print()
    print(f"  Capabilities: {evo.get_status()['score']:.3f}")
    print(f"  Ollama: {'Connected' if llm.check_available() else 'Not running (offline mode)'}")
    print()

    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


def main():
    """CLI entry point for the server."""
    args = sys.argv[1:]
    port = PORT
    host = HOST
    browser = False

    for i, arg in enumerate(args):
        if arg == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
        elif arg == "--host" and i + 1 < len(args):
            host = args[i + 1]
        elif arg == "--open":
            browser = True
        elif arg in ("--help", "-h"):
            print("Usage: yue-server [--port PORT] [--host HOST] [--open]")
            sys.exit(0)

    start_server(port=port, host=host, open_browser=browser)


if __name__ == "__main__":
    main()
