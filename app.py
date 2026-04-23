import json
import uuid
import os
import glob
import mimetypes
import urllib.parse
import urllib.request
from flask import Flask, request, Response, render_template, jsonify, send_file, stream_with_context
from memory import Memory
from agent import chat_stream
from sessions import save_session, list_sessions, load_session
from lyric_downloader import download_audio
from lyric_transcriber import get_transcription
from lyric_formatter import save_as_lrc, update_playlist, check_cache_with_entry, get_playlist_entry, safe_title
from lyric_fetcher import fetch_lyrics
from lyric_song_finder import find_song

app = Flask(__name__)

# session_id -> Memory attiva
_sessions: dict[str, Memory] = {}


def _get_memory(session_id: str) -> Memory:
    if session_id not in _sessions:
        mem = Memory()
        saved = list_sessions()
        if session_id in saved:
            messages = load_session(session_id)
            mem.load(messages)
        _sessions[session_id] = mem
    return _sessions[session_id]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    images = data.get("images") or []
    session_id = data.get("session_id", str(uuid.uuid4()))

    if not message and not images:
        return jsonify({"error": "messaggio vuoto"}), 400

    mem = _get_memory(session_id)

    def generate():
        yield f"data: {json.dumps({'type': 'session_id', 'value': session_id})}\n\n"
        for event in chat_stream(message, mem, images=images or None):
            yield f"data: {json.dumps(event)}\n\n"
        save_session(mem.get())

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@app.route("/sessions")
def get_sessions():
    return jsonify(list_sessions()[:5])


@app.route("/session/<session_id>", methods=["DELETE"])
def delete_session(session_id: str):
    path = os.path.join(os.path.dirname(__file__), "sessions", f"session_{session_id}.json")
    if os.path.exists(path):
        os.remove(path)
    _sessions.pop(session_id, None)
    return jsonify({"ok": True})


# ── LYRIC MODULE ─────────────────────────────────────────────────────────────

_LYRIC_BASE   = os.path.dirname(__file__)
_LYRIC_OUT    = os.path.join(_LYRIC_BASE, "lyrics_output")
_LYRIC_AUDIO  = os.path.join(_LYRIC_OUT, "audio")
_LYRIC_COVERS = os.path.join(_LYRIC_OUT, "covers")


def _lyric_ev(type_, **kwargs):
    kwargs["type"] = type_
    return f"data: {json.dumps(kwargs)}\n\n"


def _split_display_title(dt: str) -> tuple:
    if " -- " in dt:
        t, a = dt.split(" -- ", 1)
        return t.strip(), a.strip()
    if " - " in dt:
        t, a = dt.split(" - ", 1)
        return t.strip(), a.strip()
    return dt.strip(), ""


def _load_lyric_playlist() -> list:
    path = os.path.join(_LYRIC_OUT, "playlist.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_lyric_playlist(pl: list) -> None:
    os.makedirs(_LYRIC_OUT, exist_ok=True)
    path = os.path.join(_LYRIC_OUT, "playlist.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(pl, f, ensure_ascii=False, indent=2)


def _guess_cover_ext(url: str, content_type: str) -> str:
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";", 1)[0].strip())
        if ext == ".jpe":
            ext = ".jpg"
        if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            return ext
    path = urllib.parse.urlparse(url).path
    ext = os.path.splitext(path)[1].lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        return ext
    return ".jpg"


def _download_cover(url: str, display_title: str) -> str | None:
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RaxeusLyric/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            ct = r.headers.get("Content-Type", "")
    except Exception:
        return None
    if not data:
        return None
    os.makedirs(_LYRIC_COVERS, exist_ok=True)
    stem = safe_title(display_title)
    ext = _guess_cover_ext(url, ct)
    filename = f"{stem}{ext}"
    dest = os.path.join(_LYRIC_COVERS, filename)
    for old in glob.glob(os.path.join(_LYRIC_COVERS, f"{stem}.*")):
        if old != dest and os.path.isfile(old):
            os.remove(old)
    with open(dest, "wb") as f:
        f.write(data)
    return filename


def _ensure_cover(entry: dict) -> bool:
    changed = False
    cover = entry.get("cover")
    if cover and os.path.exists(os.path.join(_LYRIC_COVERS, cover)):
        return False
    if entry.get("no_cover"):
        return False
    if cover:
        entry.pop("cover", None)
        changed = True
    title, artist = _split_display_title(entry.get("title", ""))
    lookup = f"{title} {artist}".strip() or entry.get("title", "")
    info = find_song(lookup)
    cover_url = (info or {}).get("artwork_url", "")
    if not cover_url:
        entry["no_cover"] = True
        return True
    fn = _download_cover(cover_url, entry.get("title", lookup))
    if fn:
        entry["cover"] = fn
    else:
        entry["no_cover"] = True
    return True


@app.route("/lyric")
def lyric_page():
    return render_template("lyric.html")


@app.route("/lyric/api/process")
def lyric_process():
    query = request.args.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query vuota"}), 400

    def generate():
        cached, entry = check_cache_with_entry(query)
        if cached:
            yield _lyric_ev("done",
                            segments=cached, cached=True,
                            audio=entry.get("audio") if entry else None,
                            cover=entry.get("cover") if entry else None,
                            display_title=entry.get("title", query) if entry else query)
            return

        yield _lyric_ev("progress", message="Ricerca canzone...")
        song_info = find_song(query)
        if song_info and song_info.get("title"):
            title = song_info["title"]
            artist = song_info["artist"]
            display_title = f"{title} -- {artist}" if artist else title
        else:
            parts = [p.strip() for p in query.split(" - ", 1)]
            title = parts[0]
            artist = parts[1] if len(parts) > 1 else ""
            display_title = query

        yield _lyric_ev("song_info", display_title=display_title)

        yield _lyric_ev("progress", message="Ricerca testo online...")
        lyrics = fetch_lyrics(artist, title)
        lyrics_lines = None
        if lyrics:
            lyrics_lines = [l.strip() for l in lyrics.splitlines() if l.strip()]
            yield _lyric_ev("lyrics_found", lines=lyrics_lines)
        else:
            yield _lyric_ev("progress", message="Testo non trovato, userò trascrizione AI...")

        yield _lyric_ev("progress", message="Download audio...")
        search_q = f"{title} {artist}".strip() if (title and artist) else query
        try:
            audio_path, dl_meta = download_audio(search_q)
        except Exception as e:
            yield _lyric_ev("error", message=f"Errore download: {e}")
            return

        yield _lyric_ev("progress", message="Analisi timing audio...")
        try:
            segments = get_transcription(audio_path, hint_lyrics=lyrics)
        except Exception as e:
            if os.path.exists(audio_path):
                os.remove(audio_path)
            yield _lyric_ev("error", message=f"Errore analisi: {e}")
            return

        os.makedirs(_LYRIC_AUDIO, exist_ok=True)
        audio_filename = f"{safe_title(display_title)}.mp3"
        os.replace(audio_path, os.path.join(_LYRIC_AUDIO, audio_filename))
        lrc_path = save_as_lrc(segments, display_title)
        cover_url = (song_info or {}).get("artwork_url") or dl_meta.get("thumbnail")
        cover_filename = _download_cover(cover_url, display_title)
        update_playlist(display_title, lrc_path, audio_filename, cover_filename)

        yield _lyric_ev("done",
                        segments=segments, cached=False,
                        audio=audio_filename, cover=cover_filename,
                        display_title=display_title)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/lyric/api/playlist")
def lyric_playlist():
    pl = _load_lyric_playlist()
    updated = False
    for entry in pl:
        if _ensure_cover(entry):
            updated = True
    if updated:
        _save_lyric_playlist(pl)
    return jsonify(pl)


@app.route("/lyric/api/load")
def lyric_load():
    title = request.args.get("title", "").strip()
    segments = check_cache(title)
    if not segments:
        return jsonify({"error": "Non trovato"}), 404
    entry = get_playlist_entry(title)
    return jsonify({"segments": segments, "audio": entry.get("audio") if entry else None})


@app.route("/lyric/api/delete", methods=["POST"])
def lyric_delete():
    title = request.json.get("title", "").strip()
    if not title:
        return jsonify({"error": "Titolo mancante"}), 400
    playlist_path = os.path.join(_LYRIC_OUT, "playlist.json")
    if not os.path.exists(playlist_path):
        return jsonify({"error": "Playlist non trovata"}), 404
    with open(playlist_path, "r", encoding="utf-8") as f:
        pl = json.load(f)
    entry = next((e for e in pl if e["title"] == title), None)
    if not entry:
        return jsonify({"error": "Canzone non trovata"}), 404
    for path in [
        os.path.join(_LYRIC_OUT, entry["lrc"]),
        os.path.join(_LYRIC_AUDIO, entry["audio"]) if entry.get("audio") else None,
        os.path.join(_LYRIC_COVERS, entry["cover"]) if entry.get("cover") else None,
    ]:
        if path and os.path.exists(path):
            os.remove(path)
    with open(playlist_path, "w", encoding="utf-8") as f:
        json.dump([e for e in pl if e["title"] != title], f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})


@app.route("/lyric/api/audio/<path:filename>")
def lyric_audio(filename):
    path = os.path.join(_LYRIC_AUDIO, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File non trovato"}), 404
    return send_file(path, mimetype="audio/mpeg", conditional=True)


@app.route("/lyric/api/cover/<path:filename>")
def lyric_cover(filename):
    path = os.path.join(_LYRIC_COVERS, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File non trovato"}), 404
    mt = mimetypes.guess_type(path)[0] or "image/jpeg"
    return send_file(path, mimetype=mt, conditional=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
