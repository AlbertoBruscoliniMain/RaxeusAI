# Documento dei Requisiti — RaxeusAI

> **Studente:** Alberto Bruscolini

---

## 1. Introduzione

### 1.1 Scopo del documento

Questo documento:

- descrive il prodotto realizzato dallo studente Alberto Bruscolini;
- raccoglie i requisiti funzionali e non funzionali;
- presenta i diagrammi e i casi d'uso organizzati nelle fasi di analisi, sviluppo e rifinitura;
- definisce la roadmap di lavoro con milestone e Gantt.

### 1.2 Contesto

RaxeusAI è un'applicazione web completa con backend in Python/Flask, interfaccia dinamica con streaming in tempo reale e integrazione con un LLM locale tramite Ollama.

La persistenza non utilizza un database relazionale: le conversazioni vengono salvate come file JSON nella cartella `sessions/`, scelta coerente con la natura single-user dell'applicazione. I documenti personali dell'utente vengono invece indicizzati in un database vettoriale (ChromaDB) per la funzionalità RAG.

### 1.3 Tema d'esempio

**RaxeusAI** è un assistente AI personale che gira completamente offline tramite Ollama. Risponde in streaming token per token, esegue tool reali in autonomia (anche più tool in parallelo nello stesso turno), e dispone di un'interfaccia web con tab multiple, tema scuro, personalizzazione grafica, rendering formule matematiche tramite **KaTeX** e generazione automatica del titolo della chat tramite AI.

Include il modulo **RaxeusLyric** per la ricerca e visualizzazione karaoke di testi musicali sincronizzati in tempo reale. È disponibile come app desktop nativa sia su **macOS** (bundle `.app`) sia su **Windows** (eseguibile `.exe` via PyInstaller), ed è dotato di sistemi di robustezza ispirati al framework open-source [OpenJarvis](https://github.com/open-jarvis/OpenJarvis): LoopGuard contro i loop nel tool calling, compressione automatica del context, hardware detection con raccomandazione del modello e comando `doctor` per la diagnostica.

---

## 2. Obiettivi generali

- Permettere all'utente di conversare con un LLM locale in tempo reale, con risposte in streaming token per token.
- Eseguire tool reali in autonomia: ricerca web (Google e DuckDuckGo), esecuzione di codice Python, lettura/scrittura file, lettura PDF, ricerca Wikipedia, data e ora, esplorazione directory, ricerca RAG su documenti locali.
- Eseguire più tool call in parallelo nello stesso turno per ridurre la latenza.
- Mantenere la memoria conversazionale multi-turno con compressione automatica della cronologia oltre i 100 messaggi.
- Bloccare loop degeneri nel tool calling (chiamate identiche ripetute, pattern ping-pong, budget per tool).
- Gestire sessioni multiple: creazione, navigazione, eliminazione, ricerca e persistenza su file.
- Offrire un'interfaccia web con tab multiple, ricerca nelle chat, tema scuro e color picker per le bolle.
- Renderizzare formule matematiche LaTeX nelle risposte tramite KaTeX.
- Generare automaticamente il titolo della chat in base all'argomento discusso.
- Analizzare immagini allegate ai messaggi tramite un modello vision dedicato.
- Visualizzare in tempo reale i testi sincronizzati di una canzone ricercata dall'utente (modulo RaxeusLyric).
- Funzionare in modo identico su **macOS**, **Windows** e **Linux**, sia come applicazione web sia come app desktop nativa.

---

## 3. Stakeholder e attori

| Stakeholder | Ruolo | Interesse |
| --- | --- | --- |
| Alberto Bruscolini | Sviluppatore | Realizzare e mantenere il progetto |
| Docente | Valutatore | Verificare correttezza tecnica e completezza dei requisiti |
| Utente finale | Utente singolo locale | Usare l'assistente per domande, ricerche e automazioni |

### Attori principali

**Utente locale (Web UI)** — interagisce con l'assistente tramite il browser o l'app desktop nativa; gestisce le chat, allega immagini e usa il modulo RaxeusLyric.

**Utente locale (CLI)** — interagisce con l'assistente da terminale; usa i comandi diagnostici `doctor` e `hardware`, gestisce sessioni manualmente.

L'applicazione è **single-user** e non prevede autenticazione né registrazione.

---

## 4. Requisiti funzionali

### 4.1 Requisiti principali

| # | Requisito |
| --- | --- |
| RF-01 | Invio di messaggi all'assistente e ricezione delle risposte in streaming token per token. |
| RF-02 | Esecuzione autonoma di tool: ricerca web (Google + DuckDuckGo), lettura/scrittura file, esecuzione Python, lettura PDF, ricerca Wikipedia, data e ora, esplorazione directory, ricerca RAG. |
| RF-03 | Memoria conversazionale multi-turno: la cronologia completa viene passata al modello a ogni turno. |
| RF-04 | Compressione automatica della cronologia quando supera 100 messaggi (sliding window + troncamento tool result vecchi). |
| RF-05 | Esecuzione parallela dei tool call quando il modello ne emette più di uno nello stesso turno. |
| RF-06 | Protezione anti-loop: rilevamento di chiamate identiche ripetute, pattern ping-pong A-B-A-B e budget massimo per singolo tool (LoopGuard). |
| RF-07 | Gestione sessioni multiple: creazione, navigazione, chiusura, ricerca e persistenza su file JSON. |
| RF-08 | Interfaccia web con tab multiple, barra di ricerca, color picker per le bolle utente e tema scuro. |
| RF-09 | Rendering del markdown nelle risposte (titoli, codice, tabelle, grassetto, liste). |
| RF-10 | Rendering formule matematiche LaTeX tramite KaTeX (`$...$` inline, `$$...$$` display), attivo durante lo streaming e al caricamento dalla cache. |
| RF-11 | Generazione automatica del titolo della chat: al termine della prima risposta il modello produce un titolo di 3-4 parole che aggiorna la tab in background. |
| RF-12 | Caricamento di fino a 3 immagini per messaggio; il modello vision le analizza e risponde anche in assenza di testo. |
| RF-13 | Modulo RaxeusLyric: ricerca canzone (iTunes API), recupero testo ufficiale (lyrics.ovh), download audio (yt-dlp + FFmpeg), trascrizione con timestamp per parola (faster-Whisper), forced alignment testo-audio (programmazione dinamica), visualizzazione karaoke sincronizzata, cache locale LRC + mp3. |
| RF-14 | App desktop nativa su macOS tramite pywebview + bundle `.app` generato da `create_app.sh`. |
| RF-15 | App desktop nativa su Windows tramite pywebview + PyInstaller, eseguibile `.exe` generato da `create_app.ps1`. |
| RF-16 | Rilevamento hardware (CPU, RAM, GPU) e raccomandazione automatica del modello Qwen3 più adatto. |
| RF-17 | Comando `doctor`: diagnostica completa di versione Python, raggiungibilità Ollama, modelli e dipendenze, con report a checklist `✓` / `!` / `✗`. |
| RF-18 | Interfaccia terminale con comandi `reset`, `salva`, `sessioni`, `carica <N>`, `doctor`, `hardware`, `esci`. |

### 4.2 User stories

- **Come utente**, voglio inviare un messaggio e vedere la risposta apparire in tempo reale, token per token, senza attendere il completamento.
- **Come utente**, voglio che l'assistente cerchi informazioni su internet autonomamente quando non le conosce, senza che io debba chiederlo esplicitamente.
- **Come utente**, voglio tenere più conversazioni aperte contemporaneamente in tab separate e passare da una all'altra.
- **Come utente**, voglio ritrovare una vecchia conversazione cercandola per parola chiave nella barra di ricerca.
- **Come utente**, voglio personalizzare il colore delle bolle dei miei messaggi per ogni chat.
- **Come utente**, voglio che le mie conversazioni vengano salvate automaticamente e siano disponibili alla prossima apertura dell'app.
- **Come utente**, voglio allegare fino a 3 immagini a un messaggio per farle analizzare dall'assistente.
- **Come utente**, voglio vedere le formule matematiche renderizzate graficamente invece di leggere i simboli LaTeX grezzi.
- **Come utente**, voglio che il titolo della tab si aggiorni automaticamente con l'argomento discusso senza doverlo inserire manualmente.
- **Come utente**, voglio cercare una canzone e vedere il testo scorrere sincronizzato con la musica in tempo reale.
- **Come utente CLI**, voglio eseguire un comando `doctor` per sapere subito se tutto il sistema è configurato correttamente.
- **Come utente CLI**, voglio sapere qual è il modello Qwen3 più adatto al mio hardware prima di configurare l'applicazione.

---

## 5. Requisiti non funzionali

| # | Requisito |
| --- | --- |
| RNF-01 | **Offline-first**: il modello LLM gira localmente tramite Ollama; non è richiesta connessione internet per la chat (i tool di ricerca web la usano solo se invocati). |
| RNF-02 | **Streaming SSE**: le risposte vengono trasmesse tramite Server-Sent Events; il browser riceve e visualizza i token man mano che vengono generati. |
| RNF-03 | **Backend Python/Flask**: tutto il server è scritto in Python 3.10+ con Flask; nessun framework frontend pesante. |
| RNF-04 | **Ambiente virtuale**: il progetto è installabile e avviabile tramite `venv` e `pip install -r requirements.txt`. |
| RNF-05 | **Tema scuro responsivo**: l'interfaccia web usa variabili CSS, si adatta a qualsiasi larghezza e non usa framework CSS esterni. |
| RNF-06 | **Persistenza sessioni**: le conversazioni sopravvivono al riavvio dell'app e vengono ripristinate automaticamente. |
| RNF-07 | **Modularità**: ogni responsabilità è in un modulo separato (`memory.py`, `agent.py`, `tools.py`, `sessions.py`, `loop_guard.py`, ecc.). |
| RNF-08 | **Cross-platform**: subprocess Python usano `sys.executable`; path con `os.path.join`; rilevamento hardware con API native per ogni OS. |
| RNF-09 | **Gestione del context**: la compressione automatica della cronologia evita di saturare la finestra del modello durante chat molto lunghe. |
| RNF-10 | **Robustezza agente**: LoopGuard blocca silenziosamente i loop restituendo un messaggio di errore al modello invece di sollevare eccezioni. |

---

## 6. Casi d'uso

### 6.1 Casi d'uso essenziali

**Web UI:**

1. `Invia messaggio`
2. `Ricevi risposta in streaming`
3. `Esecuzione automatica tool`
4. `Apri nuova chat`
5. `Cambia tab attiva`
6. `Chiudi tab`
7. `Cerca tra le chat`
8. `Personalizza colore bolla`
9. `Carica sessione passata`
10. `Allega immagini al messaggio`
11. `Visualizza formula matematica`
12. `Generazione automatica titolo chat`

**RaxeusLyric:**

13. `Cerca canzone`
14. `Visualizza testi sincronizzati`
15. `Riproduci audio`

**CLI:**

16. `Avvia assistente da terminale`
17. `Diagnostica del sistema (doctor)`
18. `Rilevamento hardware`

### 6.2 Descrizione semplificata dei casi d'uso

| Caso d'uso | Descrizione |
| --- | --- |
| **Invia messaggio** | L'utente digita un testo nella textarea e preme Invio (o il tasto "invia"); il frontend esegue una POST a `/chat` con testo, ID sessione e eventuali immagini base64. |
| **Ricevi risposta in streaming** | Il backend apre una connessione SSE e invia eventi `token` con ogni chunk di testo; il frontend aggiorna la bolla AI in tempo reale e chiama `marked.parse()` + `renderMathInElement()` ad ogni aggiornamento. |
| **Esecuzione automatica tool** | Durante la generazione, il modello emette una o più `tool_call`; il backend le esegue (anche in parallelo) e restituisce i risultati al modello che continua la risposta. |
| **Apri nuova chat** | L'utente clicca `+`; viene creato un UUID univoco, aggiunta una nuova tab con titolo "Nuova chat" e localStorage inizializzato. |
| **Cambia tab attiva** | L'utente clicca su una tab esistente; il frontend carica la cronologia da localStorage e ridisegna la chat. |
| **Chiudi tab** | L'utente clicca la `×` sulla tab; localStorage e sessione server vengono eliminati, si attiva la tab precedente. |
| **Cerca tra le chat** | L'utente digita nella barra di ricerca; le tab vengono filtrate in tempo reale per titolo (case-insensitive). |
| **Personalizza colore bolla** | L'utente clicca il pallino colorato, sceglie un preset o un colore custom; il colore viene salvato in `localStorage` con chiave `bubble_color_<id>`. |
| **Carica sessione passata** | All'avvio vengono recuperate le ultime 5 sessioni dal server; selezionandone una, la cronologia viene ripristinata nella tab corrente. |
| **Allega immagini al messaggio** | L'utente seleziona fino a 3 file dal selettore; `FileReader` li converte in data URI e mostra le anteprime; all'invio vengono inclusi nel payload JSON e il backend li passa al modello vision. |
| **Visualizza formula matematica** | Le risposte contenenti espressioni LaTeX (`$...$`, `$$...$$`) vengono renderizzate graficamente da KaTeX; il rendering avviene sia durante lo streaming che al ricaricamento dalla cache. |
| **Generazione automatica titolo chat** | Al completamento della prima risposta, il frontend chiama `POST /title`; il backend invoca `generate_title()` che chiede al modello un titolo breve (3-4 parole) e lo restituisce; la tab si aggiorna senza interrompere il flusso. |
| **Cerca canzone** | L'utente digita il nome di una canzone in RaxeusLyric; il frontend apre un `EventSource` su `/lyric/api/process`; il backend esegue la pipeline (iTunes → lyrics.ovh → yt-dlp → Whisper → forced alignment) inviando eventi SSE di avanzamento. |
| **Visualizza testi sincronizzati** | I segmenti con timestamp vengono renderizzati come righe cliccabili; `syncLyrics()` evidenzia la riga attiva ad ogni `timeupdate` dell'audio e fa auto-scroll (inibito per 2.5s se l'utente ha scrollato manualmente). |
| **Riproduci audio** | Il player in fondo alla pagina RaxeusLyric usa `<audio>` nativo con seek tramite click sulla barra di avanzamento; supporto Range HTTP per lo scrubbing immediato. |
| **Diagnostica del sistema** | Il comando `doctor` (o `python main.py doctor`) verifica Python ≥ 3.10, raggiungibilità di Ollama, presenza dei modelli configurati e delle dipendenze; stampa un report a checklist. |
| **Rilevamento hardware** | Il comando `hardware` rileva CPU, RAM totale e GPU (NVIDIA via `nvidia-smi`, Apple via `system_profiler`), calcola la memoria utilizzabile e suggerisce il tier Qwen3 più adatto. |

### 6.3 Relazioni tra casi d'uso: include ed extend

**Definizioni:**

- `<<include>>` — il caso d'uso base **include sempre** il sotto-caso; il comportamento è obbligatorio.
- `<<extend>>` — il sotto-caso **estende opzionalmente** il base; si attiva solo in certe condizioni.

**Relazioni `<<include>>`:**

| Base | → | Include |
| --- | --- | --- |
| `Invia messaggio` | include | `Ricevi risposta in streaming` |
| `Ricevi risposta in streaming` | include | `Esecuzione automatica tool` |
| `Cerca canzone` | include | `Visualizza testi sincronizzati` |
| `Visualizza testi sincronizzati` | include | `Riproduci audio` |

**Relazioni `<<extend>>`:**

| Extend | → | Base | Condizione |
| --- | --- | --- | --- |
| `Allega immagini al messaggio` | extend | `Invia messaggio` | Se l'utente ha selezionato almeno un'immagine |
| `Visualizza formula matematica` | extend | `Ricevi risposta in streaming` | Se la risposta contiene espressioni LaTeX |
| `Generazione automatica titolo chat` | extend | `Ricevi risposta in streaming` | Solo al completamento della prima risposta nella chat |
| `Carica sessione passata` | extend | `Apri nuova chat` | Se l'utente sceglie una sessione esistente invece di crearne una nuova |
| `Personalizza colore bolla` | extend | `Apri nuova chat` | La personalizzazione è opzionale |

### 6.4 Diagramma dei casi d'uso

**Attori e use case:**

```mermaid
graph LR
    U1["👤 Utente locale\n· Web UI ·"]

    U1 --> a(["Invia messaggio"])
    U1 --> b(["Apri nuova chat"])
    U1 --> c(["Cambia tab attiva"])
    U1 --> d(["Chiudi tab"])
    U1 --> e(["Cerca tra le chat"])
    U1 --> f(["Personalizza colore bolla"])
    U1 --> g(["Carica sessione passata"])
    U1 --> h(["Allega immagini al messaggio"])
    U1 --> i(["Cerca canzone · RaxeusLyric"])

    U2["👤 Utente locale\n· CLI ·"]

    U2 --> j(["Avvia assistente da terminale"])
    U2 --> k(["Diagnostica sistema · doctor"])
    U2 --> l(["Rilevamento hardware"])
    U2 --> m(["Salva / Carica sessione"])
```

**Relazioni include / extend:**

```mermaid
graph LR
    IM(["Invia messaggio"])
    RS(["Ricevi risposta in streaming"])
    ET(["Esecuzione automatica tool"])
    FM(["Visualizza formula matematica"])
    GT(["Generazione titolo chat"])
    AI(["Allega immagini al messaggio"])
    CC(["Cerca canzone"])
    VT(["Visualizza testi sincronizzati"])
    RA(["Riproduci audio"])
    SP(["Carica sessione passata"])
    NC(["Apri nuova chat"])

    IM      -->|"«include»"| RS
    RS      -->|"«include»"| ET
    RS      -. "«extend»" .-> FM
    RS      -. "«extend»" .-> GT
    AI      -. "«extend»" .-> IM
    SP      -. "«extend»" .-> NC
    CC      -->|"«include»"| VT
    VT      -->|"«include»"| RA
```

---

## 7. Glossario dei termini

| Termine | Definizione |
| --- | --- |
| **LLM** | Large Language Model — modello di linguaggio addestrato su grandi corpus di testo che genera risposte token per token. |
| **Ollama** | Strumento open-source per eseguire modelli LLM localmente; espone un'API compatibile con OpenAI. |
| **Token** | Unità minima di testo elaborata dal modello (circa 3-4 caratteri in media). |
| **Tool calling** | Capacità del modello di richiamare funzioni esterne durante la generazione, riceverne il risultato e continuare la risposta. |
| **Streaming** | Tecnica che invia la risposta token per token man mano che viene generata, invece di aspettare il completamento. |
| **SSE** | Server-Sent Events — protocollo HTTP per aggiornamenti push unidirezionali dal server al browser su una connessione persistente. |
| **Sessione** | Conversazione singola identificata da UUID, salvata come file JSON in `sessions/`. |
| **Memoria conversazionale** | Lista dei messaggi della sessione corrente, passata integralmente al modello a ogni turno. |
| **RAG** | Retrieval-Augmented Generation — tecnica che arricchisce la risposta del modello con documenti locali recuperati tramite ricerca semantica vettoriale (ChromaDB). |
| **ChromaDB** | Database vettoriale embedded in Python; usato da RaxeusAI per indicizzare e cercare documenti locali. |
| **Tab** | Scheda nella web UI che rappresenta una sessione di chat aperta. |
| **LoopGuard** | Modulo che protegge l'agente da loop di tool calling; rileva chiamate identiche ripetute, pattern ping-pong e budget esauriti per singolo tool. Ispirato a OpenJarvis. |
| **OpenJarvis** | Framework open-source (Apache 2.0) da cui RaxeusAI prende spunto per LoopGuard, esecuzione parallela dei tool, compressione del context, hardware detection e comando `doctor`. |
| **KaTeX** | Libreria JavaScript per il rendering rapido di formule matematiche LaTeX nel browser. |
| **pywebview** | Libreria Python che apre una finestra nativa con WebKit (WKWebView su macOS, Edge WebView2 su Windows) puntata a un server Flask locale. |
| **PyInstaller** | Tool che impacchetta un progetto Python in un eseguibile standalone (`.exe`); usato su Windows. |
| **Vision model** | Modello multimodale capace di ricevere immagini come input; in RaxeusAI è configurato tramite `VISION_MODEL` in `config.py`. |
| **Hardware tier** | Classificazione della macchina in base a RAM/VRAM disponibile, usata per suggerire il modello Qwen3 più adatto. |
| **LRC** | Formato standard per testi musicali sincronizzati; ogni riga è preceduta da un timestamp `[mm:ss.xx]`. |
| **Whisper / faster-whisper** | Modello di riconoscimento vocale di OpenAI (addestrato su 680.000 ore); faster-whisper è la reimplementazione con CTranslate2, 4× più veloce e con timestamp per singola parola. |
| **yt-dlp** | Strumento per il download di audio/video da YouTube; usato da RaxeusLyric per scaricare la traccia audio. |
| **Forced alignment** | Algoritmo di programmazione dinamica che allinea le parole del testo ufficiale con le parole trascritte da Whisper (che portano i timestamp), producendo un timestamp preciso per ogni riga. |

---

## 8. Pianificazione e milestone

| Settimana | Date | Attività |
| --- | --- | --- |
| 1 | 14–18 apr | Analisi requisiti, setup ambiente (Ollama, venv, Flask), struttura moduli |
| 2 | 21–25 apr | Backend: `memory.py`, `agent.py`, loop con streaming, tool calling base |
| 3 | 28 apr–2 mag | Tool avanzati (RAG, PDF, Wikipedia), web UI (SSE, tab, sessioni), immagini |
| 4 | 5–9 mag | App desktop (pywebview, create_app.sh/ps1), KaTeX, titolo smart, RaxeusLyric |
| 5 | 12–16 mag | Nuovi loghi, AppIcon, fix ffmpeg, documentazione tecnica (CODE.md, RAXEUS_LYRIC.md) |
| 6 | 19–31 mag | Testing, correzione bug, consegna finale su GitHub |

**Consegna prevista: 31 maggio 2026**

### 8.1 Gantt semplificato

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title       Piano di progetto RaxeusAI

    section Analisi e setup
    Analisi requisiti e UML   :a1, 2026-04-14, 2d
    Setup venv e Flask        :a2, after a1,   3d

    section Backend core
    Memory e agent loop       :b1, after a2,   4d
    Streaming SSE             :b2, after b1,   2d
    Tool calling base         :b3, after b2,   3d

    section Funzionalità avanzate
    Tool avanzati e RAG       :c1, after b3,   4d
    Web UI — tab e sessioni   :c2, after c1,   3d
    Caricamento immagini      :c3, after c2,   2d
    KaTeX e titolo smart      :c4, after c3,   2d

    section Modulo RaxeusLyric
    Download e trascrizione   :d1, after b3,   5d
    Forced alignment          :d2, after d1,   3d
    Player e UI lyric         :d3, after d2,   3d

    section App desktop
    Bundle macOS (.app)       :e1, after c2,   2d
    Bundle Windows (.exe)     :e2, after e1,   2d
    Nuovi loghi e icone       :e3, after e2,   2d

    section Rifinitura
    Documentazione tecnica    :f1, after e3,   5d
    Testing e bug fix         :f2, after f1,   7d
    Consegna GitHub           :milestone, 2026-05-31, 0d
```
