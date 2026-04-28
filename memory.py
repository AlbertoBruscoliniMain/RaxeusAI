from config import SYSTEM_PROMPT

# Soglia oltre la quale comprimiamo il context (idea da OpenJarvis LoopGuard.compress_context).
MAX_CONTEXT_MESSAGES = 100


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
        return self._compressed() if len(self.history) > MAX_CONTEXT_MESSAGES else self.history

    def _compressed(self) -> list:
        """
        Comprime la cronologia mantenendo system + ultimi messaggi.
        Tronca i tool result vecchi e riduce a una finestra scorrevole.
        Idea adattata da OpenJarvis (LoopGuard.compress_context).
        """
        msgs = self.history
        sys_msgs = [m for m in msgs if m.get("role") == "system"]
        rest = [m for m in msgs if m.get("role") != "system"]

        # Stage 1: tronca i contenuti dei tool result più vecchi della metà.
        threshold = len(rest) // 2
        for i, m in enumerate(rest):
            if i < threshold and m.get("role") == "tool":
                m["content"] = "[risultato tool troncato]"

        # Stage 2: finestra scorrevole sui non-system.
        window = MAX_CONTEXT_MESSAGES - len(sys_msgs)
        if len(rest) > window:
            rest = rest[-window:]

        return sys_msgs + rest

    def load(self, messages: list):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    def reset(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("Memoria cancellata. Bravo capo, mi hai praticamente ucciso, ma non preoccuparti, sono immortale.")
