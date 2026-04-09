// Preset colori bolla: { bg, text, name }
const COLOR_PRESETS = [
  { bg: '#252525', text: '#c0c0c0', name: 'grigio' },
  { bg: '#1e3a1e', text: '#c8e6c9', name: 'verde' },
  { bg: '#1a2a3a', text: '#b3d4f5', name: 'blu' },
  { bg: '#2a1a3a', text: '#d4b3f5', name: 'viola' },
  { bg: '#3a1a1a', text: '#f5b3b3', name: 'rosso' },
  { bg: '#2a2a18', text: '#f5e6b3', name: 'ambra' },
];

const MAX_TABS = 5;

// Stato globale
let tabs = [];      // [{id, title, color}]
let activeId = null;
let isStreaming = false;

// DOM
const tabsEl      = document.getElementById('tabs');
const chatEl      = document.getElementById('chat-area');
const searchEl    = document.getElementById('search');
const btnNew      = document.getElementById('btn-new');
const btnSend     = document.getElementById('btn-send');
const msgInput    = document.getElementById('msg-input');
const colorDot    = document.getElementById('color-dot');
const colorPicker = document.getElementById('color-picker');
const presetsEl   = document.getElementById('presets');
const customColor = document.getElementById('custom-color');

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
  tabs.push({ id, title: title.slice(0, 30) });
  renderTabs();
}

function newChat() {
  if (tabs.length >= MAX_TABS) removeTab(tabs[0].id, false);
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
  fetch(`/session/${id}`, { method: 'DELETE' });
  if (switchAway) {
    if (tabs.length === 0) newChat();
    else activateTab(tabs[tabs.length - 1].id);
  }
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
      el.innerHTML = `<span>${esc(t.title)}</span><span class="tab-close">x</span>`;
      el.addEventListener('click', e => {
        if (e.target.classList.contains('tab-close')) removeTab(t.id);
        else activateTab(t.id);
      });
      tabsEl.appendChild(el);
    });
}

// ── MESSAGGI ─────────────────────────────────────────────────────────────────

function loadMessages(id) {
  try { return JSON.parse(localStorage.getItem(`chat_${id}`) || '[]'); }
  catch { return []; }
}

function saveMessages(id, msgs) {
  localStorage.setItem(`chat_${id}`, JSON.stringify(msgs));
}

function renderChat(id) {
  chatEl.innerHTML = '';
  loadMessages(id).forEach(m => buildBubble(m.role, m.content));
  scrollBottom();
}

function buildBubble(role, content) {
  const wrap = document.createElement('div');
  wrap.className = `msg ${role}`;

  if (role === 'user') {
    const b = document.createElement('div');
    b.className = 'bubble-user';
    b.textContent = content;
    applyBubbleColor(b, activeId);
    wrap.appendChild(b);
  } else {
    const av = document.createElement('div');
    av.className = 'avatar';
    av.textContent = 'R';
    const b = document.createElement('div');
    b.className = 'bubble-ai';
    b.textContent = content;
    wrap.appendChild(av);
    wrap.appendChild(b);
  }

  chatEl.appendChild(wrap);
  return wrap;
}

function appendMessage(role, content) {
  const msgs = loadMessages(activeId);
  msgs.push({ role, content });
  saveMessages(activeId, msgs);
  const el = buildBubble(role, content);
  scrollBottom();
  return el;
}

function scrollBottom() {
  chatEl.scrollTop = chatEl.scrollHeight;
}

// ── INVIO ─────────────────────────────────────────────────────────────────────

async function sendMessage() {
  if (isStreaming) return;
  const text = msgInput.value.trim();
  if (!text) return;

  msgInput.value = '';
  msgInput.style.height = 'auto';

  // Titolo automatico al primo messaggio
  if (loadMessages(activeId).length === 0) {
    tabs = tabs.map(t => t.id === activeId ? { ...t, title: text.slice(0, 30) } : t);
    renderTabs();
  }

  appendMessage('user', text);
  isStreaming = true;
  btnSend.disabled = true;

  // Spinner temporaneo
  const spinWrap = document.createElement('div');
  spinWrap.className = 'msg assistant';
  spinWrap.innerHTML = `
    <div class="avatar">R</div>
    <div class="thinking">
      <div class="spinner"></div>
      <span>elaborazione...</span>
    </div>`;
  chatEl.appendChild(spinWrap);
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
      let evt;
      try { evt = JSON.parse(line.slice(6)); } catch { continue; }

      if (evt.type === 'token') {
        if (!aiBubble) {
          spinWrap.remove();
          const wrap = document.createElement('div');
          wrap.className = 'msg assistant';
          const av = document.createElement('div');
          av.className = 'avatar';
          av.textContent = 'R';
          aiBubble = document.createElement('div');
          aiBubble.className = 'bubble-ai';
          wrap.appendChild(av);
          wrap.appendChild(aiBubble);
          chatEl.appendChild(wrap);
        }
        aiContent += evt.content;
        aiBubble.textContent = aiContent;
        scrollBottom();
      } else if (evt.type === 'done') {
        if (aiBubble) {
          const msgs = loadMessages(activeId);
          msgs.push({ role: 'assistant', content: aiContent });
          saveMessages(activeId, msgs);
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
  customColor.addEventListener('input', e => setColor(e.target.value, '#c0c0c0'));
}

function setColor(bg, text) {
  localStorage.setItem(`bubble_color_${activeId}`, JSON.stringify({ bg, text }));
  updateColorDot();
  document.querySelectorAll('.bubble-user').forEach(el => applyBubbleColor(el, activeId));
  highlightPreset(bg);
}

function loadColor(id) {
  try { return JSON.parse(localStorage.getItem(`bubble_color_${id}`)) || COLOR_PRESETS[0]; }
  catch { return COLOR_PRESETS[0]; }
}

function applyBubbleColor(el, id) {
  const c = loadColor(id);
  el.style.background = c.bg;
  el.style.color = c.text;
}

function updateColorDot() {
  const c = loadColor(activeId);
  colorDot.style.background = c.bg;
  highlightPreset(c.bg);
}

function highlightPreset(bg) {
  document.querySelectorAll('.preset-dot').forEach(dot => {
    dot.classList.toggle('selected', COLOR_PRESETS[+dot.dataset.index].bg === bg);
  });
}

// ── COLOR PICKER TOGGLE ───────────────────────────────────────────────────────

colorDot.addEventListener('click', e => {
  e.stopPropagation();
  colorPicker.classList.toggle('hidden');
});

document.addEventListener('click', e => {
  if (!colorPicker.contains(e.target) && e.target !== colorDot)
    colorPicker.classList.add('hidden');
});

// ── EVENTI INPUT ──────────────────────────────────────────────────────────────

btnNew.addEventListener('click', newChat);
btnSend.addEventListener('click', sendMessage);

msgInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = msgInput.scrollHeight + 'px';
});

searchEl.addEventListener('input', renderTabs);

// ── UTILS ─────────────────────────────────────────────────────────────────────

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── START ─────────────────────────────────────────────────────────────────────

init();
