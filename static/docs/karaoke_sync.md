# ⏱️ Sincronizzazione (Karaoke)

Avere il testo di una canzone è bello, ma avere il testo sincronizzato perfettamente con la voce dell'artista è magia pura. 

## Generazione di File .LRC

Dopo che la *Trascrizione Magica* ha estratto le parole, un secondo algoritmo analizza i millisecondi esatti in cui ogni parola viene pronunciata all'interno del flusso audio.

```mermaid
gantt
    title Sincronizzazione Temporale
    dateFormat s
    axisFormat %S
    section Voce
    "Imagine there's no heaven" :a1, 0, 4s
    "It's easy if you try"      :a2, 4s, 8s
    "No hell below us"          :a3, 8s, 11s
```

### Il Risultato Finale
Viene generato un file testuale con dei "Timestamp". L'interfaccia di RaxeusLyric legge questo file e, comunicando costantemente con il player audio, **illumina le frasi nel momento esatto in cui il cantante le pronuncia**, creando un'esperienza Karaoke coinvolgente e totalmente automatica.
