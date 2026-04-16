# Linguaggi di Programmazione — Guida Completa 2025

## Cos'è un linguaggio di programmazione

Un linguaggio di programmazione è un sistema formale per comunicare istruzioni a un computer. Si divide in:

- **Linguaggi compilati**: il codice sorgente viene tradotto in codice macchina prima dell'esecuzione (C, C++, Rust, Go). Più veloci a runtime.
- **Linguaggi interpretati**: il codice viene eseguito riga per riga da un interprete (Python, JavaScript lato server). Più flessibili e rapidi da sviluppare.
- **Linguaggi che usano VM**: compilati in bytecode eseguito da una macchina virtuale (Java, Kotlin, C#). Portabilità elevata.

---

## I 10 linguaggi più usati nel 2025

### 1. Python
**Paradigma:** multi-paradigma (procedurale, orientato agli oggetti, funzionale)
**Tipizzazione:** dinamica, forte

Python è il linguaggio più popolare al mondo nel 2025 per machine learning, AI e data science. La sua sintassi è pulita e leggibile, quasi simile all'inglese naturale.

**Casi d'uso principali:**
- Intelligenza artificiale e machine learning (TensorFlow, PyTorch, scikit-learn)
- Data analysis e visualizzazione (Pandas, NumPy, Matplotlib)
- Backend web (Django, FastAPI, Flask)
- Scripting e automazione
- Agenti AI (LangChain, LlamaIndex)

**Sintassi base:**
```python
# Funzione
def saluta(nome):
    return f"Ciao, {nome}!"

# Lista e comprensione
numeri = [x**2 for x in range(10) if x % 2 == 0]

# Classe
class Animale:
    def __init__(self, nome):
        self.nome = nome
    def parla(self):
        raise NotImplementedError
```

**Pro:** librerie enormi, facile da imparare, ottimo per prototipare rapidamente.
**Contro:** lento rispetto a linguaggi compilati, GIL limita il multithreading reale.

---

### 2. JavaScript
**Paradigma:** multi-paradigma (event-driven, funzionale, orientato agli oggetti)
**Tipizzazione:** dinamica, debole

L'unico linguaggio nativo del browser. Nel 2025 è usato dal 98% dei siti web lato client. Con Node.js è diventato full-stack.

**Casi d'uso principali:**
- Frontend web (React, Vue, Angular, Svelte)
- Backend con Node.js ed Express
- App mobile con React Native
- API e microservizi

**Sintassi base:**
```javascript
// Arrow function
const somma = (a, b) => a + b;

// Async/await
async function fetchDati(url) {
    const res = await fetch(url);
    return res.json();
}

// Destructuring
const { nome, eta } = persona;
const [primo, ...resto] = array;
```

**Pro:** ecosistema immenso (npm), full-stack, esecuzione nel browser.
**Contro:** coercion implicita causa bug sottili, "JavaScript fatigue" per la velocità di cambiamento dell'ecosistema.

---

### 3. TypeScript
**Paradigma:** orientato agli oggetti, funzionale
**Tipizzazione:** statica, forte (superset di JavaScript)

TypeScript aggiunge tipizzazione statica a JavaScript. Compilato in JS puro. Nel 2025 è lo standard per progetti frontend e backend di medie e grandi dimensioni.

**Sintassi base:**
```typescript
interface Utente {
    id: number;
    nome: string;
    email?: string; // opzionale
}

function saluta(utente: Utente): string {
    return `Ciao, ${utente.nome}`;
}

// Generics
function primo<T>(arr: T[]): T {
    return arr[0];
}
```

**Pro:** cattura errori in fase di sviluppo, autocomplete migliore, codice più manutenibile.
**Contro:** overhead di configurazione, curva di apprendimento sui tipi avanzati.

---

### 4. Java
**Paradigma:** orientato agli oggetti
**Tipizzazione:** statica, forte

"Write once, run anywhere" — Java gira sulla JVM, rendendolo multipiattaforma. Pilastro dell'informatica enterprise da 30 anni.

**Casi d'uso principali:**
- Backend enterprise (Spring Boot)
- App Android (legacy)
- Software bancario e finanziario
- Big Data (Hadoop, Spark)

**Sintassi base:**
```java
public class Persona {
    private String nome;
    private int eta;

    public Persona(String nome, int eta) {
        this.nome = nome;
        this.eta = eta;
    }

    public String getNome() { return nome; }

    public static void main(String[] args) {
        Persona p = new Persona("Alice", 30);
        System.out.println(p.getNome());
    }
}
```

**Pro:** fortissima retrocompatibilità, ecosistema maturo, performance eccellente con JIT.
**Contro:** verboso, boilerplate elevato, lento a prototipare.

---

### 5. C#
**Paradigma:** orientato agli oggetti, funzionale
**Tipizzazione:** statica, forte

Linguaggio di Microsoft per .NET. Nel 2025 è usato per desktop Windows, web con ASP.NET, e videogiochi con Unity.

**Casi d'uso principali:**
- App desktop Windows (WPF, WinUI)
- Web API con ASP.NET Core
- Videogiochi (Unity — praticamente monopolio nel settore)
- Cloud Azure

**Sintassi base:**
```csharp
record Persona(string Nome, int Eta); // record immutabile

var persone = new List<Persona> {
    new("Alice", 30),
    new("Bob", 25)
};

var adulti = persone
    .Where(p => p.Eta >= 18)
    .OrderBy(p => p.Nome)
    .ToList();
```

**Pro:** LINQ (query su collezioni potentissime), pattern moderni, Unity.
**Contro:** legato all'ecosistema Microsoft, meno diffuso su Linux/macOS rispetto a Java.

---

### 6. C e C++
**Paradigma:** procedurale (C), multi-paradigma con OOP (C++)
**Tipizzazione:** statica, debole

C è il padre di quasi tutti i linguaggi moderni. C++ aggiunge OOP e template. Usati dove le performance sono critiche.

**Casi d'uso principali:**
- Sistemi operativi (Linux kernel è in C)
- Driver e firmware
- Motori grafici (Unreal Engine è in C++)
- Trading ad alta frequenza
- Embedded systems

**Sintassi C base:**
```c
#include <stdio.h>

int fattoriale(int n) {
    if (n <= 1) return 1;
    return n * fattoriale(n - 1);
}

int main() {
    printf("%d\n", fattoriale(5)); // 120
    return 0;
}
```

**Pro:** performance massima, controllo totale sulla memoria, ovunque.
**Contro:** gestione manuale della memoria (bug, memory leak), difficile da imparare correttamente.

---

### 7. Rust
**Paradigma:** multi-paradigma (sistemi, funzionale)
**Tipizzazione:** statica, forte

Il linguaggio del futuro per i sistemi. Offre sicurezza della memoria garantita a compile-time senza garbage collector — zero cost abstractions.

**Concetto chiave — Ownership:**
```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1; // s1 è "moved", non più valido
    // println!("{}", s1); // ERRORE di compilazione

    let s3 = String::from("world");
    let s4 = &s3; // borrow: s3 è ancora valido
    println!("{} {}", s3, s4);
}
```

**Pro:** impossibile avere buffer overflow o use-after-free, performance = C/C++, eccellente per WebAssembly.
**Contro:** curva di apprendimento ripidissima (borrow checker), compilazione lenta.

---

### 8. Go (Golang)
**Paradigma:** procedurale, concorrente
**Tipizzazione:** statica, forte

Creato da Google nel 2009. Semplice come Python, veloce come C. La concorrenza è built-in con goroutine e channel.

**Casi d'uso principali:**
- Microservizi e API REST
- Cloud e DevOps (Docker e Kubernetes sono scritti in Go)
- Tool CLI
- Sistemi distribuiti

**Sintassi base:**
```go
package main

import "fmt"

// Goroutine — thread leggero
func worker(id int, ch chan string) {
    ch <- fmt.Sprintf("worker %d finito", id)
}

func main() {
    ch := make(chan string, 3)
    for i := 1; i <= 3; i++ {
        go worker(i, ch)
    }
    for i := 0; i < 3; i++ {
        fmt.Println(<-ch)
    }
}
```

**Pro:** goroutine ultra-leggere (migliaia in parallelo), compilazione rapidissima, binario singolo senza dipendenze.
**Contro:** gestione errori verbosa, generics arrivati tardi (v1.18).

---

### 9. Kotlin
**Paradigma:** orientato agli oggetti, funzionale
**Tipizzazione:** statica, forte

Linguaggio ufficiale Google per Android. Interoperabile 100% con Java, sintassi molto più concisa.

```kotlin
data class Utente(val nome: String, val eta: Int)

val utenti = listOf(
    Utente("Alice", 30),
    Utente("Bob", 17)
)

val adulti = utenti.filter { it.eta >= 18 }.map { it.nome }
println(adulti) // [Alice]
```

---

### 10. Swift
**Paradigma:** orientato agli oggetti, funzionale, protocol-oriented
**Tipizzazione:** statica, forte

Linguaggio nativo Apple per iOS, macOS, watchOS. Moderno, sicuro, performante.

```swift
struct Persona {
    let nome: String
    var eta: Int

    var isAdulto: Bool { eta >= 18 }
}

let alice = Persona(nome: "Alice", eta: 30)
print(alice.isAdulto) // true
```

---

## Concetti fondamentali trasversali

### Tipi di dati
| Tipo | Descrizione | Esempio |
|---|---|---|
| Intero | numero senza virgola | `42`, `-7` |
| Float/Double | numero con virgola | `3.14` |
| Stringa | testo | `"hello"` |
| Booleano | vero o falso | `true`, `false` |
| Array/Lista | sequenza ordinata | `[1, 2, 3]` |
| Dizionario/Map | coppie chiave-valore | `{"chiave": "valore"}` |
| Null/None | assenza di valore | `null`, `None`, `nil` |

### Strutture di controllo (universali)
```
if / else if / else     → scelta condizionale
for / while             → ciclo (loop)
switch / match          → scelta multipla
try / catch / finally   → gestione errori
```

### Paradigmi principali

**Programmazione procedurale:** codice organizzato in funzioni che si chiamano in sequenza. Base di C.

**Programmazione orientata agli oggetti (OOP):**
- **Classe**: schema per creare oggetti
- **Oggetto**: istanza di una classe
- **Ereditarietà**: una classe eredita da un'altra
- **Encapsulation**: dati nascosti, accesso controllato
- **Polimorfismo**: stesso metodo, comportamento diverso

**Programmazione funzionale:**
- Funzioni pure (stesso input → stesso output, no side effect)
- Immutabilità dei dati
- Higher-order functions (map, filter, reduce)
- Composizione di funzioni

### Algoritmi fondamentali

**Complessità temporale (Big O):**
- O(1) — costante: accesso a un array per indice
- O(log n) — logaritmica: ricerca binaria
- O(n) — lineare: scorrere una lista
- O(n log n) — linearitmica: quicksort, mergesort
- O(n²) — quadratica: bubble sort, doppio ciclo annidato
- O(2^n) — esponenziale: algoritmi brute force su sottoinsiemi

**Strutture dati:**
- **Array**: accesso O(1), inserimento O(n)
- **Lista collegata**: inserimento O(1), accesso O(n)
- **Stack**: LIFO (Last In First Out)
- **Queue**: FIFO (First In First Out)
- **Hash table (dizionario)**: accesso e inserimento O(1) medio
- **Albero binario**: ricerca O(log n) se bilanciato
- **Grafo**: per relazioni complesse tra nodi

### Git — controllo versione
```bash
git init                    # inizializza repo
git add .                   # aggiunge tutti i file
git commit -m "messaggio"   # salva snapshot
git branch feature          # crea ramo
git checkout feature        # cambia ramo
git merge feature           # unisce ramo
git push origin main        # carica su remote
git pull                    # scarica aggiornamenti
```

### Concetti web fondamentali
- **HTTP/HTTPS**: protocollo per comunicare tra client e server
- **REST API**: architettura per API web (GET, POST, PUT, DELETE)
- **JSON**: formato dati per scambiare informazioni tra sistemi
- **Frontend**: ciò che l'utente vede (HTML, CSS, JavaScript)
- **Backend**: logica lato server (Python, Java, Node.js, ecc.)
- **Database**: dove i dati vengono salvati (SQL: PostgreSQL, MySQL; NoSQL: MongoDB, Redis)
- **Docker**: containerizzazione — impacchetta l'app con le sue dipendenze
- **CI/CD**: automazione di test e deploy (GitHub Actions, Jenkins)

---

## Quale linguaggio scegliere

| Obiettivo | Linguaggio consigliato |
|---|---|
| Imparare a programmare | Python |
| Sito web frontend | JavaScript / TypeScript |
| App web full-stack | TypeScript (Node.js + React) |
| App mobile iOS | Swift |
| App mobile Android | Kotlin |
| Backend enterprise | Java / C# |
| AI e machine learning | Python |
| Microservizi cloud | Go |
| Sistemi e performance massima | Rust / C++ |
| Videogiochi | C# (Unity) / C++ (Unreal) |
| Scripting e automazione | Python / Bash |
