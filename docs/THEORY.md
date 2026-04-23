# Teoria — Come funziona un assistente AI

> Concetti teorici dietro il progetto Raxeus.
> Per la documentazione del codice vedi [CODE.md](CODE.md). Per bug e fix vedi [BUGS.md](BUGS.md).

---

## Cos'è un LLM

Un **Large Language Model** (LLM) è un modello statistico addestrato su miliardi di testi. Non "capisce" nel senso umano — predice il token (pezzo di testo) più probabile da generare dato un contesto. Il risultato è testo che appare intelligente e coerente.

Esempi: GPT-4 (OpenAI), Claude (Anthropic), Llama (Meta), Qwen (Alibaba), Gemma (Google).

---

## Perché non puoi crearne uno da zero su un PC

Addestrare un LLM da zero richiede:

- Miliardi di parametri da ottimizzare su miliardi di testi
- Centinaia di GPU (A100, H100) per settimane o mesi
- Dataset enormi — centinaia di GB di testo pulito e curato
- Competenze profonde di machine learning e infrastruttura

È quello che fanno Anthropic, OpenAI, Google, Meta. Non è roba da singola macchina.

**Quello che fai invece:** usi il cervello (LLM) già addestrato da altri, e ci costruisci intorno struttura, memoria e personalità. È esattamente come funziona il 99% delle app AI commerciali.

---

## Fine-tuning — la via di mezzo

"Addestrare" non significa solo creare da zero. Esiste il **fine-tuning**: prendi un modello open-source esistente e lo riaddestri su dati tuoi, cambiandone il comportamento in modo permanente.

Esempio: prendi Llama 3 (Meta, open-source) → lo addestri su 10.000 conversazioni mediche → ottieni un modello che ragiona come un medico specializzato.

| Tecnica | Come funziona | Quando usarla |
|---|---|---|
| **System prompt** | Istruzioni date al modello ad ogni conversazione | Personalità, stile, ruolo |
| **Fine-tuning** | Riaddestramento su dati specifici | Dominio specifico, conoscenze proprietarie |
| **Pre-training da zero** | Addestrare da zero su miliardi di testi | Solo grandi aziende |

Il fine-tuning richiede una buona GPU o servizi cloud (Google Colab, RunPod) — fattibile su hardware consumer, non su CPU sola.

---

## I 4 blocchi di qualsiasi assistente AI

### 1. Il modello (cervello)
L'LLM che genera le risposte. Può essere locale (Ollama) o remoto via API (OpenAI, Groq, Anthropic). Non lo crei tu — lo usi.

### 2. La memoria (contesto)
Una lista di messaggi passati inviata al modello ad ogni turno. Senza di essa il modello dimentica tutto ad ogni risposta — ogni chiamata all'API è stateless di default.

Il modello non "ricorda" davvero: gli stai semplicemente passando tutta la conversazione precedente ad ogni richiesta.

### 3. I tool (mani)
Funzioni reali che il modello può decidere di chiamare — cercare sul web, leggere file, eseguire comandi. Il modello genera una richiesta strutturata (JSON), il tuo codice esegue la funzione, il risultato torna al modello che risponde. Questo è il salto da "chatbot" ad "agente AI".

### 4. Il loop agente
Ciclo continuo: utente parla → AI risponde o chiama un tool → risultato → AI risponde di nuovo. Un agente può fare più passaggi autonomi prima di rispondere all'utente.

---

## Streaming

Per default, un modello genera tutta la risposta e la restituisce in una volta. Con lo **streaming** i token arrivano uno alla volta appena prodotti — come si vede su ChatGPT.

Tecnicamente: l'API apre una connessione HTTP persistente (Server-Sent Events) e manda i chunk man mano. Il client li riceve e li stampa in tempo reale. Il risultato finale è identico, ma l'esperienza percepita è molto più reattiva.

---

## Function calling (tool use)

Il meccanismo con cui un LLM può chiamare funzioni esterne. Il funzionamento:

1. Insieme ai messaggi, mandi al modello una lista di **tool disponibili** (nome, descrizione, parametri in JSON Schema)
2. Il modello decide se rispondere direttamente o chiamare un tool
3. Se chiama un tool, restituisce un oggetto JSON con nome e argomenti invece di testo
4. Il tuo codice esegue la funzione corrispondente
5. Il risultato viene reinserito nella conversazione come messaggio `tool`
6. Il modello riceve il risultato e genera la risposta finale

Questo ciclo può ripetersi più volte (il modello può chiamare più tool in sequenza) prima di rispondere all'utente.

```
Utente → Modello → tool_call → esegui → risultato → Modello → risposta
                       ↑___________________________|  (loop se serve)
```

---

## Sessioni persistenti

Per default la memoria esiste solo durante l'esecuzione del programma — alla chiusura, tutto si perde. Per mantenere le conversazioni tra sessioni diverse si serializza la history in un file JSON.

Al riavvio si può ricaricare la history precedente e continuare da dove si era rimasti. Il system prompt viene sempre reinserito fresco (non salvato) per garantire che la personalità sia sempre aggiornata.

---

## Modelli locali — confronto

Tutti i runner locali funzionano allo stesso modo nel codice (API compatibile OpenAI), ma differiscono per performance e portabilità.

| Tool | Descrizione | Pro | Contro |
|---|---|---|---|
| **Ollama** | Server locale semplicissimo | Cross-platform, facile, buono su Apple Silicon | Meno controllo di llama.cpp |
| **LM Studio** | Ollama con GUI grafica | Interfaccia visiva, server integrato | Solo desktop |
| **llama.cpp** | Engine C++ diretto | Velocissimo, massimo controllo | Setup tecnico |
| **MLX** | Framework Apple per M-series | Il più veloce su Apple Silicon, usa Neural Engine | Solo Apple Silicon — non portabile |
| **GPT4All** | Tutto-in-uno con GUI | Semplicissimo | Modelli meno aggiornati |

### Perché Ollama in questo progetto
- Gira offline, cross-platform
- Nessuna registrazione, nessun costo, nessun limite
- API compatibile OpenAI — cambiare provider richiede 1 riga
- Su M3 usa Metal acceleration automaticamente

---

## Cloud gratuito — quando ha senso

| Provider | Modelli | Limite free |
|---|---|---|
| **Groq** | Llama 3.3 70B, Gemma, Mixtral | 14.400 req/giorno |
| **Google Gemini** | Gemini 2.0 Flash | 1.500 req/giorno |
| **Mistral AI** | Mistral Small, Codestral | Crediti iniziali |
| **Hugging Face** | Qualsiasi modello open-source | Lento ma gratuito |

Utile per: testare modelli grandi (70B+) non scaricabili in locale, sviluppare su macchine senza Ollama, confrontare output tra modelli diversi.

---

## Modelli vision (multimodali)

Un modello **multimodale** accetta input di tipo diverso — testo e immagini — nella stessa chiamata API. Internamente, il modello converte ogni immagine in una sequenza di token visivi tramite un **image encoder** (solitamente un Vision Transformer) e li concatena ai token testuali prima di passarli al transformer linguistico.

### Formato OpenAI multimodale

Quando si inviano immagini, il campo `content` del messaggio non è più una stringa ma un array di blocchi:

```json
{
  "role": "user",
  "content": [
    { "type": "text", "text": "Cosa c'è in questa immagine?" },
    { "type": "image_url", "image_url": { "url": "data:image/jpeg;base64,..." } }
  ]
}
```

L'immagine viene codificata come **data URI base64** — una stringa che include il tipo MIME e i byte dell'immagine codificati in ASCII. Questo evita la necessità di caricare l'immagine su un server separato: viaggia direttamente nel corpo della richiesta JSON.

### Come funziona in RaxeusAI

1. L'utente seleziona fino a 3 immagini nell'UI — `FileReader` le converte in data URI nel browser
2. Il payload POST `/chat` include il campo `images: [dataUri, ...]`
3. `agent.chat_stream()` costruisce il messaggio multimodale e lo invia a `VISION_MODEL` (default: `llava`)
4. La risposta viene streamata normalmente come testo
5. In memoria viene salvata solo la versione testuale (`[N immagini allegate]`) per compatibilità con i turni successivi che usano il modello testo

### Modelli vision disponibili su Ollama

| Modello | RAM ~| Note |
|---|---|---|
| `llava:7b` | ~5GB | buona qualità generale, usato di default |
| `llava:13b` | ~9GB | migliore ma più lento |
| `moondream` | ~2GB | leggerissimo, qualità limitata |
| `minicpm-v` | ~6GB | ottimo per testi nelle immagini |
| `qwen2-vl` | ~5GB | buona qualità, multilingue |

Per cambiare modello vision basta modificare `VISION_MODEL` in `config.py`.

---

## Modelli consigliati per Mac M3 16GB

La RAM unificata di Apple Silicon è condivisa tra CPU e GPU — puoi girare modelli più grandi del previsto.

| Modello | RAM usata | Qualità |
|---|---|---|
| Llama 3.2 3B | ~2GB | buona |
| Qwen2.5 7B 4bit | ~4GB | ottima |
| Gemma 3 9B 4bit | ~6GB | ottima |
| **Qwen3 8B** ← usato qui | ~5GB | ottima |
| Qwen2.5 14B 4bit | ~9GB | eccellente |
| Phi-4 14B 4bit | ~9GB | eccellente |

Con 16GB si arriva comodamente a modelli 14B in 4bit — qualità paragonabile a GPT-3.5.

---

## Il system prompt

Il system prompt è il messaggio iniziale con ruolo `system` inviato al modello prima di qualsiasi input utente. Definisce personalità, stile, limiti e comportamento dell'assistente. Non è "magia" — è testo come qualsiasi altro, ma posizionato prima della conversazione.

Cambiare il system prompt è il modo più rapido per creare un'AI con carattere diverso senza toccare il codice.

---

## Server-Sent Events (SSE)

Meccanismo HTTP per inviare dati dal server al browser in modo continuo su una singola connessione. Il server manda righe nel formato `data: <payload>\n\n` e il browser le riceve man mano che arrivano.

In RaxeusAI viene usato per lo streaming dei token: ogni pezzo di testo generato dal modello viene inviato immediatamente al browser invece di aspettare la risposta completa.

```
Client                         Server
  |--- POST /chat ----------->|
  |<-- data: {"type":"token"} |  (ripetuto per ogni token)
  |<-- data: {"type":"done"}  |
```

A differenza dei WebSocket (bidirezionali), SSE è unidirezionale server→client e non richiede librerie speciali — funziona con `fetch()` nativo leggendo `res.body` come stream.

---

## Architettura web vs terminale vs desktop

RaxeusAI supporta tre modalità sullo stesso backend:

| Modalità | Entry point | Streaming | Sessioni | UI |
|---|---|---|---|---|
| Terminale | `main.py` → `agent.chat()` | stdout diretto | `sessions.py` manuale | shell |
| Web | `app.py` → `agent.chat_stream()` | SSE via HTTP | `sessions.py` + localStorage | browser |
| Desktop | `launcher.py` → `app.py` | SSE via HTTP (localhost) | `sessions.py` + localStorage | finestra nativa WebKit |

Le tre modalità condividono `Memory`, `tools.py` e `sessions.py` — solo il layer di presentazione è diverso. La modalità desktop è tecnicamente identica alla web: `launcher.py` avvia lo stesso `app.py` su una porta libera, e `pywebview` apre quella URL in una finestra WebKit nativa invece di affidarsi al browser di sistema.

---

## App desktop nativa — pywebview

**pywebview** è una libreria Python che apre una finestra nativa del sistema operativo con un motore WebKit embedded, puntata a una URL locale. Il risultato è un'app che appare e si comporta come un'applicazione nativa (dock macOS, icona, cmd+W per chiudere) pur girando su un frontend HTML/CSS/JS identico alla versione web.

### Perché non Electron

Electron (usato da VS Code, Slack, Discord) fa la stessa cosa ma porta con sé Chromium (~150MB) e Node.js. pywebview su macOS usa il WebKit già installato nel sistema (`WKWebView` di macOS) — nessun download aggiuntivo, dimensioni minime.

### Come funziona su macOS

```
launcher.py
    │
    ├─→ threading.Thread(target=flask) ──→ Flask su 127.0.0.1:<porta_libera>
    │         daemon=True
    │
    └─→ webview.create_window(url)
              │
              ▼
        WKWebView (WebKit nativo macOS)
              │
              ▼
        Renderizza l'interfaccia HTML come un browser
              │  (nessuna barra URL, nessun tab, nessun menu browser)
```

Il thread Flask è `daemon=True`: quando l'utente chiude la finestra WebKit, pywebview termina il run loop, Python esce, e il thread daemon viene ucciso automaticamente dal runtime senza bisogno di cleanup esplicito.

### Bundle macOS (.app)

Su macOS un'applicazione è una **directory** con estensione `.app` e una struttura interna precisa:

```
RaxeusAI.app/
├── Contents/
│   ├── Info.plist        ← metadati: nome, icona, bundle ID, versione
│   ├── MacOS/
│   │   └── RaxeusAI      ← eseguibile: script bash che attiva il venv e chiama launcher.py
│   └── Resources/
│       └── AppIcon.icns  ← icona multi-risoluzione (16px → 1024px)
```

`Info.plist` è un XML che macOS legge per sapere come mostrare l'app: icona in Finder/Dock, nome visualizzato, versione. La chiave `NSAllowsLocalNetworking: true` è necessaria perché la WebView carichi URL `127.0.0.1` (App Transport Security di macOS blocca HTTP non-HTTPS per default).

### Icona .icns

Il formato `.icns` è un container che include lo stesso logo a più risoluzioni (16, 32, 64, 128, 256, 512, 1024px e varianti @2x). macOS sceglie automaticamente la risoluzione giusta in base al contesto (Finder, Dock, Spotlight). Lo strumento `iconutil` converte un `.iconset` (cartella di PNG) in `.icns`.

### macOS TCC e posizione del progetto

macOS protegge alcune cartelle utente speciali tramite il sistema **TCC** (Transparency, Consent, and Control). Le app non firmate da un Apple Developer non possono accedere a Desktop, Documenti e Download senza permesso esplicito — qualsiasi processo avviato dal bundle `.app` riceve `[Errno 1] Operation not permitted` su qualsiasi file in quelle cartelle, inclusi script Python, template Flask e dipendenze del venv.

La restrizione si applica all'intero contesto del bundle: bash, Python, `cp` — qualsiasi processo figlio eredita la stessa limitazione TCC.

**Regola:** il progetto RaxeusAI deve trovarsi in una cartella NON protetta:

| Posizione | Protetta TCC | Funziona |
|---|---|---|
| `~/Desktop/RaxeusAI/` | Sì | No |
| `~/Documents/RaxeusAI/` | Sì | No |
| `~/Downloads/RaxeusAI/` | Sì | No |
| `~/RaxeusAI/` | No | Sì |
| `~/Projects/RaxeusAI/` | No | Sì |

Dopo qualsiasi spostamento del progetto è obbligatorio rieseguire `bash create_app.sh` — il bundle contiene path assoluti.

---

## RaxeusLyric — modulo testi musicali sincronizzati

RaxeusLyric è un modulo aggiuntivo integrato in RaxeusAI che genera testi musicali sincronizzati in tempo reale con l'audio. Il flusso combina tre tecnologie distinte: ricerca metadati, recupero testi e trascrizione AI.

### Pipeline completa

```
Query utente ("Imagine - John Lennon")
       │
       ▼
iTunes Search API  →  titolo canonico + artista + copertina album
       │
       ▼
lyrics.ovh API  →  testo ufficiale della canzone (se disponibile)
       │
       ▼
yt-dlp  →  download audio da YouTube (mp3, 192kbps)
       │
       ▼
faster-whisper  →  trascrizione audio con word timestamps
       │
       ▼
Forced alignment  →  ogni riga del testo → timestamp preciso
       │
       ▼
LRC file + playlist JSON  →  cache locale per ricaricamenti istantanei
```

### Whisper e la trascrizione audio

**OpenAI Whisper** è un modello di riconoscimento vocale addestrato su 680.000 ore di audio multilingue. Funziona come un encoder-decoder: l'audio viene convertito in uno spettrogramma mel e passato a un transformer che produce il testo corrispondente.

**faster-whisper** è una reimplementazione ottimizzata di Whisper che usa CTranslate2 (engine C++ per inferenza efficiente) invece di PyTorch. È fino a 4x più veloce con meno memoria RAM, mantenendo la stessa qualità di output.

La trascrizione viene eseguita con `beam_size=5` e `word_timestamps=True` — quest'ultimo parametro è fondamentale perché produce il timestamp di inizio e fine per ogni singola parola, non solo per ogni segmento.

### Forced alignment — sincronizzazione precisa

Quando il testo ufficiale è disponibile, il problema è: "a quale secondo esatto corrisponde ogni riga del testo?". Whisper trascrive l'audio in autonomia ma può sbagliare parole, saltare ritornelli ripetuti, o mescolare sezioni.

Il modulo usa un algoritmo di **semi-global alignment** per allineare le parole del testo ufficiale con le parole trascritte da Whisper (che portano i timestamp):

1. **Normalizzazione**: ogni parola viene ridotta a caratteri alfanumerici in minuscolo
2. **Scoring**: coppie di parole ricevono un punteggio (EXACT_MATCH=2.6, STRONG_MATCH=1.8, WEAK_MATCH=1.05, MISMATCH=-1.8)
3. **Programmazione dinamica**: costruisce una matrice n×m per trovare il percorso di allineamento ottimale con penalty per gap (GAP_LYRIC=-1.15, GAP_WHISPER=-0.45)
4. **Traceback**: risale la matrice per recuperare le coppie di parole allineate
5. **Interpolazione**: le righe senza match diretto ricevono timestamp interpolati linearmente tra i match vicini

Il risultato è monotono: ogni riga ha un timestamp maggiore della precedente, anche nei ritornelli ripetuti.

### yt-dlp e il download audio

**yt-dlp** è un fork attivamente mantenuto di youtube-dl. Cerca su YouTube il brano più rilevante per la query data, scarica solo la traccia audio (non il video) nel formato migliore disponibile, e la converte in mp3 via FFmpeg. La ricerca usa `ytsearch1:` per prendere il primo risultato.

Il file viene scaricato in `temp_audio/`, poi spostato definitivamente in `lyrics_output/audio/` una volta completata la trascrizione.

### Cache e persistenza

Ogni canzone elaborata viene salvata in tre file:
- **`.lrc`** — formato standard per testi sincronizzati, con timestamp `[mm:ss.xx]` per ogni riga
- **`audio/*.mp3`** — file audio per la riproduzione
- **`covers/*.jpg/png`** — copertina album scaricata da iTunes o YouTube

La **playlist** (`lyrics_output/playlist.json`) funge da indice: mappa ogni titolo al path dei suoi file. Al prossimo accesso alla stessa canzone, la pipeline salta tutto e serve direttamente i dati dalla cache.

---

## RAG — Retrieval Augmented Generation

RAG è la tecnica con cui un agente AI risponde su documenti specifici **senza fine-tuning**. Invece di riaddestrare il modello, i documenti vengono cercati al momento della domanda e passati come contesto nella risposta.

### Come funziona in RaxeusAI

```
Domanda utente
      │
      ▼
rag_search(query)  →  ChromaDB cerca i chunk più simili via embedding
      │
      ▼
Chunk rilevanti  →  aggiunti al contesto della chiamata API
      │
      ▼
Modello risponde basandosi sui tuoi documenti reali
```

### Pipeline completa

1. **Indicizzazione** (eseguita una volta, poi aggiornata): `rag_index.py` legge i file, li divide in chunk da 600 caratteri con overlap di 60, li vettorizza con `all-MiniLM-L6-v2` (modello ONNX locale ~80MB) e li salva in `rag_db/` (ChromaDB persistente su disco).

2. **Retrieval** (ad ogni domanda): il tool `rag_search` converte la query dell'utente nello stesso spazio vettoriale e cerca i 4 chunk più vicini per similarità coseno.

3. **Augmentation**: i chunk trovati tornano al modello come risultato del tool call — il modello li legge e risponde come se avesse "letto" il documento.

### Embedding e similarità vettoriale

Un embedding è una rappresentazione numerica del significato di un testo: una lista di ~384 numeri (per `all-MiniLM-L6-v2`) che posiziona il testo in uno spazio dove testi simili sono vicini. La ricerca trova i chunk più vicini alla query misurando la **similarità coseno** tra i vettori.

Questo è diverso dalla ricerca full-text (grep): trova concetti simili anche se le parole esatte non compaiono.

### ChromaDB

Database vettoriale embedded in Python — gira nel processo, nessun server separato. Salva su disco in `rag_db/` tramite `PersistentClient`. Supporta `upsert` per aggiornare documenti già indicizzati senza duplicati.

### Deduplication e chunk overlap

L'overlap (60 caratteri) evita di perdere contesto ai bordi dei chunk: se una frase importante cade tra due chunk, almeno uno dei due la conterrà intera. L'ID univoco `abs_path::indice` garantisce che rieseguire `rag_index.py` sullo stesso file aggiorni i chunk esistenti invece di duplicarli.

---

## Cosa puoi costruire con questa base

| Progetto | Cosa aggiungere |
|---|---|
| Assistente vocale | TTS (text-to-speech) + STT (speech-to-text) |
| Bot Telegram | python-telegram-bot + stesso agent.py |
| UI grafica | Streamlit (rapido) o React (completo) |
| Tutor personalizzato | system prompt specifico + fine-tuning |
| RAG (risponde su documenti tuoi) | **già implementato** — usa `rag_index.py` per indicizzare |
| App desktop nativa macOS | **già implementato** — `launcher.py` + `create_app.sh`; progetto in `~/RaxeusAI/` |
