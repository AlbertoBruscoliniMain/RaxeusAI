import json
import concurrent.futures
import threading
import queue as _queue
import urllib.request
from openai import OpenAI
from memory import Memory
from config import MODEL, VISION_MODEL, VISION_FALLBACKS, OLLAMA_URL
from tools import TOOL_SCHEMAS, execute_tool
from loop_guard import LoopGuard

client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
memory = Memory()
_guard = LoopGuard()

_resolved_vision_model: str | None = None


def _list_ollama_models() -> list[str]:
    base = OLLAMA_URL.rstrip("/").removesuffix("/v1")
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=3) as r:
            data = json.loads(r.read())
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:
        return []


def _resolve_vision_model() -> str:
    """Restituisce il primo modello vision disponibile in Ollama, partendo
    dal VISION_MODEL preferito e cadendo sui fallback. Cached dopo la prima
    chiamata. Se nessuno è installato, restituisce comunque VISION_MODEL
    (l'errore arriverà al primo uso, ma con messaggio chiaro)."""
    global _resolved_vision_model
    if _resolved_vision_model is not None:
        return _resolved_vision_model
    installed = set(_list_ollama_models())
    if not installed:
        _resolved_vision_model = VISION_MODEL
        return _resolved_vision_model
    candidates = (VISION_MODEL,) + tuple(VISION_FALLBACKS)
    base_names = {n.split(":")[0]: n for n in installed}
    for cand in candidates:
        if cand in installed:
            _resolved_vision_model = cand
            return cand
        base = cand.split(":")[0]
        if base in base_names:
            _resolved_vision_model = base_names[base]
            return _resolved_vision_model
    _resolved_vision_model = VISION_MODEL
    return _resolved_vision_model


def _exec_one(tc: dict) -> tuple[dict, str]:
    """Esegue una singola tool call, applicando il LoopGuard."""
    name = tc["function"]["name"]
    args_raw = tc["function"]["arguments"] or "{}"
    verdict = _guard.check_call(name, args_raw)
    if verdict.blocked:
        return tc, f"[Loop guard] {verdict.reason}"
    try:
        args = json.loads(args_raw)
    except json.JSONDecodeError:
        args = {}
    return tc, execute_tool(name, args)


def _exec_parallel(tool_calls_list: list[dict]) -> list[tuple[dict, str]]:
    """
    Esegue più tool call in parallelo (idea da OpenJarvis OrchestratorAgent).
    Mantiene l'ordine originale.
    """
    if len(tool_calls_list) <= 1:
        return [_exec_one(tc) for tc in tool_calls_list]
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(tool_calls_list)) as pool:
        futures = [pool.submit(_exec_one, tc) for tc in tool_calls_list]
        return [f.result() for f in futures]


def chat(user_input: str) -> str:
    memory.add("user", user_input)
    _guard.reset()

    while True:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=memory.get(),
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            stream=True,
        )

        full_content = ""
        tool_calls_acc = {}

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                full_content += delta.content
                print(delta.content, end="", flush=True)

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    i = tc.index
                    if i not in tool_calls_acc:
                        tool_calls_acc[i] = {"id": "", "name": "", "arguments": ""}
                    if tc.id:
                        tool_calls_acc[i]["id"] = tc.id
                    if tc.function and tc.function.name:
                        tool_calls_acc[i]["name"] = tc.function.name
                    if tc.function and tc.function.arguments:
                        tool_calls_acc[i]["arguments"] += tc.function.arguments

        if tool_calls_acc:
            tool_calls_list = [
                {
                    "id": tool_calls_acc[i]["id"],
                    "type": "function",
                    "function": {
                        "name": tool_calls_acc[i]["name"],
                        "arguments": tool_calls_acc[i]["arguments"],
                    },
                }
                for i in sorted(tool_calls_acc)
            ]

            memory.add_assistant_tool_calls(full_content, tool_calls_list)

            for tc, result in _exec_parallel(tool_calls_list):
                memory.add_tool_result(tc["id"], tc["function"]["name"], result)
        else:
            memory.add("assistant", full_content)
            return full_content


def generate_title(first_message: str) -> str:
    """Genera un titolo breve (max 4 parole) per una chat dato il primo messaggio."""
    import re
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{
                "role": "user",
                "content": (
                    f"Genera un titolo di massimo 4 parole in italiano che riassuma l'argomento "
                    f"di questa richiesta: «{first_message[:300]}». "
                    "Rispondi SOLO con il titolo, niente altro."
                ),
            }],
            stream=False,
        )
        title = resp.choices[0].message.content.strip()
        title = re.sub(r"<think>.*?</think>", "", title, flags=re.DOTALL).strip()
        title = title.strip('"').strip("'").strip()
        return title[:40] if title else first_message[:30]
    except Exception:
        return first_message[:30]


def reset():
    memory.reset()
    _guard.reset()


def chat_stream(user_input: str, mem: Memory, images: list | None = None):
    """Generator per la web UI: yielda eventi SSE invece di stampare su stdout."""
    guard = LoopGuard()

    if images:
        yield {"type": "thinking"}

        content = [{"type": "text", "text": user_input or "Descrivi queste immagini."}]
        for img_b64 in images:
            content.append({"type": "image_url", "image_url": {"url": img_b64}})

        vision_system = (
            "Sei un assistente di analisi visiva. Osserva attentamente le immagini "
            "fornite e rispondi in italiano basandoti SOLO su ciò che vedi davvero. "
            "Se l'immagine contiene testo, leggilo letteralmente prima di interpretare. "
            "Non inventare dettagli non presenti. Non assumere personalità o tono: "
            "rispondi in modo diretto, fattuale e concreto."
        )
        # Il modello vision non accetta tool_calls nello storico: prendiamo solo
        # i messaggi con contenuto testuale puro per dargli un minimo di contesto.
        recent = []
        for m in mem.get():
            if m.get("role") not in ("user", "assistant"):
                continue
            text = m.get("content", "")
            if isinstance(text, str) and text.strip():
                recent.append({"role": m["role"], "content": text})
        recent = recent[-6:]

        vision_messages = (
            [{"role": "system", "content": vision_system}]
            + recent
            + [{"role": "user", "content": content}]
        )

        # Il primo caricamento del modello vision in Ollama può richiedere decine
        # di secondi: eseguiamo la chiamata in un thread e yieldiamo eventi
        # `thinking` ogni 10s per tenere viva la connessione SSE (WKWebView
        # chiude le richieste senza dati dopo ~60s).
        vision_model = _resolve_vision_model()
        q = _queue.Queue()
        def _vision_worker():
            try:
                stream = client.chat.completions.create(
                    model=vision_model,
                    messages=vision_messages,
                    stream=True,
                )
                for chunk in stream:
                    q.put(("chunk", chunk))
                q.put(("done", None))
            except Exception as e:
                q.put(("error", e))
        threading.Thread(target=_vision_worker, daemon=True).start()

        full_content = ""
        while True:
            try:
                kind, value = q.get(timeout=10)
            except _queue.Empty:
                yield {"type": "thinking"}
                continue
            if kind == "error":
                err_str = str(value)
                if "not found" in err_str.lower() or "404" in err_str:
                    msg = (
                        f"❌ Nessun modello vision disponibile in Ollama.\n\n"
                        f"Installane uno con uno di questi comandi:\n"
                        f"```\nollama pull {VISION_MODEL}\nollama pull llava\nollama pull moondream\n```"
                    )
                else:
                    msg = f"❌ Errore con il modello vision ({vision_model}): {err_str}"
                yield {"type": "token", "content": msg}
                full_content = msg
                break
            if kind == "done":
                break
            chunk = value
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                full_content += delta.content
                yield {"type": "token", "content": delta.content}

        n = len(images)
        img_note = f"[{n} {'immagine allegata' if n == 1 else 'immagini allegate'}]"
        mem.add("user", f"{img_note}\n{user_input}" if user_input else img_note)
        mem.add("assistant", full_content)
        yield {"type": "done"}
        return

    mem.add("user", user_input)

    while True:
        stream = client.chat.completions.create(
            model=MODEL,
            messages=mem.get(),
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            stream=True,
        )

        full_content = ""
        tool_calls_acc = {}

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                full_content += delta.content
                yield {"type": "token", "content": delta.content}

            if delta.tool_calls:
                yield {"type": "thinking"}
                for tc in delta.tool_calls:
                    i = tc.index
                    if i not in tool_calls_acc:
                        tool_calls_acc[i] = {"id": "", "name": "", "arguments": ""}
                    if tc.id:
                        tool_calls_acc[i]["id"] = tc.id
                    if tc.function and tc.function.name:
                        tool_calls_acc[i]["name"] = tc.function.name
                    if tc.function and tc.function.arguments:
                        tool_calls_acc[i]["arguments"] += tc.function.arguments

        if tool_calls_acc:
            tool_calls_list = [
                {
                    "id": tool_calls_acc[i]["id"],
                    "type": "function",
                    "function": {
                        "name": tool_calls_acc[i]["name"],
                        "arguments": tool_calls_acc[i]["arguments"],
                    },
                }
                for i in sorted(tool_calls_acc)
            ]
            mem.add_assistant_tool_calls(full_content, tool_calls_list)

            results = []
            if len(tool_calls_list) <= 1:
                results = [_exec_with_guard(tc, guard) for tc in tool_calls_list]
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=len(tool_calls_list)) as pool:
                    futures = [pool.submit(_exec_with_guard, tc, guard) for tc in tool_calls_list]
                    results = [f.result() for f in futures]

            for tc, result in results:
                mem.add_tool_result(tc["id"], tc["function"]["name"], result)
        else:
            mem.add("assistant", full_content)
            yield {"type": "done"}
            return


def _exec_with_guard(tc: dict, guard: LoopGuard) -> tuple[dict, str]:
    name = tc["function"]["name"]
    args_raw = tc["function"]["arguments"] or "{}"
    verdict = guard.check_call(name, args_raw)
    if verdict.blocked:
        return tc, f"[Loop guard] {verdict.reason}"
    try:
        args = json.loads(args_raw)
    except json.JSONDecodeError:
        args = {}
    return tc, execute_tool(name, args)
