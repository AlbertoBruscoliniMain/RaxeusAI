import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import logging

logging.getLogger("werkzeug").setLevel(logging.ERROR)

_HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(_HERE)
sys.path.insert(0, _HERE)

import webview
from app import app as flask_app

OLLAMA_HOST = "127.0.0.1"
OLLAMA_PORT = 11434
WINDOW_STATE_FILE = os.path.join(_HERE, "sessions", "_window_state.json")


# ── OLLAMA AUTO-START ────────────────────────────────────────────────────────

def _ollama_is_up(timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((OLLAMA_HOST, OLLAMA_PORT), timeout=timeout):
            return True
    except OSError:
        return False


def _find_ollama_binary() -> str | None:
    found = shutil.which("ollama")
    if found:
        return found
    candidates = [
        "/usr/local/bin/ollama",
        "/opt/homebrew/bin/ollama",
        "/Applications/Ollama.app/Contents/Resources/ollama",
        "/Applications/Ollama.app/Contents/MacOS/Ollama",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def _start_ollama() -> bool:
    """Avvia `ollama serve` in background. True se il server risponde entro 20s."""
    binary = _find_ollama_binary()
    if not binary:
        return False
    try:
        subprocess.Popen(
            [binary, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        return False
    for _ in range(80):
        if _ollama_is_up():
            return True
        time.sleep(0.25)
    return False


def _show_error(message: str) -> None:
    """Dialog nativo macOS via osascript."""
    try:
        subprocess.run([
            "osascript", "-e",
            f'display dialog "{message}" with title "RaxeusAI" with icon stop buttons {{"OK"}}',
        ], check=False)
    except Exception:
        sys.stderr.write(message + "\n")


def _ensure_ollama() -> bool:
    if _ollama_is_up():
        return True
    if _start_ollama():
        return True
    _show_error(
        "Impossibile contattare Ollama su 127.0.0.1:11434.\\n\\n"
        "Installa Ollama da https://ollama.com e riavvia l'app."
    )
    return False


# ── FLASK ────────────────────────────────────────────────────────────────────

def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _start_flask(port):
    flask_app.run(host="127.0.0.1", port=port, debug=False,
                  threaded=True, use_reloader=False)


def _wait_for_flask(url, retries=40, delay=0.15):
    for _ in range(retries):
        try:
            urllib.request.urlopen(url, timeout=1)
            return True
        except Exception:
            time.sleep(delay)
    return False


# ── WINDOW STATE ─────────────────────────────────────────────────────────────

def _load_window_state() -> dict:
    try:
        with open(WINDOW_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "width": int(data.get("width", 1280)),
            "height": int(data.get("height", 820)),
            "x": data.get("x"),
            "y": data.get("y"),
        }
    except Exception:
        return {"width": 1280, "height": 820, "x": None, "y": None}


def _save_window_state(window) -> None:
    try:
        os.makedirs(os.path.dirname(WINDOW_STATE_FILE), exist_ok=True)
        state = {
            "width": getattr(window, "width", 1280),
            "height": getattr(window, "height", 820),
            "x": getattr(window, "x", None),
            "y": getattr(window, "y", None),
        }
        with open(WINDOW_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


# ── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not _ensure_ollama():
        sys.exit(1)

    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"

    t = threading.Thread(target=_start_flask, args=(port,), daemon=True)
    t.start()

    if not _wait_for_flask(url):
        _show_error("Il server interno non si è avviato. Riprova.")
        sys.exit(1)

    state = _load_window_state()
    window_kwargs = dict(
        title="RaxeusAI",
        url=url,
        width=state["width"],
        height=state["height"],
        min_size=(800, 600),
        text_select=True,
    )
    if state["x"] is not None and state["y"] is not None:
        window_kwargs["x"] = state["x"]
        window_kwargs["y"] = state["y"]

    window = webview.create_window(**window_kwargs)
    window.events.closing += lambda: _save_window_state(window)

    from webview.menu import Menu, MenuAction, MenuSeparator

    def _ui_new_chat():
        window.evaluate_js("if (typeof newChat==='function') newChat();")

    def _ui_open_lyric():
        window.load_url(url + "/lyric")

    def _ui_open_chat():
        window.load_url(url + "/")

    def _ui_about():
        window.evaluate_js(
            "document.getElementById('btn-info')?.click();"
        )

    def _ui_help():
        window.evaluate_js(
            "document.getElementById('btn-agent-help')?.click();"
        )

    menu_items = [
        Menu("File", [
            MenuAction("Nuova chat", _ui_new_chat),
            MenuSeparator(),
            MenuAction("Apri Chat", _ui_open_chat),
            MenuAction("Apri RaxeusLyric", _ui_open_lyric),
        ]),
        Menu("Info", [
            MenuAction("Cosa so fare?", _ui_help),
            MenuAction("About RaxeusAI", _ui_about),
        ]),
    ]

    webview.start(menu=menu_items)
