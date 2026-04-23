# Codice — Documentazione tecnica

> Documentazione di ogni file del progetto Raxeus.
> Per i concetti teorici vedi [THEORY.md](THEORY.md). Per bug e fix vedi [BUGS.md](BUGS.md).

---

## Struttura del progetto

```
RaxeusAI/
├── config.py               → configurazione centralizzata (modello, URL, personalità, RAG_DB_PATH)
├── memory.py               → gestione cronologia conversazione + tool messages
├── agent.py                → loop agente con streaming, tool calling e chat_stream per la web UI
├── tools.py                → funzioni eseguibili dall'AI (web, file, PDF, Wikipedia, ora, RAG)
├── rag_index.py            → script CLI per indicizzare documenti nel database vettoriale RAG
├── sessions.py             → salvataggio e caricamento sessioni su file JSON
├── main.py                 → loop terminale (ancora funzionante)
├── app.py                  → server Flask: chat AI + modulo RaxeusLyric
│
├── lyric_downloader.py     → download audio da YouTube via yt-dlp
├── lyric_transcriber.py    → trascrizione Whisper + forced alignment testi
├── lyric_formatter.py      → salvataggio LRC, gestione playlist JSON, cache
├── lyric_fetcher.py        → recupero testi da lyrics.ovh API
├── lyric_song_finder.py    → ricerca metadati canzone via iTunes API
│
├── templates/
│   ├── index.html          → SPA chat: tutto il markup dell'interfaccia web
│   └── lyric.html          → pagina RaxeusLyric: player + testi sincronizzati
├── static/
│   ├── style.css           → tema scuro, layout completo
│   ├── app.js              → logica tab, streaming SSE, color picker, localStorage + bottone RaxeusLyric
│   └── logo.png            → icona/logo Raxeus
│
├── launcher.py             → entry point desktop: avvia Flask in thread + finestra nativa pywebview
├── create_app.sh           → script una-tantum: crea RaxeusAI.app sul Desktop (icona + bundle macOS)
├── AppIcon.icns            → icona macOS generata da create_app.sh (non committare)
│
├── rag_db/                 → generata a runtime — database vettoriale ChromaDB (persistent)
├── lyrics_output/          → generata a runtime
│   ├── playlist.json       → indice di tutte le canzoni elaborate
│   ├── *.lrc               → testi sincronizzati in formato LRC
│   ├── audio/              → file mp3 delle canzoni
│   └── covers/             → copertine album
├── requirements.txt        → dipendenze Python
└── venv/                   → ambiente virtuale (prompt: "Raxeus")
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
| `MODEL` | `str` | Nome del modello Ollama da usare per testo |
| `VISION_MODEL` | `str` | Nome del modello Ollama per analisi immagini (default: `llava`) |
| `OLLAMA_URL` | `str` | Endpoint del server Ollama locale |
| `AI_NAME` | `str` | Nome dell'assistente, usato nel prompt e nell'UI |
| `SYSTEM_PROMPT` | `str` | Personalità e istruzioni comportamentali dell'AI |
| `RAG_DB_PATH` | `str` | Path assoluto della cartella `rag_db/` per il database vettoriale |

**Modifiche applicate:**
- `AI_NAME` cambiato da `"Jarvis"` a `"Raxeus"`
- `SYSTEM_PROMPT` riscritto con personalità orgogliosa, pomposa, narcisista — si vanta di ogni risposta
- Data corrente iniettata dinamicamente all'avvio via `datetime.now()` — il modello sa sempre che anno è
- Aggiunta regola esplicita: usare i tool senza annunciarlo, mai fidarsi del training data per info recenti
- Aggiunta istruzione RAG: usare `rag_search` per domande su file/note/documenti personali dell'utente
- Aggiunto `RAG_DB_PATH` come costante di configurazione centralizzata

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

**`chat_stream(user_input, mem, images=None)`:** versione generator di `chat` per la web UI. Invece di stampare su stdout, yielda dizionari:
- `{"type": "token", "content": "..."}` — per ogni chunk di testo generato
- `{"type": "thinking"}` — quando il modello inizia una tool call
- `{"type": "done"}` — quando la risposta è completa

Viene chiamata da `app.py` e i dizionari vengono serializzati come eventi SSE inviati al browser.

**Flusso con immagini (`images` non None):**
1. Costruisce un messaggio multimodale OpenAI-format: `content = [{"type": "text", ...}, {"type": "image_url", "image_url": {"url": "data:image/...;base64,..."}}]`
2. Appende il messaggio alla history esistente (senza modificare `mem`) e chiama `VISION_MODEL` — senza tool schemas (la maggior parte dei modelli vision non li supporta)
3. Yielda i token normalmente
4. Salva in `mem` la versione **testo-only** del messaggio utente (`[N immagini allegate]` + eventuale testo) — così i turni successivi continuano con `MODEL` senza storia multimodale incompatibile

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
| `rag_search` | `rag_search(query, n_results)` | Cerca nei documenti personali indicizzati (ChromaDB). Restituisce i chunk più rilevanti con fonte |

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
- `rag_search` usa `chromadb.PersistentClient` (guard `_CHROMA_OK`); se la collection `documents` non esiste restituisce messaggio guida; `n_results=4` di default; ogni risultato è formattato con `[Fonte: path]` seguito dal chunk di testo

---

## rag_index.py

Script CLI standalone per indicizzare file di testo nel database vettoriale RAG. Non fa parte del loop agente — viene eseguito manualmente dall'utente per aggiornare la knowledge base.

```
Uso: python rag_index.py <file_o_cartella> [...]
```

**Formati supportati:** `.txt` `.md` `.pdf`

**Costanti:**
| Costante | Valore | Descrizione |
|---|---|---|
| `CHUNK_SIZE` | 600 | Caratteri per chunk |
| `CHUNK_OVERLAP` | 60 | Caratteri di sovrapposizione tra chunk adiacenti |
| `SUPPORTED_EXT` | `.txt .md .pdf` | Estensioni processate |

**Flusso:**
1. `collect_files(paths)` — espande file e cartelle ricorsivamente, filtra per estensione
2. `read_file(path)` — legge il testo grezzo (utf-8 con `errors="ignore"`; PDF via `pypdf`)
3. `chunk_text(text)` — sliding window con overlap; ignora chunk vuoti
4. `collection.upsert(...)` — inserisce o aggiorna i chunk nel DB con ID `abs_path::index` e metadata `source` + `file`
5. Stampa progress per ogni file e conteggio finale

**Deduplicazione:** usa `upsert` invece di `add` — rieseguire su un file già indicizzato aggiorna i chunk senza duplicare.

**Embedding:** ChromaDB usa `all-MiniLM-L6-v2` (ONNX, ~80MB) scaricato automaticamente al primo avvio — non richiede configurazione.

**Reset:** eliminare la cartella `rag_db/` e rieseguire.

---

## lyric_downloader.py

Scarica l'audio di una canzone da YouTube tramite **yt-dlp**.

```python
def download_audio(query: str) -> tuple[str, dict]
```

Cerca `ytsearch1:<query>` su YouTube, scarica solo la traccia audio nel miglior formato disponibile e la converte in mp3 a 192kbps via FFmpeg postprocessor. L'output va in `temp_audio/` (cartella temporanea dentro RaxeusAI). Restituisce `(file_path, metadata)` dove metadata contiene artista, titolo e URL thumbnail estratti dai metadati YouTube.

---

## lyric_transcriber.py

Trascrive l'audio e sincronizza i testi con i timestamp. È il modulo più complesso del progetto.

```python
def get_transcription(file_path: str, hint_lyrics: str = None) -> list[dict]
```

Restituisce una lista di segmenti `{"start": float, "end": float, "text": str}`.

**Flusso:**
1. Carica il modello `WhisperModel("small", device="cpu", compute_type="int8")` — modello small quantizzato, ~500MB RAM
2. Trascrive con `word_timestamps=True` per ottenere timestamp per ogni parola
3. Se `hint_lyrics` è fornito (testo ufficiale), chiama `_forced_align()` invece di usare la trascrizione grezza

**`_forced_align(lines, whisper_segs)`:** algoritmo di forced alignment a due fasi:
- `_collect_whisper_words` — estrae tutte le parole Whisper con i loro timestamp
- `_collect_lyric_words` — tokenizza le righe del testo, tenendo traccia dell'indice riga e posizione nella riga
- `_semi_global_align` — programmazione dinamica con matrice score n×m; i gap nel testo lirico costano `-1.15`, i gap Whisper costano `-0.45` (Whisper può aggiungere parole extra), i mismatch costano `-1.8`, i match esatti valgono `+2.6`
- Traceback della matrice → lista di coppie `(lyric_word_idx, whisper_word_idx)` allineate
- `_fill_missing_times` — interpolazione lineare per righe senza match diretto

**`_word_score(a, b)`:** valuta la somiglianza tra due parole normalizzate. Usa `difflib.SequenceMatcher` per coppie lunghe, con soglie 0.9 (strong) e 0.8 (weak).

---

## lyric_formatter.py

Gestisce il formato LRC, la playlist JSON e la cache locale.

```python
def save_as_lrc(segments, song_title) -> str          # salva file .lrc, ritorna il path
def update_playlist(title, lrc_path, audio, cover)    # aggiunge/aggiorna entry in playlist.json
def get_playlist_entry(query) -> dict | None          # cerca entry per titolo (fuzzy: "Title -- Artist")
def check_cache(query) -> list | None                 # ritorna segmenti se la canzone è in cache
def load_from_lrc(lrc_path) -> list                   # parse di un .lrc → lista segmenti
```

**Formato LRC:** ogni riga del testo è preceduta da `[mm:ss.xx]`. Il file include header `[ti:]` e `[by:AutoLyric AI]`.

**`_title_matches(stored, query)`:** corrispondenza fuzzy — considera match sia `"Imagine"` che `"Imagine -- John Lennon"` per la query `"Imagine"`.

**Output dir:** `lyrics_output/` relativa a `__file__` (dentro RaxeusAI dopo la copia del modulo).

---

## lyric_fetcher.py

Recupera il testo ufficiale di una canzone da **lyrics.ovh** (API pubblica, gratuita, senza chiave).

```python
def fetch_lyrics(artist: str, title: str) -> str | None
```

Prova più combinazioni artista/titolo in ordine: `(artista, titolo)` → `(artista_breve, titolo)` → `(titolo, artista)` (per query del tipo "Canzone - Artista"). `clean_title()` rimuove suffissi YouTube come `(Official Video)`, `[Lyrics]`, `(Remaster 2021)`, ecc. I marcatori di sezione (`[Verse 1]`, `[Chorus]`, ecc.) vengono rimossi dal testo restituito.

---

## lyric_song_finder.py

Identifica titolo canonico, artista e copertina tramite **iTunes Search API**.

```python
def find_song(query: str) -> dict | None
# ritorna {"title": str, "artist": str, "artwork_url": str} oppure None
```

Richiesta a `https://itunes.apple.com/search` con `entity=song&limit=1`. La copertina viene upgradrata automaticamente da 100×100px a 512×512px sostituendo la dimensione nell'URL. Timeout 7 secondi, nessuna dipendenza extra (usa solo `urllib` della stdlib).

---

## launcher.py

Entry point per la modalità **app desktop nativa**. Avvia Flask in un thread background e apre l'interfaccia in una finestra WebKit nativa tramite `pywebview` — nessun browser, nessuna barra URL.

```python
def _find_free_port() -> int: ...       # sceglie una porta TCP libera a runtime
def _start_flask(port: int) -> None:    # gira in thread daemon
def _wait_for_flask(url, retries, delay) -> bool:  # polling finché Flask è pronto
```

**Flusso di avvio:**
1. `logging.getLogger("werkzeug").setLevel(logging.ERROR)` — sopprime il banner Werkzeug prima di qualsiasi import Flask
2. `_HERE = os.path.dirname(os.path.abspath(__file__))` + `os.chdir(_HERE)` — garantisce che i path relativi di Flask (templates, static, sessions) funzionino da qualsiasi cwd; `sys.path.insert(0, _HERE)` rende importabile `app.py`
3. `_find_free_port()` — ottiene una porta TCP libera su `127.0.0.1` (nessun conflitto anche con più istanze)
4. Flask parte in un `threading.Thread` con `daemon=True` — viene ucciso automaticamente alla chiusura della finestra
5. `_wait_for_flask()` — polling con `urllib.request.urlopen` ogni 0.15s (max 40 tentativi = 6s timeout)
6. `webview.create_window()` + `webview.start()` — apre la finestra nativa e avvia il run loop (bloccante)

**Dettagli tecnici:**
- `debug=False` e `use_reloader=False` su Flask — obbligatori in modalità thread (il reloader fork il processo e rompe il run loop)
- La finestra parte 1280×820 con `min_size=(800, 600)`, `text_select=True` (testo selezionabile come in un browser)
- Il progetto deve trovarsi **fuori dalle cartelle protette da macOS TCC** (Desktop, Documents, Downloads) — vedi THEORY.md sezione TCC

**Avvio diretto (senza .app):**
```bash
source venv/bin/activate
python launcher.py
```

---

## create_app.sh

Script bash da eseguire **una sola volta** (o dopo aggiornamenti al logo o spostamento del progetto) per generare `RaxeusAI.app` sul Desktop macOS.

**Fasi:**

| Step | Operazione |
|---|---|
| 1 | Crop centrato del logo (1928×1138 → 1138×1138 quadrato) con `sips --cropOffset` |
| 2 | Generazione di tutte le risoluzioni richieste da macOS (`iconutil`): 16, 32, 64, 128, 256, 512px + varianti @2x |
| 3 | Conversione in `.icns` con `iconutil -c icns` |
| 4 | Creazione struttura `.app/Contents/{MacOS,Resources}` |
| 5 | Scrittura `Info.plist` (bundle ID, nome, icona, `NSAllowsLocalNetworking`) |
| 6 | Scrittura script eseguibile `Contents/MacOS/RaxeusAI` con path assoluti al venv e al launcher |
| 7 | `lsregister` — registra l'app con Launch Services per aggiornare l'icona in Finder |

**Struttura del bundle generato:**
```
RaxeusAI.app/
├── Contents/
│   ├── Info.plist
│   ├── MacOS/
│   │   └── RaxeusAI          ← bash script: cd ~/RaxeusAI && exec venv/python launcher.py
│   └── Resources/
│       └── AppIcon.icns
```

**Contenuto script `Contents/MacOS/RaxeusAI`:**
```bash
#!/bin/bash
cd "/Users/alby/RaxeusAI"
exec "/Users/alby/RaxeusAI/venv/bin/python" "/Users/alby/RaxeusAI/launcher.py"
```

**Note:**
- Il bundle contiene path assoluti → va ricreato con `bash create_app.sh` se il progetto viene spostato
- **Il progetto DEVE stare fuori da Desktop/Documents/Downloads** — macOS TCC blocca i processi del bundle dall'accedere a quelle cartelle (vedi THEORY.md). Il path corretto è `~/RaxeusAI/`
- Prima apertura: tasto destro → **Apri** (Gatekeeper blocca le app non firmate con firma Apple)
- `AppIcon.icns` è generato localmente — non va committato (aggiunto a `.gitignore`)

**Ricreazione:**
```bash
cd ~/RaxeusAI
bash create_app.sh
```

---

## app.py

Server Flask che espone la web UI. Mantiene un dizionario `_sessions: dict[str, Memory]` con una `Memory` attiva per ogni conversazione aperta nel browser.

### Endpoint chat (originali)

| Metodo | Path | Descrizione |
|---|---|---|
| `GET` | `/` | Serve `templates/index.html` |
| `POST` | `/chat` | Riceve `{message, session_id, images?}`, risponde in SSE con eventi `token`, `thinking`, `done` |
| `GET` | `/sessions` | Restituisce lista delle ultime 5 sessioni salvate su disco |
| `DELETE` | `/session/<id>` | Elimina il file sessione dal disco e rimuove la Memory dal dizionario |

**Gestione immagini in `/chat`:** accetta il campo opzionale `images` — lista di data URI base64 (`data:image/jpeg;base64,...`). Permette invio senza testo se almeno un'immagine è presente. Passa la lista a `chat_stream(images=...)` che smista al modello vision.

**`_get_memory(session_id)`:** recupera la Memory dal dizionario; se non esiste la crea, e se esiste un file sessione corrispondente lo carica automaticamente da disco.

### Endpoint RaxeusLyric (aggiunti)

| Metodo | Path | Descrizione |
|---|---|---|
| `GET` | `/lyric` | Serve `templates/lyric.html` |
| `GET` | `/lyric/api/process?query=` | Pipeline completa in SSE: ricerca → testo → download → trascrizione |
| `GET` | `/lyric/api/playlist` | Restituisce la playlist JSON con copertine validate |
| `GET` | `/lyric/api/load?title=` | Carica canzone dalla cache (segmenti + audio) |
| `POST` | `/lyric/api/delete` | Elimina canzone: rimuove LRC, mp3 e copertina + aggiorna playlist |
| `GET` | `/lyric/api/audio/<filename>` | Serve il file mp3 con `conditional=True` (supporto Range per seek) |
| `GET` | `/lyric/api/cover/<filename>` | Serve la copertina con mimetype auto-rilevato |

**Costanti di percorso:**
```python
_LYRIC_BASE   = os.path.dirname(__file__)          # radice RaxeusAI/
_LYRIC_OUT    = _LYRIC_BASE / "lyrics_output"      # output generale
_LYRIC_AUDIO  = _LYRIC_OUT  / "audio"             # mp3
_LYRIC_COVERS = _LYRIC_OUT  / "covers"            # copertine
```

**`/lyric/api/process` — eventi SSE emessi:**

| Evento `type` | Payload | Quando |
|---|---|---|
| `progress` | `message: str` | Ogni step della pipeline |
| `song_info` | `display_title: str` | Dopo risoluzione iTunes |
| `lyrics_found` | `lines: list[str]` | Quando il testo ufficiale è trovato |
| `error` | `message: str` | In caso di errore bloccante |
| `done` | `segments, audio, cover, cached, display_title` | Pipeline completata |

**Helper interni:**
- `_download_cover(url, title)` — scarica la copertina, deduplicandola per stem (rimuove versioni precedenti con estensione diversa)
- `_ensure_cover(entry)` — verifica che la copertina esista su disco; se manca, la ri-scarica da iTunes; usato in `/lyric/api/playlist` per riparare la libreria
- `_split_display_title(dt)` — separa `"Titolo -- Artista"` in `(titolo, artista)`, fallback su `" - "`

**Avvio:**
```bash
source venv/bin/activate
python app.py
# chat AI:    http://localhost:5000
# RaxeusLyric: http://localhost:5000/lyric
```

---

## templates/index.html

SPA unica. Contiene solo il markup HTML strutturale — nessuna logica. Carica `style.css` e `app.js`. Il DOM viene popolato interamente da `app.js` a runtime.

Struttura: `#topbar` (logo, `#btn-info`, ricerca, tab, pallino colore) → `#chat-area` (messaggi) → `#input-wrap` (`#img-preview-strip` + `#input-bar`: pulsante allega, textarea, pulsante invia) → `#info-overlay` (modal info, nascosto di default).

**Elementi aggiunti per immagini:**
- `#img-preview-strip` — div sopra l'input bar che mostra le anteprime delle immagini selezionate (nascosto quando vuoto via `:empty`)
- `#btn-attach` — label che wrappa l'`<input type="file" id="img-input" accept="image/*" multiple>` nascosto; click sul label apre il selettore file nativo

**Elementi aggiunti:**
- `#btn-info` — pulsante `ⓘ` accanto al logo, apre il modal info
- `#info-overlay` — overlay a schermo intero con sfondo semi-trasparente
- `#info-modal` — riquadro centrato con `#info-close` (✕) e `#info-cards` (contenitore card popolato da JS)

## templates/lyric.html

Pagina autonoma per il modulo RaxeusLyric. Struttura a tre zone:

- **Header** — logo Raxeus cliccabile (torna a `/`), barra di ricerca, bottone "← Chat"
- **Body** — sidebar sinistra (libreria canzoni) + area centrale (testi)
- **Player bar** — nascosta di default, appare quando l'audio è disponibile

**Funzionalità JavaScript inline** (nessun file esterno oltre a `lyric.html` stesso):
- `doSearch()` — apre un `EventSource` su `/lyric/api/process?query=` e gestisce tutti i tipi di evento SSE
- `renderLyrics(segs)` / `renderLyricsPreview(lines)` — due modalità: preview senza timestamp (durante il download) e testo finale con timestamp cliccabili
- `syncLyrics(ct)` — chiamata a ogni `timeupdate` dell'audio; trova il segmento attivo con ricerca lineare dal fondo, aggiorna classi `.active` / `.past` e scrolla automaticamente (inibito per 2.5s se l'utente ha scrollato manualmente)
- `seek(e)` — calcola la posizione relativa del click sulla barra di avanzamento e salta l'audio al timestamp corrispondente
- `refreshPlaylist()` / `loadFromPlaylist()` / `deleteSong()` — CRUD completo della libreria tramite le API `/lyric/api/*`

Tutte le chiamate API usano il prefisso `/lyric/api/` per non collidere con le route della chat.

---

## static/style.css

Tema scuro completo. Usa variabili CSS (`--bg`, `--bubble-bg`, `--bubble-text`, ecc.) per mantenere i colori coerenti e permettere futuri temi.

Elementi principali: `#topbar`, `.tab`, `.tab.active`, `.bubble-user`, `.bubble-ai`, `.spinner`, `#color-dot`, `#color-picker`, `.preset-dot`.

**Classi aggiunte per immagini:**
- `#btn-attach` — icona SVG cliccabile, colore dimmer con hover; wrappa l'input file nascosto
- `#img-preview-strip` — flex row con gap; nascosto automaticamente quando vuoto (`:empty { display: none }`)
- `.img-preview-wrap` — container relativo per thumbnail + bottone rimozione
- `.img-preview-thumb` — 58×58px, `object-fit: cover`, bordo sottile, border-radius 7px
- `.img-preview-rm` — cerchio 17×17px in posizione assoluta top-right, bottone ×
- `.bubble-imgs` — strip orizzontale di immagini dentro la bolla utente, flex + gap
- `.bubble-img` — immagine nella bolla, max 180×180px, border-radius 8px, `cursor: pointer`

**Elementi aggiunti:**
- `#btn-info` — stesso stile di `#btn-new` (niente bordo, colore dimmer, hover)
- `#info-overlay` / `#info-modal` — overlay fisso z-index 300, modal `#161616` con box-shadow
- `.info-card` — flex card con `background: #111`, bordo sottile, hover che schiarisce il bordo
- `.info-card-header` — riga avatar + testo (username + nome reale)
- `.info-card-avatar` — immagine circolare 38×38px
- `.info-card-desc` — bio in testo dim, `flex: 1` per occupare lo spazio disponibile
- `.info-card-stats` — riga inferiore con repo e follower in font 10px
- `.info-card-loading` — testo centrato mostrato durante il fetch

---

## static/app.js

Tutta la logica del frontend. Nessuna dipendenza esterna.

| Responsabilità | Funzioni chiave |
|---|---|
| Gestione tab | `addTab`, `activateTab`, `removeTab`, `renderTabs`, `newChat` |
| Messaggi e localStorage | `appendMessage`, `buildBubble`, `loadMessages`, `saveMessages`, `renderChat` |
| Streaming SSE | `sendMessage` — legge il body come stream, aggiorna la bolla AI token per token |
| Color picker | `setColor`, `loadColor`, `applyBubbleColor`, `updateColorDot`, `buildPresets` |
| Immagini | `renderImagePreviews`, `updateChatBottom`, listener su `imgInput` |

**Persistenza locale:** i messaggi di ogni chat sono in `localStorage` con chiave `chat_<session_id>`. Il colore bolla è in `bubble_color_<session_id>`. Al ricaricamento tutto viene ripristinato.

**Gestione immagini:**
- `selectedImages` — array di stato globale `[{file, dataUrl}]`, max 3 elementi
- `imgInput` change listener — converte ogni `File` in data URI via `FileReader.readAsDataURL`, aggiunge a `selectedImages`, chiama `renderImagePreviews`
- `renderImagePreviews()` — svuota e ricostruisce `#img-preview-strip`; ogni thumb ha un bottone × che rimuove l'elemento dall'array e ridisegna
- `updateChatBottom()` — misura `offsetHeight` di `#input-wrap` e lo imposta come `bottom` di `#chat-area`, necessario perché il preview strip cresce dinamicamente
- `buildBubble(role, content, images=[])` — se `images` non è vuoto, crea `.bubble-imgs` con i tag `<img>` prima del testo nella bolla utente
- `sendMessage` — raccoglie `selectedImages`, li svuota prima dell'invio, salva in localStorage solo il testo (o placeholder `[N immagini allegate]`), costruisce la bolla con le immagini reali, include `images: imagesToSend.map(i => i.dataUrl)` nel payload JSON verso `/chat`

**Nota localStorage:** le immagini non vengono salvate in localStorage (peso eccessivo). Al ricaricamento della pagina le bolle con immagini mostrano solo il testo placeholder; le immagini rimangono visibili solo durante la sessione corrente.

**Elementi aggiunti:**
- `btnInfo`, `infoOverlay`, `infoClose` — DOM refs per il modal info
- `loadInfoCards()` — fetch parallelo dei profili `AlbertoBruscoliniMain` e `AlbertoBruscolini` via `api.github.com/users/<username>`; costruisce le card dinamicamente e le inserisce in `#info-cards`; usa il flag `infoCardsLoaded` per evitare fetch ripetuti
- Event listeners: `btnInfo` → rimuove `.hidden` dall'overlay e chiama `loadInfoCards()`; `infoClose` → aggiunge `.hidden`; click sull'overlay stesso → chiude se il target è l'overlay (non la card)
- **Bottone RaxeusLyric** — iniettato via IIFE alla fine del file; crea un `<a href="/lyric">` con stile inline completo e lo inserisce nella topbar tramite `insertBefore(btn, colorWrap)`, prima del pallino colore. Hover gestito via `mouseenter`/`mouseleave` per non toccare `style.css`. Navigazione nella stessa finestra pywebview (nessun `target="_blank"`).

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
flask
chromadb
pywebview
```

**Dipendenze originali:** `duckduckgo-search`, `googlesearch-python`, `requests`, `beautifulsoup4` per ricerca web e fetch pagine; `pypdf` per PDF; `flask` per la web UI.

**Dipendenze aggiunte per RAG:**
- `chromadb` — database vettoriale locale persistente; include automaticamente `onnxruntime` e scarica `all-MiniLM-L6-v2` al primo utilizzo per gli embedding

**Dipendenze aggiunte per app desktop:**
- `pywebview` — finestra WebKit nativa su macOS; installa automaticamente `pyobjc-core`, `pyobjc-framework-WebKit`, `pyobjc-framework-Cocoa`, `pyobjc-framework-Quartz` e `bottle`

**Dipendenze per immagini:**
- Nessun pacchetto Python aggiuntivo — la conversione in base64 avviene interamente nel browser (JS `FileReader`); il payload arriva al backend come stringa e viene passato direttamente all'API OpenAI nel formato multimodale già supportato dall'SDK (`openai>=1.0`)
- Richiede **modello vision su Ollama**: `ollama pull llava` (o qualsiasi altro modello vision-capable — cambiare `VISION_MODEL` in `config.py`)

**Dipendenze aggiunte per RaxeusLyric** (installate nel venv, non ancora in requirements.txt):

| Pacchetto | Versione | Scopo |
|---|---|---|
| `yt-dlp` | 2026.3.17 | Download audio da YouTube |
| `faster-whisper` | 1.2.1 | Trascrizione audio con word timestamps |
| `ctranslate2` | 4.7.1 | Engine C++ per inferenza Whisper ottimizzata |
| `onnxruntime` | 1.24.4 | Dipendenza di faster-whisper per VAD |
| `huggingface-hub` | 1.10.2 | Download automatico pesi del modello Whisper |
| `tokenizers` | 0.22.2 | Tokenizzazione (dipendenza faster-whisper) |
| `av` | 17.0.0 | Lettura file audio (binding PyAV/FFmpeg) |
| `numpy` | 2.4.4 | Array numerici per il processing audio |

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

**Modalità terminale (classica):**
```bash
ollama serve
source venv/bin/activate
python main.py
```

**Modalità web (browser):**
```bash
ollama serve
source venv/bin/activate
python app.py
# apri http://localhost:5000
```

**Modalità desktop nativa (app macOS):**
```bash
# Il progetto deve essere in ~/RaxeusAI (non in Desktop/Documents/Downloads)

# Prima volta — crea RaxeusAI.app sul Desktop:
cd ~/RaxeusAI
bash create_app.sh
# Poi: doppio click su RaxeusAI.app (prima apertura: tasto destro → Apri)

# Se sposti il progetto, rigenera sempre il bundle:
bash create_app.sh

# Oppure, avvio diretto senza .app:
ollama serve
source venv/bin/activate
python launcher.py
```
