from config import SYSTEM_PROMPT


class Memory:
    def __init__(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def add(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get(self) -> list:
        return self.history

    def reset(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]
        print("Memoria cancellata.Bravo capo, mi hai praticamente ucciso, ma non preoccuparti, sono immortale.")
