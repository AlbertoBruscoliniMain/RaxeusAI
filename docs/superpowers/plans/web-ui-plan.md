# Web UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere un'interfaccia web Flask a RaxeusAI che sostituisce il terminale, con tab, streaming SSE, color picker per la bolla utente e persistenza sessioni.

**Architecture:** Flask serve una SPA (`index.html`). Il backend espone 4 endpoint; lo streaming dei token avviene via SSE. `agent.py` e `sessions.py` non vengono modificati — `app.py` crea una propria istanza di `Memory` per ogni sessione attiva, mantenuta in un dizionario in memoria.

**Tech Stack:** Flask, vanilla JS (ES6), CSS custom, SSE, localStorage

---

## File map

| File | Azione | Responsabilità |
|---|---|---|
| `app.py` | Crea | Server Flask, endpoint REST + SSE, gestione sessioni in memoria |
| `templates/index.html` | Crea | Markup SPA completo |
| `static/style.css` | Crea | Tema scuro, layout topbar + chat + input |
| `static/app.js` | Crea | Logica tab, SSE streaming, color picker, localStorage |
| `requirements.txt` | Modifica | Aggiunge `flask` |
| `CODE.md` | Modifica | Documenta i 4 nuovi file |
| `THEORY.md` | Modifica | Spiega SSE e architettura web |

---

### Task 1: Dipendenza Flask

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Aggiungi flask a requirements.txt**

Contenuto finale del file:
```
openai
ddgs
googlesearch-python
requests
beautifulsoup4
pypdf
flask
```

- [ ] **Step 2: Installa nel venv**

```bash
source venv/bin/activate
pip install flask
```

Output atteso: `Successfully installed flask-3.x.x`

- [ ] **Step 3: Verifica import**

```bash
python -c "import flask; print(flask.__version__)"
```

Output atteso: numero di versione senza errori.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "deps: add flask"
```

---

### Task 2: Backend Flask — app.py

**Files:**
- Create: `app.py`

Il backend mantiene un dizionario `sessions: dict[str, Memory]` — una `Memory` per session_id. Le sessioni vengono caricate da disco quando richieste e non esistono ancora in memoria.

- [ ] **Step 1: Crea app.py**

```python
import json
import uuid
from flask import Flask, request, Response, render_template, jsonify
from memory import Memory
from agent import chat_stream
from sessions import save_session, list_sessions, load_session

app = Flask(__name__)

# session_id -> Memory
_sessions: dict[str, Memory] = {}


def _get_memory(session_id: str) -> Memory:
    if session_id not in _sessions:
        mem = Memory()
        saved = list_sessions()
        if session_id in saved:
            messages = load_session(session_id)
            mem.load(messages)
        _sessions[session_id] = mem
    return _sessions[session_id]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    session_id = data.get("session_id", str(uuid.uuid4()))
    if not message:
        return jsonify({"error": "messaggio vuoto"}), 400

    mem = _get_memory(session_id)

    def generate():
        yield f"data: {json.dumps({'type': 'session_id', 'value': session_id})}\n\n"
        for event in chat_stream(message, mem):
            yield f"data: {json.dumps(event)}\n\n"
        save_session(mem.get())

    return Response(generate(), mimetype="text/event-stream",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"})


@app.route("/sessions")
def get_sessions():
    return jsonify(list_sessions()[:5])


@app.route("/session/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    import os
    from pathlib import Path
    path = Path(__file__).parent / "sessions" / f"session_{session_id}.json"
    if path.exists():
        os.remove(path)
    _sessions.pop(session_id, None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
```

- [ ] **Step 2: Aggiungi chat_stream ad agent.py**

`chat_stream` è una versione generator di `chat` che yielda eventi invece di stampare. Aggiungila in fondo ad `agent.py` senza toccare la funzione `chat` esistente:

```python
def chat_stream(user_input: str, mem: Memory):
    """Generator che yielda eventi SSE per la web UI."""
    mem.add("user", user_input)

    while True:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=mem.get(),
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            stream=True,
        )

        full_content = ""
        tool_calls_acc = {}

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                full_content += delta.content
                yield {"type": "token", "content": delta.content}

            if delta.tool_calls:
                yield {"type": "thinking"}
                for tc in delta.tool_calls:
                    i = tc.index
                    if i not in tool_calls_acc:
                        tool_calls_acc[i] = {"id": "", "name": "", "arguments": ""}
                    if tc.id:
                        tool_calls_acc[i]["id"] = tc.id
                    if tc.function and tc.function.name:
                        tool_calls_acc[i]["name"] = tc.function.name
                    if tc.function and tc.function.arguments:
                        tool_calls_acc[i]["arguments"] += tc.function.arguments

        if tool_calls_acc:
            tool_calls_list = [
                {
                    "id": tool_calls_acc[i]["id"],
                    "type": "function",
                    "function": {
                        "name": tool_calls_acc[i]["name"],
                        "arguments": tool_calls_acc[i]["arguments"],
                    },
                }
                for i in sorted(tool_calls_acc)
            ]
            mem.add_assistant_tool_calls(full_content, tool_calls_list)
            for tc in tool_calls_list:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}
                result = execute_tool(name, args)
                mem.add_tool_result(tc["id"], name, result)
        else:
            mem.add("assistant", full_content)
            yield {"type": "done"}
            return
```

- [ ] **Step 3: Aggiungi import json in agent.py se non presente**

Controlla la prima riga di `agent.py` — `import json` deve già esserci. Se manca aggiungila.

- [ ] **Step 4: Testa gli endpoint a mano**

```bash
source venv/bin/activate
python app.py &
curl http://localhost:5000/sessions
```

Output atteso: `[]` oppure lista JSON di session id.

```bash
kill %1
```

- [ ] **Step 5: Commit**

```bash
git add app.py agent.py
git commit -m "feat: Flask backend con SSE streaming"
```

---

### Task 3: Markup HTML — templates/index.html

**Files:**
- Create: `templates/index.html`

- [ ] **Step 1: Crea la cartella templates**

```bash
mkdir -p templates
```

- [ ] **Step 2: Crea templates/index.html**

```html
<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Raxeus</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>

  <div id="topbar">
    <span id="logo">Raxeus</span>

    <div id="search-wrap">
      <input id="search" type="text" placeholder="cerca...">
    </div>

    <div id="tabs"></div>

    <button id="btn-new">+</button>

    <div id="color-dot-wrap">
      <div id="color-dot"></div>
      <div id="color-picker" class="hidden">
        <div class="picker-label">Colore bolla</div>
        <div id="presets"></div>
        <input type="color" id="custom-color" title="Colore custom">
      </div>
    </div>
  </div>

  <div id="chat-area"></div>

  <div id="input-wrap">
    <div id="input-bar">
      <textarea id="msg-input" rows="1" placeholder="Messaggio..."></textarea>
      <button id="btn-send">invia</button>
    </div>
  </div>

  <script src="/static/app.js"></script>
</body>
</html>
```

- [ ] **Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: markup HTML SPA"
```

---

### Task 4: Stile — static/style.css

**Files:**
- Create: `static/style.css`

- [ ] **Step 1: Crea la cartella static**

```bash
mkdir -p static
```

- [ ] **Step 2: Crea static/style.css**

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #0d0d0d;
  --bg2: #111;
  --border: #1a1a1a;
  --border2: #252525;
  --text: #c0c0c0;
  --text-dim: #555;
  --text-dimmer: #333;
  --accent: #555;
  --bubble-bg: #252525;
  --bubble-text: #c0c0c0;
}

html, body {
  height: 100%;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 14px;
  overflow: hidden;
}

/* TOPBAR */
#topbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 44px;
  background: var(--bg);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 14px;
  z-index: 100;
}

#logo {
  font-weight: 600;
  font-size: 13px;
  letter-spacing: 0.3px;
  color: var(--text);
  white-space: nowrap;
}

#search-wrap {
  flex-shrink: 0;
}

#search {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 5px;
  padding: 4px 9px;
  font-size: 11px;
  color: var(--text);
  width: 160px;
  outline: none;
}

#search::placeholder { color: var(--text-dimmer); }

#tabs {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 2px;
  overflow: hidden;
  height: 100%;
}

.tab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 11px;
  font-size: 11px;
  color: var(--text-dim);
  border-radius: 4px 4px 0 0;
  cursor: pointer;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  height: 100%;
  user-select: none;
}

.tab.active {
  background: var(--bg2);
  color: var(--text);
  border-bottom-color: var(--accent);
}

.tab .tab-close {
  font-size: 9px;
  color: var(--text-dimmer);
  line-height: 1;
  padding: 1px 2px;
  border-radius: 2px;
}

.tab .tab-close:hover { color: var(--text-dim); }

#btn-new {
  background: none;
  border: none;
  color: var(--text-dimmer);
  font-size: 16px;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

#btn-new:hover { color: var(--text-dim); }

/* PALLINO COLORE */
#color-dot-wrap {
  position: relative;
  flex-shrink: 0;
}

#color-dot {
  width: 11px;
  height: 11px;
  border-radius: 50%;
  background: var(--bubble-bg);
  border: 1.5px solid #666;
  cursor: pointer;
}

#color-picker {
  position: absolute;
  top: 22px;
  right: 0;
  background: #161616;
  border: 1px solid var(--border2);
  border-radius: 8px;
  padding: 10px 13px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  box-shadow: 0 6px 24px rgba(0,0,0,.7);
  z-index: 200;
}

#color-picker.hidden { display: none; }

.picker-label {
  font-size: 10px;
  color: var(--text-dimmer);
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

#presets {
  display: flex;
  gap: 7px;
  align-items: center;
}

.preset-dot {
  width: 17px;
  height: 17px;
  border-radius: 50%;
  border: 1px solid var(--border2);
  cursor: pointer;
  flex-shrink: 0;
}

.preset-dot.selected {
  border: 2px solid #aaa;
}

#custom-color {
  width: 17px;
  height: 17px;
  border-radius: 50%;
  border: 1px solid var(--border2);
  cursor: pointer;
  padding: 0;
  background: none;
}

/* CHAT */
#chat-area {
  position: fixed;
  top: 44px;
  bottom: 64px;
  left: 0; right: 0;
  overflow-y: auto;
  padding: 28px 22%;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.msg {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.msg.user {
  justify-content: flex-end;
}

.avatar {
  width: 22px;
  height: 22px;
  background: #151515;
  border-radius: 50%;
  border: 1px solid #222;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  color: var(--text-dim);
  flex-shrink: 0;
  margin-top: 2px;
}

.bubble-ai {
  font-size: 13px;
  color: #b0b0b0;
  line-height: 1.65;
  padding-top: 1px;
  max-width: 75%;
  white-space: pre-wrap;
  word-break: break-word;
}

.bubble-user {
  background: var(--bubble-bg);
  color: var(--bubble-text);
  border-radius: 14px 14px 3px 14px;
  padding: 9px 13px;
  font-size: 13px;
  line-height: 1.6;
  max-width: 68%;
  white-space: pre-wrap;
  word-break: break-word;
}

.thinking {
  display: flex;
  align-items: center;
  gap: 7px;
  color: var(--text-dim);
  font-size: 12px;
  font-style: italic;
}

.spinner {
  width: 12px;
  height: 12px;
  border: 1.5px solid #2a2a2a;
  border-top-color: var(--text-dim);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* INPUT */
#input-wrap {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  padding: 10px 22% 14px;
  background: var(--bg);
}

#input-bar {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
}

#msg-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text);
  font-size: 13px;
  font-family: inherit;
  resize: none;
  line-height: 1.5;
  max-height: 120px;
  overflow-y: auto;
}

#msg-input::placeholder { color: var(--text-dimmer); }

#btn-send {
  background: var(--bg2);
  border: 1px solid var(--border2);
  border-radius: 5px;
  padding: 5px 12px;
  color: #888;
  font-size: 12px;
  cursor: pointer;
  font-family: inherit;
  flex-shrink: 0;
}

#btn-send:hover { color: var(--text); }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2a2a; border-radius: 2px; }
```

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: tema scuro CSS"
```

---

### Task 5: Logica frontend — static/app.js

**Files:**
- Create: `static/app.js`

- [ ] **Step 1: Crea static/app.js**

```javascript
// Preset colori bolla: [bg, text, nome]
const COLOR_PRESETS = [
  { bg: '#252525', text: '#c0c0c0', name: 'grigio' },
  { bg: '#1e3a1e', text: '#c8e6c9', name: 'verde' },
  { bg: '#1a2a3a', text: '#b3d4f5', name: 'blu' },
  { bg: '#2a1a3a', text: '#d4b3f5', name: 'viola' },
  { bg: '#3a1a1a', text: '#f5b3b3', name: 'rosso' },
  { bg: '#2a2a18', text: '#f5e6b3', name: 'ambra' },
];

const MAX_TABS = 5;

// Stato
let tabs = [];         // [{id, title, color}]
let activeId = null;
let isStreaming = false;

// DOM
const tabsEl = document.getElementById('tabs');
const chatEl = document.getElementById('chat-area');
const searchEl = document.getElementById('search');
const btnNew = document.getElementById('btn-new');
const btnSend = document.getElementById('btn-send');
const msgInput = document.getElementById('msg-input');
const colorDot = document.getElementById('color-dot');
const colorPicker = document.getElementById('color-picker');
const presetsEl = document.getElementById('presets');
const customColorEl = document.getElementById('custom-color');

// ── INIT ─────────────────────────────────────────────────────────────────────

async function init() {
  buildPresets();
  const res = await fetch('/sessions');
  const ids = await res.json();
  ids.slice(0, MAX_TABS).forEach(id => addTab(id, id));
  if (tabs.length === 0) newChat();
  else activateTab(tabs[0].id);
}

// ── TAB ───────────────────────────────────────────────────────────────────────

function addTab(id, title) {
  const color = loadColor(id);
  tabs.push({ id, title: title.slice(0, 30), color });
  renderTabs();
}

function newChat() {
  if (tabs.length >= MAX_TABS) {
    const oldest = tabs[0];
    removeTab(oldest.id, false);
  }
  const id = crypto.randomUUID();
  addTab(id, 'Nuova chat');
  activateTab(id);
}

function activateTab(id) {
  activeId = id;
  renderTabs();
  renderChat(id);
  updateColorDot();
}

function removeTab(id, switchAway = true) {
  tabs = tabs.filter(t => t.id !== id);
  localStorage.removeItem(`chat_${id}`);
  localStorage.removeItem(`bubble_color_${id}`);
  if (switchAway) {
    if (tabs.length === 0) newChat();
    else activateTab(tabs[tabs.length - 1].id);
  }
  fetch(`/session/${id}`, { method: 'DELETE' });
  renderTabs();
}

function renderTabs() {
  const query = searchEl.value.toLowerCase();
  tabsEl.innerHTML = '';
  tabs
    .filter(t => t.title.toLowerCase().includes(query))
    .forEach(t => {
      const el = document.createElement('div');
      el.className = 'tab' + (t.id === activeId ? ' active' : '');
      el.dataset.id = t.id;
      el.innerHTML = `<span class="tab-title">${esc(t.title)}</span><span class="tab-close">x</span>`;
      el.addEventListener('click', e => {
        if (e.target.classList.contains('tab-close')) removeTab(t.id);
        else activateTab(t.id);
      });
      tabsEl.appendChild(el);
    });
}

// ── CHAT STORAGE ──────────────────────────────────────────────────────────────

function loadMessages(id) {
  try { return JSON.parse(localStorage.getItem(`chat_${id}`) || '[]'); }
  catch { return []; }
}

function saveMessages(id, msgs) {
  localStorage.setItem(`chat_${id}`, JSON.stringify(msgs));
}

function renderChat(id) {
  const msgs = loadMessages(id);
  chatEl.innerHTML = '';
  msgs.forEach(m => appendMessage(m.role, m.content, false));
  scrollBottom();
}

function appendMessage(role, content, scroll = true) {
  const msgs = loadMessages(activeId);
  msgs.push({ role, content });
  saveMessages(activeId, msgs);

  const el = document.createElement('div');
  el.className = 'msg ' + role;

  if (role === 'user') {
    const bubble = document.createElement('div');
    bubble.className = 'bubble-user';
    bubble.textContent = content;
    applyBubbleColor(bubble, activeId);
    el.appendChild(bubble);
  } else {
    const av = document.createElement('div');
    av.className = 'avatar';
    av.textContent = 'R';
    const bubble = document.createElement('div');
    bubble.className = 'bubble-ai';
    bubble.textContent = content;
    el.appendChild(av);
    el.appendChild(bubble);
  }

  chatEl.appendChild(el);
  if (scroll) scrollBottom();
  return el;
}

function scrollBottom() {
  chatEl.scrollTop = chatEl.scrollHeight;
}

// ── INVIO MESSAGGIO ───────────────────────────────────────────────────────────

async function sendMessage() {
  if (isStreaming) return;
  const text = msgInput.value.trim();
  if (!text) return;

  msgInput.value = '';
  msgInput.style.height = 'auto';

  // Titolo automatico al primo messaggio
  const msgs = loadMessages(activeId);
  if (msgs.length === 0) {
    const title = text.slice(0, 30);
    tabs = tabs.map(t => t.id === activeId ? { ...t, title } : t);
    renderTabs();
  }

  appendMessage('user', text);
  isStreaming = true;
  btnSend.disabled = true;

  // Bolla AI con spinner
  const thinkEl = document.createElement('div');
  thinkEl.className = 'msg assistant';
  const av = document.createElement('div');
  av.className = 'avatar';
  av.textContent = 'R';
  const thinking = document.createElement('div');
  thinking.className = 'thinking';
  thinking.innerHTML = '<div class="spinner"></div><span>elaborazione...</span>';
  thinkEl.appendChild(av);
  thinkEl.appendChild(thinking);
  chatEl.appendChild(thinkEl);
  scrollBottom();

  let aiContent = '';
  let aiBubble = null;

  const res = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text, session_id: activeId }),
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();
    for (const line of lines) {
      if (!line.startsWith('data: ')) continue;
      const evt = JSON.parse(line.slice(6));
      if (evt.type === 'token') {
        if (!aiBubble) {
          thinkEl.remove();
          const wrapper = document.createElement('div');
          wrapper.className = 'msg assistant';
          const av2 = document.createElement('div');
          av2.className = 'avatar';
          av2.textContent = 'R';
          aiBubble = document.createElement('div');
          aiBubble.className = 'bubble-ai';
          wrapper.appendChild(av2);
          wrapper.appendChild(aiBubble);
          chatEl.appendChild(wrapper);
        }
        aiContent += evt.content;
        aiBubble.textContent = aiContent;
        scrollBottom();
      } else if (evt.type === 'done') {
        if (aiBubble) {
          const msgs2 = loadMessages(activeId);
          msgs2.push({ role: 'assistant', content: aiContent });
          saveMessages(activeId, msgs2);
        }
      }
    }
  }

  isStreaming = false;
  btnSend.disabled = false;
}

// ── COLORE BOLLA ──────────────────────────────────────────────────────────────

function buildPresets() {
  COLOR_PRESETS.forEach((p, i) => {
    const dot = document.createElement('div');
    dot.className = 'preset-dot';
    dot.style.background = p.bg;
    dot.dataset.index = i;
    dot.addEventListener('click', () => setColor(p.bg, p.text));
    presetsEl.appendChild(dot);
  });

  customColorEl.addEventListener('input', e => {
    const bg = e.target.value;
    setColor(bg, '#c0c0c0');
  });
}

function setColor(bg, text) {
  localStorage.setItem(`bubble_color_${activeId}`, JSON.stringify({ bg, text }));
  tabs = tabs.map(t => t.id === activeId ? { ...t, color: { bg, text } } : t);
  updateColorDot();
  applyColorToAll(activeId);
  highlightSelectedPreset(bg);
}

function loadColor(id) {
  try {
    return JSON.parse(localStorage.getItem(`bubble_color_${id}`)) || COLOR_PRESETS[0];
  } catch {
    return COLOR_PRESETS[0];
  }
}

function applyBubbleColor(el, id) {
  const color = loadColor(id);
  el.style.background = color.bg;
  el.style.color = color.text;
}

function applyColorToAll(id) {
  document.querySelectorAll('.bubble-user').forEach(el => applyBubbleColor(el, id));
}

function updateColorDot() {
  const tab = tabs.find(t => t.id === activeId);
  if (!tab) return;
  const color = loadColor(activeId);
  colorDot.style.background = color.bg;
  highlightSelectedPreset(color.bg);
}

function highlightSelectedPreset(bg) {
  document.querySelectorAll('.preset-dot').forEach(dot => {
    const idx = parseInt(dot.dataset.index);
    dot.classList.toggle('selected', COLOR_PRESETS[idx].bg === bg);
  });
}

// ── COLOR PICKER TOGGLE ───────────────────────────────────────────────────────

colorDot.addEventListener('click', e => {
  e.stopPropagation();
  colorPicker.classList.toggle('hidden');
});

document.addEventListener('click', e => {
  if (!colorPicker.contains(e.target) && e.target !== colorDot) {
    colorPicker.classList.add('hidden');
  }
});

// ── EVENTI ────────────────────────────────────────────────────────────────────

btnNew.addEventListener('click', newChat);
btnSend.addEventListener('click', sendMessage);

msgInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = msgInput.scrollHeight + 'px';
});

searchEl.addEventListener('input', renderTabs);

// ── UTILS ─────────────────────────────────────────────────────────────────────

function esc(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── START ─────────────────────────────────────────────────────────────────────

init();
```

- [ ] **Step 2: Commit**

```bash
git add static/app.js
git commit -m "feat: logica frontend tab, streaming SSE, color picker"
```

---

### Task 6: Test manuale end-to-end

- [ ] **Step 1: Avvia Ollama**

```bash
ollama serve
```

- [ ] **Step 2: Avvia Flask**

```bash
source venv/bin/activate
python app.py
```

Output atteso: `* Running on http://127.0.0.1:5000`

- [ ] **Step 3: Verifica nel browser**

Apri `http://localhost:5000`. Checklist:
- la topbar compare con logo, search, tab "Nuova chat", pallino grigio
- scrivi un messaggio, premi invio — compare spinner poi risposta in streaming
- il titolo della tab si aggiorna con le prime 30 lettere del messaggio
- clicca `+` — si apre una seconda chat vuota
- clicca il pallino — compare popup con 6 preset
- scegli blu — il pallino cambia colore, le bolle diventano blu
- torna alla prima tab — il pallino torna al colore di quella chat
- ricarica la pagina — le chat ricompaiono (sessioni persistite)

- [ ] **Step 4: Commit**

```bash
git add .
git commit -m "chore: struttura file web UI completa"
```

---

### Task 7: Aggiorna CODE.md e THEORY.md

**Files:**
- Modify: `CODE.md`
- Modify: `THEORY.md`

- [ ] **Step 1: Aggiorna la struttura progetto in CODE.md**

Sostituisci il blocco struttura esistente con:

```
RaxeusAI/
├── config.py        → configurazione centralizzata (modello, URL, personalità)
├── memory.py        → gestione cronologia conversazione + tool messages
├── agent.py         → loop agente con streaming, tool calling e chat_stream per la web UI
├── tools.py         → funzioni eseguibili dall'AI (web, file, PDF, Wikipedia, ora)
├── sessions.py      → salvataggio e caricamento sessioni su file JSON
├── main.py          → loop terminale (ancora funzionante)
├── app.py           → server Flask per la web UI
├── templates/
│   └── index.html   → SPA dell'interfaccia web
├── static/
│   ├── style.css    → tema scuro, layout completo
│   └── app.js       → logica tab, SSE, color picker, localStorage
├── requirements.txt → dipendenze Python
└── venv/            → ambiente virtuale (prompt: "Raxeus")
```

- [ ] **Step 2: Aggiungi sezione app.py in CODE.md**

Aggiungi dopo la sezione `## tools.py`:

```markdown
## app.py

Server Flask che espone la web UI. Mantiene un dizionario `_sessions: dict[str, Memory]`
con una Memory attiva per ogni conversazione aperta nel browser.

### Endpoint

| Metodo | Path | Descrizione |
|---|---|---|
| `GET` | `/` | Serve `templates/index.html` |
| `POST` | `/chat` | Riceve `{message, session_id}`, risponde in SSE con eventi `token`, `thinking`, `done` |
| `GET` | `/sessions` | Restituisce la lista delle ultime 5 sessioni salvate su disco |
| `DELETE` | `/session/<id>` | Elimina il file sessione e rimuove la Memory dal dizionario |

**Funzione `_get_memory(session_id)`:** recupera la Memory dal dizionario; se non esiste la crea,
e se esiste un file di sessione corrispondente lo carica automaticamente.

**Avvio:**
```bash
source venv/bin/activate
python app.py
# http://localhost:5000
```
```

- [ ] **Step 3: Aggiungi sezione agent.py — chat_stream in CODE.md**

Nella sezione `## agent.py` esistente, aggiungi sotto il flusso di `chat`:

```markdown
**`chat_stream(user_input, mem)`:** versione generator di `chat` per la web UI.
Invece di stampare in stdout, yielda dizionari:
- `{"type": "token", "content": "..."}` — per ogni chunk di testo
- `{"type": "thinking"}` — quando inizia una tool call
- `{"type": "done"}` — quando la risposta è completa

Viene chiamata da `app.py` e i dizionari vengono serializzati come eventi SSE.
```

- [ ] **Step 4: Aggiungi sezione templates/ e static/ in CODE.md**

```markdown
## templates/index.html

SPA unica. Contiene solo il markup HTML — nessuna logica. Carica `style.css` e `app.js`.
Struttura: topbar (`#topbar`) → area chat (`#chat-area`) → barra input (`#input-wrap`).
Il DOM viene popolato interamente da `app.js` a runtime.

## static/style.css

Tema scuro completo. Usa variabili CSS (`--bg`, `--bubble-bg`, `--bubble-text`, ecc.)
per permettere eventuali futuri temi. Non contiene logica — solo stile.

Elementi principali: `#topbar`, `.tab`, `.tab.active`, `.bubble-user`, `.bubble-ai`,
`.spinner`, `#color-dot`, `#color-picker`.

## static/app.js

Tutta la logica del frontend. Nessuna dipendenza esterna.

| Responsabilità | Funzioni chiave |
|---|---|
| Gestione tab | `addTab`, `activateTab`, `removeTab`, `renderTabs` |
| Messaggi + localStorage | `appendMessage`, `loadMessages`, `saveMessages`, `renderChat` |
| Streaming SSE | `sendMessage` — legge il body della risposta come stream, aggiorna la bolla AI token per token |
| Color picker | `setColor`, `loadColor`, `applyBubbleColor`, `updateColorDot`, `buildPresets` |

**Persistenza locale:** i messaggi di ogni chat sono salvati in `localStorage` con chiave
`chat_<session_id>`. Il colore bolla è salvato con chiave `bubble_color_<session_id>`.
Al ricaricamento della pagina tutto viene ripristinato.

**Max 5 tab:** aprire la sesta chat chiude automaticamente la prima (la più vecchia).

**Titolo automatico:** al primo invio in una chat, il titolo della tab si imposta
con le prime 30 caratteri del messaggio utente.
```

- [ ] **Step 5: Aggiungi sezione SSE in THEORY.md**

Aggiungi in fondo a `THEORY.md`:

```markdown
## Server-Sent Events (SSE)

Meccanismo HTTP per inviare dati dal server al browser in modo continuo su una singola
connessione. Il server manda righe nel formato `data: <payload>\n\n` e il browser le
riceve man mano che arrivano.

In RaxeusAI viene usato per lo streaming dei token: ogni pezzo di testo generato dal
modello viene inviato immediatamente al browser invece di aspettare la risposta completa.

```
Client                        Server
  |--- POST /chat ----------->|
  |<-- data: {"type":"token"} |  (ripetuto per ogni token)
  |<-- data: {"type":"done"}  |
  |                           |
```

A differenza dei WebSocket (bidirezionali), SSE è unidirezionale server→client e
non richiede librerie speciali — funziona con `fetch()` nativo leggendo `res.body`
come stream.

## Architettura web vs terminale

RaxeusAI supporta due modalità di utilizzo sullo stesso backend:

| Modalità | Entry point | Streaming | Sessioni |
|---|---|---|---|
| Terminale | `main.py` → `agent.chat()` | stdout diretto | `sessions.py` manuale |
| Web | `app.py` → `agent.chat_stream()` | SSE via HTTP | `sessions.py` + localStorage |

Le due modalità condividono `Memory`, `tools.py` e `sessions.py` — solo il layer
di presentazione è diverso.
```

- [ ] **Step 6: Commit finale**

```bash
git add CODE.md THEORY.md
git commit -m "docs: documenta web UI, SSE, app.py, static/, templates/"
```
