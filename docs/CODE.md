# Codice — Documentazione tecnica

> Documentazione di ogni file del progetto Raxeus.
> Per i concetti teorici vedi [THEORY.md](THEORY.md). Per bug e fix vedi [BUGS.md](BUGS.md).

---

## Struttura del progetto

```
RaxeusAI/
├── config.py           → configurazione centralizzata (modello, URL, personalità)
├── memory.py           → gestione cronologia conversazione + tool messages
├── agent.py            → loop agente con streaming, tool calling e chat_stream per la web UI
├── tools.py            → funzioni eseguibili dall'AI (web, file, PDF, Wikipedia, ora)
├── sessions.py         → salvataggio e caricamento sessioni su file JSON
├── main.py             → loop terminale (ancora funzionante)
├── app.py              → server Flask per la web UI
├── templates/
│   └── index.html      → SPA: tutto il markup dell'interfaccia web
├── static/
│   ├── style.css       → tema scuro, layout completo
│   └── app.js          → logica tab, streaming SSE, color picker, localStorage
├── requirements.txt    → dipendenze Python
└── venv/               → ambiente virtuale (prompt: "Raxeus")
```

---

## config.py

Punto centrale di configurazione. Tutto ciò che può essere cambiato senza toccare la logica sta qui.

```python
MODEL = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/v1"
AI_NAME = "Raxeus"
SYSTEM_PROMPT = f"""..."""
```

| Variabile | Tipo | Descrizione |
|---|---|---|
| `MODEL` | `str` | Nome del modello Ollama da usare |
| `OLLAMA_URL` | `str` | Endpoint del server Ollama locale |
| `AI_NAME` | `str` | Nome dell'assistente, usato nel prompt e nell'UI |
| `SYSTEM_PROMPT` | `str` | Personalità e istruzioni comportamentali dell'AI |

**Modifiche applicate:**
- `AI_NAME` cambiato da `"Jarvis"` a `"Raxeus"`
- `SYSTEM_PROMPT` riscritto con personalità orgogliosa, pomposa, narcisista — si vanta di ogni risposta
- Data corrente iniettata dinamicamente all'avvio via `datetime.now()` — il modello sa sempre che anno è
- Aggiunta regola esplicita: usare i tool senza annunciarlo, mai fidarsi del training data per info recenti

---

## memory.py

Gestisce la cronologia della conversazione. Il modello è stateless — ad ogni chiamata gli passiamo tutta la history.

```python
class Memory:
    def add(self, role, content): ...
    def add_assistant_tool_calls(self, content, tool_calls): ...
    def add_tool_result(self, tool_call_id, tool_name, result): ...
    def get(self) -> list: ...
    def load(self, messages): ...
    def reset(self): ...
```

| Metodo | Descrizione |
|---|---|
| `add` | Aggiunge un messaggio `user` o `assistant` standard |
| `add_assistant_tool_calls` | Aggiunge il messaggio assistant che contiene le chiamate ai tool (richiesto dal protocollo OpenAI) |
| `add_tool_result` | Aggiunge il risultato dell'esecuzione di un tool con ruolo `tool` |
| `get` | Restituisce tutta la history da passare all'API |
| `load` | Carica una lista di messaggi salvati (da sessione), reinserendo il system prompt fresco |
| `reset` | Svuota la history, reinserisce solo il system prompt |

**Modifiche rispetto alla versione base:**
- Aggiunti `add_assistant_tool_calls` e `add_tool_result` per supportare il protocollo di function calling
- Aggiunto `load` per il caricamento delle sessioni salvate

---

## agent.py

Cuore del progetto. Gestisce il loop agente con streaming in tempo reale e tool calling.

```python
client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
memory = Memory()

def chat(user_input: str) -> str: ...
def reset(): ...
```

**Flusso completo di `chat`:**

```
1. memory.add("user", input)
2. chiamata streaming al modello con tools definiti
3. accumula chunk → testo stampato in tempo reale
4. se arrivano tool_calls → accumula i chunk del tool call
5. se tool_calls presenti:
   - memory.add_assistant_tool_calls(...)
   - per ogni tool: esegui silenziosamente → memory.add_tool_result(...)
   - torna al punto 2 (loop)
6. se nessun tool_call → memory.add("assistant", testo) → return
```

**Dettagli tecnici:**
- `stream=True` — i token arrivano uno alla volta, vengono stampati con `print(..., end="", flush=True)`
- I tool call arrivano anch'essi in chunk durante lo streaming e vengono accumulati per indice (`tool_calls_acc`)
- Il loop continua finché il modello non produce una risposta senza tool call
- `api_key="ollama"` è un placeholder — Ollama non richiede autenticazione

**Modifiche rispetto alla versione base:**
- Aggiunto streaming completo della risposta
- Aggiunto agentic loop con tool calling
- Rimossi print di debug dei tool call (fix BUG-002)
- `memory` è esposto a livello di modulo per permettere a `main.py` di importarlo per le sessioni
- Aggiunto `chat_stream` per la web UI (vedi sotto)

**`chat_stream(user_input, mem)`:** versione generator di `chat` per la web UI. Invece di stampare su stdout, yielda dizionari:
- `{"type": "token", "content": "..."}` — per ogni chunk di testo generato
- `{"type": "thinking"}` — quando il modello inizia una tool call
- `{"type": "done"}` — quando la risposta è completa

Viene chiamata da `app.py` e i dizionari vengono serializzati come eventi SSE inviati al browser.

---

## tools.py

Definisce le funzioni che Raxeus può eseguire autonomamente. Ogni tool ha:
- La funzione Python che lo implementa
- Lo schema JSON Schema che descrive al modello nome, scopo e parametri

### Tool disponibili

| Tool | Funzione | Descrizione |
|---|---|---|
| `google_search` | `google_search(query)` | **[principale]** Cerca su Google + legge le prime 2 pagine con `fetch_url`. Fallback automatico su `web_search` se Google fallisce |
| `fetch_url` | `fetch_url(url)` | Legge il contenuto testuale di una pagina web (max 3000 char) |
| `web_search` | `web_search(query)` | **[fallback]** Cerca su DuckDuckGo via `ddgs`, restituisce titolo + snippet + URL dei primi 5 risultati |
| `read_file` | `read_file(path)` | Legge un file dal filesystem e ne restituisce il contenuto |
| `write_file` | `write_file(path, content)` | Scrive o sovrascrive un file |
| `append_file` | `append_file(path, content)` | Aggiunge testo in fondo a un file senza sovrascriverlo |
| `list_dir` | `list_dir(path)` | Elenca i file e le cartelle in una directory (default: `.`) |
| `read_pdf` | `read_pdf(path)` | Estrae e restituisce il testo da un file PDF (max 4000 char, richiede `pypdf`) |
| `wikipedia_search` | `wikipedia_search(query, lang)` | Cerca su Wikipedia e restituisce il sommario della pagina (default lang: `it`) |
| `run_python` | `run_python(code)` | Esegue codice Python in subprocess, restituisce stdout/stderr (timeout 10s) |
| `get_datetime` | `get_datetime()` | Restituisce data e ora corrente formattata |

### Struttura di ogni tool schema

```python
{
    "type": "function",
    "function": {
        "name": "nome_tool",
        "description": "Cosa fa — il modello usa questa stringa per decidere quando chiamarlo",
        "parameters": {
            "type": "object",
            "properties": { ... },
            "required": [...]
        }
    }
}
```

### execute_tool

```python
def execute_tool(name: str, args: dict) -> str
```

Dispatcher centrale: riceve nome e argomenti dal modello, chiama la funzione corrispondente, restituisce il risultato come stringa. Gestisce eccezioni senza crashare.

**Note:**
- `run_python` usa il `python3` di sistema, non il venv
- `web_search` usa la libreria `ddgs` (rinomina di `duckduckgo-search`) — stderr soppresso via redirect `sys.stderr`
- `google_search` legge direttamente le prime 2 pagine trovate con `fetch_url`, fallback automatico su `web_search`
- `fetch_url` usa `requests` + `beautifulsoup4` per estrarre solo il testo pulito dalla pagina, rimuovendo script/stili/nav
- Alcuni siti bloccano `fetch_url` con 403 (vedi BUG-005 in BUGS.md)
- L'output di `run_python` è limitato a 2000 caratteri per non intasare la history
- `append_file` apre in modalità `"a"` — crea il file se non esiste, aggiunge in fondo se esiste
- `list_dir` usa `os.listdir` con output ordinato alfabeticamente
- `read_pdf` usa `pypdf` (guard `_PYPDF_OK`), estrae testo pagina per pagina, limite 4000 char
- `wikipedia_search` usa l'API REST di Wikipedia (`/api/rest_v1/page/summary/`) — nessuna dipendenza extra, usa `requests` già presente; supporta qualsiasi lingua via parametro `lang`

---

## app.py

Server Flask che espone la web UI. Mantiene un dizionario `_sessions: dict[str, Memory]` con una `Memory` attiva per ogni conversazione aperta nel browser.

### Endpoint

| Metodo | Path | Descrizione |
|---|---|---|
| `GET` | `/` | Serve `templates/index.html` |
| `POST` | `/chat` | Riceve `{message, session_id}`, risponde in SSE con eventi `token`, `thinking`, `done` |
| `GET` | `/sessions` | Restituisce lista delle ultime 5 sessioni salvate su disco |
| `DELETE` | `/session/<id>` | Elimina il file sessione dal disco e rimuove la Memory dal dizionario |

**`_get_memory(session_id)`:** recupera la Memory dal dizionario; se non esiste la crea, e se esiste un file sessione corrispondente lo carica automaticamente da disco.

**Avvio:**
```bash
source venv/bin/activate
python app.py
# apri http://localhost:5000
```

---

## templates/index.html

SPA unica. Contiene solo il markup HTML strutturale — nessuna logica. Carica `style.css` e `app.js`. Il DOM viene popolato interamente da `app.js` a runtime.

Struttura: `#topbar` (logo, ricerca, tab, pallino colore) → `#chat-area` (messaggi) → `#input-wrap` (textarea + pulsante invia).

---

## static/style.css

Tema scuro completo. Usa variabili CSS (`--bg`, `--bubble-bg`, `--bubble-text`, ecc.) per mantenere i colori coerenti e permettere futuri temi.

Elementi principali: `#topbar`, `.tab`, `.tab.active`, `.bubble-user`, `.bubble-ai`, `.spinner`, `#color-dot`, `#color-picker`, `.preset-dot`.

---

## static/app.js

Tutta la logica del frontend. Nessuna dipendenza esterna.

| Responsabilità | Funzioni chiave |
|---|---|
| Gestione tab | `addTab`, `activateTab`, `removeTab`, `renderTabs`, `newChat` |
| Messaggi e localStorage | `appendMessage`, `buildBubble`, `loadMessages`, `saveMessages`, `renderChat` |
| Streaming SSE | `sendMessage` — legge il body come stream, aggiorna la bolla AI token per token |
| Color picker | `setColor`, `loadColor`, `applyBubbleColor`, `updateColorDot`, `buildPresets` |

**Persistenza locale:** i messaggi di ogni chat sono in `localStorage` con chiave `chat_<session_id>`. Il colore bolla è in `bubble_color_<session_id>`. Al ricaricamento tutto viene ripristinato.

**Max 5 tab:** aprire la sesta chat chiude automaticamente la prima (la più vecchia).

**Titolo automatico:** al primo invio, il titolo della tab si imposta con le prime 30 caratteri del messaggio utente.

---

## sessions.py

Gestisce il salvataggio e caricamento delle conversazioni su file JSON nella cartella `sessions/`.

```python
def save_session(history: list) -> str       # salva, ritorna il path
def list_sessions() -> list[str]             # lista timestamp disponibili
def load_session(timestamp: str) -> list     # carica e ritorna i messaggi
```

**Formato file:** `sessions/session_YYYYMMDD_HHMMSS.json`

**Cosa viene salvato:** tutti i messaggi tranne il system prompt (che viene sempre reinserito fresco al caricamento).

**Nota:** la cartella `sessions/` è in `.gitignore` — le conversazioni personali non vanno su GitHub.

---

## main.py

Loop principale interattivo. Gestisce input utente, comandi speciali e visualizzazione streaming.

```python
print(f"{AI_NAME}: ", end="", flush=True)
chat(user)   # chat() stampa i token in streaming
print()      # newline finale
```

### Comandi disponibili

| Comando | Effetto |
|---|---|
| `esci` | Messaggio di uscita e chiusura |
| `reset` | Cancella la memoria della sessione corrente |
| `salva` | Salva la conversazione corrente in `sessions/` |
| `sessioni` | Lista le sessioni salvate con numero indice |
| `carica <N>` | Carica la sessione numero N dalla lista |
| qualsiasi testo | Inviato all'AI |

**Modifiche rispetto alla versione base:**
- Aggiunto import di `memory` da `agent` per le operazioni di sessione
- Aggiunto import di `sessions.py` per salvataggio/caricamento
- Aggiunta gestione `KeyboardInterrupt` (Ctrl+C) per uscita pulita
- Rimosso `reply = chat(user)` — ora `chat()` stampa in streaming direttamente, il return serve solo internamente

---

## requirements.txt

```
openai
ddgs
googlesearch-python
requests
beautifulsoup4
pypdf
```

**Modifiche:** aggiunte `duckduckgo-search`, `googlesearch-python`, `requests` e `beautifulsoup4` per ricerca web e fetch pagine. Aggiunta `pypdf` per la lettura di file PDF. Aggiunta `flask` per la web UI.

---

## venv

Ambiente virtuale Python creato con `python3 -m venv venv`.

Il prompt del venv è stato rinominato da `(venv)` a `(Raxeus)` modificando `venv/bin/activate`:

```bash
VIRTUAL_ENV_PROMPT=Raxeus
PS1="(Raxeus) ${PS1:-}"
```

**Attivazione:**
```bash
source venv/bin/activate
```

**Installazione dipendenze:**
```bash
pip install -r requirements.txt
```

---

## Come avviare il progetto

```bash
# 1. Avvia Ollama
ollama serve

# 2. Dalla cartella del progetto
source venv/bin/activate
python main.py
```
