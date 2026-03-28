# Bug & Fix Log

Storico dei bug risolti e problemi noti del progetto Raxeus.

---

## Bug risolti

---

### BUG-001 — Raxeus risponde con dati vecchi (fermo al 2023)

**Stato:** ✅ Risolto

**Sintomo:** Anche chiedendo informazioni recenti, Raxeus rispondeva con dati del suo training data (fermi al periodo di addestramento del modello), ignorando che poteva cercare su internet.

**Causa:** `google_search` restituiva solo URL — nessun testo. Il modello riceveva una lista di link ma non poteva leggerne il contenuto, quindi cadeva sul proprio training data per formulare la risposta.

**Fix applicato:**
1. `google_search` aggiornato con `advanced=True` — ora restituisce titolo, descrizione e URL per ogni risultato
2. Aggiunto tool `fetch_url` — permette al modello di leggere il contenuto testuale di una pagina web dato il suo URL
3. Flusso aggiornato: `google_search` trova le pagine → `fetch_url` ne legge il contenuto → il modello risponde con dati reali e aggiornati

---

### BUG-002 — Output interno dei tool visibile all'utente

**Stato:** ✅ Risolto

**Sintomo:** Durante una ricerca o esecuzione di tool, il terminale mostrava righe tipo `→ google_search({'query': '...'})` e `← risultato...`, interrompendo il flusso di lettura della risposta.

**Causa:** In `agent.py` erano presenti `print()` espliciti per mostrare il nome del tool chiamato e un'anteprima del risultato, pensati per debug.

**Fix applicato:** Rimossi i `print` di debug in `agent.py`. Ora il tool viene eseguito silenziosamente — l'utente vede solo la risposta finale.

---

### BUG-003 — venv con percorsi rotti dopo spostamento cartella

**Stato:** ✅ Risolto

**Sintomo:** Dopo che la cartella del progetto è stata rinominata da `AI personale` a `RaxeusAI`, il venv non si avviava e `pip` crashava con `cannot execute`.

**Causa:** Il file `venv/bin/activate` e gli script interni del venv contengono percorsi assoluti hardcoded al momento della creazione. Spostare o rinominare la cartella rompe questi riferimenti.

**Fix applicato:** Ricreato il venv da zero nella nuova posizione con `python3 -m venv venv` e reinstallate tutte le dipendenze.

**Nota per il futuro:** I venv non sono portabili — se sposti la cartella del progetto, ricreare sempre il venv.

---

### BUG-004 — `__pycache__` committato su GitHub

**Stato:** ✅ Risolto

**Sintomo:** Il primo commit includeva i file compilati `.pyc` nella cartella `__pycache__/`.

**Causa:** Il `.gitignore` iniziale conteneva solo `venv/`, senza escludere `__pycache__`.

**Fix applicato:** Aggiornato `.gitignore` con `__pycache__/` e `*.pyc`. I file già tracciati sono stati rimossi con `git rm -r --cached __pycache__/`.

---

## Bug noti / da monitorare

---

### BUG-005 — `fetch_url` bloccato da siti con anti-scraping

**Stato:** ⚠️ Noto, parzialmente mitigato

**Sintomo:** Alcuni siti (es. LinkedIn, siti con Cloudflare) restituiscono errore 403 o pagina vuota quando `fetch_url` tenta di leggerli.

**Causa:** I siti rilevano il traffico automatico e bloccano le richieste non provenienti da browser reali.

**Mitigazione attuale:** `User-Agent` impostato a stringa browser standard.

**Possibile fix futuro:** Usare `playwright` o `selenium` per fetch con browser headless reale, oppure filtrare i domini problematici.

---

### BUG-006 — Memoria illimitata: context window overflow

**Stato:** ⚠️ Noto, non ancora risolto

**Sintomo:** In conversazioni molto lunghe o con molte chiamate a tool (che aggiungono messaggi extra alla history), il modello può raggiungere il limite di contesto e iniziare a troncare i messaggi più vecchi o restituire errori.

**Causa:** La `Memory` accumula tutti i messaggi senza limite. I risultati dei tool possono essere molto lunghi (fino a 3000 caratteri ciascuno).

**Possibile fix futuro:** Implementare una strategia di truncation — mantenere sempre il system prompt, gli ultimi N messaggi utente/assistant, e comprimere/rimuovere i messaggi tool più vecchi.

---

### BUG-007 — `run_python` usa il Python di sistema, non il venv

**Stato:** ⚠️ Noto, comportamento atteso ma da documentare

**Sintomo:** Se il codice eseguito da `run_python` importa librerie installate solo nel venv (es. `openai`), ottiene `ModuleNotFoundError`.

**Causa:** `subprocess.run(["python3", ...])` lancia il Python di sistema, non quello del venv.

**Possibile fix futuro:** Usare `sys.executable` invece di `"python3"` per lanciare il Python del venv corrente.
