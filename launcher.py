import os
import sys
import socket
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


if __name__ == "__main__":
    port = _find_free_port()
    url = f"http://127.0.0.1:{port}"

    t = threading.Thread(target=_start_flask, args=(port,), daemon=True)
    t.start()

    if not _wait_for_flask(url):
        sys.exit(1)

    webview.create_window(
        "RaxeusAI", url, width=1280, height=820,
        min_size=(800, 600), text_select=True,
    )
    webview.start()
