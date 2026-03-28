import json
from openai import OpenAI
from memory import Memory
from config import MODEL, OLLAMA_URL
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
