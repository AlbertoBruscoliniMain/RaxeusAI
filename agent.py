from openai import OpenAI
from memory import Memory
from config import MODEL, OLLAMA_URL, AI_NAME

client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
memory = Memory()


def chat(user_input: str) -> str:
    memory.add("user", user_input)

    response = client.chat.completions.create(
        model=MODEL,
        messages=memory.get(),
    )

    reply = response.choices[0].message.content
    memory.add("assistant", reply)
    return reply


def reset():
    memory.reset()
