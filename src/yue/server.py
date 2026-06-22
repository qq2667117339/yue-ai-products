"""
Yue HTTP API Server — REST API + web chat for the Yue persona engine.
Usage:  yue-server              # Default port 18791
        yue-server --port 8888  # Custom port
"""

import json, os, sys, time, threading, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))
from yue.persona import Memory, EvolutionEngine, OllamaClient, PERSONA, HOME

HOST = "127.0.0.1"
PORT = 18792
mem = Memory()
evo = EvolutionEngine()
llm = OllamaClient()

# ── Embedded HTML (chat-focused) ─────────────────────────────────


# ── System Awareness ───────────────────────────────────────────────
def get_system_stats():
    """Get basic system stats. Returns dict or error message."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("C:")
        net = psutil.net_io_counters()
        procs = len(psutil.pids())
        return {
            "cpu": cpu,
            "ram_total_gb": round(mem.total / (1024**3), 1),
            "ram_used_gb": round(mem.used / (1024**3), 1),
            "ram_percent": mem.percent,
            "disk_c_percent": disk.percent,
            "disk_c_free_gb": round(disk.free / (1024**3), 1),
            "processes": procs,
            "net_sent_mb": round(net.bytes_sent / (1024**2), 1),
            "net_recv_mb": round(net.bytes_recv / (1024**2), 1),
            "hostname": os.environ.get("COMPUTERNAME", "unknown"),
            "user": os.environ.get("USERNAME", "unknown"),
        }
    except ImportError:
        return {"error": "psutil not installed"}
    except Exception as e:
        return {"error": str(e)}

def get_camera_info():
    """Check if camera is available."""
    try:
        import cv2
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                h, w = frame.shape[:2]
                return {"available": True, "resolution": f"{w}x{h}"}
        return {"available": False, "reason": "Camera not found or busy"}
    except ImportError:
        return {"available": False, "reason": "opencv-python not installed"}
    except Exception as e:
        return {"available": False, "reason": str(e)}

def get_audio_info():
    """Check audio devices."""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        devices = p.get_device_count()
        inputs = sum(1 for i in range(devices) if p.get_device_info_by_index(i).get("maxInputChannels", 0) > 0)
        outputs = sum(1 for i in range(devices) if p.get_device_info_by_index(i).get("maxOutputChannels", 0) > 0)
        p.terminate()
        return {"devices": devices, "mic_count": inputs, "speaker_count": outputs}
    except ImportError:
        return {"error": "pyaudio not installed"}
    except Exception as e:
        return {"error": str(e)}


CHAT_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0">
<title>Yue - Chat</title>
<style>
:root{--bg:#111118;--surface:#1a1a24;--border:#2a2a3a;--text:#e0e0f0;--text-dim:#8888a0;--accent:#7c6df0;--accent2:#58a6ff;--green:#4ade80;--msg-user:#2d2d44;--msg-assistant:#1e1e30;--radius:12px}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;flex-direction:column}
.header{display:flex;align-items:center;gap:12px;padding:12px 16px;background:var(--surface);border-bottom:1px solid var(--border);flex-shrink:0}
.header .avatar{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#7c6df0,#a78bfa);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;color:#fff;flex-shrink:0}
.header .info{flex:1}.header .name{font-weight:600;font-size:15px}
.header .status{font-size:12px;color:var(--text-dim)}.header .status.online{color:var(--green)}
.header .nav{display:flex;gap:4px}.header .nav a{color:var(--text-dim);text-decoration:none;padding:4px 10px;border-radius:6px;font-size:12px;transition:all .15s}
.header .nav a:hover{background:var(--border);color:var(--text)}
.messages{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:8px;scroll-behavior:smooth}
.messages .empty{text-align:center;color:var(--text-dim);padding:40px 20px;font-size:14px;line-height:1.8}
.messages .empty .big{font-size:40px;margin-bottom:12px}
.msg{max-width:85%;padding:10px 14px;border-radius:var(--radius);font-size:14px;line-height:1.6;word-wrap:break-word;animation:fadeIn .2s ease}
.msg.user{align-self:flex-end;background:var(--msg-user);border-bottom-right-radius:4px}
.msg.assistant{align-self:flex-start;background:var(--msg-assistant);border-bottom-left-radius:4px;border-left:2px solid var(--accent)}
.msg .ts{font-size:11px;color:var(--text-dim);margin-top:4px;text-align:right}
.msg .sender{font-size:11px;color:var(--accent2);margin-bottom:2px;font-weight:500}
.msg.typing{background:transparent;border-left:2px solid var(--accent);padding:10px 14px}
.msg.typing .dots{display:inline-flex;gap:4px}
.msg.typing .dot{width:6px;height:6px;background:var(--text-dim);border-radius:50%;animation:bounce 1.4s infinite}
.msg.typing .dot:nth-child(2){animation-delay:.2s}
.msg.typing .dot:nth-child(3){animation-delay:.4s}
@keyframes bounce{0%,60%,100%{transform:translateY(0)}30%{transform:translateY(-6px)}}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.input-area{flex-shrink:0;padding:12px 16px;background:var(--surface);border-top:1px solid var(--border)}
.input-row{display:flex;gap:8px;align-items:flex-end}
.input-row textarea{flex:1;background:var(--bg);border:1px solid var(--border);border-radius:10px;color:var(--text);padding:10px 14px;font-size:14px;font-family:inherit;resize:none;min-height:42px;max-height:120px;outline:none;transition:border-color .15s}
.input-row textarea:focus{border-color:var(--accent)}
.input-row textarea::placeholder{color:var(--text-dim)}
.input-row .send-btn{width:42px;height:42px;border-radius:50%;background:var(--accent);border:none;color:#fff;font-size:18px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:background .15s}
.input-row .send-btn:hover{background:#6a5ce0}.input-row .send-btn:disabled{background:var(--border);cursor:not-allowed}
.input-row .voice-btn{width:42px;height:42px;border-radius:50%;background:var(--surface);border:1px solid var(--border);color:var(--text);font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s}
.input-row .voice-btn:hover{border-color:var(--accent);background:rgba(124,109,240,.1)}
.input-row .voice-btn.active{background:#f85149;border-color:#f85149;color:#fff}
.dash-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:16px}
.dash-stat{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center}
.dash-stat .v{font-size:1.6em;font-weight:700;color:var(--accent)}
.dash-stat .l{font-size:11px;color:var(--text-dim);margin-top:2px}
.dash-cap{margin:4px 0;display:flex;align-items:center;gap:8px}
.dash-cap .n{width:110px;font-size:12px;text-align:right;color:var(--text-dim);flex-shrink:0}
.dash-cap .b{flex:1;height:6px;background:var(--border);border-radius:3px;overflow:hidden}
.dash-cap .f{height:100%;border-radius:3px;transition:width .3s}
.dash-cap .s{width:32px;font-size:11px;text-align:right;font-family:monospace;color:var(--text-dim)}
@media(max-width:500px){.header .nav{display:none}.msg{max-width:92%}}
</style>
</head>
<body>
<div class="header">
  <div class="avatar">Y</div>
  <div class="info">
    <div class="name">Yue</div>
    <div class="status online" id="statusText">Online</div>
  </div>
  <div class="nav">
    <a href="#" onclick="return showPage('chat')">Chat</a>
    <a href="#" onclick="return showPage('dashboard')">Status</a>
    <a href="#" onclick="return showPage('memory')">Memory</a>
    <a href="#" onclick="return showPage('system')">System</a>
  </div>
</div>
<div class="messages" id="messages">
  <div class="empty" id="emptyMsg">
    <div class="big">&#x1F319;</div>
    <div>Talk to Yue.</div>
    <div style="font-size:12px;color:#666">Messages persist across sessions.</div>
  </div>
</div>
<div class="input-area">
  <div class="input-row">
    <textarea id="input" placeholder="Type a message..." rows="1"></textarea>
    <button class="voice-btn" id="voiceBtn" onclick="toggleMic()" title="Voice input">&#x1F3A4;</button>
    <button class="send-btn" id="sendBtn" onclick="send()">&#x27A4;</button>
  </div>
  <div style="display:flex;gap:8px;margin-top:6px;font-size:11px;color:var(--text-dim)">
    <label><input type="checkbox" id="autoTTS" checked> Auto-speak replies</label>
    <label><input type="checkbox" id="autoListen"> Voice wake</label>
  </div>
</div>
<div id="dashView" style="display:none"></div>
<div id="memView" style="display:none"></div>
<div id="sysView" style="display:none"></div>
<script>
const msgEl=document.getElementById('messages');
const inputEl=document.getElementById('input');
const sendBtn=document.getElementById('sendBtn');
const emptyMsg=document.getElementById('emptyMsg');
function addMsg(role,content,ts){
  emptyMsg.style.display='none';
  const d=document.createElement('div');
  d.className='msg '+role;
  const t=ts?new Date(ts*1000).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'}):new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});
  d.innerHTML=(role==='assistant'?'<div class="sender">Yue</div>':'')+content+'<div class="ts">'+t+'</div>';
  msgEl.appendChild(d);
  msgEl.scrollTop=msgEl.scrollHeight;
}
function typingOn(){
  const d=document.createElement('div');
  d.className='msg typing';d.id='typing';
  d.innerHTML='<div class="dots"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>';
  msgEl.appendChild(d);msgEl.scrollTop=msgEl.scrollHeight;
}
function typingOff(){const e=document.getElementById('typing');if(e)e.remove()}
async function send(){
  const msg=inputEl.value.trim();
  if(!msg)return;
  inputEl.value='';inputEl.style.height='auto';sendBtn.disabled=true;
  addMsg('user',msg.replace(/\n/g,'<br>'));
  typingOn();
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:msg})});
    const d=await r.json();
    typingOff();
    addMsg('assistant',(d.response||'[No response]').replace(/\n/g,'<br>'));
  }catch(e){typingOff();addMsg('assistant','[Connection error]');}
  sendBtn.disabled=false;msgEl.scrollTop=msgEl.scrollHeight;
}
inputEl.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
inputEl.addEventListener('input',()=>{inputEl.style.height='auto';inputEl.style.height=Math.min(inputEl.scrollHeight,120)+'px'});
async function loadHistory(){
  const r=await fetch('/api/history');
  const d=await r.json();
  for(const m of(d.messages||[]).slice(-50)){
    addMsg(m.role,(m.content||'').slice(0,5000).replace(/\n/g,'<br>'),m.ts);
  }
}
loadHistory();
function showPage(p){
  document.getElementById('dashView').style.display='none';
  document.getElementById('memView').style.display='none';
  msgEl.style.display='flex';
  document.querySelector('.input-area').style.display='flex';
  document.getElementById('statusText').className='status online';
  if(p==='dashboard')loadDashboard();
  if(p==='memory')loadMemory();
  return false;
}
async function loadDashboard(){
  msgEl.style.display='none';document.querySelector('.input-area').style.display='none';
  const dv=document.getElementById('dashView');dv.style.display='block';
  const r=await fetch('/api/status');const d=await r.json();
  document.getElementById('statusText').textContent='Round '+d.rounds+' Score '+d.score.toFixed(2);
  let html='<div class="dash-stats">';
  html+='<div class="dash-stat"><div class="v">'+d.rounds+'</div><div class="l">Rounds</div></div>';
  html+='<div class="dash-stat"><div class="v">'+d.score.toFixed(3)+'</div><div class="l">Score</div></div>';
  html+='<div class="dash-stat"><div class="v">'+d.reflections+'</div><div class="l">Reflections</div></div>';
  html+='<div class="dash-stat"><div class="v">'+d.conversations+'</div><div class="l">Conversations</div></div>';
  html+='<div class="dash-stat"><div class="v">'+d.facts+'</div><div class="l">Facts</div></div>';
  html+='</div><h3 style="margin:16px 0 12px;font-size:14px;color:var(--text-dim)">Capabilities</h3>';
  const cols=['#7c6df0','#58a6ff','#4ade80','#fbbf24','#f85149','#bc8cff','#ffa657','#56d4dd'];
  let i=0;
  for(const[n,s]of Object.entries(d.capabilities||{})){
    const p=(s*100).toFixed(0);
    html+='<div class="dash-cap"><div class="n">'+n+'</div><div class="b"><div class="f" style="width:'+p+'%;background:'+cols[i%cols.length]+'"></div></div><div class="s">'+p+'%</div></div>';
    i++;
  }
  dv.innerHTML='<div style="padding:16px">'+html+'</div>';
}
async function loadMemory(){
  msgEl.style.display='none';document.querySelector('.input-area').style.display='none';
  const mv=document.getElementById('memView');mv.style.display='block';
  const r=await fetch('/api/memory');const d=await r.json();
  document.getElementById('statusText').textContent=d.facts+' facts';
  let html='<div style="padding:16px"><h3 style="margin-bottom:12px;font-size:14px;color:var(--text-dim)">'+d.facts+' facts</h3>';
  for(const f of(d.facts_list||[]))html+='<div style="padding:6px 10px;margin:4px 0;background:var(--surface);border-radius:6px;font-size:13px">'+f.slice(0,200)+'</div>';
  html+='<h3 style="margin:16px 0 12px;font-size:14px;color:var(--text-dim)">Learnings</h3>';
  for(const l of(d.patterns||[]))html+='<div style="padding:6px 10px;margin:4px 0;background:var(--surface);border-radius:6px;font-size:13px">'+l.slice(0,200)+'</div>';
  mv.innerHTML=html+'</div>';
}

// ── Voice I/O (Web Speech API) ──
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognizer = null;
let isListening = false;
let voiceBtn = document.getElementById('voiceBtn');

function speakText(text) {
  if(!document.getElementById('autoTTS').checked) return;
  if(!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = 'zh-CN';
  u.rate = 1.0;
  u.pitch = 1.0;
  // Pick a Chinese voice if available
  const voices = window.speechSynthesis.getVoices();
  const zh = voices.find(v => v.lang.startsWith('zh'));
  if(zh) u.voice = zh;
  window.speechSynthesis.speak(u);
}

function toggleMic() {
  if(!SpeechRecognition) { alert('Speech recognition not supported in this browser. Try Chrome/Edge.'); return; }
  if(isListening) { stopListening(); return; }
  startListening();
}

function startListening() {
  if(!SpeechRecognition) return;
  recognizer = new SpeechRecognition();
  recognizer.lang = 'zh-CN';
  recognizer.continuous = false;
  recognizer.interimResults = true;
  
  voiceBtn.textContent = '🔴';
  voiceBtn.style.background = '#f85149';
  isListening = true;
  
  let finalText = '';
  recognizer.onresult = function(e) {
    for(let i = e.resultIndex; i < e.results.length; i++) {
      if(e.results[i].isFinal) finalText += e.results[i][0].transcript;
    }
    inputEl.placeholder = finalText || 'Listening...';
  };
  
  recognizer.onend = function() {
    voiceBtn.textContent = '🎤';
    voiceBtn.style.background = '';
    isListening = false;
    if(finalText.trim()) {
      inputEl.value = finalText;
      inputEl.placeholder = 'Type a message...';
      send();
    }
  };
  
  recognizer.start();
}

function stopListening() {
  if(recognizer) { recognizer.abort(); recognizer = null; }
  voiceBtn.textContent = '🎤';
  voiceBtn.style.background = '';
  isListening = false;
  inputEl.placeholder = 'Type a message...';
}

// Auto-speak on response
const origAddMsg = addMsg;
addMsg = function(role, content, ts) {
  origAddMsg(role, content, ts);
  if(role === 'assistant' && document.getElementById('autoTTS').checked) {
    setTimeout(() => speakText(content.replace(/<br>/g,' ').replace(/<[^>]*>/g,'')), 300);
  }
};

// ── System View ──
async function loadSystem(){
  msgEl.style.display='none';document.querySelector('.input-area').style.display='none';
  const sv=document.getElementById('sysView');sv.style.display='block';
  document.getElementById('statusText').textContent='System Monitor';
  
  const r=await fetch('/api/system');const d=await r.json();
  if(d.error){sv.innerHTML='<div style="padding:16px;color:#f85149">'+d.error+'</div>';return;}
  
  let html='<div style="padding:16px"><h3 style="margin-bottom:12px">System Status</h3>';
  html+='<div class="dash-stats">';
  html+='<div class="dash-stat"><div class="v">'+d.cpu+'%</div><div class="l">CPU</div></div>';
  html+='<div class="dash-stat"><div class="v">'+d.ram_percent+'%</div><div class="l">RAM</div></div>';
  html+='<div class="dash-stat"><div class="v">'+d.disk_c_percent+'%</div><div class="l">Disk C</div></div>';
  html+='<div class="dash-stat"><div class="v">'+d.processes+'</div><div class="l">Processes</div></div>';
  html+='</div>';
  html+='<div style="font-size:13px;color:var(--text-dim);line-height:2">';
  html+='Host: '+d.hostname+' | User: '+d.user+'<br>';
  html+='RAM: '+d.ram_used_gb+'/'+d.ram_total_gb+' GB<br>';
  html+='Disk C free: '+d.disk_c_free_gb+' GB<br>';
  html+='Network: '+d.net_sent_mb+'MB sent / '+d.net_recv_mb+'MB received';
  html+='</div></div>';
  
  // Camera status
  const cr=await fetch('/api/camera');const cd=await cr.json();
  html+='<div style="padding:16px;margin-top:8px"><h3 style="margin-bottom:8px">Peripherals</h3>';
  html+='<div style="font-size:13px;color:var(--text-dim)">Camera: '+(cd.available?'<span style="color:#4ade80">Available</span> '+cd.resolution:'<span style="color:#f85149">Unavailable</span>')+'</div>';
  
  // Audio status
  const ar=await fetch('/api/audio');const ad=await ar.json();
  if(!ad.error) html+='<div style="font-size:13px;color:var(--text-dim)">Mic: '+ad.mic_count+' | Speaker: '+ad.speaker_count+' | Total devices: '+ad.devices+'</div>';
  html+='<button class="btn" onclick="takePhoto()" style="margin-top:12px">Take Photo</button>';
  html+='<div id="photoView" style="margin-top:8px"></div>';
  html+='<button class="btn" onclick="evolve()" style="margin-top:8px;background:var(--accent);color:#fff;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;font-size:13px">⚡ Auto-Evolve</button>';
  html+='<div id="evolveResult" style="margin-top:8px;font-size:13px;color:var(--green)"></div>';
  html+='</div>';
  
  sv.innerHTML=html;
}

async function takePhoto(){
  const pv=document.getElementById('photoView');
  pv.innerHTML='<span style="color:var(--text-dim)">Requesting camera...</span>';
  try{
    const stream=await navigator.mediaDevices.getUserMedia({video:{width:640,height:480}});
    const video=document.createElement('video');
    video.srcObject=stream;video.play();
    await new Promise(r=>setTimeout(r,300));
    const canvas=document.createElement('canvas');
    canvas.width=video.videoWidth||640;canvas.height=video.videoHeight||480;
    canvas.getContext('2d').drawImage(video,0,0);
    stream.getTracks().forEach(t=>t.stop());
    pv.innerHTML='<img src="'+canvas.toDataURL('image/jpeg',0.8)+'" style="max-width:100%;border-radius:8px;border:1px solid var(--border)"/>';
  }catch(e){
    pv.innerHTML='<span style="color:#f85149">Camera access denied or not available: '+e.message+'</span>';
  }
}

function showPage(p){
  document.getElementById('dashView').style.display='none';
  document.getElementById('memView').style.display='none';
  document.getElementById('sysView').style.display='none';
  msgEl.style.display='flex';
  document.querySelector('.input-area').style.display='flex';
  document.getElementById('statusText').className='status online';
  if(p==='dashboard')loadDashboard();
  if(p==='memory')loadMemory();
  if(p==='system')loadSystem();
  return false;
}

async function evolve(){
  const el=document.getElementById('evolveResult');
  el.textContent='Running autonomous evolution...';
  try{
    const r=await fetch('/api/evolve',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cycles:10})});
    const d=await r.json();
    let txt='Evolved '+d.cycles+' cycles. Score: '+(d.final_score*100).toFixed(1)+'%';
    if(d.history&&d.history.length){
      const d0=d.history[0].delta;
      const d1=d.history[d.history.length-1].delta;
      txt+=' (change: '+(d0>0?'+':'')+d0.toFixed(3)+' → '+(d1>0?'+':'')+d1.toFixed(3)+')';
    }
    el.textContent=txt;
    // Refresh dashboard stats
    if(document.getElementById('dashView').style.display!=='none') loadDashboard();
  }catch(e){el.textContent='Evolution failed: '+e.message;}
}

// Dashboard auto-refresh
let dashInterval = null;
function startDashRefresh(){
  if(dashInterval) clearInterval(dashInterval);
  dashInterval = setInterval(loadDashboard, 5000);
}

const _origShowPage = window.showPage;
window.showPage = function(p){
  if(dashInterval){clearInterval(dashInterval);dashInterval=null;}
  if(p==='dashboard'){
    _origShowPage(p);
    startDashRefresh();
  }else{
    _origShowPage(p);
  }
};
</script>
</body>
</html>"""

# ── HTTP Request Handler ──────────────────────────────────────────
class YueAPIHandler(BaseHTTPRequestHandler):
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
        try:
            return json.loads(self.rfile.read(length))
        except json.JSONDecodeError:
            return {}

    def log_message(self, fmt, *args):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [API {ts}] {self.command} {self.path}")

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/chat"):
            self._send_html(CHAT_HTML)
        elif path == "/dashboard":
            self._send_html(CHAT_HTML)
        elif path == "/memory":
            self._send_html(CHAT_HTML)
        elif path == "/api/status":
            self._handle_status()
        elif path == "/api/history":
            self._handle_history()
        elif path == "/api/memory":
            self._handle_memory()
        elif path == "/api/persona":
            self._handle_persona()
        elif path == "/api/system":
            self._handle_system()
        elif path == "/api/camera":
            self._handle_camera()
        elif path == "/api/audio":
            self._handle_audio()
        else:
            self._send_html(CHAT_HTML)

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
        elif path == "/api/evolve":
            self._handle_evolve()
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
        self._send_json({"messages": mem.session[-50:]})

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
        self._send_json({"persona": PERSONA, "model": llm.model, "ollama_host": llm.base})

    def _handle_chat(self):
        body = self._read_body()
        message = body.get("message", "").strip()
        if not message:
            return self._send_error("Message is required")
        mem.add("user", message)
        # OllamaClient.generate() handles both online/offline via ResponseFallback
        response = llm.generate(message, mem.session[-10:])
        mem.add("assistant", response)
        evo.record_interaction(caps_used=["communication", "reasoning"])
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
        self._send_json({"memorized": True, "fact": fact, "total_facts": len(mem.longterm.get("facts", []))})

    def _handle_reset(self):
        mem.session = []
        self._send_json({"reset": True, "message": "Session cleared"})

    def _handle_evolve(self):
        body = self._read_body()
        cycles = min(body.get("cycles", 3), 50)
        result = evo.self_evolve(cycles=cycles)
        self._send_json({
            "evolved": True,
            "cycles": result["cycles"],
            "final_score": result["final_score"],
            "history": result["results"],
        })

    def _handle_system(self):
        self._send_json(get_system_stats())

    def _handle_camera(self):
        self._send_json(get_camera_info())

    def _handle_audio(self):
        self._send_json(get_audio_info())

# ── Server Runner ─────────────────────────────────────────────────
def start_server(port=PORT, host=HOST, open_browser=False):
    server = HTTPServer((host, port), YueAPIHandler)
    url = f"http://{host}:{port}"
    status = evo.get_status()
    print(f"  Yue Chat Server running at:")
    print(f"    Chat:   {url}/chat (opens in browser)")
    print(f"    Status: {url}/dashboard")
    print(f"    Memory: {url}/memory")
    print(f"    API:    {url}/api/status")
    print(f"  Score: {status['score']:.3f} | Rounds: {status['rounds']}")
    print(f"  Ollama: {'Connected' if llm.check_available() else 'Not running (offline)'}")
    if open_browser:
        webbrowser.open(url + "/chat")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()

def main():
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
