# Progetti Personali — Area Personale VS

Tutti i progetti di Alberto Bruscolini si trovano in `/Users/alby/Desktop/AREA PERSONALE VS/`.

---

## RaxeusAI

**Percorso:** `AREA PERSONALE VS/RaxeusAI/`
**Repository:** https://github.com/AlbertoBruscoliniMain/RaxeusAI
**Stack:** Python, Flask, Ollama, ChromaDB

### Cos'è
Assistente AI personale locale con memoria, tool use, interfaccia web e RAG. Gira completamente offline su Ollama (modello: qwen3:8b). Progetto principale e più completo.

### Architettura
- `config.py` — configurazione centralizzata: MODEL, OLLAMA_URL, AI_NAME, SYSTEM_PROMPT, RAG_DB_PATH
- `memory.py` — gestione cronologia conversazione (lista di messaggi passata al modello ad ogni turno)
- `agent.py` — loop agente con streaming e tool calling. Due funzioni: `chat()` per terminale, `chat_stream()` per web UI (yielda eventi SSE)
- `tools.py` — tutte le funzioni eseguibili dall'AI: google_search, web_search, fetch_url, read_file, write_file, append_file, list_dir, read_pdf, run_python, get_datetime, wikipedia_search, rag_search
- `sessions.py` — salvataggio/caricamento conversazioni in JSON in `sessions/`
- `main.py` — CLI interattiva con comandi: reset, salva, sessioni, carica N, esci
- `app.py` — server Flask con endpoint `/chat` (SSE), `/sessions`, `/lyric` (modulo RaxeusLyric)
- `rag_index.py` — script CLI per indicizzare file nel database vettoriale RAG
- `rag_docs/` — documenti di conoscenza indicizzati per il RAG

### Modulo RaxeusLyric
Pipeline completa per testi musicali sincronizzati in tempo reale:
1. iTunes Search API → titolo canonico + artista + copertina
2. lyrics.ovh API → testo ufficiale della canzone
3. yt-dlp → download audio da YouTube (mp3, 192kbps)
4. faster-whisper → trascrizione con word timestamps
5. Forced alignment semi-globale → ogni riga del testo → timestamp preciso
6. Cache LRC + playlist.json → ricaricamenti istantanei

File: `lyric_downloader.py`, `lyric_transcriber.py`, `lyric_formatter.py`, `lyric_fetcher.py`, `lyric_song_finder.py`

### RAG (Retrieval Augmented Generation)
- Vector store: ChromaDB persistente in `rag_db/`
- Embedding model: all-MiniLM-L6-v2 (ONNX, ~80MB, scaricato automaticamente)
- Indicizzazione: `python rag_index.py <file_o_cartella>` — supporta .txt .md .pdf
- Chunk size: 600 caratteri, overlap 60
- Tool `rag_search` chiamato automaticamente dall'AI per domande su documenti personali

### Personalità di Raxeus
Raxeus è orgoglioso, pomposo, narcisista. Si vanta di ogni risposta. Parla di sé in terza persona quando soddisfatto. È condescendente in modo bonario. Non dice mai "non lo so" — usa i tool direttamente senza annunciarlo. Risponde sempre in italiano.

### Come avviare
```bash
# Terminale
ollama serve
source venv/bin/activate
python main.py

# Web UI
ollama serve
source venv/bin/activate
python app.py
# → http://localhost:5000
# → http://localhost:5000/lyric (RaxeusLyric)
```

### Dipendenze principali
openai, ddgs, googlesearch-python, requests, beautifulsoup4, pypdf, flask, chromadb, yt-dlp, faster-whisper

---

## OpenJarvis

**Percorso:** `AREA PERSONALE VS/OpenJarvis/`
**Repository:** https://github.com/open-jarvis/OpenJarvis
**Stack:** Python, Rust (estensioni via PyO3), FastAPI, uv
**Origine:** Stanford SAIL / Scaling Intelligence Lab / Hazy Research

### Cos'è
Framework open-source per AI personale locale-first. Motto: "Personal AI, On Personal Devices." Backend inference locale (Ollama, vLLM, llama.cpp, SGLang) con fallback cloud (OpenAI, Anthropic, Gemini, OpenRouter). Ricerca dimostra che modelli locali gestiscono già l'88.7% delle query single-turn.

### Architettura
- `src/` — core Python del framework
- `rust/` — estensioni Rust compilate via PyO3 + maturin (performance critica)
- `frontend/` — interfaccia web
- `configs/` — configurazioni modelli e hardware
- `examples/` — esempi di utilizzo
- `tests/` — test suite
- `deploy/` — configurazioni deployment
- `docs/` — documentazione MkDocs

### Tre pilastri
1. **Shared primitives** — building blocks per agenti on-device
2. **Evaluations** — metriche che includono energia, FLOPs, latenza, costo (non solo accuracy)
3. **Learning loop** — migliora i modelli usando trace data locali

### Installazione e utilizzo
```bash
git clone https://github.com/open-jarvis/OpenJarvis.git
cd OpenJarvis
uv sync                    # core
uv sync --extra server     # + FastAPI server
uv sync --extra dev        # + strumenti sviluppo

# Build estensione Rust
uv run maturin develop -m rust/crates/openjarvis-python/Cargo.toml

# Utilizzo
uv run jarvis init          # rileva hardware, consiglia motore
uv run jarvis ask "..."     # fai una domanda
uv run jarvis doctor        # diagnostica
```

### Note tecniche
- Richiede Python 3.14+
- Gestione dipendenze con `uv` (non pip standard)
- Rust richiede rustup installato
- Su Python 3.14: `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` prima di maturin
- Backend inference separato: Ollama (consigliato), vLLM, llama.cpp, SGLang
- Cloud: set variabile d'ambiente con API key (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, ecc.)
- Lock file: `uv.lock` (non modificare manualmente)
- Sponsor: Stanford, Google Cloud, Lambda Labs, Ollama, IBM Research

---

## RizzBot2.0

**Percorso:** `AREA PERSONALE VS/RizzBot2.0/`
**Stack:** Python, discord.py, yt-dlp, PyNaCl, davey

### Cos'è
Bot Discord per la riproduzione di musica vocale. Si connette a canali vocali e riproduce audio scaricato da YouTube tramite yt-dlp. Architettura a cog (moduli separati).

### Struttura
- `main.py` — entry point, carica il venv manualmente, configura intents, carica cog music, gestisce `on_ready`
- `cogs/music.py` — tutta la logica musicale (join, play, queue, skip, stop)
- `utils/` — utility condivise
- `requirements.txt` — discord.py >= 2.6.0, PyNaCl >= 1.5.0, yt-dlp >= 2024.1.1, aiohttp, python-dotenv, davey

### Note tecniche
- Il venv viene aggiunto manualmente a `sys.path` per garantire funzionamento indipendente da come viene lanciato
- `libopus` caricato manualmente: cerca prima in Homebrew Apple Silicon (`/opt/homebrew/lib/libopus.dylib`), poi Intel Mac, poi fallback Linux
- Token Discord da variabile d'ambiente via `python-dotenv` (file `.env`)
- Intents: `voice_states=True` (necessario per eventi vocali)
- `discord.Intents.default()` come base
- Prefix comandi: `!`

### Come avviare
```bash
# Creare .env con: DISCORD_TOKEN=il_tuo_token
source venv/bin/activate
python main.py
```

---

## auto_lyric_ai

**Percorso:** `AREA PERSONALE VS/auto_lyric_ai/`
**Stack:** Python, Flask, Whisper, yt-dlp, lyrics.ovh

### Cos'è
Precursore del modulo RaxeusLyric. Genera testi musicali sincronizzati in tempo reale con l'audio. Supporta interfaccia web (Flask) e CLI.

### Pipeline
1. Query utente (es. "Imagine - John Lennon")
2. Check cache (`lyrics_output/playlist.json`)
3. `song_finder.py` → iTunes API → titolo canonico, artista, cover
4. `lyrics_fetcher.py` → lyrics.ovh API → testo ufficiale
5. `downloader.py` → yt-dlp → audio mp3
6. `transcriber.py` → Whisper → trascrizione con word timestamps
7. Forced alignment → testo ufficiale + timestamp Whisper
8. Salvataggio `.lrc` e metadati

### Struttura
- `app.py` — Flask web server, route `/api/process` in SSE
- `main.py` — CLI
- `song_finder.py` — ricerca iTunes
- `lyrics_fetcher.py` — recupero testo da lyrics.ovh
- `downloader.py` — yt-dlp wrapper
- `transcriber.py` — Whisper + forced alignment
- `formatter.py` — salvataggio LRC, gestione playlist
- `templates/` — UI web
- `lyrics_output/` — output: playlist.json, *.lrc, audio/, covers/
- `docs/` — documentazione tecnica

### Differenze da RaxeusLyric
RaxeusLyric è integrato direttamente in RaxeusAI come modulo, con frontend più avanzato, bottone nella topbar, gestione cover migliorata e supporto Range HTTP per l'audio.

---

## AlbertoBruscolini.github.io

**Percorso:** `AREA PERSONALE VS/AlbertoBruscolini.github.io/`
**Repository:** https://github.com/AlbertoBruscolini/AlbertoBruscolini.github.io
**Stack:** HTML, CSS puro, JavaScript vanilla

### Cos'è
Portfolio personale di Alberto Bruscolini. Single-page website hostato su GitHub Pages.

### Caratteristiche tecniche
- Dark mode di default con light mode toggle
- CSS custom properties (variabili CSS) per temi
- Accent color: `#7B61FF` (viola) in dark mode, `#6B4FEF` in light mode
- Font: Familjen Grotesk (testo) + Martian Mono (codice monospace)
- Neon green per accenti speciali: `#39FF14` (dark) / `#16a34a` (light)
- Background dark: `#0d0d0d`, bg2: `#131313`
- Transizioni: `background 0.25s, color 0.25s`
- `scroll-behavior: smooth`
- Meta viewport per responsive
- `overflow-x: hidden` per evitare scroll orizzontale
- School banner in cima (collegamento ISIS Gobetti)

### Struttura HTML
- Nav con logo e toggle tema
- Hero section
- Sezione progetti
- Sezione skills/tecnologie
- Footer

---

## Tecnologie comuni tra i progetti

| Tecnologia | RaxeusAI | OpenJarvis | RizzBot | AutoLyric | Portfolio |
|---|---|---|---|---|---|
| Python | ✓ | ✓ | ✓ | ✓ | — |
| Flask | ✓ | — | — | ✓ | — |
| Ollama | ✓ | ✓ | — | — | — |
| yt-dlp | ✓ | — | ✓ | ✓ | — |
| Whisper | ✓ | — | — | ✓ | — |
| HTML/CSS/JS | ✓ | ✓ | — | ✓ | ✓ |
| SSE | ✓ | — | — | ✓ | — |
| Rust | — | ✓ | — | — | — |

---

## Note di sviluppo comuni

### Gestione virtual environment
Tutti i progetti Python usano un venv locale nella cartella del progetto. Il venv di RaxeusAI ha prompt rinominato "Raxeus" (`venv/bin/activate` → `VIRTUAL_ENV_PROMPT=Raxeus`).

### Pattern git usato
Branch principale: `main`. Commit in italiano con messaggi descrittivi. Repository su account `AlbertoBruscoliniMain` (GitHub principale) e `AlbertoBruscolini` (account secondario). Cartella `sessions/` e `rag_db/` in `.gitignore` (dati personali/generati).

### Schema colori comune (dark theme)
- Background: `#0d0d0d` o `#131313`
- Accent: `#7B61FF` (viola)
- Testo: `#ECECEC`
- Border: `#1f1f1f`
- Muted: `#555` / `#888`

### macOS-specific
- Libreria opus per Discord bot: path Homebrew Apple Silicon `/opt/homebrew/lib/libopus.dylib`
- Ollama su M3: usa Metal acceleration automaticamente
- Venv Python 3.14 (versione usata nei progetti)
