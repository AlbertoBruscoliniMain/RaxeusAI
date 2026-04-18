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
const btnInfo     = document.getElementById('btn-info');
const infoOverlay = document.getElementById('info-overlay');
const infoClose   = document.getElementById('info-close');

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
    const av = document.createElement('img');
    av.className = 'avatar';
    av.src = '/static/logo.png';
    av.alt = 'Raxeus';
    const b = document.createElement('div');
    b.className = 'bubble-ai';
    b.innerHTML = marked.parse(content);
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
    <img class="avatar" src="/static/logo.png" alt="Raxeus">
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
          const av = document.createElement('img');
          av.className = 'avatar';
          av.src = '/static/logo.png';
          av.alt = 'Raxeus';
          aiBubble = document.createElement('div');
          aiBubble.className = 'bubble-ai';
          wrap.appendChild(av);
          wrap.appendChild(aiBubble);
          chatEl.appendChild(wrap);
        }
        aiContent += evt.content;
        aiBubble.innerHTML = marked.parse(aiContent);
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
btnInfo.addEventListener('click', () => { infoOverlay.classList.remove('hidden'); loadInfoCards(); });
infoClose.addEventListener('click', () => infoOverlay.classList.add('hidden'));
infoOverlay.addEventListener('click', e => {
  if (e.target === infoOverlay) infoOverlay.classList.add('hidden');
});
btnSend.addEventListener('click', sendMessage);

msgInput.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

msgInput.addEventListener('input', () => {
  msgInput.style.height = 'auto';
  msgInput.style.height = msgInput.scrollHeight + 'px';
});

searchEl.addEventListener('input', renderTabs);

// ── INFO CARDS ────────────────────────────────────────────────────────────────

const PORTFOLIO_URL = 'https://AlbertoBruscoliniMain.github.io';
const GH_ACCOUNTS = ['AlbertoBruscoliniMain', 'AlbertoBruscolini'];
let infoCardsLoaded = false;

async function loadInfoCards() {
  if (infoCardsLoaded) return;
  const container = document.getElementById('info-cards');
  container.innerHTML = '<div class="info-card-loading">caricamento...</div>';

  try {
    const profiles = await Promise.all(
      GH_ACCOUNTS.map(u => fetch(`https://api.github.com/users/${u}`).then(r => r.json()))
    );

    container.innerHTML = '';
    profiles.forEach(p => {
      const card = document.createElement('a');
      card.className = 'info-card';
      card.href = PORTFOLIO_URL;
      card.target = '_blank';
      card.rel = 'noopener';
      card.innerHTML = `
        <div class="info-card-header">
          <img class="info-card-avatar" src="${p.avatar_url}" alt="avatar">
          <div>
            <div class="info-card-name">${p.login}</div>
            ${p.name ? `<div class="info-card-user">${p.name}</div>` : ''}
          </div>
        </div>
        ${p.bio ? `<div class="info-card-desc">${p.bio}</div>` : ''}
        <div class="info-card-stats">
          <span class="info-card-stat">📦 ${p.public_repos} repo</span>
          <span class="info-card-stat">👥 ${p.followers} follower</span>
        </div>`;
      container.appendChild(card);
    });

    infoCardsLoaded = true;
  } catch {
    container.innerHTML = '<div class="info-card-loading">impossibile caricare i dati</div>';
  }
}

// ── UTILS ─────────────────────────────────────────────────────────────────────

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── RAXEUS LYRIC BUTTON ───────────────────────────────────────────────────────

(function () {
  const btn = document.createElement('a');
  btn.href = '/lyric';
  btn.textContent = 'RaxeusLyric';
  btn.style.cssText = [
    'background:none',
    'border:1px solid #2a2a2a',
    'border-radius:5px',
    'padding:3px 10px',
    'font-size:11px',
    'font-weight:600',
    'color:#888',
    'text-decoration:none',
    'flex-shrink:0',
    'letter-spacing:0.2px',
    'transition:color .15s,border-color .15s',
    'line-height:1',
    'white-space:nowrap',
  ].join(';');
  btn.addEventListener('mouseenter', () => { btn.style.color = '#c0c0c0'; btn.style.borderColor = '#444'; });
  btn.addEventListener('mouseleave', () => { btn.style.color = '#888'; btn.style.borderColor = '#2a2a2a'; });

  // Inserisce prima del pallino colore, che è sempre l'ultimo elemento della topbar
  const colorWrap = document.getElementById('color-dot-wrap');
  colorWrap.parentNode.insertBefore(btn, colorWrap);
})();

// ── START ─────────────────────────────────────────────────────────────────────

init();
