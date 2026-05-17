# Bug & Fix Log

Storico dei bug risolti e problemi noti del progetto Raxeus.

---

## Bug risolti

---

### BUG-001 — Raxeus risponde con dati vecchi (fermo al 2023)

**Stato:** ✅ Risolto (fix multipli)

**Sintomo:** Anche chiedendo informazioni recenti, Raxeus rispondeva con dati del suo training data (fermi al periodo di addestramento del modello), ignorando che poteva cercare su internet.

**Causa (primo fix):** `google_search` restituiva solo URL — nessun testo. Il modello riceveva una lista di link ma non poteva leggerne il contenuto, quindi cadeva sul proprio training data per formulare la risposta.

**Causa (secondo fix):** Il system prompt non istruiva esplicitamente il modello a usare i tool per informazioni recenti. Il modello rispondeva con il suo training data anche quando i tool erano disponibili.

**Fix applicati:**
1. `google_search` ora chiama direttamente `fetch_url` sulle prime 2 pagine trovate — restituisce contenuto reale
2. System prompt aggiornato: regola esplicita di usare i tool senza annunciarlo, mai usare il training data per info recenti
3. `advanced=True` rimosso da `google_search` (causava risultati vuoti su alcune versioni della libreria)
4. `duckduckgo-search` sostituito con `ddgs` (la libreria è stata rinominata) — fix del RuntimeWarning visibile a schermo
5. Warning stderr di `ddgs` soppresso con redirect `sys.stderr` dentro `web_search`
6. Data corrente iniettata nel system prompt via `datetime.now()` — il modello non può più confondersi sull'anno

---

### BUG-002 — Output interno dei tool visibile all'utente

**Stato:** ✅ Risolto

**Sintomo:** Durante una ricerca o esecuzione di tool, il terminale mostrava righe tipo `→ google_search({'query': '...'})` e `← risultato...`, interrompendo il flusso di lettura della risposta.

**Causa:** In `agent.py` erano presenti `print()` espliciti per mostrare il nome del tool chiamato e un'anteprima del risultato, pensati per debug.

**Fix applicato:** Rimossi i `print` di debug in `agent.py`. Ora il tool viene eseguito silenziosamente — l'utente vede solo la risposta finale.

---

### BUG-003 — venv con percorsi rotti dopo spostamento cartella

**Stato:** ✅ Risolto

**Sintomo:** Dopo che la cartella del progetto è stata rinominata da `AI personale` a `RaxeusAI`, il venv non si avviava e `pip` crashava con `cannot execute`.

**Causa:** Il file `venv/bin/activate` e gli script interni del venv contengono percorsi assoluti hardcoded al momento della creazione. Spostare o rinominare la cartella rompe questi riferimenti.

**Fix applicato:** Ricreato il venv da zero nella nuova posizione con `python3 -m venv venv` e reinstallate tutte le dipendenze.

**Nota per il futuro:** I venv non sono portabili — se sposti la cartella del progetto, ricreare sempre il venv.

---

### BUG-004 — `__pycache__` committato su GitHub

**Stato:** ✅ Risolto

**Sintomo:** Il primo commit includeva i file compilati `.pyc` nella cartella `__pycache__/`.

**Causa:** Il `.gitignore` iniziale conteneva solo `venv/`, senza escludere `__pycache__`.

**Fix applicato:** Aggiornato `.gitignore` con `__pycache__/` e `*.pyc`. I file già tracciati sono stati rimossi con `git rm -r --cached __pycache__/`.

---

### BUG-008 — Chatbox: spinner infinito quando Ollama è giù

**Stato:** ✅ Risolto

**Sintomo:** ogni prompt inviato dalla web UI lasciava lo spinner "elaborazione…" girare all'infinito senza alcun messaggio d'errore in chat. Si riproduceva al 100% lanciando l'app desktop senza avere Ollama in esecuzione.

**Causa:** in `chat_stream` di `agent.py`, la chiamata `client.chat.completions.create(stream=True)` sollevava un `ConnectionError` (porta 11434 rifiutata) **non catturato**. L'eccezione terminava il generator SSE; il browser riceveva solo l'evento iniziale `session_id` e non vedeva mai il `done`. Il listener `for await reader.read()` continuava ad aspettare dati che non sarebbero mai arrivati.

**Fix applicati:**
1. `try/except` attorno a `client.chat.completions.create(...)` in `chat_stream`: l'eccezione produce un `token` con messaggio chiaro (`❌ Impossibile contattare Ollama su 127.0.0.1:11434…`) e un `done`
2. Diagnosi specifica per errori comuni: connessione rifiutata, modello non installato (`ollama pull qwen3:8b`), altri errori generici
3. Loop di chunk wrappato in try che cattura anche eccezioni mid-stream e le notifica come errore in chat
4. `launcher.py` ora **avvia automaticamente Ollama** se la porta 11434 non risponde: cerca il binario in PATH/Homebrew/`/Applications/Ollama.app` e lo lancia con `subprocess.Popen([binary, "serve"], start_new_session=True)`. Se non lo trova, mostra un dialog `osascript` che invita a installarlo

---

### BUG-009 — Foto di documenti illeggibili dal modello vision

**Stato:** ⚠️ Mitigato — fix vero ancora da fare (BETA)

**Sintomo:** Allegando la foto di un documento (es. screenshot di un PDF), il modello rispondeva *"il documento non è completo, non riesco a leggere i contenuti"* anche con testo perfettamente leggibile.

**Causa:** L'unico modello vision installato di default sulla macchina di test era `llava:latest`. LLaVA ha capacità OCR molto deboli — vede che c'è del testo ma non lo trascrive. Lo stesso vale per `moondream`. Il modello realmente competente per OCR su Ollama (gennaio 2026) è `qwen2.5vl` (anche 3B).

**Mitigazioni applicate:**
1. System prompt vision riformulato in chiave "OCR + analista visivo" con istruzione esplicita: "Non dire mai 'il documento non è completo' senza prima aver provato a trascrivere ciò che vedi: se una parola è incerta, mettila tra `[parentesi quadre]`"
2. Quando l'utente allega un'immagine **senza scrivere niente**, il prompt di default chiede esplicitamente una trascrizione parola per parola
3. **Hint automatico in chat** quando il modello risolto è in `weak_ocr = {"llava", "llava:latest", "llava:7b", "llava:13b", "moondream", "moondream:latest"}`: prima della risposta compare un riquadro che suggerisce `ollama pull qwen2.5vl:3b`
4. Per i **documenti PDF/DOCX/testo** è stato aggiunto l'endpoint `/extract` che bypassa completamente il modello vision: il testo viene estratto server-side con `pypdf`/`python-docx` e prefisso al prompt del modello testo standard. Questo risolve il caso d'uso più frequente (analizzare un PDF) senza dipendere dall'OCR

**Fix vero da fare:** offrire il pull di `qwen2.5vl:3b` direttamente dall'interfaccia (modal "vuoi installare il modello consigliato? ~3GB") invece di limitarsi a un hint testuale. **Rimandato per mancanza di tempo nel ciclo di sviluppo corrente.**

---

### BUG-010 — Pulsante stop: stream Ollama continua in background

**Stato:** ✅ Risolto

**Sintomo:** Cliccando stop il browser interrompeva la SSE ma Ollama continuava a generare token "nel vuoto" per minuti, occupando CPU/GPU.

**Causa:** Cancellare la `fetch` lato browser provocava un `GeneratorExit` lato Flask al prossimo `yield`, ma il generator chiudeva senza notificare il client HTTP del modello.

**Fix applicato:** `try/except GeneratorExit` in `chat_stream` (sia nel blocco testo che in quello vision) che chiama esplicitamente `stream.close()` sull'oggetto OpenAI prima di re-sollevare l'eccezione per il cleanup. Salva inoltre la risposta parziale in `Memory` col marker `[interrotto]` così la cronologia resta coerente.

---

## Bug noti / da monitorare

---

### BUG-005 — `fetch_url` bloccato da siti con anti-scraping

**Stato:** ⚠️ Noto, parzialmente mitigato

**Sintomo:** Alcuni siti (es. LinkedIn, siti con Cloudflare) restituiscono errore 403 o pagina vuota quando `fetch_url` tenta di leggerli.

**Causa:** I siti rilevano il traffico automatico e bloccano le richieste non provenienti da browser reali.

**Mitigazione attuale:** `User-Agent` impostato a stringa browser standard.

**Possibile fix futuro:** Usare `playwright` o `selenium` per fetch con browser headless reale, oppure filtrare i domini problematici.

---

### BUG-006 — Memoria illimitata: context window overflow

**Stato:** ⚠️ Noto, non ancora risolto

**Sintomo:** In conversazioni molto lunghe o con molte chiamate a tool (che aggiungono messaggi extra alla history), il modello può raggiungere il limite di contesto e iniziare a troncare i messaggi più vecchi o restituire errori.

**Causa:** La `Memory` accumula tutti i messaggi senza limite. I risultati dei tool possono essere molto lunghi (fino a 3000 caratteri ciascuno).

**Possibile fix futuro:** Implementare una strategia di truncation — mantenere sempre il system prompt, gli ultimi N messaggi utente/assistant, e comprimere/rimuovere i messaggi tool più vecchi.

---

### BUG-007 — `run_python` usa il Python di sistema, non il venv

**Stato:** ⚠️ Noto, comportamento atteso ma da documentare

**Sintomo:** Se il codice eseguito da `run_python` importa librerie installate solo nel venv (es. `openai`), ottiene `ModuleNotFoundError`.

**Causa:** `subprocess.run(["python3", ...])` lancia il Python di sistema, non quello del venv.

**Possibile fix futuro:** Usare `sys.executable` invece di `"python3"` per lanciare il Python del venv corrente.

---

### BUG-011 — Chatbox e app desktop crashano su Windows

**Stato:** 🔴 Aperto — blocca l'uso su Windows. Non risolto per mancanza di tempo nel ciclo di sviluppo corrente.

**Sintomo:** Su Windows l'app desktop (bundle generato da `create_app.ps1` o lancio diretto di `python launcher.py`) crasha all'avvio o appena qualcosa va storto. La chatbox tramite browser (`python app.py` + apertura manuale di `http://localhost:5050`) parte ma alcuni endpoint backend chiamano `osascript` e falliscono.

**Causa:** Tutto il codice cross-cutting aggiunto nelle ultime release è scritto per macOS:

| File | Codice macOS-only |
|---|---|
| `launcher.py` | `_show_error` usa `osascript -e 'display dialog'` — su Windows il binario non esiste |
| `launcher.py` | `_find_ollama_binary` cerca solo `/opt/homebrew/bin`, `/usr/local/bin`, `/Applications/Ollama.app/...` |
| `launcher.py` | `subprocess.Popen(..., start_new_session=True)` — POSIX-only, su Windows va sostituito con `creationflags=DETACHED_PROCESS` |
| `app.py` | `_send_native_notification` lancia `osascript display notification` |
| `create_app.sh` | bash + `sips` + `iconutil` — strumenti macOS |

`create_app.ps1` esiste e genera un eseguibile via PyInstaller, ma il `launcher.py` bundlato è lo stesso codice macOS, quindi l'`.exe` crasha appena tenta di mostrare un dialog o cercare Ollama.

**Workaround attuale:** su Windows usare solo la modalità CLI: `python main.py`. Funziona regolarmente.

**Fix da fare (port Windows):**
- `_show_error`: dispatcher su `platform.system()`; su Windows `Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show(...)` via `powershell -NoProfile -Command`
- `_find_ollama_binary`: aggiungere `%LOCALAPPDATA%\Programs\Ollama\ollama.exe` e `C:\Program Files\Ollama\ollama.exe`
- `_start_ollama`: usare `creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS` su Windows
- `_send_native_notification`: balloon tip via `System.Windows.Forms.NotifyIcon` o toast WinRT (Win10+)
- Menu pywebview: testare che la callback funzioni anche con il chrome Win32 di pywebview (potrebbe servire Edge WebView2 invece del default)
- `create_app.ps1`: invariato dal punto di vista dello script, ma da rigenerare dopo il port di `launcher.py`

---

### BUG-012 — Solo 5 chat visibili nella topbar

**Stato:** ⚠️ Noto, comportamento atteso ma limitante

**Sintomo:** Se hai più di 5 sessioni salvate sul disco, l'interfaccia ne mostra solo 5 nella topbar (le più recenti). Le altre restano in `sessions/*.json` ma non sono raggiungibili dalla web UI.

**Causa:** `GET /sessions` ritorna `list_sessions()[:5]` e il limite client-side `MAX_TABS = 5`.

**Workaround:** lanciare `python main.py` e usare `sessioni` + `carica N` per caricare manualmente una sessione vecchia.

**Possibile fix:** menu "Tutte le chat" nella topbar che apre un overlay con la lista completa filtrabile.
