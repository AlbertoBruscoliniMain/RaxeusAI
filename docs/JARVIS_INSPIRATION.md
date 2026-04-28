# Cosa è stato preso da OpenJarvis

Riferimento: [open-jarvis/OpenJarvis](https://github.com/open-jarvis/OpenJarvis) — licenza Apache 2.0.

OpenJarvis è un framework completo per AI personale locale (Stanford Scaling Intelligence Lab). RaxeusAI è un progetto molto più piccolo e non lo integra direttamente: ne prende **solo le idee** che migliorano l'agente senza alterarne lo stack (Ollama + Flask + Python). Tutto il codice è stato riscritto in italiano e adattato alla nostra architettura.

Le idee qui elencate non implicano dipendenza dal pacchetto `openjarvis`: il suo codice non viene importato, viene solo studiato come riferimento di design.

---

## Idee adottate

### 1. LoopGuard — protezione anti-loop sull'agente
- **File RaxeusAI:** [loop_guard.py](../loop_guard.py)
- **File OpenJarvis:** `src/openjarvis/agents/loop_guard.py`
- **Cosa fa:** rileva e blocca tre pattern degenerati nel tool calling:
  1. **Chiamate identiche ripetute** (hash SHA-256 di `name + arguments`).
  2. **Pattern ping-pong** A-B-A-B o A-B-C-A-B-C nelle chiamate consecutive.
  3. **Budget per singolo tool** (es. l'agente cerca su Google all'infinito).
- **Differenze rispetto a OpenJarvis:** versione Python pura, senza il backend Rust opzionale e senza il sistema di "warn-before-block". Niente eventi su un EventBus.
- **Integrato in:** [agent.py](../agent.py) — sia in `chat()` (CLI) che in `chat_stream()` (web), il guard è creato per ogni conversazione e resettato a ogni `reset()`.

### 2. Esecuzione parallela dei tool call
- **File RaxeusAI:** [agent.py](../agent.py) — `_exec_parallel`
- **File OpenJarvis:** `src/openjarvis/agents/orchestrator.py` — `_run_function_calling` (sezione `parallel_tools`)
- **Cosa fa:** quando il modello emette più tool call nello stesso turno, le esegue in parallelo con `concurrent.futures.ThreadPoolExecutor`, mantenendo l'ordine originale dei risultati. Su una richiesta che combina `google_search` + `wikipedia_search` + `read_file`, la latenza scende dal "somma dei tempi" al "max dei tempi".

### 3. Compressione del context (sliding window)
- **File RaxeusAI:** [memory.py](../memory.py) — `Memory._compressed`
- **File OpenJarvis:** `src/openjarvis/agents/loop_guard.py` — `LoopGuard.compress_context`
- **Cosa fa:** quando la cronologia supera `MAX_CONTEXT_MESSAGES` (default 100), tronca i `tool result` più vecchi della metà a `[risultato tool troncato]` e applica una finestra scorrevole sul resto. Il messaggio `system` (personalità di Raxeus) viene sempre preservato.
- **Differenze rispetto a OpenJarvis:** OpenJarvis ha 4 stage di compressione progressiva, qui ne usiamo 2 (sufficienti per chat di consumer use). Niente drop di tool call/result pair dal centro.

### 4. Hardware detection + raccomandazione modello
- **File RaxeusAI:** [hardware.py](../hardware.py)
- **File OpenJarvis:** `src/openjarvis/core/config.py` — `detect_hardware`, `recommend_model`, `_MODEL_TIERS`
- **Cosa fa:** rileva piattaforma, CPU, RAM, GPU (NVIDIA via `nvidia-smi`, Apple via `system_profiler`) e suggerisce il modello Qwen3 più adatto in base alla memoria disponibile. La logica è cross-platform: su Windows usa `ctypes.windll.kernel32.GlobalMemoryStatusEx` per la RAM.
- **Differenze:** OpenJarvis ha tier basati su Qwen3.5 MoE e supporta vLLM/MLX/llama.cpp. Qui abbiamo solo Ollama + Qwen3 dense (1.7B/4B/8B/14B/32B).

### 5. Comando `doctor`
- **File RaxeusAI:** [doctor.py](../doctor.py) + comando `doctor` in [main.py](../main.py)
- **File OpenJarvis:** `src/openjarvis/cli/doctor_cmd.py`
- **Cosa fa:** diagnostica al volo del sistema:
  - Versione Python (>= 3.10)
  - Hardware rilevato e modello suggerito
  - Raggiungibilità di Ollama
  - Presenza dei modelli in `config.MODEL` e `config.VISION_MODEL`
  - Presenza delle dipendenze Python
- **Output stile checklist** (`✓` / `!` / `✗`), come in OpenJarvis.

---

## Idee NON adottate (e perché)

| Componente OpenJarvis | Motivo dell'esclusione |
|---|---|
| **Skills system** (`hermes:*`, `openclaw:*`) | Aggiunge un livello di indirezione enorme. RaxeusAI ha già i tool nativi che bastano. |
| **NativeReActAgent** (Thought/Action/Observation) | Cambierebbe lo stile delle risposte di Raxeus, e l'utente ha richiesto che la personalità non venga toccata. Il function-calling nativo di Qwen3 è già abbastanza buono. |
| **Engine multipli** (vLLM, SGLang, MLX, llama.cpp, LM Studio, Exo, Nexa) | Stiamo intenzionalmente solo su Ollama: zero dipendenze pesanti, zero Rust, install in due righe. |
| **Backend Rust** (`_rust_bridge`, `LoopGuard` in Rust) | Il volume di chiamate non lo giustifica. |
| **EventBus + telemetry** | Per una chat consumer la complessità non è ripagata. |
| **Connectors** (Gmail, GCal, GDrive, Linear, Slack, ecc.) | Fuori scope. |
| **`jarvis init` interattivo con preset** | Sostituito dal comando `hardware` + `doctor`. |
| **Learning loop / SFT/GRPO** | Roba da ricerca, fuori scope per un assistente personale. |

---

## Licenza e attribuzione

OpenJarvis è rilasciato sotto **Apache License 2.0** ([LICENSE](https://github.com/open-jarvis/OpenJarvis/blob/main/LICENSE)). RaxeusAI non redistribuisce codice di OpenJarvis: ne riprende solo idee architetturali. Questo file serve come attribuzione esplicita delle fonti di ispirazione.
