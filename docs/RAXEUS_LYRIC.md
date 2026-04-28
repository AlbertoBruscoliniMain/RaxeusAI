# RaxeusLyric — Documentazione tecnica

> Modulo integrato in RaxeusAI per testi musicali sincronizzati in tempo reale.
> Per i concetti generali del progetto vedi [THEORY.md](THEORY.md). Per la documentazione degli altri file vedi [CODE.md](CODE.md).

---

## Cos'è RaxeusLyric

RaxeusLyric è un sottomodulo di RaxeusAI accessibile all'URL `/lyric`. Permette di cercare una canzone, scaricarla da YouTube, ottenere il testo ufficiale e mostrarlo sincronizzato con l'audio — come un karaoke in tempo reale nel browser.

Non è un'app separata: condivide lo stesso server Flask (`app.py`), lo stesso venv e lo stesso processo di `launcher.py`. Il bottone **RaxeusLyric** nella topbar della chat naviga alla stessa origin, senza aprire tab esterne.

---

## Come si accede

| Percorso | Cosa mostra |
|---|---|
| `/` | Chat AI principale |
| `/lyric` | RaxeusLyric — ricerca e karaoke |

Il bottone nella topbar della chat è iniettato da un IIFE in `app.js`:

```javascript
// static/app.js — fondo del file
(function () {
  const btn = document.createElement('a');
  btn.href = '/lyric';
  btn.textContent = 'RaxeusLyric';
  // stile inline — hover via mouseenter/mouseleave
  const colorWrap = document.getElementById('color-dot-wrap');
  colorWrap.parentNode.insertBefore(btn, colorWrap);
})();
```

La navigazione è `href` diretto (stessa finestra pywebview) — nessun `target="_blank"`, perché aprire nuove finestre pywebview richiederebbe configurazione extra.

---

## Pipeline completa

Quando l'utente cerca una canzone, il browser apre un `EventSource` su `/lyric/api/process?query=...` e riceve eventi SSE man mano che ogni step si completa:

```
Query: "Imagine - John Lennon"
       │
       ▼
[1] iTunes Search API
       │  titolo canonico, artista, URL copertina album
       ▼
[2] lyrics.ovh API
       │  testo ufficiale (se disponibile)
       ▼
[3] yt-dlp
       │  download audio mp3 da YouTube → temp_audio/
       ▼
[4] faster-whisper
       │  trascrizione con word_timestamps=True
       ▼
[5] Forced alignment (se testo disponibile)
       │  ogni riga del testo → timestamp preciso
       ▼
[6] Salvataggio
       │  .lrc + audio/*.mp3 + covers/*.jpg + playlist.json
       ▼
[done] Segmenti + audio → browser → karaoke in tempo reale
```

---

## File coinvolti

### lyric_song_finder.py

Identifica il titolo canonico della canzone tramite **iTunes Search API** (pubblica, senza chiave).

```python
def find_song(query: str) -> dict | None
# ritorna {"title": str, "artist": str, "artwork_url": str} o None
```

```python
# Esempio di chiamata interna
url = "https://itunes.apple.com/search?term=Imagine+John+Lennon&entity=song&limit=1"
# risposta: {"results": [{"trackName": "Imagine", "artistName": "John Lennon",
#             "artworkUrl100": "https://...100x100bb.jpg"}]}

# La copertina viene upgradrata da 100x100 a 512x512:
artwork_url = data["artworkUrl100"].replace("100x100bb", "512x512bb")
```

Timeout 7s, usa solo `urllib` della stdlib — nessuna dipendenza aggiuntiva.

---

### lyric_fetcher.py

Recupera il testo ufficiale della canzone da **lyrics.ovh** (API REST gratuita, senza chiave).

```python
def fetch_lyrics(artist: str, title: str) -> str | None
```

Prova più combinazioni nell'ordine:

```python
# 1. (artista, titolo)  →  GET https://api.lyrics.ovh/v1/{artist}/{title}
# 2. (artista_breve, titolo)  →  artista troncato al primo "feat." o "&"
# 3. (titolo, artista)  →  inversione per query tipo "Imagine - John Lennon"
```

**`clean_title(title)`** — rimuove suffissi YouTube prima della ricerca:

```python
# Rimuove: (Official Video), [Lyrics], (Remaster 2021), (feat. ...), ecc.
# via regex: r'\s*[\(\[].*?[\)\]]'  +  blacklist di pattern comuni
```

**Post-processing del testo restituito:**
- Rimozione dei marcatori di sezione: `[Verse 1]`, `[Chorus]`, `[Bridge]`, ecc.
- Stripping di righe vuote eccessive

---

### lyric_downloader.py

Scarica l'audio da YouTube usando **yt-dlp**.

```python
def download_audio(query: str) -> tuple[str, dict]
# ritorna (file_path, {"artist": str, "title": str, "thumbnail": str})
```

```python
ffmpeg_location = "/opt/homebrew/bin"   # path esplicito — il processo non eredita il PATH di Homebrew

ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "mp3",
        "preferredquality": "192",
    }],
    "ffmpeg_location": ffmpeg_location,
    "default_search": "ytsearch1",     # prende il primo risultato YouTube
    "quiet": True,
    "no_warnings": True,
}
```

**Perché `ffmpeg_location` esplicito:** `yt-dlp` chiama FFmpeg tramite subprocess. Se Python è avviato da un bundle `.app` o da un launcher senza PATH completo, FFmpeg in `/opt/homebrew/bin` non viene trovato. Passare il path della directory che contiene `ffmpeg` e `ffprobe` risolve il problema senza modificare PATH a livello di sistema.

**Logistica del file:** l'audio viene scaricato in `temp_audio/` con nome uguale al titolo YouTube (`%(title)s.mp3`). Dopo la trascrizione, `app.py` lo sposta definitivamente in `lyrics_output/audio/` con nome normalizzato (`safe_title(display_title).mp3`).

---

### lyric_transcriber.py

Trascrive l'audio e sincronizza i testi con i timestamp. È il modulo algoritmicamente più complesso.

```python
def get_transcription(file_path: str, hint_lyrics: str = None) -> list[dict]
# ritorna [{"start": float, "end": float, "text": str}, ...]
```

#### Trascrizione Whisper

```python
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe(
    file_path,
    beam_size=5,
    word_timestamps=True,   # fondamentale: timestamp per ogni singola parola
    language="it",          # auto-detect se None
)
```

`faster-whisper` usa CTranslate2 (engine C++ ottimizzato) invece di PyTorch — 4x più veloce, meno RAM. Il modello `small` è ~500MB e gira su CPU senza GPU.

`word_timestamps=True` è il parametro critico: invece di dare un timestamp per segmento, restituisce il timestamp di ogni parola — questi vengono poi usati dall'algoritmo di forced alignment per posizionare ogni riga del testo al secondo giusto.

#### Forced alignment

Quando `hint_lyrics` è disponibile (testo da lyrics.ovh), non si usa la trascrizione Whisper direttamente perché:
- Whisper può trascrivere male alcune parole
- I ritornelli ripetuti possono essere saltati o duplicati
- Il testo ufficiale è più accurato del riconoscimento vocale

Il modulo allinea le parole del **testo ufficiale** con le parole trascritte da **Whisper** (che hanno i timestamp), tramite programmazione dinamica:

```python
def _semi_global_align(lyric_words: list, whisper_words: list) -> list[tuple]:
    """
    Matrice score n×m:
    - EXACT_MATCH   = +2.6   (parole identiche dopo normalizzazione)
    - STRONG_MATCH  = +1.8   (similarità SequenceMatcher >= 0.9)
    - WEAK_MATCH    = +1.05  (similarità >= 0.8)
    - MISMATCH      = -1.8
    - GAP_LYRIC     = -1.15  (parola del testo senza corrispondenza Whisper)
    - GAP_WHISPER   = -0.45  (parola Whisper extra — Whisper aggiunge rumori/filler)
    """
    n, m = len(lyric_words), len(whisper_words)
    score = [[0.0] * (m + 1) for _ in range(n + 1)]
    # ... fill matrix ...
    # traceback → lista di (lyric_idx, whisper_idx) allineati
```

**Interpolazione lineare:** le righe del testo senza match diretto Whisper (es. ritornelli non trascritti chiaramente) ricevono un timestamp interpolato linearmente tra il match precedente e il successivo — garantisce monotonia dei timestamp.

---

### lyric_formatter.py

Gestisce il formato LRC, la playlist JSON e la cache locale.

```python
def save_as_lrc(segments: list, song_title: str) -> str
def update_playlist(title, lrc_path, audio, cover) -> None
def check_cache(query: str) -> list | None
def check_cache_with_entry(query: str) -> tuple[list | None, dict | None]
def get_playlist_entry(query: str) -> dict | None
def load_from_lrc(lrc_path: str) -> list
def safe_title(s: str) -> str
```

**Formato LRC** generato da `save_as_lrc`:

```lrc
[ti:Imagine -- John Lennon]
[by:AutoLyric AI]
[00:00.00]Imagine there's no heaven
[00:07.20]It's easy if you try
[00:14.55]No hell below us
...
```

**`safe_title(s)`:** normalizza una stringa per usarla come nome file — rimuove caratteri non sicuri, sostituisce spazi con underscore, limita la lunghezza.

**`check_cache_with_entry(query)`:** cerca nella playlist il titolo corrispondente alla query (matching fuzzy via `_title_matches`), carica il `.lrc` e restituisce `(segments, entry)`. Se la cache è presente, l'intera pipeline (download + trascrizione) viene saltata.

**`_title_matches(stored, query)`:** considera match sia `"Imagine"` che `"Imagine -- John Lennon"` per la query `"imagine john lennon"` — normalizza entrambi a minuscolo senza punteggiatura prima di confrontare.

---

## Integrazione con app.py

Tutti i moduli lyric vengono orchestrati da `app.py`. Non sanno niente dell'uno dell'altro — `app.py` è il controller che li coordina.

### Route principali

```python
# app.py

@app.route("/lyric")
def lyric_page():
    return render_template("lyric.html")


@app.route("/lyric/api/process")
def lyric_process():
    query = request.args.get("query", "").strip()

    def generate():
        # 1. Cache check
        cached, entry = check_cache_with_entry(query)
        if cached:
            yield _lyric_ev("done", segments=cached, cached=True,
                            audio=entry.get("audio"), display_title=entry["title"])
            return

        # 2. iTunes → titolo canonico
        yield _lyric_ev("progress", message="Ricerca canzone...")
        song_info = find_song(query)
        display_title = f"{song_info['title']} -- {song_info['artist']}"
        yield _lyric_ev("song_info", display_title=display_title)

        # 3. lyrics.ovh → testo ufficiale
        yield _lyric_ev("progress", message="Ricerca testo online...")
        lyrics = fetch_lyrics(artist, title)
        if lyrics:
            yield _lyric_ev("lyrics_found", lines=lyrics.splitlines())

        # 4. yt-dlp → download audio
        yield _lyric_ev("progress", message="Download audio...")
        audio_path, dl_meta = download_audio(search_q)

        # 5. Whisper + forced alignment → segmenti
        yield _lyric_ev("progress", message="Analisi timing audio...")
        segments = get_transcription(audio_path, hint_lyrics=lyrics)

        # 6. Salvataggio definitivo
        audio_filename = f"{safe_title(display_title)}.mp3"
        os.replace(audio_path, os.path.join(_LYRIC_AUDIO, audio_filename))
        lrc_path = save_as_lrc(segments, display_title)
        cover_filename = _download_cover(cover_url, display_title)
        update_playlist(display_title, lrc_path, audio_filename, cover_filename)

        yield _lyric_ev("done", segments=segments, audio=audio_filename,
                        cover=cover_filename, display_title=display_title)

    return Response(stream_with_context(generate()),
                    mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

### Tabella completa degli endpoint

| Metodo | Path | Descrizione |
|---|---|---|
| `GET` | `/lyric` | Serve `templates/lyric.html` |
| `GET` | `/lyric/api/process?query=` | Pipeline completa in SSE |
| `GET` | `/lyric/api/playlist` | Restituisce playlist JSON con copertine validate |
| `GET` | `/lyric/api/load?title=` | Carica canzone dalla cache (segmenti + audio filename) |
| `POST` | `/lyric/api/delete` | Elimina canzone: rimuove LRC + mp3 + copertina, aggiorna playlist |
| `GET` | `/lyric/api/audio/<filename>` | Serve mp3 con `conditional=True` (supporto Range per seek) |
| `GET` | `/lyric/api/cover/<filename>` | Serve copertina con mimetype auto-rilevato |

### Helper interni di app.py

**`_download_cover(url, display_title) -> str | None`**  
Scarica la copertina dall'URL (iTunes o YouTube thumbnail), la salva in `lyrics_output/covers/` con nome `safe_title(display_title).<ext>`. Prima di salvare, elimina eventuali versioni precedenti con estensione diversa (deduplicazione per stem). Ritorna il filename relativo o `None` se il download fallisce.

**`_ensure_cover(entry) -> bool`**  
Chiamata da `/lyric/api/playlist` su ogni voce della libreria. Verifica che il file copertina esista su disco; se manca (file eliminato manualmente, o non scaricato originariamente), lo ri-scarica da iTunes. Ritorna `True` se ha modificato l'entry (così `app.py` sa che deve riscrivere `playlist.json`).

**`_split_display_title(dt) -> tuple[str, str]`**  
Separa `"Titolo -- Artista"` in `("Titolo", "Artista")`. Fallback su `" - "` (singolo trattino). Usato per passare titolo e artista separati alle API di ricerca.

**`_lyric_ev(type_, **kwargs) -> str`**  
Formatta un evento SSE:
```python
def _lyric_ev(type_, **kwargs):
    kwargs["type"] = type_
    return f"data: {json.dumps(kwargs)}\n\n"
```

---

## Frontend: lyric.html

La pagina è completamente autonoma — nessun file JavaScript esterno. Tutta la logica è in un `<script>` inline.

### Layout

```
┌─────────────────────────────────────────────────┐
│ Header: [logo] | [barra ricerca] [Genera] [Chat]│
├──────────────┬──────────────────────────────────┤
│   Sidebar    │         Area testi               │
│  (libreria)  │   [nome canzone] [status pill]   │
│              │                                  │
│  ♪ Canzone 1 │   Imagine there's no heaven      │
│  ♪ Canzone 2 │   It's easy if you try           │
│              │ ► No hell below us   ← attiva    │
│              │   Above us only sky              │
├──────────────┴──────────────────────────────────┤
│ Player: [▶] [titolo]   0:14 / 3:07  [━━●────]  │
└─────────────────────────────────────────────────┘
```

### Flusso JavaScript — ricerca

```javascript
function doSearch() {
    const q = searchInput.value.trim();
    // Apre EventSource (SSE) — connessione HTTP persistente
    const es = new EventSource(`/lyric/api/process?query=${encodeURIComponent(q)}`);

    es.onmessage = e => {
        const d = JSON.parse(e.data);
        if (d.type === 'progress')     setStatus(d.message, 'spin');
        if (d.type === 'song_info')    songName.textContent = d.display_title;
        if (d.type === 'lyrics_found') renderLyricsPreview(d.lines);   // preview senza timestamp
        if (d.type === 'error')        { setStatus(d.message, 'err'); es.close(); }
        if (d.type === 'done')         {
            es.close();
            loadSong(d.display_title, d.segments, d.audio, d.cached);
            refreshPlaylist();
        }
    };
}
```

### Sincronizzazione testi — `syncLyrics`

```javascript
// Chiamata ad ogni evento "timeupdate" dell'elemento <audio>
function syncLyrics(currentTime) {
    let active = -1;
    // Ricerca lineare dal fondo: il segmento attivo è l'ultimo con start <= currentTime
    for (let i = segments.length - 1; i >= 0; i--) {
        if (segments[i].start <= currentTime) { active = i; break; }
    }
    if (active === lastActiveIdx) return;   // nessun cambio, skip DOM update
    lastActiveIdx = active;

    document.querySelectorAll('.lyric-line').forEach((el, i) => {
        el.classList.remove('active', 'past');
        if (i < active)       el.classList.add('past');
        else if (i === active) el.classList.add('active');
    });

    // Auto-scroll verso la riga attiva (inibito per 2.5s se l'utente ha scrollato)
    if (active >= 0 && !userScrolling) {
        document.getElementById(`l${active}`)
                .scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}
```

### Seek (click sulla barra di avanzamento)

```javascript
function seek(e) {
    if (!audioEl.duration) return;
    const r = progressTrack.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width));
    audioEl.currentTime = pct * audioEl.duration;
}
// supporta sia click singolo che drag (mousedown + mousemove)
```

---

## Struttura dei file generati a runtime

```
RaxeusAI/
├── temp_audio/                     ← download temporaneo (svuotato dopo ogni elaborazione)
│   └── <YouTube title>.mp3
│
└── lyrics_output/
    ├── playlist.json               ← indice completo della libreria
    ├── <safe_title>.lrc            ← testi sincronizzati in formato LRC standard
    ├── audio/
    │   └── <safe_title>.mp3        ← audio definitivo (spostato da temp_audio/)
    └── covers/
        └── <safe_title>.jpg/.png   ← copertina album (da iTunes o thumbnail YouTube)
```

**`playlist.json` — struttura di ogni entry:**

```json
{
  "title": "Imagine -- John Lennon",
  "lrc": "Imagine___John_Lennon.lrc",
  "audio": "Imagine___John_Lennon.mp3",
  "cover": "Imagine___John_Lennon.jpg",
  "added": "2026-04-28"
}
```

---

## Dipendenze

| Pacchetto | Versione | Scopo |
|---|---|---|
| `yt-dlp` | ≥2026.3 | Download audio da YouTube |
| `faster-whisper` | ≥1.2 | Trascrizione audio con word timestamps |
| `ctranslate2` | ≥4.7 | Engine C++ per inferenza Whisper ottimizzata |
| `onnxruntime` | ≥1.24 | VAD (Voice Activity Detection) richiesto da faster-whisper |
| `huggingface-hub` | ≥0.20 | Download automatico pesi modello Whisper al primo avvio |
| `av` | ≥17.0 | Lettura file audio (binding PyAV/FFmpeg) |
| `numpy` | ≥1.24 | Array numerici per processing audio |

**ffmpeg esterno:** richiesto da `yt-dlp` per la conversione mp3. Su macOS si installa con `brew install ffmpeg`. Il path `/opt/homebrew/bin` è hardcoded in `lyric_downloader.py`.

---

## Avvio

RaxeusLyric non ha un entry point separato — è integrato in `app.py`:

```bash
ollama serve
source venv/bin/activate
python app.py
# chat:         http://localhost:5000
# RaxeusLyric:  http://localhost:5000/lyric
```

Oppure tramite l'app desktop (`launcher.py` / `RaxeusAI.app`) — in quel caso entrambe le pagine sono accessibili dalla stessa finestra pywebview.
