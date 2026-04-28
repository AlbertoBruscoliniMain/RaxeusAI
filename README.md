<p align="center">
  <img src="static/logo.png" alt="Raxeus" height="160">
  &nbsp;&nbsp;&nbsp;&nbsp;
  <img src="static/logo_lyric.png" alt="RaxeusLyric" height="160">
</p>

<h1 align="center">RaxeusAI</h1>

<p align="center">
  Assistente AI personale con memoria, tool use e interfaccia web — completamente offline, costruito su Ollama.
</p>

<p align="center">
  <b>Raxeus</b> — chat AI con tool use, memoria e visione &nbsp;|&nbsp; <b>RaxeusLyric</b> — testi musicali sincronizzati in tempo reale
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
- **RaxeusLyric** — modulo integrato per testi musicali sincronizzati: cerca una canzone, scarica l'audio, trascrive con Whisper e mostra il karaoke in tempo reale

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
├── launcher.py             # Avvia Flask in thread daemon e apre finestra nativa (WKWebView su Mac, Edge WebView2 su Windows)
├── create_app.sh           # Script bash: genera il bundle RaxeusAI.app con icona per macOS
├── create_app.ps1          # Script PowerShell: genera RaxeusAI.exe su Desktop via PyInstaller (Windows)
├── hardware.py             # Rilevamento CPU/RAM/GPU + raccomandazione modello Ollama (idea da OpenJarvis)
├── loop_guard.py           # Anti-loop sul tool calling: hash, ping-pong, budget (idea da OpenJarvis)
├── doctor.py               # Diagnostica del sistema: Python, Ollama, modelli, dipendenze (idea da OpenJarvis)
├── lyric_song_finder.py    # Identifica la canzone in riproduzione su macOS tramite osascript
├── lyric_fetcher.py        # Recupera testo e timestamp sincronizzati da API esterne (Genius/LRC)
├── lyric_downloader.py     # Scarica il file audio della canzone corrente per la trascrizione
├── lyric_transcriber.py    # Trascrive l'audio con Whisper e genera i timestamp parola per parola
├── lyric_formatter.py      # Formatta e allinea i testi per la visualizzazione sincronizzata
├── templates/
│   ├── index.html          # Markup interfaccia web principale (chat con tab multiple)
│   └── lyric.html          # Template per la visualizzazione dei testi sincronizzati (RaxeusLyric)
├── static/
│   ├── style.css           # Tema scuro e layout responsive
│   └── app.js              # Logica client: tab, streaming SSE, color picker, ricerca chat
└── requirements.txt        # Dipendenze Python del progetto
```

### Descrizione per file

| File | Cosa fa | A cosa serve |
|---|---|---|
| `config.py` | Definisce le costanti globali (modello, URL, nome AI, system prompt, path RAG) | Punto unico di configurazione: cambiare modello o personalità senza toccare altro codice |
| `memory.py` | Mantiene la lista dei messaggi della sessione corrente | Passa la cronologia completa al modello ad ogni turno, abilitando la memoria multi-turno |
| `agent.py` | Implementa il loop agente: invia messaggi, riceve risposte in streaming, rileva e esegue tool call, reinvia i risultati | Cuore del sistema: gestisce l'intero ciclo di ragionamento dell'AI |
| `tools.py` | Definisce le funzioni dei tool (web search, file, Python, PDF, Wikipedia, RAG…) e il loro schema JSON | Permette al modello di agire nel mondo reale chiamando funzioni esterne |
| `sessions.py` | Salva e carica le conversazioni come file JSON nella cartella `sessions/` | Persistenza delle chat tra sessioni diverse |
| `rag_index.py` | Legge i file in `rag_docs/`, li divide in chunk e li indicizza in ChromaDB | Costruisce la base di conoscenza locale consultabile dal tool `rag_search` |
| `main.py` | Loop CLI con comandi `reset`, `salva`, `sessioni`, `carica`, `esci` | Modalità terminale per uso rapido senza browser |
| `app.py` | Server Flask con endpoint `/chat` (POST) e `/stream` (SSE), gestione sessioni lato server | Backend della web UI: riceve i messaggi e trasmette le risposte token per token |
| `launcher.py` | Avvia Flask in un thread daemon e apre la web UI in una finestra nativa (WKWebView su Mac, Edge WebView2 su Windows) | Permette di usare RaxeusAI come app desktop senza aprire il browser |
| `create_app.sh` | Genera `RaxeusAI.app` con icona `.icns` sul Desktop tramite `sips`/`iconutil` | Crea il bundle macOS avviabile con doppio clic |
| `create_app.ps1` | Genera `RaxeusAI\RaxeusAI.exe` sul Desktop con PyInstaller, icona `.ico` da Pillow | Crea l'eseguibile Windows avviabile con doppio clic |
| `hardware.py` | Rileva CPU/RAM/GPU e suggerisce il modello Ollama più adatto | Aiuta l'utente a scegliere `MODEL` in base alla macchina; usato da `doctor` |
| `loop_guard.py` | Blocca pattern degeneri nel tool calling (hash identico, ping-pong, budget per tool) | Evita che l'agente si avviti in cicli inutili — idea adattata da OpenJarvis |
| `doctor.py` | Diagnostica completa: Python, Ollama, modelli, dipendenze | Comando `doctor` nella CLI; chiarisce subito perché qualcosa non funziona |
| `lyric_song_finder.py` | Interroga Music.app via osascript per ottenere titolo e artista della traccia corrente | Primo passo del modulo RaxeusLyric: identifica cosa si sta ascoltando |
| `lyric_fetcher.py` | Chiama API (Genius, LRC lib) per scaricare il testo con timestamp sincronizzati | Recupera i testi karaoke-style allineati alla traccia |
| `lyric_downloader.py` | Scarica l'audio della canzone corrente in un file temporaneo | Fornisce il file audio a Whisper per la trascrizione locale |
| `lyric_transcriber.py` | Esegue Whisper sull'audio scaricato e restituisce i segmenti con timestamp | Trascrizione locale come alternativa/verifica ai testi scaricati da API |
| `lyric_formatter.py` | Allinea e formatta i testi per la visualizzazione progressiva nel browser | Prepara i dati per il template `lyric.html` |
| `templates/index.html` | Struttura HTML della web UI principale: area chat, barra laterale sessioni, tab | Scheletro della pagina, collegato a `app.js` e `style.css` |
| `templates/lyric.html` | Pagina per la visualizzazione dei testi sincronizzati in tempo reale | Interfaccia del modulo RaxeusLyric |
| `static/style.css` | Definisce tema scuro, layout flex, stile bolle e animazioni | Aspetto visivo dell'intera applicazione web |
| `static/app.js` | Gestisce tab, invio messaggi, ricezione SSE, color picker, ricerca chat, localStorage | Tutta la logica interattiva del browser |
| `requirements.txt` | Lista le dipendenze Python con versioni | Permette di ricreare l'ambiente con `pip install -r requirements.txt` |

---

## Requisiti

- Python 3.10+
- [Ollama](https://ollama.com) installato e in esecuzione
- Modello testo (default: `qwen3:8b`) e modello vision (default: `llava`) scaricati localmente

```bash
ollama pull qwen3:8b
ollama pull llava
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
VISION_MODEL = "llava"                    # Modello Ollama per le immagini
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
| [docs/RAXEUS_LYRIC.md](docs/RAXEUS_LYRIC.md) | Come funziona il modulo RaxeusLyric: pipeline, codice, integrazione con l'app principale |
| [docs/WEB-UI.md](docs/WEB-UI.md) | Come funziona l'interfaccia web |
| [docs/BUGS.md](docs/BUGS.md) | Bug noti e fix applicati |
| [docs/JARVIS_INSPIRATION.md](docs/JARVIS_INSPIRATION.md) | Cosa è stato preso da [OpenJarvis](https://github.com/open-jarvis/OpenJarvis) e cosa no, file per file |
