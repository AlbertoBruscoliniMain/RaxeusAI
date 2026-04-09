# Superpowers — Cos'è e come funziona

> Per la documentazione del codice vedi [CODE.md](CODE.md). Per i concetti teorici vedi [THEORY.md](THEORY.md).

---

## Cos'è Superpowers

Superpowers è un plugin per Claude Code (il tool AI da terminale di Anthropic) che aggiunge un sistema di "skill" — istruzioni specializzate che guidano Claude in task complessi come progettare feature, scrivere piani di implementazione ed eseguirli step by step.

In questo progetto è stato usato per progettare e implementare la web UI di Raxeus.

---

## La cartella .superpowers/

Generata automaticamente dal plugin durante le sessioni di brainstorming. Contiene file temporanei di lavoro — mockup HTML visualizzati nel browser durante il design, file di stato delle sessioni, PID del server locale.

**Non serve toccarla.** Non contiene documentazione utile. Si può aggiungere a `.gitignore`.

```
.superpowers/
└── brainstorm/
    └── <session-id>/
        ├── content/   → mockup HTML mostrati nel browser durante il design
        └── state/     → stato della sessione (eventi click, PID server, ecc.)
```

---

## Il workflow usato

Quando si aggiunge una feature con Superpowers si seguono tre fasi:

**1. Brainstorming** — Claude fa domande una alla volta per capire cosa costruire, mostra mockup nel browser, propone 2-3 approcci, presenta il design e chiede approvazione. Risultato: una spec scritta.

**2. Piano** — Claude scrive un piano di implementazione step-by-step con codice esatto, comandi e test per ogni task.

**3. Esecuzione** — Claude esegue il piano task per task, con verifica dopo ogni step.

---

## La cartella docs/ (rimossa)

Conteneva la spec e il piano della web UI, generati automaticamente durante il workflow Superpowers. Ora quei contenuti sono stati spostati qui e in [WEB-UI.md](WEB-UI.md). La cartella `docs/` è stata eliminata perché aggiungeva struttura senza utilità reale — tutto quello che serve è già nei file `.md` nella root.
