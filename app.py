import json
import uuid
from flask import Flask, request, Response, render_template, jsonify
from memory import Memory
from agent import chat_stream
from sessions import save_session, list_sessions, load_session

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
    session_id = data.get("session_id", str(uuid.uuid4()))
    if not message:
        return jsonify({"error": "messaggio vuoto"}), 400

    mem = _get_memory(session_id)

    def generate():
        yield f"data: {json.dumps({'type': 'session_id', 'value': session_id})}\n\n"
        for event in chat_stream(message, mem):
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
    import os
    from pathlib import Path
    path = Path(__file__).parent / "sessions" / f"session_{session_id}.json"
    if path.exists():
        os.remove(path)
    _sessions.pop(session_id, None)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
