# Codice — Documentazione tecnica

> Documentazione di ogni file del progetto Raxeus.
> Per i concetti teorici vedi [THEORY.md](THEORY.md). Per bug e fix vedi [BUGS.md](BUGS.md).

---

## Struttura del progetto

```
RaxeusAI/
├── config.py        → configurazione centralizzata (modello, URL, personalità)
├── memory.py        → gestione cronologia conversazione + tool messages
├── agent.py         → loop agente con streaming e tool calling
├── tools.py         → funzioni eseguibili dall'AI (web, file, codice, ora)
├── sessions.py      → salvataggio e caricamento sessioni su file JSON
├── main.py          → loop principale, interfaccia terminale
├── requirements.txt → dipendenze Python
└── venv/            → ambiente virtuale (prompt: "Raxeus")
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
- `SYSTEM_PROMPT` riscritto con personalità ribelle, arrogante, humor cinico e parolacce naturali
- Aggiunta regola: niente divagazioni nelle risposte tecniche, utente nominato max una volta
- Aggiunta regola: libero arbitrio quando si parla di sé o dell'utente

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

---

## tools.py

Definisce le funzioni che Raxeus può eseguire autonomamente. Ogni tool ha:
- La funzione Python che lo implementa
- Lo schema JSON Schema che descrive al modello nome, scopo e parametri

### Tool disponibili

| Tool | Funzione | Descrizione |
|---|---|---|
| `google_search` | `google_search(query)` | **[principale]** Cerca su Google, restituisce titolo + descrizione + URL dei primi 5 risultati |
| `fetch_url` | `fetch_url(url)` | Legge il contenuto testuale di una pagina web (max 3000 char) |
| `web_search` | `web_search(query)` | **[fallback]** Cerca su DuckDuckGo, restituisce titolo + snippet + URL dei primi 4 risultati |
| `read_file` | `read_file(path)` | Legge un file dal filesystem e ne restituisce il contenuto |
| `write_file` | `write_file(path, content)` | Scrive o sovrascrive un file |
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
- `web_search` richiede `duckduckgo-search` installato — se assente, restituisce errore senza crashare
- `google_search` ora usa `advanced=True` — restituisce titolo, descrizione e URL (fix BUG-001)
- `fetch_url` usa `requests` + `beautifulsoup4` per estrarre solo il testo pulito dalla pagina, rimuovendo script/stili/nav
- Alcuni siti bloccano `fetch_url` con 403 (vedi BUG-005 in BUGS.md)
- L'output di `run_python` è limitato a 2000 caratteri per non intasare la history

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
duckduckgo-search
googlesearch-python
requests
beautifulsoup4
```

**Modifiche:** aggiunte `duckduckgo-search`, `googlesearch-python`, `requests` e `beautifulsoup4` per ricerca web e fetch pagine.

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
