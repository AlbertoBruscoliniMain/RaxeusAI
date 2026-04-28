<table align="center">
  <tr>
    <td align="center">
      <img src="static/logo.png" alt="Raxeus" height="180">
    </td>
    <td width="40"></td>
    <td align="center">
      <img src="static/logo_lyric.png" alt="RaxeusLyric" height="180">
    </td>
  </tr>
</table>

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
- **Tool call paralleli** — più tool nello stesso turno vengono eseguiti in parallelo (idea da OpenJarvis)
- **LoopGuard** — blocca chiamate identiche ripetute, pattern ping-pong e budget per tool (idea da OpenJarvis)
- **Memoria conversazionale con compressione automatica** — sliding window quando la cronologia supera 100 messaggi (idea da OpenJarvis)
- **Sessioni persistenti** — le conversazioni possono essere salvate su file JSON e ricaricate in sessioni successive
- **Interfaccia web** — tab multiple, ricerca nelle chat, color picker per la bolla utente
- **Caricamento immagini** — allega fino a 3 foto per messaggio; il modello vision le analizza e risponde, anche senza testo
- **Rendering formule matematiche** — le risposte con LaTeX (`$...$`, `$$...$$`) vengono renderizzate graficamente nel browser tramite KaTeX
- **Titolo chat generato dall'AI** — al termine della prima risposta, il modello genera automaticamente un titolo di 3-4 parole che descrive l'argomento trattato
- **Hardware detection + comando `doctor`** — al primo avvio scopri qual è il modello giusto per il tuo hardware (idea da OpenJarvis)
- **App desktop nativa su macOS e Windows** — bundle `.app` o `.exe` con icona, doppio click e parte

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
├── config.py               # Modello, URL Ollama, system prompt e personalità
├── memory.py               # Gestione cronologia conversazione (lista messaggi multi-turno)
├── agent.py                # Loop agente: streaming, tool calling, chat_stream per la web UI
├── tools.py                # Implementazione e schema JSON di tutti i tool disponibili
├── sessions.py             # Salvataggio e caricamento sessioni in file JSON
├── rag_index.py            # Indicizzazione documenti in ChromaDB per ricerca RAG
├── main.py                 # Entry point interfaccia a riga di comando
├── app.py                  # Server Flask: endpoint REST e streaming SSE per la web UI
├── launcher.py             # Avvia Flask in thread daemon e apre finestra nativa
├── create_app.sh           # Script bash: genera il bundle RaxeusAI.app con icona per macOS
├── create_app.ps1          # Script PowerShell: genera RaxeusAI.exe su Desktop (Windows)
├── hardware.py             # Rilevamento CPU/RAM/GPU + raccomandazione modello Ollama
├── loop_guard.py           # Anti-loop sul tool calling: hash, ping-pong, budget
├── doctor.py               # Diagnostica del sistema: Python, Ollama, modelli, dipendenze
├── templates/
│   └── index.html          # Markup interfaccia web principale (chat con tab multiple)
├── static/
│   ├── style.css           # Tema scuro e layout responsive
│   ├── app.js              # Logica client: tab, streaming SSE, color picker, ricerca chat
│   ├── logo.png            # Logo RaxeusAI
│   └── logo_lyric.png      # Logo RaxeusLyric
└── requirements.txt        # Dipendenze Python del progetto
```

---

## Requisiti

- Python 3.10+
- [Ollama](https://ollama.com) installato e in esecuzione
- Modello testo (default: `qwen3:8b`) e modello vision (default: `qwen2.5vl:7b`) scaricati localmente

```bash
ollama pull qwen3:8b
ollama pull qwen2.5vl:7b
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
| `doctor` | Esegue diagnostica completa del sistema |
| `hardware` | Mostra hardware rilevato e modello suggerito |
| `esci` | Chiude il programma |

---

## Configurazione

Tutte le impostazioni principali si trovano in `config.py`:

```python
MODEL = "qwen3:8b"                        # Modello Ollama per il testo
VISION_MODEL = "qwen2.5vl:7b"            # Modello Ollama per le immagini
OLLAMA_URL = "http://localhost:11434/v1"  # Endpoint API
AI_NAME = "Raxeus"                        # Nome dell'assistente
SYSTEM_PROMPT = "..."                     # Personalità e istruzioni base
```

`MODEL` deve supportare function calling. `VISION_MODEL` può essere qualsiasi modello vision disponibile su Ollama (`llava`, `moondream`, `minicpm-v`, `qwen2-vl`, ecc.).

---

## App desktop

**macOS:**
```bash
cd ~/RaxeusAI
bash create_app.sh
# → RaxeusAI.app sul Desktop. Prima apertura: tasto destro → Apri.
```

**Windows:**
```powershell
cd $HOME\RaxeusAI
powershell -ExecutionPolicy Bypass -File .\create_app.ps1
# → Desktop\RaxeusAI\RaxeusAI.exe — doppio click per avviare.
```

---

## Documentazione

| File | Contenuto |
|---|---|
| [docs/THEORY.md](docs/THEORY.md) | Concetti teorici: LLM, streaming, SSE, tool calling, LoopGuard, architettura |
| [docs/CODE.md](docs/CODE.md) | Documentazione tecnica di ogni file e dei flussi principali |
| [docs/WEB-UI.md](docs/WEB-UI.md) | Come funziona l'interfaccia web |
| [docs/BUGS.md](docs/BUGS.md) | Bug noti e fix applicati |
| [docs/JARVIS_INSPIRATION.md](docs/JARVIS_INSPIRATION.md) | Cosa è stato preso da [OpenJarvis](https://github.com/open-jarvis/OpenJarvis) e cosa no |

---

## RaxeusLyric

RaxeusAI include il modulo integrato **RaxeusLyric** (`/lyric`): cerca una canzone, scarica l'audio da YouTube, recupera il testo ufficiale e lo mostra sincronizzato con la musica in tempo reale — accessibile direttamente dalla chat tramite il bottone in topbar.

→ Documentazione completa: [docs/RAXEUS_LYRIC.md](docs/RAXEUS_LYRIC.md)
