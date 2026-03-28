# Teoria — Come funziona un assistente AI

> Concetti teorici dietro il progetto Raxeus.
> Per la documentazione del codice vedi [CODE.md](CODE.md). Per bug e fix vedi [BUGS.md](BUGS.md).

---

## Cos'è un LLM

Un **Large Language Model** (LLM) è un modello statistico addestrato su miliardi di testi. Non "capisce" nel senso umano — predice il token (pezzo di testo) più probabile da generare dato un contesto. Il risultato è testo che appare intelligente e coerente.

Esempi: GPT-4 (OpenAI), Claude (Anthropic), Llama (Meta), Qwen (Alibaba), Gemma (Google).

---

## Perché non puoi crearne uno da zero su un PC

Addestrare un LLM da zero richiede:

- Miliardi di parametri da ottimizzare su miliardi di testi
- Centinaia di GPU (A100, H100) per settimane o mesi
- Dataset enormi — centinaia di GB di testo pulito e curato
- Competenze profonde di machine learning e infrastruttura

È quello che fanno Anthropic, OpenAI, Google, Meta. Non è roba da singola macchina.

**Quello che fai invece:** usi il cervello (LLM) già addestrato da altri, e ci costruisci intorno struttura, memoria e personalità. È esattamente come funziona il 99% delle app AI commerciali.

---

## Fine-tuning — la via di mezzo

"Addestrare" non significa solo creare da zero. Esiste il **fine-tuning**: prendi un modello open-source esistente e lo riaddestri su dati tuoi, cambiandone il comportamento in modo permanente.

Esempio: prendi Llama 3 (Meta, open-source) → lo addestri su 10.000 conversazioni mediche → ottieni un modello che ragiona come un medico specializzato.

| Tecnica | Come funziona | Quando usarla |
|---|---|---|
| **System prompt** | Istruzioni date al modello ad ogni conversazione | Personalità, stile, ruolo |
| **Fine-tuning** | Riaddestramento su dati specifici | Dominio specifico, conoscenze proprietarie |
| **Pre-training da zero** | Addestrare da zero su miliardi di testi | Solo grandi aziende |

Il fine-tuning richiede una buona GPU o servizi cloud (Google Colab, RunPod) — fattibile su hardware consumer, non su CPU sola.

---

## I 4 blocchi di qualsiasi assistente AI

### 1. Il modello (cervello)
L'LLM che genera le risposte. Può essere locale (Ollama) o remoto via API (OpenAI, Groq, Anthropic). Non lo crei tu — lo usi.

### 2. La memoria (contesto)
Una lista di messaggi passati inviata al modello ad ogni turno. Senza di essa il modello dimentica tutto ad ogni risposta — ogni chiamata all'API è stateless di default.

Il modello non "ricorda" davvero: gli stai semplicemente passando tutta la conversazione precedente ad ogni richiesta.

### 3. I tool (mani)
Funzioni reali che il modello può decidere di chiamare — cercare sul web, leggere file, eseguire comandi. Il modello genera una richiesta strutturata (JSON), il tuo codice esegue la funzione, il risultato torna al modello che risponde. Questo è il salto da "chatbot" ad "agente AI".

### 4. Il loop agente
Ciclo continuo: utente parla → AI risponde o chiama un tool → risultato → AI risponde di nuovo. Un agente può fare più passaggi autonomi prima di rispondere all'utente.

---

## Streaming

Per default, un modello genera tutta la risposta e la restituisce in una volta. Con lo **streaming** i token arrivano uno alla volta appena prodotti — come si vede su ChatGPT.

Tecnicamente: l'API apre una connessione HTTP persistente (Server-Sent Events) e manda i chunk man mano. Il client li riceve e li stampa in tempo reale. Il risultato finale è identico, ma l'esperienza percepita è molto più reattiva.

---

## Function calling (tool use)

Il meccanismo con cui un LLM può chiamare funzioni esterne. Il funzionamento:

1. Insieme ai messaggi, mandi al modello una lista di **tool disponibili** (nome, descrizione, parametri in JSON Schema)
2. Il modello decide se rispondere direttamente o chiamare un tool
3. Se chiama un tool, restituisce un oggetto JSON con nome e argomenti invece di testo
4. Il tuo codice esegue la funzione corrispondente
5. Il risultato viene reinserito nella conversazione come messaggio `tool`
6. Il modello riceve il risultato e genera la risposta finale

Questo ciclo può ripetersi più volte (il modello può chiamare più tool in sequenza) prima di rispondere all'utente.

```
Utente → Modello → tool_call → esegui → risultato → Modello → risposta
                       ↑___________________________|  (loop se serve)
```

---

## Sessioni persistenti

Per default la memoria esiste solo durante l'esecuzione del programma — alla chiusura, tutto si perde. Per mantenere le conversazioni tra sessioni diverse si serializza la history in un file JSON.

Al riavvio si può ricaricare la history precedente e continuare da dove si era rimasti. Il system prompt viene sempre reinserito fresco (non salvato) per garantire che la personalità sia sempre aggiornata.

---

## Modelli locali — confronto

Tutti i runner locali funzionano allo stesso modo nel codice (API compatibile OpenAI), ma differiscono per performance e portabilità.

| Tool | Descrizione | Pro | Contro |
|---|---|---|---|
| **Ollama** | Server locale semplicissimo | Cross-platform, facile, buono su Apple Silicon | Meno controllo di llama.cpp |
| **LM Studio** | Ollama con GUI grafica | Interfaccia visiva, server integrato | Solo desktop |
| **llama.cpp** | Engine C++ diretto | Velocissimo, massimo controllo | Setup tecnico |
| **MLX** | Framework Apple per M-series | Il più veloce su Apple Silicon, usa Neural Engine | Solo Apple Silicon — non portabile |
| **GPT4All** | Tutto-in-uno con GUI | Semplicissimo | Modelli meno aggiornati |

### Perché Ollama in questo progetto
- Gira offline, cross-platform
- Nessuna registrazione, nessun costo, nessun limite
- API compatibile OpenAI — cambiare provider richiede 1 riga
- Su M3 usa Metal acceleration automaticamente

---

## Cloud gratuito — quando ha senso

| Provider | Modelli | Limite free |
|---|---|---|
| **Groq** | Llama 3.3 70B, Gemma, Mixtral | 14.400 req/giorno |
| **Google Gemini** | Gemini 2.0 Flash | 1.500 req/giorno |
| **Mistral AI** | Mistral Small, Codestral | Crediti iniziali |
| **Hugging Face** | Qualsiasi modello open-source | Lento ma gratuito |

Utile per: testare modelli grandi (70B+) non scaricabili in locale, sviluppare su macchine senza Ollama, confrontare output tra modelli diversi.

---

## Modelli consigliati per Mac M3 16GB

La RAM unificata di Apple Silicon è condivisa tra CPU e GPU — puoi girare modelli più grandi del previsto.

| Modello | RAM usata | Qualità |
|---|---|---|
| Llama 3.2 3B | ~2GB | buona |
| Qwen2.5 7B 4bit | ~4GB | ottima |
| Gemma 3 9B 4bit | ~6GB | ottima |
| **Qwen3 8B** ← usato qui | ~5GB | ottima |
| Qwen2.5 14B 4bit | ~9GB | eccellente |
| Phi-4 14B 4bit | ~9GB | eccellente |

Con 16GB si arriva comodamente a modelli 14B in 4bit — qualità paragonabile a GPT-3.5.

---

## Il system prompt

Il system prompt è il messaggio iniziale con ruolo `system` inviato al modello prima di qualsiasi input utente. Definisce personalità, stile, limiti e comportamento dell'assistente. Non è "magia" — è testo come qualsiasi altro, ma posizionato prima della conversazione.

Cambiare il system prompt è il modo più rapido per creare un'AI con carattere diverso senza toccare il codice.

---

## Cosa puoi costruire con questa base

| Progetto | Cosa aggiungere |
|---|---|
| Assistente vocale | TTS (text-to-speech) + STT (speech-to-text) |
| Bot Telegram | python-telegram-bot + stesso agent.py |
| UI grafica | Streamlit (rapido) o React (completo) |
| Tutor personalizzato | system prompt specifico + fine-tuning |
| RAG (risponde su documenti tuoi) | vettorizzazione testi + retrieval |
