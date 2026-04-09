# RaxeusAI — Web UI

Invece del terminale, Raxeus si apre nel browser. Gira tutto in locale tramite Flask.

---

## Come funziona

`app.py` avvia un server Flask. Aprendo `http://localhost:5000` compare l'interfaccia. Il backend usa `agent.py` e `sessions.py` già esistenti senza toccarli. I token della risposta arrivano in streaming via SSE (Server-Sent Events), esattamente come su ChatGPT.

---

## Interfaccia

**Topbar** — barra scura in cima con: logo "Raxeus", barra di ricerca che filtra le tab, le tab delle chat aperte (max 5), pulsante `+` per nuova chat, pallino colorato tutto a destra.

**Chat** — messaggi AI a sinistra senza bolla, messaggi utente a destra con bolla colorata. Durante i tool call compare uno spinner con "elaborazione..." senza altri dettagli.

**Input** — barra in fondo, invio con tasto o `Enter`.

---

## Colore bolla

Il pallino in alto a destra mostra il colore della chat attiva. Cliccandolo apre un piccolo popup con 6 preset (grigio scuro di default, verde, blu, viola, rosso, ambra) più un color picker custom. Ogni chat ha il suo colore, salvato in `localStorage`.

---

## Tab e chat

Massimo 5 tab aperte. Il titolo di ogni tab si assegna automaticamente dalle prime 30 lettere del primo messaggio. Aprire una sesta chat chiude quella più vecchia. Le sessioni vengono salvate su file tramite `sessions.py` già esistente.

---

## File nuovi

- `app.py` — server Flask + endpoint
- `templates/index.html` — tutta l'interfaccia
- `static/style.css` — tema scuro
- `static/app.js` — logica tab, streaming, color picker
