from config import SYSTEM_PROMPT


class Memory:
    def __init__(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def add_assistant_tool_calls(self, content: str, tool_calls: list):
        self.history.append({
            "role": "assistant",
            "content": content or "",
            "tool_calls": tool_calls,
        })

    def add_tool_result(self, tool_call_id: str, tool_name: str, result: str):
        self.history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": result,
        })

    def get(self) -> list:
        return self.history

    def load(self, messages: list):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    def reset(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("Memoria cancellata. Bravo capo, mi hai praticamente ucciso, ma non preoccuparti, sono immortale.")
