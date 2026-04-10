<p align="center">
  <img src="static/logo.png" alt="Raxeus" height="80">
</p>

<h1 align="center">RaxeusAI</h1>

<p align="center">
  Assistente AI personale con memoria, tool use e interfaccia web — completamente offline, costruito su Ollama.
</p>

---

## Panoramica

RaxeusAI è un agente AI locale scritto in Python. Usa un modello LLM tramite [Ollama](https://ollama.com) con API compatibile OpenAI, e implementa un loop agente completo: memoria multi-turno, function calling, streaming dei token e persistenza delle sessioni.

Il progetto supporta due modalità di utilizzo sullo stesso backend:

| Modalità | Entry point | Interfaccia |
|---|---|---|
| Terminale | `main.py` | CLI interattiva |
| Web | `app.py` | Browser via Flask + SSE |

Compatibile con **macOS**, **Windows** e **Linux**.

---

## Funzionalità

- **Streaming token-by-token** — le risposte appaiono in tempo reale, sia nel terminale che nel browser
- **Tool use autonomo** — l'AI decide autonomamente quando e quali tool chiamare, senza richiedere conferma
- **Memoria conversazionale** — tutta la cronologia viene mantenuta e passata al modello ad ogni turno
- **Sessioni persistenti** — le conversazioni possono essere salvate su file JSON e ricaricate in sessioni successive
- **Interfaccia web** — tab multiple, ricerca nelle chat, color picker per la bolla utente

### Tool disponibili

| Tool | Funzione |
|---|---|
| `google_search` | Ricerca web via Google (principale) |
| `web_search` | Ricerca web via DuckDuckGo (fallback) |
| `fetch_url` | Lettura contenuto testuale di una pagina web |
| `wikipedia_search` | Ricerca e sommario da Wikipedia |
| `read_file` | Lettura file dal filesystem |
| `write_file` | Scrittura/sovrascrittura file |
| `append_file` | Aggiunta testo in fondo a un file |
| `list_dir` | Esplorazione directory |
| `read_pdf` | Estrazione testo da file PDF |
| `run_python` | Esecuzione codice Python (timeout 10s) |
| `get_datetime` | Data e ora corrente |

---

## Struttura del progetto

```
RaxeusAI/
├── config.py           # Modello, URL Ollama, system prompt e personalità
├── memory.py           # Gestione cronologia conversazione
├── agent.py            # Loop agente: streaming, tool calling, chat_stream per la web UI
├── tools.py            # Implementazione e schema JSON dei tool disponibili
├── sessions.py         # Salvataggio e caricamento sessioni in JSON
├── main.py             # Interfaccia a riga di comando
├── app.py              # Server Flask per la web UI (SSE)
├── templates/
│   └── index.html      # Markup interfaccia web
├── static/
│   ├── style.css       # Tema scuro
│   └── app.js          # Logica tab, streaming SSE, color picker
└── requirements.txt
```

---

## Requisiti

- Python 3.10+
- [Ollama](https://ollama.com) installato e in esecuzione
- Il modello configurato scaricato localmente (default: `qwen3:8b`)

```bash
ollama pull qwen3:8b
```

---

## Installazione

> Se stai clonando su una nuova macchina, crea un venv nuovo — quello nella repo è compilato per macOS e non è riutilizzabile su altri sistemi.

```bash
python -m venv venv
```

macOS / Linux:
```bash
source venv/bin/activate
```

Windows:
```bat
venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

---

## Avvio

**Interfaccia terminale:**

macOS / Linux:
```bash
ollama serve
source venv/bin/activate
python main.py
```

Windows:
```bat
ollama serve
venv\Scripts\activate
python main.py
```

**Interfaccia web:**

macOS / Linux:
```bash
ollama serve
source venv/bin/activate
python app.py
# apri http://localhost:5000
```

Windows:
```bat
ollama serve
venv\Scripts\activate
python app.py
```

### Comandi disponibili nel terminale

| Comando | Effetto |
|---|---|
| `reset` | Cancella la memoria della sessione corrente |
| `salva` | Salva la conversazione su file JSON |
| `sessioni` | Elenca le sessioni salvate |
| `carica <N>` | Carica la sessione numero N |
| `esci` | Chiude il programma |

---

## Configurazione

Tutte le impostazioni principali si trovano in `config.py`:

```python
MODEL = "qwen3:8b"                        # Modello Ollama da usare
OLLAMA_URL = "http://localhost:11434/v1"  # Endpoint API
AI_NAME = "Raxeus"                        # Nome dell'assistente
SYSTEM_PROMPT = "..."                     # Personalità e istruzioni base
```

Per cambiare modello basta modificare `MODEL`. Qualsiasi modello disponibile su Ollama con supporto al function calling è compatibile.

---

## Documentazione

| File | Contenuto |
|---|---|
| [docs/THEORY.md](docs/THEORY.md) | Concetti teorici: LLM, streaming, SSE, tool calling, architettura |
| [docs/CODE.md](docs/CODE.md) | Documentazione tecnica di ogni file e dei flussi principali |
| [docs/WEB-UI.md](docs/WEB-UI.md) | Come funziona l'interfaccia web |
| [docs/BUGS.md](docs/BUGS.md) | Bug noti e fix applicati |
