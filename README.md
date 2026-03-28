# Raxeus — AI Personale

Documentazione del progetto e guida completa su come funziona un assistente AI, cosa è stato fatto e perché.

---

## Cos'è questo progetto

Un assistente AI personale costruito in Python che gira localmente sul tuo Mac, con memoria conversazionale, personalità definita e connessione a un modello linguistico via Ollama.

**Cosa fa:**
- Ricorda la conversazione (memoria multi-turno)
- Ha una personalità definita tramite system prompt
- Risponde in italiano con uno stile personalizzato
- Gira completamente offline sul tuo Mac

---

## Struttura del progetto

```
AI personale/
├── config.py        → nome AI, modello usato, system prompt (personalità)
├── memory.py        → gestisce la cronologia della conversazione
├── agent.py         → logica di comunicazione con il modello
├── main.py          → loop principale, interfaccia terminale
├── requirements.txt → dipendenze Python
└── venv/            → ambiente virtuale Python (chiamato "Raxeus")
```

---

## Come avviarlo

**1. Avvia Ollama** (il server che esegue il modello):
```bash
ollama serve
```

**2. Attiva il venv e avvia l'AI:**
```bash
cd "AI personale"
source venv/bin/activate
python main.py
```

**Comandi durante la chat:**
- `reset` — cancella la memoria della conversazione
- `esci` — chiude il programma

---

## Ollama e le alternative — quale scegliere

Quando costruisci un assistente AI hai bisogno di qualcosa che "pensi" — un modello linguistico. Ecco le opzioni principali:

---

### Modelli locali (offline, gratuiti per sempre)

Girano sul tuo PC, nessun dato esce dalla macchina, nessun costo.

| Tool | Descrizione | Pro | Contro |
|---|---|---|---|
| **Ollama** | Server locale semplicissimo, API compatibile OpenAI | Facilissimo, cross-platform, ottimo su Apple Silicon | Meno controllo rispetto a llama.cpp |
| **LM Studio** | Come Ollama ma con interfaccia grafica | GUI intuitiva, server API integrato | Solo desktop |
| **llama.cpp** | Engine C++ diretto, massima efficienza | Velocissimo, controllo totale | Setup più tecnico |
| **GPT4All** | Tutto-in-uno con GUI | Semplicissimo da avviare | Modelli meno aggiornati |
| **Jan** | GUI moderna + API locale | Interfaccia pulita | Ancora giovane come progetto |
| **MLX** | Framework Apple ottimizzato per M-series | Il più veloce su Mac M1/M2/M3/M4, usa Neural Engine | **Solo Apple Silicon** — non gira su altre macchine |

> **Nota su MLX:** Se il codice deve girare solo su Mac Apple Silicon è la scelta migliore in assoluto per performance. Ma non è portabile — su Windows, Linux o Intel Mac non parte.

---

### Cloud gratuito (con limiti mensili)

Nessun modello da scaricare, basta una chiave API. Ideali per sviluppare e testare.

| Provider | Modelli disponibili | Limite free |
|---|---|---|
| **Groq** | Llama 3.3 70B, Gemma, Mixtral | 14.400 req/giorno |
| **Google Gemini** | Gemini 2.0 Flash | 1.500 req/giorno |
| **Mistral AI** | Mistral Small, Codestral | Crediti iniziali |
| **Together AI** | Llama, Qwen e altri | $1 di crediti gratuiti |
| **Hugging Face** | Qualsiasi modello open-source | Lento ma gratuito |

> **Groq** è il migliore per sviluppare: gratuito, velocissimo (streaming reale), modelli di alto livello come Llama 3.3 70B.

---

### Come si usano nel codice

Tutti questi provider espongono un'API compatibile con lo standard OpenAI. Cambi solo l'URL — il codice Python resta identico:

```python
from openai import OpenAI

# Ollama (locale)
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

# Groq (cloud gratuito)
client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key="TUA_KEY")

# LM Studio (locale)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lmstudio")
```

---

### Perché in questo progetto si usa Ollama

- Gira completamente offline
- Funziona su Mac, Windows e Linux senza cambiare una riga di codice
- Su M3 gira bene grazie all'accelerazione Metal
- Nessuna registrazione, nessun limite, nessun costo

---

## Perché non puoi creare un'AI da zero su un solo PC

Questa è la distinzione più importante da capire.

### Cosa hai fatto con questo progetto

Hai costruito un **assistente AI funzionante** — ha memoria, personalità, risponde in modo intelligente, può essere esteso con tool, voce, integrazioni esterne. Per la maggior parte degli usi pratici, **è già "un'AI"**.

### Cosa NON hai fatto

Non hai creato un modello linguistico da zero. Stai usando il "cervello" (LLM) già addestrato da qualcun altro — Meta, Google, Alibaba (Qwen) — e ci costruisci intorno la struttura.

### Perché creare un LLM da zero è impossibile su un PC

Addestrare un Large Language Model da zero richiede:

- **Miliardi di parametri** da ottimizzare su miliardi di testi
- **Centinaia di GPU** (A100, H100) che lavorano in parallelo per settimane o mesi
- **Dataset enormi** — centinaia di gigabyte di testo pulito e curato
- **Competenze profonde** di machine learning, matematica e infrastruttura

È quello che fanno Anthropic (Claude), OpenAI (GPT), Google (Gemini), Meta (Llama). Non è roba da progetto personale su una singola macchina.

### La distinzione pratica

| Obiettivo | Fattibile da solo? |
|---|---|
| Chatbot personale / assistente | ✅ Sì, basta la struttura base |
| Bot con voce, memoria, tool | ✅ Sì, aggiungi moduli |
| AI con personalità custom | ✅ Basta cambiare il system prompt |
| Fine-tuning su dati tuoi | ✅ Sì, con una buona GPU o servizi cloud |
| Addestrare un modello da zero | ❌ No, serve un cluster di GPU e mesi di lavoro |
| Replicare ChatGPT da zero | ❌ No, serve un'intera azienda |

---

## Il fine-tuning — la via di mezzo

"Addestrare" non significa solo creare un modello da zero. Esiste una via di mezzo concreta: il **fine-tuning**.

Prendi un modello open-source già esistente (es. Llama 3 di Meta) e lo riaddestri su dati tuoi, cambiandone il comportamento in modo profondo e permanente — non solo tramite prompt.

**Esempio pratico:** prendi Llama 3 e lo addestri su 10.000 conversazioni mediche → ottieni un modello che ragiona come un medico specializzato. Questo puoi farlo anche su hardware consumer con una buona GPU, oppure su servizi cloud come Google Colab o RunPod.

**La differenza rispetto al system prompt:**
- Il system prompt cambia il *comportamento* del modello a runtime — ogni volta
- Il fine-tuning cambia il modello *in modo permanente* — il cambiamento è nel modello stesso

| Tecnica | Come funziona | Quando usarla |
|---|---|---|
| **System prompt** | Istruzioni date al modello ad ogni conversazione | Personalità, stile, ruolo |
| **Fine-tuning** | Riaddestramento su dati specifici | Dominio specifico, conoscenze proprietarie |
| **Pre-training da zero** | Addestrare un modello da zero su miliardi di testi | Solo grandi aziende con cluster GPU |

---

## Modelli consigliati per Mac M3 16GB

Con 16GB di RAM unificata puoi girare comodamente modelli fino a 14B parametri in quantizzazione 4bit.

| Modello | RAM usata | Qualità | Velocità |
|---|---|---|---|
| Llama 3.2 3B | ~2GB | buona | velocissima |
| Qwen2.5 7B (4bit) | ~4GB | ottima | veloce |
| Gemma 3 9B (4bit) | ~6GB | ottima | veloce |
| **Qwen3 8B** ← usato qui | ~5GB | ottima | veloce |
| Qwen2.5 14B (4bit) | ~9GB | eccellente | media |
| Phi-4 14B (4bit) | ~9GB | eccellente | media |

---

## I 4 blocchi fondamentali di un assistente AI

Qualsiasi assistente AI, da questo progetto fino alle app commerciali, si basa su questi 4 componenti:

### 1. Il modello (cervello)
Il Large Language Model che genera le risposte. Può essere locale (Ollama) o cloud (OpenAI, Anthropic, Groq).

### 2. La memoria (contesto)
Una lista di messaggi passati inviata al modello ad ogni turno. Senza di essa il modello dimentica tutto ad ogni risposta.

### 3. I tool (mani)
Funzioni Python che il modello può chiamare per eseguire azioni reali: cercare sul web, leggere file, eseguire comandi. Questo è il vero salto da "chatbot" ad "agente AI".

### 4. Il loop agente
Il ciclo continuo: utente parla → AI risponde o chiama un tool → risultato → AI risponde di nuovo.

---

## Possibili espansioni future

Con questa struttura base si possono aggiungere:

- **Voce** — sintesi vocale (TTS) e riconoscimento vocale (STT)
- **Tool** — funzioni che Raxeus può eseguire (cerca sul web, leggi file, apri app)
- **Bot Telegram** — stessa AI accessibile da Telegram
- **Memoria persistente** — salvataggio conversazioni su file o database
- **UI grafica** — interfaccia web con Streamlit o React
- **Fine-tuning** — addestrare il modello su conversazioni specifiche
