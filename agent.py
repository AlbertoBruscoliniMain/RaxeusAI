import json
from openai import OpenAI
from memory import Memory
from config import MODEL, VISION_MODEL, OLLAMA_URL
from tools import TOOL_SCHEMAS, execute_tool

client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
memory = Memory()


def chat(user_input: str) -> str:
    memory.add("user", user_input)

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

            for tc in tool_calls_list:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}

                result = execute_tool(name, args)
                memory.add_tool_result(tc["id"], name, result)
        else:
            memory.add("assistant", full_content)
            return full_content


def reset():
    memory.reset()


def chat_stream(user_input: str, mem: Memory, images: list | None = None):
    """Generator per la web UI: yielda eventi SSE invece di stampare su stdout."""

    if images:
        content = [{"type": "text", "text": user_input or "Descrivi queste immagini."}]
        for img_b64 in images:
            content.append({"type": "image_url", "image_url": {"url": img_b64}})

        vision_messages = mem.get() + [{"role": "user", "content": content}]
        stream = client.chat.completions.create(
            model=VISION_MODEL,
            messages=vision_messages,
            stream=True,
        )

        full_content = ""
        for chunk in stream:
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
            for tc in tool_calls_list:
                name = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except json.JSONDecodeError:
                    args = {}
                result = execute_tool(name, args)
                mem.add_tool_result(tc["id"], name, result)
        else:
            mem.add("assistant", full_content)
            yield {"type": "done"}
            return
