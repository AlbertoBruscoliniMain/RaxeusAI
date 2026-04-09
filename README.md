# RaxeusAI

Assistente AI personale costruito in Python, gira localmente sul Mac tramite Ollama. Ha memoria conversazionale, personalità definita, tool reali che può usare autonomamente e un'interfaccia web.

---

## Avvio

**Terminale:**
```bash
ollama serve
source venv/bin/activate
python main.py
```

**Web UI (browser):**
```bash
ollama serve
source venv/bin/activate
python app.py
# apri http://localhost:5000
```

---

## Cosa fa

- Risponde in streaming token per token
- Usa tool in autonomia senza chiederti il permesso: cerca su Google, legge file, esegue Python, legge PDF, cerca su Wikipedia, elenca directory, aggiunge testo a file
- Ricorda tutta la conversazione (memoria multi-turno)
- Salva e ricarica le sessioni passate
- Interfaccia web con tab multiple, ricerca nelle chat, colore bolla personalizzabile

---

## Struttura

```
RaxeusAI/
├── config.py           → modello, URL Ollama, personalità (system prompt)
├── memory.py           → cronologia conversazione
├── agent.py            → loop agente: streaming, tool calling, chat_stream per la web UI
├── tools.py            → tool disponibili (web, file, PDF, Wikipedia, Python, ora)
├── sessions.py         → salvataggio/caricamento sessioni JSON
├── main.py             → interfaccia terminale
├── app.py              → server Flask per la web UI
├── templates/
│   └── index.html      → markup dell'interfaccia web
├── static/
│   ├── style.css       → tema scuro
│   └── app.js          → logica tab, streaming SSE, color picker
└── requirements.txt
```

---

## Comandi terminale

| Comando | Effetto |
|---|---|
| `reset` | Cancella la memoria della sessione corrente |
| `salva` | Salva la conversazione su file |
| `sessioni` | Lista le sessioni salvate |
| `carica <N>` | Carica la sessione numero N |
| `esci` | Chiude il programma |

---

## Documentazione

| File | Contenuto |
|---|---|
| [docs/CODE.md](docs/CODE.md) | Documentazione tecnica di ogni file |
| [docs/THEORY.md](docs/THEORY.md) | Concetti teorici: LLM, streaming, SSE, tool calling |
| [docs/WEB-UI.md](docs/WEB-UI.md) | Come funziona l'interfaccia web |
| [docs/BUGS.md](docs/BUGS.md) | Bug noti e fix applicati |
| [docs/SUPERPOWERS.md](docs/SUPERPOWERS.md) | Cos'è la cartella `.superpowers/` |
