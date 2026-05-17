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

<p align="center">
  <img src="https://img.shields.io/badge/status-BETA-orange?style=flat-square">
  <img src="https://img.shields.io/badge/platform-macOS-blue?style=flat-square">
  <img src="https://img.shields.io/badge/runtime-Ollama-black?style=flat-square">
  <img src="https://img.shields.io/badge/python-3.10+-yellow?style=flat-square">
</p>

> **⚠️ La chatbox è in BETA — solo macOS.**
>
> Due cose non sono ancora a posto e **non c'è stato tempo per fixarle in questa release**:
>
> 1. **La chatbox/app desktop gira solo su macOS.** Su Windows l'app crasha all'avvio (`launcher.py` usa codice macOS-only: `osascript`, path Homebrew, notifiche AppleScript). Vedi [docs/BUGS.md BUG-011](docs/BUGS.md). La modalità terminale (`python main.py`) funziona ovunque.
> 2. **L'invio di foto con testo richiede di installare manualmente `qwen2.5vl:3b`** (vedi sotto e [docs/BUGS.md BUG-009](docs/BUGS.md)) — il modello vision di default `llava` ha OCR insufficiente. Per allegare PDF/DOCX questo problema **non si pone**: vengono estratti server-side senza passare per il modello vision.

---

## Panoramica

RaxeusAI è un agente AI locale scritto in Python. Usa un modello LLM tramite [Ollama](https://ollama.com) con API compatibile OpenAI, e implementa un loop agente completo: memoria multi-turno, function calling, streaming dei token e persistenza delle sessioni.

Il progetto supporta due modalità di utilizzo sullo stesso backend:

| Modalità | Entry point | Interfaccia | Piattaforma |
|---|---|---|---|
| Terminale | `main.py` | CLI interattiva | macOS, Windows, Linux |
| Web / app desktop | `app.py` o `launcher.py` | Browser via Flask + SSE oppure finestra nativa pywebview | **solo macOS** |

> **⚠️ La chatbox (web UI + app desktop) gira solo su macOS.** Il `launcher.py` è scritto specificamente per macOS (auto-start Ollama via Homebrew, dialog `osascript`, notifiche AppleScript, menu pywebview testato solo su macOS). Su Windows **l'app crasha all'avvio** e `create_app.ps1` produce un eseguibile non funzionante. Non è stato possibile portare il codice per mancanza di tempo nel ciclo di sviluppo corrente — vedi [docs/BUGS.md BUG-011](docs/BUGS.md). La modalità terminale (`python main.py`) invece **funziona su qualsiasi sistema**.

---

## Funzionalità

### Core agente
- **Streaming token-by-token** — le risposte appaiono in tempo reale, sia nel terminale che nel browser
- **Tool use autonomo** — l'AI decide autonomamente quando e quali tool chiamare, senza richiedere conferma
- **Tool call paralleli** — più tool nello stesso turno vengono eseguiti in parallelo (idea da OpenJarvis)
- **LoopGuard** — blocca chiamate identiche ripetute, pattern ping-pong e budget per tool (idea da OpenJarvis)
- **Memoria conversazionale con compressione automatica** — sliding window quando la cronologia supera 100 messaggi (idea da OpenJarvis)
- **Sessioni persistenti** — le conversazioni possono essere salvate su file JSON e ricaricate in sessioni successive
- **Hardware detection + comando `doctor`** — al primo avvio scopri qual è il modello giusto per il tuo hardware (idea da OpenJarvis)

### Chatbox (web UI + app desktop)
- **Tab multiple** (max 5) con ricerca chat, color picker bolla, titolo generato dall'AI
- **Pulsante Stop** — interrompe lo streaming in corso e chiude lo stream Ollama lato server (non lascia generazioni in background)
- **Allega documenti** — PDF, DOCX, testo, codice (max 10MB cad., max 3 per messaggio): estrazione server-side via `pypdf`/`python-docx`, niente OCR
- **Allega immagini** — fino a 3 foto per messaggio inviate al modello vision (`qwen2.5vl` consigliato, vedi sotto)
- **Rendering Markdown + LaTeX + Mermaid** — risposte con formule (`$...$`, `$$...$$` via KaTeX) e diagrammi vengono renderizzate graficamente
- **Auto-start Ollama** (macOS) — l'app desktop lancia `ollama serve` da sola se la porta 11434 non risponde
- **Menu nativo** — File / Info nella menu bar macOS, navigazione tra Chat e RaxeusLyric
- **Notifiche di sistema** — quando la risposta arriva ma la finestra non è in primo piano
- **Persistenza dimensione finestra** — l'app riapre dove l'hai lasciata
- **Cold-start ottimizzato** — import lazy delle librerie pesanti (chromadb, requests, pypdf): tempo di apertura ridotto di ~400 ms

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
├── create_app.ps1          # Script Windows (PyInstaller) — NON FUNZIONANTE, vedi BUGS.md
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
- [Ollama](https://ollama.com) installato (l'app desktop lo avvia da sola se non è in esecuzione)
- Modello testo (default: `qwen3:8b`) e modello vision (default: `qwen2.5vl:7b`) scaricati localmente

```bash
ollama pull qwen3:8b        # modello testo (richiesto)
ollama pull qwen2.5vl:7b    # modello vision con OCR forte (consigliato, ~5GB)
ollama pull qwen2.5vl:3b    # alternativa più leggera (~3GB)
```

> **Importante per l'OCR di foto/screenshot:** se hai solo `llava` o `moondream` installati (i default di molti tutorial Ollama), l'analisi di immagini contenenti testo darà risultati pessimi. Usa `qwen2.5vl:3b` come minimo. L'app rileva il modello attivo e te lo segnala in chat se è troppo debole.

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

**Interfaccia web (solo macOS):**

```bash
ollama serve
source venv/bin/activate
python app.py
# apri http://localhost:5050
```

> Su Windows il server Flask parte ma il `launcher.py` (che apre la finestra nativa) crasha; il browser puro potrebbe funzionare per testing ma non è una via supportata.

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

## App desktop (deploy) — solo macOS

Lo "deploy" di RaxeusAI è il bundle nativo. Non c'è un server da pubblicare: tutto gira in locale via Ollama, quindi creare il bundle è l'unica operazione di rilascio necessaria.

```bash
cd ~/RaxeusAI
bash create_app.sh
# → ~/Desktop/RaxeusAI.app
# Prima apertura: tasto destro → Apri (per aggirare Gatekeeper)
```

`create_app.sh` genera l'icona `.icns`, costruisce il bundle `.app` con `Info.plist` corretto, e lancia `lsregister` per far comparire l'icona in Finder. Rilanciarlo dopo modifiche al codice **non è necessario** — il bundle punta al `launcher.py` originale via path assoluti.

**Pulizia / reinstallazione:**
```bash
rm -rf ~/Desktop/RaxeusAI.app   # rimuove il bundle
bash create_app.sh              # ricrea da zero
```

### Stato Windows

`create_app.ps1` esiste nella repo ma **non produce un'app funzionante**: il `launcher.py` che viene bundlato usa API specifiche macOS (`osascript`, path `/opt/homebrew`, notifiche AppleScript) e crasha all'avvio su Windows. Lo script PowerShell e l'`.exe` generato vanno considerati **placeholder** finché non sarà fatto il port — vedi [docs/BUGS.md BUG-011](docs/BUGS.md) per la lista di cosa portare. Su Windows usa `python main.py` (CLI), che funziona regolarmente.

---

## Documentazione

| File | Contenuto |
|---|---|
| [docs/WEB-UI.md](docs/WEB-UI.md) | **Guida completa alla chatbox** — layout, tab, immagini, documenti, stop, notifiche, menu, OCR, limiti BETA |
| [docs/CODE.md](docs/CODE.md) | Documentazione tecnica di ogni file e dei flussi principali |
| [docs/THEORY.md](docs/THEORY.md) | Concetti teorici: LLM, streaming, SSE, tool calling, LoopGuard, architettura |
| [docs/BUGS.md](docs/BUGS.md) | Bug noti e fix applicati (BUG-001…BUG-012) |
| [docs/RAXEUS_LYRIC.md](docs/RAXEUS_LYRIC.md) | Modulo RaxeusLyric: karaoke con trascrizione AI |
| [docs/JARVIS_INSPIRATION.md](docs/JARVIS_INSPIRATION.md) | Cosa è stato preso da [OpenJarvis](https://github.com/open-jarvis/OpenJarvis) e cosa no |

---

## RaxeusLyric

RaxeusAI include il modulo integrato **RaxeusLyric** (`/lyric`): cerca una canzone, scarica l'audio da YouTube, recupera il testo ufficiale e lo mostra sincronizzato con la musica in tempo reale — accessibile direttamente dalla chat tramite il bottone in topbar.

→ Documentazione completa: [docs/RAXEUS_LYRIC.md](docs/RAXEUS_LYRIC.md)
