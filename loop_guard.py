"""
LoopGuard — rileva e blocca loop degenerativi nel tool calling dell'agente.

Idea adattata da OpenJarvis (src/openjarvis/agents/loop_guard.py).
Versione Python pura, semplificata: niente Rust backend.

Cosa rileva:
1. Stessa chiamata identica ripetuta troppe volte (hash SHA-256 di name+args).
2. Pattern ping-pong A-B-A-B nelle chiamate consecutive.
3. Budget per singolo tool (es. uno cerca su Google all'infinito).
"""
from __future__ import annotations

import hashlib
from collections import deque
from dataclasses import dataclass


@dataclass
class LoopGuardConfig:
    enabled: bool = True
    max_identical_calls: int = 3
    ping_pong_window: int = 6
    per_tool_budget: int = 8


@dataclass
class LoopVerdict:
    blocked: bool = False
    reason: str = ""


class LoopGuard:
    def __init__(self, config: LoopGuardConfig | None = None):
        self.cfg = config or LoopGuardConfig()
        self._counts: dict[str, int] = {}
        self._sequence: deque[str] = deque(maxlen=self.cfg.ping_pong_window * 2)
        self._per_tool: dict[str, int] = {}

    def check_call(self, name: str, arguments: str) -> LoopVerdict:
        if not self.cfg.enabled:
            return LoopVerdict()

        h = hashlib.sha256(f"{name}:{arguments}".encode()).hexdigest()[:16]
        self._counts[h] = self._counts.get(h, 0) + 1
        if self._counts[h] > self.cfg.max_identical_calls:
            return LoopVerdict(
                blocked=True,
                reason=(
                    f"Chiamata identica a '{name}' ripetuta "
                    f"{self._counts[h]} volte (limite {self.cfg.max_identical_calls})."
                ),
            )

        self._per_tool[name] = self._per_tool.get(name, 0) + 1
        if self._per_tool[name] > self.cfg.per_tool_budget:
            return LoopVerdict(
                blocked=True,
                reason=f"Tool '{name}' ha superato il budget ({self.cfg.per_tool_budget}).",
            )

        self._sequence.append(name)
        if len(self._sequence) >= self.cfg.ping_pong_window and self._is_ping_pong():
            return LoopVerdict(
                blocked=True,
                reason="Pattern di chiamate ripetitivo (ping-pong) rilevato.",
            )

        return LoopVerdict()

    def reset(self) -> None:
        self._counts.clear()
        self._sequence.clear()
        self._per_tool.clear()

    def _is_ping_pong(self) -> bool:
        seq = list(self._sequence)
        n = len(seq)
        for period in (2, 3):
            if n >= period * 2:
                tail = seq[-period * 2:]
                pat = tail[:period]
                if all(tail[i] == pat[i % period] for i in range(len(tail))):
                    return True
        return False
