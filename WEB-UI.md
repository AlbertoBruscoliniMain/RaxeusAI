# Web UI — Come funziona l'interfaccia

> Per i dettagli tecnici del codice vedi [CODE.md](CODE.md). Per i concetti teorici (SSE, architettura) vedi [THEORY.md](THEORY.md).

---

## Idea di base

Invece del terminale, Raxeus si apre nel browser. Gira tutto in locale tramite Flask. Il backend riusa `agent.py` e `sessions.py` già esistenti — l'unica cosa nuova è `app.py` che fa da ponte tra il browser e il modello.

---

## Come avviarla

```bash
source venv/bin/activate
python app.py
# apri http://localhost:5000
```

`main.py` (il terminale) continua a funzionare normalmente — le due modalità sono indipendenti.

---

## Interfaccia

**Topbar** — barra scura fissa in cima. Da sinistra: logo "Raxeus", campo di ricerca che filtra le tab mentre scrivi, tab delle chat aperte (max 5), pulsante `+` per aprire una nuova chat, pallino colorato tutto a destra.

**Area chat** — messaggi AI a sinistra (solo testo, niente bolla), messaggi utente a destra con bolla colorata. Durante i tool call (ricerche web, esecuzione Python, ecc.) compare uno spinner con "elaborazione..." — nessun dettaglio tecnico esposto.

**Barra input** — fissa in fondo. Invio con il pulsante o con `Enter`. `Shift+Enter` va a capo senza inviare.

---

## Tab e chat

- Massimo 5 tab aperte contemporaneamente. Aprirne una sesta chiude automaticamente la più vecchia.
- Il titolo di ogni tab si assegna automaticamente: le prime 30 caratteri del primo messaggio inviato.
- La barra di ricerca in alto filtra le tab visibili in tempo reale.
- Le sessioni vengono salvate su file JSON tramite `sessions.py`. Al riavvio di `app.py` le ultime 5 sessioni vengono ricaricate come tab.

---

## Colore bolla

Ogni chat ha il proprio colore per la bolla dei messaggi utente, salvato in `localStorage` — cambia chat, cambia colore.

Il pallino in alto a destra riflette il colore della chat attiva. Cliccandolo apre un popup con:

| Preset | Sfondo |
|---|---|
| Grigio scuro (default) | `#252525` |
| Verde | `#1e3a1e` |
| Blu | `#1a2a3a` |
| Viola | `#2a1a3a` |
| Rosso scuro | `#3a1a1a` |
| Ambra | `#2a2a18` |
| Custom | color picker hex libero |

---

## Streaming dei token

Le risposte arrivano token per token in tempo reale, esattamente come su ChatGPT. Tecnicamente avviene via SSE (Server-Sent Events) — per capire come funziona vedi la sezione dedicata in [THEORY.md](THEORY.md).
