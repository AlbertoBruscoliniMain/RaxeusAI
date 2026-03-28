# Codice — Documentazione tecnica

> Documentazione di ogni file del progetto Raxeus.
> Per i concetti teorici vedi [THEORY.md](THEORY.md).

---

## Struttura del progetto

```
AI personale/
├── config.py        → configurazione centralizzata (modello, URL, personalità)
├── memory.py        → gestione cronologia conversazione
├── agent.py         → logica di comunicazione con Ollama
├── main.py          → loop principale, interfaccia terminale
├── requirements.txt → dipendenze Python
└── venv/            → ambiente virtuale (prompt: "Raxeus")
```

---

## config.py

Punto centrale di configurazione. Tutto ciò che può essere cambiato senza toccare la logica sta qui.

```python
MODEL = "qwen3:8b"
OLLAMA_URL = "http://localhost:11434/v1"
AI_NAME = "Raxeus"
SYSTEM_PROMPT = f"""..."""
```

| Variabile | Tipo | Descrizione |
|---|---|---|
| `MODEL` | `str` | Nome del modello Ollama da usare |
| `OLLAMA_URL` | `str` | Endpoint del server Ollama locale |
| `AI_NAME` | `str` | Nome dell'assistente, usato nel prompt e nell'UI |
| `SYSTEM_PROMPT` | `str` | Personalità e istruzioni comportamentali dell'AI |

**Modifiche applicate:**
- `AI_NAME` cambiato da `"Jarvis"` a `"Raxeus"`
- `SYSTEM_PROMPT` riscritto completamente per dare personalità ribelle, arrogante e con humor cinico
- Aggiunta regola: niente divagazioni nelle risposte tecniche, nomina utente al massimo una volta
- Aggiunta regola: libero arbitrio quando si parla di sé o dell'utente
- Aggiunta regola: uso naturale di parolacce italiane

---

## memory.py

Gestisce la cronologia della conversazione. Il modello è stateless — ad ogni chiamata gli passiamo tutta la history.

```python
class Memory:
    def __init__(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def add(self, role: str, content: str): ...
    def get(self) -> list: ...
    def reset(self): ...
```

| Metodo | Parametri | Descrizione |
|---|---|---|
| `__init__` | — | Inizializza la history con il system prompt |
| `add` | `role: str`, `content: str` | Aggiunge un messaggio (`user` o `assistant`) |
| `get` | — | Restituisce tutta la history da passare all'API |
| `reset` | — | Svuota la history, reinserisce solo il system prompt |

**Modifiche applicate:**
- Messaggio del metodo `reset` personalizzato: `"Memoria cancellata. Bravo capo, mi hai praticamente ucciso, ma non preoccuparti, sono immortale."`

---

## agent.py

Comunica con Ollama usando il client OpenAI (compatibile). Espone due funzioni pubbliche usate da `main.py`.

```python
client = OpenAI(base_url=OLLAMA_URL, api_key="ollama")
memory = Memory()

def chat(user_input: str) -> str: ...
def reset(): ...
```

| Funzione | Parametri | Ritorno | Descrizione |
|---|---|---|---|
| `chat` | `user_input: str` | `str` | Aggiunge il messaggio utente, chiama il modello, salva e ritorna la risposta |
| `reset` | — | — | Delega il reset alla memoria |

**Flusso di `chat`:**
1. Aggiunge `user_input` alla memory con ruolo `user`
2. Chiama `client.chat.completions.create` passando tutta la history
3. Estrae il testo dalla risposta
4. Salva la risposta in memory con ruolo `assistant`
5. Ritorna il testo

**Note:** `api_key="ollama"` è un placeholder — Ollama non richiede autenticazione ma il client OpenAI vuole una stringa non vuota.

---

## main.py

Loop principale interattivo. Legge input da terminale, chiama `agent.chat`, stampa la risposta.

```python
while True:
    user = input("Tu: ").strip()

    if not user: continue
    if user.lower() == "esci": ...
    if user.lower() == "reset": ...

    reply = chat(user)
    print(f"{AI_NAME}: {reply}\n")
```

| Comando | Effetto |
|---|---|
| `esci` | Stampa messaggio di uscita e termina il programma |
| `reset` | Chiama `agent.reset()`, cancella la memoria |
| qualsiasi altro testo | Inviato all'AI, risposta stampata |

**Modifiche applicate:**
- Messaggio di uscita personalizzato: `"Ci si becca capo"`

---

## requirements.txt

```
openai
```

Una sola dipendenza. Il client `openai` viene usato per comunicare con Ollama tramite la sua API compatibile OpenAI — non richiede account OpenAI.

---

## venv

Ambiente virtuale Python creato con `python3 -m venv venv`.

Il prompt del venv è stato rinominato da `(venv)` a `(Raxeus)` modificando direttamente `venv/bin/activate`:

```bash
# venv/bin/activate
VIRTUAL_ENV_PROMPT=Raxeus   # ← era "venv"
PS1="(Raxeus) ${PS1:-}"     # ← era "(venv)"
```

**Attivazione:**
```bash
source venv/bin/activate
```

**Dipendenze installate:**
- `openai` 2.30.0 + dipendenze transitive (httpx, pydantic, anyio, ecc.)

---

## Come avviare il progetto

```bash
# 1. Avvia Ollama (se non già in esecuzione)
ollama serve

# 2. Dalla cartella del progetto
source venv/bin/activate
python main.py
```
