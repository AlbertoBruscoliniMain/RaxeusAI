# Chatbox — Guida completa all'interfaccia

> **Stato: BETA — solo macOS.** La chatbox e l'app desktop **girano esclusivamente su macOS**: `launcher.py` usa codice macOS-specifico (`osascript`, path Homebrew, notifiche AppleScript, dialog nativi). Il bundler Windows è stato rimosso dalla repo perché non funzionante — vedi [BUG-011](BUGS.md). Su Windows è disponibile solo la modalità terminale (`python main.py`).
>
> Anche su macOS alcune feature sono ancora in stabilizzazione. Vedi "[Limiti noti](#limiti-noti--cose-da-fixare)" in fondo prima di segnalare bug.
>
> Per i dettagli del codice vedi [CODE.md](CODE.md). Per i concetti teorici (SSE, streaming, tool calling) vedi [THEORY.md](THEORY.md). Per lo storico bug e fix vedi [BUGS.md](BUGS.md).

---

## Indice

1. [Idea di base](#idea-di-base)
2. [Avvio](#avvio)
3. [Layout dell'interfaccia](#layout-dellinterfaccia)
4. [Chat e tab](#chat-e-tab)
5. [Streaming dei token e pulsante Stop](#streaming-dei-token-e-pulsante-stop)
6. [Colore bolla](#colore-bolla)
7. [Allegati: immagini e documenti](#allegati-immagini-e-documenti)
8. [Modelli vision e OCR](#modelli-vision-e-ocr)
9. [Menu nativo (app desktop)](#menu-nativo-app-desktop)
10. [Notifiche di sistema](#notifiche-di-sistema)
11. [Persistenza](#persistenza)
12. [Modal "Info" e "Cosa so fare?"](#modal-info-e-cosa-so-fare)
13. [RaxeusLyric (modulo integrato)](#raxeuslyric-modulo-integrato)
14. [Limiti noti / cose da fixare](#limiti-noti--cose-da-fixare)

---

## Idea di base

La chatbox è l'interfaccia web di RaxeusAI. Tutto gira in **locale**: il backend è Flask (`app.py`), il modello è Ollama, il frontend è una SPA vanilla in `templates/index.html` + `static/app.js`. Lo streaming dei token avviene via **SSE** (Server-Sent Events).

Due modi per usarla:

| Modalità | Come si avvia | Cosa apre |
|---|---|---|
| Browser | `python app.py` | finestra del browser su `http://localhost:5050` |
| App desktop nativa | doppio click su `RaxeusAI.app` | finestra WebKit senza barra URL |

Il codice è lo stesso — l'app desktop è solo `launcher.py` che fa partire Flask in un thread e apre `pywebview`.

---

## Avvio

**Browser (dev):**
```bash
ollama serve            # se non è già attivo
source venv/bin/activate
python app.py
# apri http://localhost:5050
```

**App desktop (macOS):**
```bash
# Prima volta — crea RaxeusAI.app sul Desktop:
cd ~/RaxeusAI
bash create_app.sh

# Poi: doppio click sull'app. Prima apertura: tasto destro → Apri (Gatekeeper).
```

L'app desktop **avvia automaticamente Ollama** se non è in esecuzione (cerca il binario in PATH, Homebrew o `/Applications/Ollama.app`). Se non lo trova mostra un dialog nativo che invita a installarlo da [ollama.com](https://ollama.com).

---

## Layout dell'interfaccia

```
┌───────────────────────────────────────────────────────────────┐
│ [logo] [ⓘ] [?] [cerca] [tab1] [tab2] … [+]    [pallino colore]│  ← topbar
├───────────────────────────────────────────────────────────────┤
│                                                               │
│   Risposta AI (con avatar a sinistra)                         │
│                                                                │
│                            ┌──────────────────┐                │
│                            │  Messaggio user  │  ← bolla       │
│                            └──────────────────┘    colorata    │
│                                                                │
├───────────────────────────────────────────────────────────────┤
│ [📎] [textarea messaggio                          ] [invia]    │  ← input bar
└───────────────────────────────────────────────────────────────┘
```

**Topbar (fissa in cima):**
- `logo` Raxeus
- `ⓘ` apre il modal con info su autori del progetto (profili GitHub)
- `?` apre il modal "Cosa so fare?" con la mappa delle feature
- campo `cerca…` filtra le tab visibili mentre scrivi
- tab delle chat aperte (max 5)
- `+` apre una nuova chat
- pallino colore in fondo a destra: cambia il colore della bolla della chat attiva

**Area chat:**
- I messaggi AI sono **senza bolla** (solo testo + avatar logo a sinistra)
- I messaggi utente sono in una **bolla colorata** a destra (colore personalizzabile per chat)
- Durante l'elaborazione compare uno **spinner** con "elaborazione…"
- Il rendering supporta Markdown (via `marked.js`), formule LaTeX (`$...$`, `$$...$$` via KaTeX) e diagrammi Mermaid

**Input bar (fissa in fondo):**
- `📎` apre il selettore file (immagini *e* documenti)
- `textarea` cresce automaticamente; `Enter` invia, `Shift+Enter` va a capo
- `invia` diventa `stop` rosso durante lo streaming (vedi [Stop](#streaming-dei-token-e-pulsante-stop))
- Sopra l'input bar, una **strip di anteprime** mostra gli allegati selezionati prima dell'invio

---

## Chat e tab

- **Massimo 5 tab aperte** contemporaneamente. Aprirne una sesta chiude automaticamente la più vecchia (e cancella la sua sessione su disco).
- Ogni tab ha un `session_id` (UUID v4) e una `Memory` sul backend. La cronologia viene salvata in `sessions/session_<id>.json` ad ogni risposta completata.
- **All'avvio dell'app**, le ultime 5 sessioni vengono ricaricate come tab via `GET /sessions`. Le sessioni precedenti restano su disco ma non sono più visibili (si possono comunque caricare manualmente con `python main.py` → `carica N`).
- **Titolo della tab**: provvisorio coi primi 30 caratteri del primo messaggio. Quando arriva la prima risposta, il backend chiama `generate_title()` (chiamata extra a Ollama) per ottenere un titolo breve di 3-4 parole che descriva l'argomento, e lo applica via `POST /title`.
- **Chiudere una tab** (`x` sulla tab) elimina il file sessione, la `Memory` in RAM, i messaggi in `localStorage` e il colore bolla salvato per quella chat.

---

## Streaming dei token e pulsante Stop

Le risposte arrivano **token per token** in tempo reale (come ChatGPT), via SSE.

Il pulsante `invia` cambia ruolo durante lo streaming:

| Stato | Etichetta | Colore | Click |
|---|---|---|---|
| Idle | `invia` | bianco | Invia il messaggio |
| Streaming | `stop` | rosso | Interrompe la risposta |

**Come funziona lo stop:**

1. Lato browser, `AbortController` annulla la `fetch` SSE.
2. Lato Flask, il generator riceve `GeneratorExit` al prossimo `yield`.
3. In `agent.py`, il blocco intercetta `GeneratorExit`, chiama `stream.close()` sull'HTTP request verso Ollama (così il modello smette davvero di lavorare invece di continuare a "generare nel vuoto") e salva la risposta parziale in memoria col marker `[interrotto]`.
4. La bolla AI mostra il testo già ricevuto + `_[interrotto]_` in corsivo.

Se interrompi **prima** che inizi a uscire testo (es. durante un tool call lungo), vedi `[interrotto prima della risposta]`.

---

## Colore bolla

Ogni chat ha il proprio colore di bolla utente, salvato in `localStorage` con chiave `bubble_color_<session_id>`. Cambiare chat ⇒ cambia colore.

Click sul pallino in topbar (in alto a destra) per aprire il color picker:

| Preset | Sfondo | Testo |
|---|---|---|
| Grigio scuro (default) | `#252525` | `#c0c0c0` |
| Verde | `#1e3a1e` | `#c8e6c9` |
| Blu | `#1a2a3a` | `#b3d4f5` |
| Viola | `#2a1a3a` | `#d4b3f5` |
| Rosso | `#3a1a1a` | `#f5b3b3` |
| Ambra | `#2a2a18` | `#f5e6b3` |
| Custom | color picker hex libero | `#c0c0c0` |

---

## Allegati: immagini e documenti

Il pulsante `📎` apre il selettore file. Sono supportati **due flussi diversi** per due tipi di file:

### Immagini (`image/*`)

Max **3 immagini per messaggio**. Vengono convertite in data URI base64 nel browser (`FileReader`) e inviate al backend come parte del payload `/chat`. Il backend le passa al `VISION_MODEL` configurato in `config.py`.

- Trascina, paste (`Cmd+V` da appunti) o seleziona via dialog
- Anteprime quadrate 64×64 nella strip sopra l'input
- Click sul `×` di un'anteprima per rimuoverla
- Il messaggio può essere inviato anche **senza testo** se c'è almeno un'immagine: in quel caso il backend invia al modello vision un prompt di default che chiede una **trascrizione OCR completa**

### Documenti (PDF, DOCX, testo)

Max **3 documenti per messaggio**, max **10 MB cad.**.

Estensioni supportate: `.pdf` `.docx` `.txt` `.md` `.csv` `.json` `.html` `.xml` `.log` `.py` `.js` `.ts` `.css` (e molte altre — vedi `_TEXT_EXTS` in `tools.py`).

**Flusso (diverso dalle immagini):**
1. Il browser carica il file in `POST /extract` (multipart)
2. Il backend usa `_read_pdf` / `_read_docx` / `_read_plain` di `tools.py` per estrarre il testo
3. Il testo torna al browser e viene mostrato come **chip** nella strip ("📄 nome_file.pdf · N caratteri")
4. All'`invia`, il testo dei documenti viene **prefisso al messaggio** come blocco `--- Documento allegato: X ---\n<contenuto>` e il tutto va al modello testo standard

In questo modo i PDF/DOCX **non passano per il modello vision**, evitando del tutto il problema OCR — il testo arriva pulito direttamente al modello.

**In localStorage** salviamo solo `userText + [doc: nome.pdf]`, mai il contenuto estratto (potrebbe essere enorme).

---

## Modelli vision e OCR

Per analizzare il contenuto di una **foto di un documento** o di uno screenshot serve un modello vision con buona OCR. Lo stato dell'arte (gennaio 2026) per Ollama è `qwen2.5vl` (3B basta).

`config.py`:
```python
VISION_MODEL = "qwen2.5vl:7b"  # preferito
VISION_FALLBACKS = ("qwen2.5vl:3b", "llava:latest", "llava",
                    "llama3.2-vision", "minicpm-v", "moondream")
```

**Risoluzione automatica del modello:**
- `_resolve_vision_model()` in `agent.py` interroga `/api/tags` di Ollama all'avvio
- Sceglie `VISION_MODEL` se presente, altrimenti il primo dei `VISION_FALLBACKS` installato
- Il risultato è cachato per tutta la sessione

**Hint in chat per modelli OCR-deboli:**
Se il modello risolto è `llava` o `moondream` (entrambi noti per OCR scadente), prima della risposta compare automaticamente un riquadro che suggerisce:
```
ollama pull qwen2.5vl:3b
```
e di riavviare l'app.

**System prompt OCR:**
Il prompt vision è scritto in modo aggressivo per impedire al modello di "rifiutarsi" di leggere documenti densi:
> Sei un OCR + analista visivo. La tua priorità assoluta è LEGGERE il testo… Non dire mai 'il documento non è completo' senza prima aver provato a trascrivere ciò che vedi: se una parola è incerta, mettila tra `[parentesi quadre]`.

---

## Menu nativo (app desktop)

Quando lanci la versione `.app` su macOS, in alto compare un menu nativo:

| Menu | Voce | Effetto |
|---|---|---|
| **File** | Nuova chat | apre una tab vuota |
| | Apri Chat | torna alla home `/` |
| | Apri RaxeusLyric | apre `/lyric` nella stessa finestra |
| **Info** | Cosa so fare? | apre il modal "?" |
| | About RaxeusAI | apre il modal "ⓘ" |

Le voci richiamano i bottoni HTML via `window.evaluate_js()` di pywebview.

---

## Notifiche di sistema

Quando arriva una risposta lunga e la finestra **non è in primo piano**, ricevi una notifica nativa macOS.

**Trigger:**
- `document.visibilityState !== 'visible'` o `!document.hasFocus()`
- E la risposta ha richiesto >4 secondi (sotto i 4s non ti disturbiamo)

**Implementazione:**
- Frontend: chiama `POST /notify` con title + un'anteprima della risposta (140 char)
- Backend: lancia `osascript -e 'display notification ...'` in un thread

Nessuna dipendenza extra, niente permessi browser, niente PWA.

---

## Persistenza

| Cosa | Dove | Quando |
|---|---|---|
| Cronologia messaggi (lato server) | `sessions/session_<id>.json` | salvata ad ogni risposta completata |
| Cronologia messaggi (lato browser, per render veloce) | `localStorage.chat_<id>` | ad ogni messaggio |
| Colore bolla per chat | `localStorage.bubble_color_<id>` | al cambio colore |
| Dimensione/posizione finestra app | `sessions/_window_state.json` | alla chiusura della finestra |
| Sessioni in topbar all'avvio | `GET /sessions` → ultime 5 | al caricamento di `index.html` |

Lo `_window_state.json` è scritto dal `window.events.closing` di pywebview e riletto al prossimo avvio così la finestra riapre dove l'avevi lasciata.

---

## Modal "Info" e "Cosa so fare?"

**`ⓘ`** — apre un modal con due card affiancate per gli autori (`AlbertoBruscoliniMain` e `AlbertoBruscolini`). Dati fetchati al primo click da `api.github.com/users/<username>` e poi cachati per la sessione: avatar, username, nome reale, bio, repo pubblici, follower. Click sulla card apre il portfolio in una nuova scheda.

**`?`** — apre un modal "Cosa so fare?" con la mappa visuale delle feature divisa in due sezioni:

- **⚡ Core AI**: Ricerca Web (Google + DuckDuckGo), Esecuzione Python (run_python), Memoria RAG (rag_search su ChromaDB), Gestione File (read/write/list)
- **🎵 RaxeusLyric**: Download Audio AI (yt-dlp), Trascrizione Magica (Whisper), Sincronizzazione Karaoke (forced alignment)

Click su una card apre un modal di dettaglio con esempi d'uso.

---

## RaxeusLyric (modulo integrato)

Bottone in topbar (iniettato via JS) apre `/lyric` nella stessa finestra. È un'app separata dentro la stessa Flask: ricerca canzone → download YouTube → trascrizione AI → testo sincronizzato karaoke.

Documentazione completa: [docs/RAXEUS_LYRIC.md](RAXEUS_LYRIC.md).

---

## Limiti noti / cose da fixare

> **L'interfaccia è in BETA.** Quello che segue è quello che *non* è ancora a posto. È in roadmap, ma non ha fatto in tempo per questa release.

### 🟠 Upload foto / OCR (priorità alta)

- Su una macchina che ha **solo `llava` o `moondream`** installato (il caso default di Ollama), inviare la foto di un documento produce risposte tipo *"il documento non è completo, non riesco a leggere"*. Il modello vede il testo ma non riesce a estrarlo.
- **Workaround documentato**: `ollama pull qwen2.5vl:3b` e riavvia l'app. Il fallback in `agent.py` lo prende automaticamente. La chat te lo segnala quando rileva un modello OCR-debole, ma la prima volta passa in mezzo a una risposta sbagliata.
- **Fix vero da fare**: offrire il pull del modello dall'interfaccia stessa (modal "vuoi installare qwen2.5vl:3b? ~3GB") invece di limitarsi a un hint testuale. **Non ho fatto in tempo a implementarlo.**
- Per i PDF/DOCX **questo non è un problema**: passano per `/extract` con `pypdf` / `python-docx`, niente vision, testo perfetto.

### 🟠 Immagini non persistenti nel browser

Le immagini allegate non vengono salvate in `localStorage` (occuperebbero MB). Quando ricarichi una chat che conteneva immagini, vedi solo il placeholder `[N immagini allegate]`. La risposta dell'AI invece resta integra.

### 🟡 Le tab oltre la 5ª spariscono

Se hai >5 chat sul disco, l'interfaccia ne mostra solo 5. Le altre restano salvate ma non sono raggiungibili senza usare il CLI (`python main.py` → `sessioni` / `carica N`).

### 🔴 Chatbox solo su macOS

`launcher.py` è scritto in modo specifico per macOS:
- chiama `osascript` per dialog ed notifiche native
- cerca il binario `ollama` in `/opt/homebrew/bin`, `/usr/local/bin` e `/Applications/Ollama.app/Contents/Resources/`
- usa `start_new_session=True` su `Popen` (concetto POSIX, niente equivalente diretto su Windows)
- il menu pywebview è testato solo sulla menu bar macOS

Lo script bundler `create_app.ps1` è stato **rimosso dalla repo** perché produceva un eseguibile che crashava all'avvio (vedi sopra: il `launcher.py` bundlato non funzionava su Windows). Non c'è stato tempo per fare il port in questa release. Su Windows è disponibile solo `python main.py` (CLI), che funziona regolarmente. Roadmap del port in [BUG-011](BUGS.md).

### 🟡 Run_python con Python di sistema

`run_python` esegue codice col `python3` di sistema, non il venv di RaxeusAI. Se chiedi all'AI di importare `openai` o altre librerie del venv, ottieni `ModuleNotFoundError`. Vedi [BUGS.md BUG-007](BUGS.md).

### 🟡 Tool risultati grandi possono saturare il context

`google_search` può restituire fino a 6000 caratteri (2 pagine × 3000). In una chat lunga con molte ricerche, la memoria comprime ma può comunque saturare il context del modello. Vedi [BUGS.md BUG-006](BUGS.md).

---

Quando uno di questi viene risolto, lo si sposta in [BUGS.md](BUGS.md) come "✅ Risolto".
