# Linguaggi di Programmazione — Guida Approfondita Completa

## Cos'è un linguaggio di programmazione

Un linguaggio di programmazione è un sistema formale per comunicare istruzioni a un computer. Si divide in:

- **Linguaggi compilati**: il codice sorgente viene tradotto in codice macchina prima dell'esecuzione (C, C++, Rust, Go). Più veloci a runtime.
- **Linguaggi interpretati**: il codice viene eseguito riga per riga da un interprete (Python, JavaScript lato server). Più flessibili e rapidi da sviluppare.
- **Linguaggi che usano VM**: compilati in bytecode eseguito da una macchina virtuale (Java, Kotlin, C#). Portabilità elevata.

---

# PYTHON

## Panoramica
Python è il linguaggio più popolare al mondo nel 2025. Creato da Guido van Rossum nel 1991. Filosofia: "leggibilità conta" (The Zen of Python). Tipizzazione dinamica, forte. Multiparadigma: procedurale, OOP, funzionale.

## Tipi di dati built-in

```python
# Numerici
x = 42          # int
y = 3.14        # float
z = 2 + 3j      # complex

# Sequenze
lista = [1, 2, 3]           # list — mutabile
tupla = (1, 2, 3)           # tuple — immutabile
stringa = "hello"           # str — immutabile
byte_s = b"hello"           # bytes

# Mappings
diz = {"chiave": "valore"}  # dict

# Set
s = {1, 2, 3}               # set — no duplicati
fs = frozenset({1, 2, 3})   # frozenset — immutabile

# Booleano
t, f = True, False

# Nessun valore
n = None
```

## Strutture di controllo

```python
# if / elif / else
if x > 0:
    print("positivo")
elif x == 0:
    print("zero")
else:
    print("negativo")

# for su qualsiasi iterabile
for i in range(10):
    print(i)

for indice, valore in enumerate(["a", "b", "c"]):
    print(indice, valore)

for chiave, valore in diz.items():
    print(chiave, "->", valore)

# while
while condizione:
    ...

# try / except / else / finally
try:
    risultato = 10 / 0
except ZeroDivisionError as e:
    print(f"Errore: {e}")
except (TypeError, ValueError):
    pass
else:
    print("Nessun errore")
finally:
    print("Sempre eseguito")
```

## List, dict e set comprehension

```python
# List comprehension
quadrati = [x**2 for x in range(10)]
pari = [x for x in range(20) if x % 2 == 0]
matrice = [[i*j for j in range(3)] for i in range(3)]

# Dict comprehension
quadrati_dict = {x: x**2 for x in range(5)}
inverso = {v: k for k, v in diz.items()}

# Set comprehension
unici = {x % 3 for x in range(10)}

# Generator expression (lazy — non crea lista in memoria)
gen = (x**2 for x in range(1000000))
primo = next(gen)
```

## Funzioni avanzate

```python
# Args e kwargs
def funzione(*args, **kwargs):
    for a in args: print(a)
    for k, v in kwargs.items(): print(k, v)

funzione(1, 2, 3, nome="Alice", eta=30)

# Default arguments (ATTENZIONE: valori mutabili come default sono bug)
def aggiungi(elemento, lista=None):  # corretto
    if lista is None:
        lista = []
    lista.append(elemento)
    return lista

# Annotazioni di tipo (type hints)
def saluta(nome: str, volte: int = 1) -> str:
    return (nome + "\n") * volte

# Lambda — funzione anonima inline
doppio = lambda x: x * 2
somma = lambda a, b: a + b

# Funzioni di ordine superiore
numeri = [3, 1, 4, 1, 5, 9]
ordinati = sorted(numeri, key=lambda x: -x)  # decrescente
filtrati = list(filter(lambda x: x > 3, numeri))
mappati = list(map(lambda x: x**2, numeri))

# functools
from functools import reduce, partial, lru_cache

prodotto = reduce(lambda a, b: a * b, numeri)

@lru_cache(maxsize=128)  # memoization automatica
def fibonacci(n):
    if n < 2: return n
    return fibonacci(n-1) + fibonacci(n-2)

moltiplica_per_3 = partial(lambda x, y: x * y, 3)
```

## Decoratori

```python
# Decoratore base
def mio_decoratore(func):
    def wrapper(*args, **kwargs):
        print("Prima")
        risultato = func(*args, **kwargs)
        print("Dopo")
        return risultato
    return wrapper

@mio_decoratore
def saluta():
    print("Ciao!")

# Decoratore con parametri
def ripeti(volte):
    def decoratore(func):
        def wrapper(*args, **kwargs):
            for _ in range(volte):
                func(*args, **kwargs)
        return wrapper
    return decoratore

@ripeti(3)
def canta():
    print("La la la")

# Decoratori comuni
@staticmethod    # metodo senza self
@classmethod     # metodo con cls invece di self
@property        # getter come attributo
```

## Context manager (with)

```python
# File — gestione automatica chiusura
with open("file.txt", "r") as f:
    contenuto = f.read()
# f è automaticamente chiuso anche in caso di errore

# Creare un context manager custom
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    yield
    print(f"Tempo: {time.time() - start:.3f}s")

with timer():
    [x**2 for x in range(1000000)]
```

## Classi e OOP

```python
class Animale:
    # Variabile di classe (condivisa da tutte le istanze)
    conta = 0

    def __init__(self, nome: str, eta: int):
        self.nome = nome      # attributo di istanza
        self._eta = eta       # convenzione: "privato" (non enforced)
        self.__segreto = "x"  # name mangling: _Animale__segreto
        Animale.conta += 1

    # Property
    @property
    def eta(self):
        return self._eta

    @eta.setter
    def eta(self, valore):
        if valore < 0:
            raise ValueError("Età negativa")
        self._eta = valore

    # Metodi speciali (dunder methods)
    def __str__(self):    return f"{self.nome} ({self._eta} anni)"
    def __repr__(self):   return f"Animale('{self.nome}', {self._eta})"
    def __eq__(self, other): return self.nome == other.nome
    def __lt__(self, other): return self._eta < other._eta
    def __len__(self):    return self._eta

    @classmethod
    def conta_animali(cls):
        return cls.conta

    @staticmethod
    def valida_nome(nome):
        return len(nome) > 0


class Cane(Animale):
    def __init__(self, nome, eta, razza):
        super().__init__(nome, eta)
        self.razza = razza

    def abbaia(self):
        return f"{self.nome} dice: Bau!"

    def __str__(self):
        return f"{super().__str__()} - {self.razza}"


# Dataclass (Python 3.7+) — meno boilerplate
from dataclasses import dataclass, field

@dataclass
class Punto:
    x: float
    y: float
    z: float = 0.0
    tags: list = field(default_factory=list)

    def distanza(self):
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5
```

## Async / Await

```python
import asyncio
import aiohttp

# Coroutine base
async def saluta(nome: str):
    await asyncio.sleep(1)  # attesa non bloccante
    print(f"Ciao {nome}")

# Eseguire coroutine in parallelo
async def main():
    # Sequenziale
    await saluta("Alice")
    await saluta("Bob")

    # Parallelo — molto più veloce
    await asyncio.gather(
        saluta("Alice"),
        saluta("Bob"),
        saluta("Carol"),
    )

asyncio.run(main())

# HTTP async con aiohttp
async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.json()

async def fetch_many(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

## Gestione errori avanzata

```python
# Eccezioni custom
class DatabaseError(Exception):
    def __init__(self, message, codice=None):
        super().__init__(message)
        self.codice = codice

class ConnessioneError(DatabaseError):
    pass

# Catena di eccezioni
try:
    ...
except OSError as e:
    raise DatabaseError("Impossibile connettersi") from e

# ExceptionGroup (Python 3.11+)
try:
    async with asyncio.TaskGroup() as tg:
        tg.create_task(compito1())
        tg.create_task(compito2())
except* ValueError as eg:
    for e in eg.exceptions:
        print(e)
```

## Moduli e package fondamentali

```python
# Standard library
import os, sys, pathlib, shutil      # filesystem
import json, csv, configparser        # dati
import datetime, time, calendar       # tempo
import re                             # regex
import collections, itertools         # strutture dati e iteratori
import threading, multiprocessing     # concorrenza
import subprocess                     # processi esterni
import logging                        # logging
import unittest, pytest               # testing
import socket, http                   # rete

# Librerie comuni (pip)
# numpy — array numerici veloci
# pandas — dataframe e analisi dati
# matplotlib / seaborn — grafici
# scikit-learn — machine learning
# tensorflow / pytorch — deep learning
# requests — HTTP semplice
# aiohttp — HTTP async
# fastapi — API REST async
# django — web framework completo
# flask — web framework minimale
# sqlalchemy — ORM database
# pydantic — validazione dati e settings
# celery — task queue asincrona
# redis-py — client Redis
```

## Type hints avanzati (Python 3.10+)

```python
from typing import Optional, Union, Any, Callable, TypeVar
from collections.abc import Sequence, Iterator, Generator

T = TypeVar("T")

def primo(sequenza: Sequence[T]) -> T | None:
    return sequenza[0] if sequenza else None

# Match statement (Python 3.10+)
def analizza(comando: str | dict | list):
    match comando:
        case str() as s if s.startswith("go"):
            print("Movimento:", s)
        case {"azione": str(a), "target": str(t)}:
            print(f"Azione {a} su {t}")
        case [*elementi] if len(elementi) > 2:
            print("Lista lunga:", elementi)
        case _:
            print("Non riconosciuto")
```

---

# JAVASCRIPT

## Panoramica
Creato nel 1995 da Brendan Eich in 10 giorni. Unico linguaggio nativo del browser. Con Node.js è diventato full-stack. Tipizzazione dinamica, debole. Event-driven, single-threaded con event loop.

## Tipi e variabili

```javascript
// var (function-scoped, hoist) — EVITARE
var x = 1;

// let (block-scoped, mutabile) — usare
let contatore = 0;

// const (block-scoped, non riassegnabile) — preferire
const PI = 3.14159;
const obj = { a: 1 }; // obj è const, ma obj.a può cambiare

// Tipi primitivi
typeof 42          // "number"
typeof "hello"     // "string"
typeof true        // "boolean"
typeof undefined   // "undefined"
typeof null        // "object" — famoso bug di JS
typeof Symbol()    // "symbol"
typeof 42n         // "bigint"

// Coercione implicita (PERICOLOSA)
"5" + 3  // "53" (string concatenation)
"5" - 3  // 2    (numeric subtraction)
"5" == 5 // true (loose equality — EVITARE)
"5" === 5 // false (strict equality — USARE SEMPRE)
```

## Funzioni e scope

```javascript
// Function declaration (hoist)
function somma(a, b) { return a + b; }

// Function expression
const somma = function(a, b) { return a + b; };

// Arrow function (no proprio this)
const somma = (a, b) => a + b;
const quadrato = x => x ** 2;
const saluta = () => console.log("Ciao");

// Default params, rest, spread
function log(livello = "info", ...messaggi) {
    console.log(`[${livello}]`, ...messaggi);
}

// Destructuring
const [a, b, ...resto] = [1, 2, 3, 4, 5];
const { nome, eta, citta = "Milano" } = persona;
const { nome: n, eta: e } = persona; // rinominare

// Closure
function creaContatore() {
    let count = 0;
    return {
        incrementa: () => ++count,
        valore: () => count
    };
}
const c = creaContatore();
c.incrementa(); c.incrementa();
console.log(c.valore()); // 2
```

## Array — metodi fondamentali

```javascript
const nums = [1, 2, 3, 4, 5];

// Trasformazione (restituiscono nuovo array)
nums.map(x => x * 2)          // [2, 4, 6, 8, 10]
nums.filter(x => x % 2 === 0) // [2, 4]
nums.reduce((acc, x) => acc + x, 0) // 15
nums.flatMap(x => [x, x*2])   // [1,2, 2,4, 3,6, 4,8, 5,10]

// Ricerca
nums.find(x => x > 3)         // 4
nums.findIndex(x => x > 3)    // 3
nums.some(x => x > 4)         // true
nums.every(x => x > 0)        // true
nums.includes(3)              // true

// Ordinamento (MODIFICA l'array originale)
[...nums].sort((a, b) => b - a) // decrescente

// Iterazione
nums.forEach(x => console.log(x))

// Spreading e concatenazione
const tutti = [...nums, ...altriNums, 6, 7];
```

## Oggetti e prototype

```javascript
// Object literal
const persona = {
    nome: "Alice",
    eta: 30,
    saluta() { return `Ciao, sono ${this.nome}`; },
    get descrizione() { return `${this.nome}, ${this.eta} anni`; }
};

// Object methods
Object.keys(persona)          // ["nome", "eta", "saluta"]
Object.values(persona)
Object.entries(persona)       // [["nome", "Alice"], ...]
Object.assign({}, p1, p2)     // merge (shallow)
const clone = { ...persona }  // spread (shallow clone)

// Classi (syntactic sugar su prototype)
class Animale {
    #vita = 100; // campo privato (ES2022)

    constructor(nome) {
        this.nome = nome;
    }

    static crea(nome) { return new Animale(nome); }

    get salute() { return this.#vita; }

    parla() { return `${this.nome} fa un suono`; }
}

class Cane extends Animale {
    constructor(nome, razza) {
        super(nome);
        this.razza = razza;
    }
    parla() { return `${this.nome} abbaia`; }
}
```

## Async: Promise e async/await

```javascript
// Promise
const promessa = new Promise((resolve, reject) => {
    setTimeout(() => resolve("fatto!"), 1000);
});

promessa
    .then(risultato => console.log(risultato))
    .catch(err => console.error(err))
    .finally(() => console.log("finito"));

// Promise.all — aspetta tutte (fail fast)
const [a, b] = await Promise.all([fetch(url1), fetch(url2)]);

// Promise.allSettled — aspetta tutte (anche quelle fallite)
const risultati = await Promise.allSettled([p1, p2, p3]);

// Promise.race — vince la prima
const prima = await Promise.race([p1, p2]);

// async/await
async function fetchDati(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error("Errore fetch:", err);
        throw err;
    }
}
```

## Event Loop e concorrenza

JavaScript è single-threaded ma non-bloccante grazie all'event loop:
- **Call stack**: esecuzione sincrona
- **Web APIs / Node APIs**: setTimeout, fetch, fs.readFile — eseguiti in background
- **Callback queue (macrotask)**: setTimeout, setInterval
- **Microtask queue**: Promise.then, queueMicrotask — priorità su macrotask

```javascript
console.log("1");
setTimeout(() => console.log("4"), 0);
Promise.resolve().then(() => console.log("3"));
console.log("2");
// Output: 1, 2, 3, 4
```

## Moduli (ES Modules)

```javascript
// esportare
export const PI = 3.14;
export function somma(a, b) { return a + b; }
export default class Calcolatore { ... }

// importare
import Calcolatore, { PI, somma } from "./math.js";
import * as math from "./math.js";
import("./math.js").then(m => m.somma(1, 2)); // dynamic import
```

## Metodi moderni importanti

```javascript
// Optional chaining
const citta = utente?.indirizzo?.citta ?? "sconosciuta";

// Nullish coalescing
const nome = valore ?? "default"; // solo null/undefined, non 0 o ""

// Logical assignment
a ??= "default";  // assegna solo se null/undefined
a ||= "default";  // assegna se falsy
a &&= valore;     // assegna se truthy

// Object.fromEntries
const obj = Object.fromEntries(entries);

// Array.at()
arr.at(-1)  // ultimo elemento (negativo = da fine)

// structuredClone — deep clone nativo
const copia = structuredClone(oggetto);
```

---

# TYPESCRIPT

## Panoramica
TypeScript = JavaScript + tipizzazione statica. Compilato in JS. Creato da Microsoft (Anders Hejlsberg, 2012). Standard de facto per frontend e backend di medie e grandi dimensioni.

## Tipi base e annotazioni

```typescript
// Primitivi
let nome: string = "Alice";
let eta: number = 30;
let attivo: boolean = true;
let niente: null = null;
let indefinito: undefined = undefined;
let qualcosa: unknown = "valore"; // più sicuro di any
let tutto: any = "tutto";        // evitare

// Array e tuple
let numeri: number[] = [1, 2, 3];
let tupla: [string, number] = ["Alice", 30];

// Enum
enum Direzione { Su, Giù, Sinistra, Destra }
const d: Direzione = Direzione.Su;

enum Colore { Rosso = "RED", Verde = "GREEN" }
```

## Interface e Type

```typescript
// Interface — per oggetti, estendibile
interface Utente {
    id: number;
    nome: string;
    email?: string;          // opzionale
    readonly creato: Date;   // solo lettura
}

interface Amministratore extends Utente {
    permessi: string[];
}

// Type alias — più flessibile
type ID = string | number;
type Punto = { x: number; y: number };
type Callback = (err: Error | null, risultato?: string) => void;

// Union e intersection
type AdminUtente = Utente & Amministratore;
type Forma = Cerchio | Rettangolo | Triangolo;

// Discriminated union
type Forma =
    | { tipo: "cerchio"; raggio: number }
    | { tipo: "rettangolo"; larghezza: number; altezza: number };

function area(f: Forma): number {
    switch (f.tipo) {
        case "cerchio": return Math.PI * f.raggio ** 2;
        case "rettangolo": return f.larghezza * f.altezza;
    }
}
```

## Generics

```typescript
// Funzione generica
function primo<T>(arr: T[]): T | undefined {
    return arr[0];
}

// Con constraint
function massimo<T extends number | string>(a: T, b: T): T {
    return a > b ? a : b;
}

// Classe generica
class Stack<T> {
    private items: T[] = [];
    push(item: T): void { this.items.push(item); }
    pop(): T | undefined { return this.items.pop(); }
    get size(): number { return this.items.length; }
}

// Generic interface
interface Repository<T, ID> {
    findById(id: ID): Promise<T | null>;
    save(entity: T): Promise<T>;
    delete(id: ID): Promise<void>;
}
```

## Utility types

```typescript
interface Utente { id: number; nome: string; email: string; eta: number; }

Partial<Utente>        // tutti i campi opzionali
Required<Utente>       // tutti i campi obbligatori
Readonly<Utente>       // tutti i campi readonly
Pick<Utente, "id" | "nome">      // solo id e nome
Omit<Utente, "email" | "eta">    // tutto tranne email ed eta
Record<string, number>            // { [key: string]: number }
Exclude<"a" | "b" | "c", "a">   // "b" | "c"
Extract<"a" | "b" | number, string> // "a" | "b"
NonNullable<string | null | undefined> // string
ReturnType<typeof fetch>
Parameters<typeof funzione>
```

## Tipi avanzati

```typescript
// Template literal types
type Evento = `on${Capitalize<string>}`;
type Route = `/api/${string}`;

// Conditional types
type NonNullable<T> = T extends null | undefined ? never : T;
type IsArray<T> = T extends any[] ? true : false;

// Mapped types
type Opzionale<T> = { [K in keyof T]?: T[K] };
type Mutabile<T> = { -readonly [K in keyof T]: T[K] };

// Infer
type UnpackPromise<T> = T extends Promise<infer R> ? R : T;
type FirstArg<T> = T extends (first: infer F, ...rest: any[]) => any ? F : never;

// Satisfies (TS 4.9+)
const palette = {
    rosso: [255, 0, 0],
    verde: "#00ff00"
} satisfies Record<string, string | number[]>;
```

---

# JAVA

## Panoramica
Creato da James Gosling (Sun Microsystems, 1995). "Write once, run anywhere" tramite JVM. Tipizzazione statica forte, strettamente orientato agli oggetti. Standard nell'enterprise e Android (legacy).

## Tipi e variabili

```java
// Tipi primitivi
byte b = 127;           // 8 bit
short s = 32767;        // 16 bit
int i = 2147483647;     // 32 bit
long l = 9223372036L;   // 64 bit (suffisso L)
float f = 3.14f;        // 32 bit (suffisso f)
double d = 3.14159;     // 64 bit
char c = 'A';           // 16 bit Unicode
boolean v = true;

// Wrapper types (autoboxing/unboxing)
Integer numOggetto = 42;    // autoboxing da int
int numPrimitivo = numOggetto; // unboxing

// String (immutabile)
String s = "hello";
String formato = String.format("Nome: %s, Età: %d", nome, eta);
String moderno = "Nome: %s, Età: %d".formatted(nome, eta); // Java 15+

// StringBuilder per concatenazione efficiente
StringBuilder sb = new StringBuilder();
sb.append("ciao").append(" ").append("mondo");
String risultato = sb.toString();
```

## OOP completo

```java
// Classe con tutti i pattern comuni
public class Persona implements Comparable<Persona> {
    private final String nome;
    private int eta;
    private static int contatore = 0;

    // Costruttore
    public Persona(String nome, int eta) {
        this.nome = Objects.requireNonNull(nome, "nome non può essere null");
        this.eta = eta;
        contatore++;
    }

    // Getter/setter
    public String getNome() { return nome; }
    public int getEta() { return eta; }
    public void setEta(int eta) {
        if (eta < 0) throw new IllegalArgumentException("Età negativa");
        this.eta = eta;
    }

    @Override
    public int compareTo(Persona altra) {
        return Integer.compare(this.eta, altra.eta);
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof Persona)) return false;
        Persona altra = (Persona) obj;
        return Objects.equals(nome, altra.nome) && eta == altra.eta;
    }

    @Override
    public int hashCode() {
        return Objects.hash(nome, eta);
    }

    @Override
    public String toString() {
        return "Persona{nome='%s', eta=%d}".formatted(nome, eta);
    }
}

// Record (Java 16+) — immutable data class
record Punto(double x, double y) {
    // Compact constructor
    Punto {
        if (x < 0 || y < 0) throw new IllegalArgumentException("Coordinate negative");
    }
    double distanza() { return Math.sqrt(x*x + y*y); }
}

// Sealed classes (Java 17+)
sealed interface Forma permits Cerchio, Rettangolo, Triangolo {}
record Cerchio(double raggio) implements Forma {}
record Rettangolo(double l, double h) implements Forma {}
```

## Generics e collections

```java
// Generics
public class Coppia<A, B> {
    private final A primo;
    private final B secondo;
    public Coppia(A primo, B secondo) { this.primo=primo; this.secondo=secondo; }
    public A getPrimo() { return primo; }
}

// Collections Framework
List<String> lista = new ArrayList<>();
List<String> linked = new LinkedList<>();
List<String> immutabile = List.of("a", "b", "c"); // Java 9+

Map<String, Integer> mappa = new HashMap<>();
Map<String, Integer> ordinata = new TreeMap<>();
Map<String, Integer> immutabile = Map.of("a", 1, "b", 2);

Set<String> set = new HashSet<>();
Set<String> ordinato = new TreeSet<>();

Deque<Integer> coda = new ArrayDeque<>();
coda.push(1); // stack
coda.offer(1); // queue
```

## Stream API e Lambda

```java
import java.util.stream.*;

List<Persona> persone = /* ... */;

// Pipeline di stream
List<String> risultato = persone.stream()
    .filter(p -> p.getEta() >= 18)
    .sorted(Comparator.comparing(Persona::getNome))
    .map(Persona::getNome)
    .distinct()
    .limit(10)
    .collect(Collectors.toList());

// Collectors avanzati
Map<Boolean, List<Persona>> partizionate = persone.stream()
    .collect(Collectors.partitioningBy(p -> p.getEta() >= 18));

Map<String, Long> perCitta = persone.stream()
    .collect(Collectors.groupingBy(Persona::getCitta, Collectors.counting()));

// Reduction
OptionalInt max = IntStream.range(0, 100).filter(n -> n % 7 == 0).max();
int somma = IntStream.rangeClosed(1, 100).sum();

// Parallel stream (attenzione: non sempre più veloce)
long count = persone.parallelStream().filter(p -> p.getEta() > 30).count();
```

## Optional (evitare NullPointerException)

```java
Optional<String> nome = Optional.ofNullable(valore);

nome.isPresent()                        // ha un valore?
nome.get()                              // valore o NoSuchElementException
nome.orElse("default")                  // valore o default
nome.orElseGet(() -> computaDefault())  // lazy default
nome.orElseThrow(() -> new RuntimeException("vuoto"))
nome.map(String::toUpperCase)           // trasforma se presente
nome.filter(s -> s.length() > 3)        // filtra se presente
nome.ifPresent(System.out::println)     // esegui se presente
```

## Concorrenza

```java
// Thread base
Thread t = new Thread(() -> System.out.println("Thread!"));
t.start();

// ExecutorService
ExecutorService pool = Executors.newFixedThreadPool(4);
Future<Integer> futuro = pool.submit(() -> {
    // compito costoso
    return 42;
});
int risultato = futuro.get(); // bloccante
pool.shutdown();

// CompletableFuture (Java 8+)
CompletableFuture<String> cf = CompletableFuture
    .supplyAsync(() -> fetchDati())
    .thenApply(String::toUpperCase)
    .thenCompose(s -> CompletableFuture.supplyAsync(() -> processa(s)))
    .exceptionally(err -> "errore: " + err.getMessage());

// Virtual threads (Java 21+)
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    for (int i = 0; i < 10000; i++) {
        executor.submit(() -> { /* task */ });
    }
}
```

---

# C e C++

## C — il padre di tutti

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Puntatori — il concetto chiave di C
int x = 42;
int *ptr = &x;       // ptr contiene l'indirizzo di x
printf("%d", *ptr);  // dereferenziazione: legge il valore all'indirizzo
*ptr = 100;          // modifica x tramite puntatore

// Array e puntatori
int arr[] = {1, 2, 3, 4, 5};
int *p = arr;        // arr decade a puntatore al primo elemento
printf("%d", *(p+2)); // arr[2] = 3

// Allocazione dinamica
int *numeri = (int*)malloc(10 * sizeof(int));
if (!numeri) { /* gestisci errore */ }
numeri[0] = 42;
free(numeri);  // OBBLIGATORIO — altrimenti memory leak

// Stringhe (array di char terminato da '\0')
char nome[50] = "Alice";
char *copia = strdup("copia");  // alloca e copia
strlen(nome);                    // lunghezza senza '\0'
strcpy(dest, src);               // copia (pericoloso, usa strncpy)
strcmp(a, b);                    // confronta: 0 se uguali

// Strutture
typedef struct {
    char nome[50];
    int eta;
} Persona;

Persona p = {"Alice", 30};
Persona *pp = &p;
printf("%s", pp->nome);  // accesso via puntatore

// File I/O
FILE *f = fopen("file.txt", "r");
if (f) {
    char riga[256];
    while (fgets(riga, sizeof(riga), f)) {
        printf("%s", riga);
    }
    fclose(f);
}
```

## C++ — OOP su C

```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <algorithm>
#include <string>

// RAII — Resource Acquisition Is Initialization
class File {
    FILE* handle;
public:
    explicit File(const std::string& path, const std::string& mode)
        : handle(fopen(path.c_str(), mode.c_str())) {
        if (!handle) throw std::runtime_error("Impossibile aprire file");
    }
    ~File() { if (handle) fclose(handle); }  // cleanup automatico
    // Disabilita copia (rule of 5)
    File(const File&) = delete;
    File& operator=(const File&) = delete;
};

// Smart pointers — gestione memoria senza free manuale
std::unique_ptr<int> unico = std::make_unique<int>(42);  // ownership esclusiva
std::shared_ptr<int> condiviso = std::make_shared<int>(42); // reference counting
std::weak_ptr<int> debole = condiviso; // no ownership (evita circular ref)

// Templates (generics in C++)
template<typename T>
T massimo(T a, T b) { return a > b ? a : b; }

template<typename Container>
void stampa(const Container& c) {
    for (const auto& elem : c) std::cout << elem << " ";
}

// STL — Standard Template Library
std::vector<int> v = {3, 1, 4, 1, 5, 9};
std::sort(v.begin(), v.end());
std::reverse(v.begin(), v.end());
auto it = std::find(v.begin(), v.end(), 4);
std::transform(v.begin(), v.end(), v.begin(), [](int x){ return x*2; });

// Ranges (C++20)
auto risultato = v | std::views::filter([](int x){ return x > 3; })
                   | std::views::transform([](int x){ return x*2; });

// Lambda
auto somma = [](int a, int b) -> int { return a + b; };
auto cattura = [x, &y]() { return x + y; }; // cattura x per valore, y per ref

// Move semantics (efficienza)
std::string testo = "grande stringa...";
std::string altra = std::move(testo); // testo è ora in stato valido ma non specificato
```

---

# RUST

## Panoramica
Creato da Mozilla (Graydon Hoare, 2010). Linguaggio di sistemi che garantisce memory safety senza garbage collector. Stack: ownership + borrowing + lifetimes. Performance = C/C++.

## Ownership — il concetto rivoluzionario

```rust
fn main() {
    // Ogni valore ha un owner
    let s1 = String::from("hello");

    // Move: s1 trasferito a s2, s1 non più valido
    let s2 = s1;
    // println!("{}", s1); // ERRORE di compilazione

    // Clone: copia profonda esplicita
    let s3 = s2.clone();
    println!("{} {}", s2, s3); // entrambi validi

    // Copy: tipi primitivi si copiano automaticamente
    let x = 5;
    let y = x;
    println!("{} {}", x, y); // entrambi validi
}

// Borrowing — prestare riferimenti
fn lunghezza(s: &String) -> usize {  // & = immutable borrow
    s.len()
} // s non viene deallocato, solo il riferimento finisce

fn aggiungi(s: &mut String) {        // &mut = mutable borrow
    s.push_str(" mondo");
}

let mut s = String::from("hello");
aggiungi(&mut s);           // un solo mutable borrow alla volta
let len = lunghezza(&s);    // poi borrow immutabile

// Slice — riferimento a parte di un array/stringa
let s = String::from("hello world");
let hello = &s[0..5];  // &str, non String
```

## Lifetimes

```rust
// Il compilatore verifica che i riferimenti siano sempre validi
fn piu_lungo<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
// 'a = entrambi gli input e l'output hanno la stessa lifetime

struct Importante<'a> {
    parte: &'a str,  // deve vivere almeno quanto la struct
}
```

## Tipi, Struct, Enum

```rust
// Struct
#[derive(Debug, Clone, PartialEq)]
struct Rettangolo {
    larghezza: f64,
    altezza: f64,
}

impl Rettangolo {
    fn new(l: f64, h: f64) -> Self {
        Self { larghezza: l, altezza: h }
    }
    fn area(&self) -> f64 { self.larghezza * self.altezza }
    fn scala(&mut self, fattore: f64) {
        self.larghezza *= fattore;
        self.altezza *= fattore;
    }
}

// Enum con dati (molto potente in Rust)
enum Forma {
    Cerchio(f64),
    Rettangolo(f64, f64),
    Triangolo { base: f64, altezza: f64 },
}

impl Forma {
    fn area(&self) -> f64 {
        match self {
            Forma::Cerchio(r) => std::f64::consts::PI * r * r,
            Forma::Rettangolo(l, h) => l * h,
            Forma::Triangolo { base, altezza } => 0.5 * base * altezza,
        }
    }
}

// Option<T> invece di null
let valore: Option<i32> = Some(42);
let niente: Option<i32> = None;

let x = valore.unwrap_or(0);        // 42 o default
let y = valore.map(|v| v * 2);      // Some(84)
if let Some(n) = valore { println!("{}", n); }

// Result<T, E> invece di eccezioni
use std::fs;
fn leggi(path: &str) -> Result<String, std::io::Error> {
    fs::read_to_string(path)
}

match leggi("file.txt") {
    Ok(contenuto) => println!("{}", contenuto),
    Err(e) => eprintln!("Errore: {}", e),
}

// Operatore ? — propagazione errori
fn leggi_e_processa(path: &str) -> Result<usize, std::io::Error> {
    let contenuto = fs::read_to_string(path)?; // propaga Err automaticamente
    Ok(contenuto.len())
}
```

## Traits (interfacce di Rust)

```rust
trait Stampabile {
    fn stampa(&self);
    fn descrizione(&self) -> String {   // default implementation
        String::from("oggetto stampabile")
    }
}

impl Stampabile for Rettangolo {
    fn stampa(&self) {
        println!("{}x{}", self.larghezza, self.altezza);
    }
}

// Trait bounds (generics con constraints)
fn stampa_tutto<T: Stampabile + std::fmt::Debug>(item: &T) {
    item.stampa();
    println!("{:?}", item);
}

// Trait objects (dynamic dispatch)
fn crea_forma(tipo: &str) -> Box<dyn Stampabile> {
    match tipo {
        "rettangolo" => Box::new(Rettangolo::new(3.0, 4.0)),
        _ => panic!("tipo sconosciuto"),
    }
}
```

---

# GO (GOLANG)

## Panoramica
Creato da Google (Ken Thompson, Rob Pike, Robert Griesemer, 2009). Semplicità sopra tutto. Concorrenza built-in con goroutine. Compilato in binario singolo. Docker e Kubernetes sono scritti in Go.

## Basi del linguaggio

```go
package main

import (
    "fmt"
    "errors"
    "strings"
    "strconv"
)

// Variabili
var nome string = "Alice"  // esplicito
eta := 30                  // := inferisce il tipo (solo in funzioni)
const PI = 3.14159

// Tipi
var numeri []int = []int{1, 2, 3}     // slice
mappa := map[string]int{"a": 1}       // map
tupla := struct{ X, Y int }{1, 2}     // struct anonima

// Multiple return values
func dividi(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("divisione per zero")
    }
    return a / b, nil
}

risultato, err := dividi(10, 3)
if err != nil {
    fmt.Println("Errore:", err)
    return
}
fmt.Printf("%.2f\n", risultato)

// Named return values
func stats(numeri []int) (min, max, somma int) {
    min, max = numeri[0], numeri[0]
    for _, n := range numeri {
        if n < min { min = n }
        if n > max { max = n }
        somma += n
    }
    return  // naked return
}
```

## Struct e interfacce

```go
type Persona struct {
    Nome string
    Eta  int
    indirizzo string  // minuscolo = non esportato (privato)
}

// Metodi
func (p Persona) Saluta() string {
    return fmt.Sprintf("Ciao, sono %s", p.Nome)
}

func (p *Persona) Compleanno() {  // pointer receiver per modificare
    p.Eta++
}

// Embedding (composizione invece di ereditarietà)
type Dipendente struct {
    Persona  // tutti i metodi e campi di Persona
    Azienda string
}

// Interfacce implicite
type Parlante interface {
    Parla() string
}

type Cane struct{ Nome string }
func (c Cane) Parla() string { return "Bau!" }

// Cane implementa Parlante automaticamente
func faiParlare(p Parlante) {
    fmt.Println(p.Parla())
}
```

## Goroutine e Channel

```go
// Goroutine — thread ultra-leggero
go func() {
    fmt.Println("Eseguito in goroutine")
}()

// Channel — comunicazione tra goroutine
ch := make(chan int)           // unbuffered
ch := make(chan int, 10)       // buffered (non bloccante fino a 10)

go func() { ch <- 42 }()      // invia
valore := <-ch                 // ricevi (bloccante)

// Select — multiplexing su channel
select {
case v := <-ch1:
    fmt.Println("da ch1:", v)
case v := <-ch2:
    fmt.Println("da ch2:", v)
case ch3 <- dati:
    fmt.Println("inviato a ch3")
case <-time.After(1 * time.Second):
    fmt.Println("timeout")
default:
    fmt.Println("nessuno pronto")
}

// Pattern: worker pool
func workerPool(n int, lavori <-chan int, risultati chan<- int) {
    var wg sync.WaitGroup
    for i := 0; i < n; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := range lavori {
                risultati <- j * j
            }
        }()
    }
    go func() {
        wg.Wait()
        close(risultati)
    }()
}
```

---

# KOTLIN

## Panoramica
Creato da JetBrains (2011), linguaggio ufficiale Google per Android (2017). 100% interoperabile con Java. Coroutine per concorrenza. Null safety built-in.

```kotlin
// Null safety
var nome: String = "Alice"        // non-nullable
var cognome: String? = null       // nullable

val lunghezza = cognome?.length   // safe call — null se cognome è null
val len = cognome?.length ?: 0    // Elvis operator — default se null
val lUnsafe = cognome!!.length    // non-null assertion — NPE se null

// Extension functions
fun String.isPalindromic() = this == this.reversed()
fun Int.isEven() = this % 2 == 0

// Data class
data class Utente(
    val id: Int,
    val nome: String,
    val email: String? = null
)
val alice = Utente(1, "Alice")
val aliceMail = alice.copy(email = "alice@example.com")
val (id, nome) = alice  // destructuring

// Sealed class
sealed class Risultato<out T> {
    data class Successo<T>(val dati: T) : Risultato<T>()
    data class Errore(val eccezione: Exception) : Risultato<Nothing>()
    object Caricamento : Risultato<Nothing>()
}

// Coroutine
import kotlinx.coroutines.*

suspend fun fetchDati(): String {
    delay(1000)  // non blocca il thread
    return "dati"
}

fun main() = runBlocking {
    val job = launch { fetchDati() }
    val deferred = async { fetchDati() }
    val risultato = deferred.await()
    job.join()

    // Parallel
    val (a, b) = coroutineScope {
        val da = async { fetchDati() }
        val db = async { fetchDati() }
        Pair(da.await(), db.await())
    }
}
```

---

# SWIFT

## Panoramica
Creato da Apple (Chris Lattner, 2014). Linguaggio nativo per iOS, macOS, watchOS, tvOS. Protocol-oriented programming. Optionals per null safety.

```swift
// Optionals
var nome: String? = nil
let lunghezza = nome?.count ?? 0  // Optional chaining + nil coalescing

// Guard — early exit
func processa(_ valore: String?) {
    guard let s = valore, !s.isEmpty else {
        print("valore non valido")
        return
    }
    print(s.uppercased())  // s è garantito non-nil qui
}

// Enum con valori associati
enum Risultato<T> {
    case successo(T)
    case errore(String)
}

// Protocol (come interface)
protocol Descrivibile {
    var descrizione: String { get }
    func stampa()
}

extension Descrivibile {
    func stampa() { print(descrizione) }  // default implementation
}

// Struct con protocol
struct Punto: Descrivibile, Equatable {
    let x, y: Double
    var descrizione: String { "(\(x), \(y))" }
}

// SwiftUI (esempio base)
import SwiftUI

struct ContentView: View {
    @State private var contatore = 0

    var body: some View {
        VStack {
            Text("Contatore: \(contatore)")
                .font(.largeTitle)
            Button("Incrementa") {
                contatore += 1
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}
```

---

# HTML e CSS

## HTML — struttura

```html
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pagina</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <!-- Semantica -->
    <header>...</header>
    <nav>...</nav>
    <main>
        <article>...</article>
        <aside>...</aside>
    </main>
    <footer>...</footer>

    <!-- Form -->
    <form action="/submit" method="post">
        <label for="nome">Nome:</label>
        <input type="text" id="nome" name="nome" required>
        <input type="email" placeholder="email@esempio.it">
        <input type="number" min="0" max="120">
        <textarea rows="4"></textarea>
        <select>
            <option value="a">Opzione A</option>
        </select>
        <button type="submit">Invia</button>
    </form>
</body>
</html>
```

## CSS — presentazione

```css
/* Selettori */
div { }          /* elemento */
.classe { }      /* classe */
#id { }          /* id */
div.classe { }   /* elemento con classe */
div > p { }      /* figlio diretto */
div p { }        /* discendente */
a:hover { }      /* pseudo-classe */
p::first-line { }/* pseudo-elemento */
[attr="val"] { } /* attributo */

/* Box model */
.box {
    width: 300px;
    height: 200px;
    padding: 20px;          /* interno */
    border: 1px solid #333;
    margin: 10px auto;      /* esterno — auto centra orizzontalmente */
    box-sizing: border-box; /* padding incluso in width/height */
}

/* Flexbox */
.container {
    display: flex;
    flex-direction: row;        /* row | column */
    justify-content: center;    /* asse principale */
    align-items: center;        /* asse secondario */
    flex-wrap: wrap;
    gap: 16px;
}
.item { flex: 1; }             /* cresci uguale */

/* Grid */
.grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    grid-template-rows: auto;
    gap: 16px;
}
.item-grande {
    grid-column: span 2;
    grid-row: span 2;
}

/* Variabili CSS */
:root {
    --colore-primario: #7B61FF;
    --spaziatura: 16px;
    --raggio: 8px;
}
.button { background: var(--colore-primario); }

/* Media query */
@media (max-width: 768px) {
    .grid { grid-template-columns: 1fr; }
}

/* Animazioni */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animato { animation: fadeIn 0.3s ease-out; }
```

---

# SQL

## Basi e sintassi

```sql
-- DDL (Data Definition Language)
CREATE TABLE utenti (
    id          SERIAL PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    eta         INTEGER CHECK (eta >= 0),
    creato_il   TIMESTAMP DEFAULT NOW(),
    attivo      BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_utenti_email ON utenti(email);

ALTER TABLE utenti ADD COLUMN telefono VARCHAR(20);
DROP TABLE IF EXISTS tabella_vecchia;

-- DML (Data Manipulation Language)
INSERT INTO utenti (nome, email, eta) VALUES
    ('Alice', 'alice@mail.it', 30),
    ('Bob', 'bob@mail.it', 25);

UPDATE utenti SET eta = 31 WHERE nome = 'Alice';

DELETE FROM utenti WHERE attivo = FALSE;

-- DQL (Data Query Language)
SELECT nome, email
FROM utenti
WHERE eta >= 18
  AND attivo = TRUE
ORDER BY nome ASC
LIMIT 10 OFFSET 20;

-- JOIN
SELECT o.id, u.nome, o.totale
FROM ordini o
INNER JOIN utenti u ON o.utente_id = u.id
LEFT JOIN pagamenti p ON o.id = p.ordine_id
WHERE p.id IS NULL;  -- ordini non pagati

-- Aggregazione
SELECT citta, COUNT(*) as totale, AVG(eta) as eta_media
FROM utenti
GROUP BY citta
HAVING COUNT(*) > 10
ORDER BY totale DESC;

-- Subquery
SELECT nome FROM utenti
WHERE id IN (
    SELECT utente_id FROM ordini WHERE totale > 100
);

-- CTE (Common Table Expression)
WITH utenti_attivi AS (
    SELECT * FROM utenti WHERE attivo = TRUE
),
utenti_adulti AS (
    SELECT * FROM utenti_attivi WHERE eta >= 18
)
SELECT nome, email FROM utenti_adulti;

-- Window functions
SELECT
    nome,
    eta,
    AVG(eta) OVER (PARTITION BY citta) as media_citta,
    ROW_NUMBER() OVER (ORDER BY eta DESC) as classifica
FROM utenti;

-- Transazioni
BEGIN;
    UPDATE conti SET saldo = saldo - 100 WHERE id = 1;
    UPDATE conti SET saldo = saldo + 100 WHERE id = 2;
COMMIT;  -- o ROLLBACK in caso di errore
```

---

# BASH

## Scripting fondamentale

```bash
#!/bin/bash
set -euo pipefail  # exit on error, undefined var, pipe fail

# Variabili
NOME="Alice"
ETA=30
echo "Nome: $NOME, Età: $ETA"

# Variabili speciali
echo "$0"   # nome script
echo "$1"   # primo argomento
echo "$@"   # tutti gli argomenti
echo "$#"   # numero argomenti
echo "$?"   # exit code ultimo comando
echo "$$"   # PID processo corrente

# Stringhe
lunghezza=${#NOME}           # lunghezza
maiuscolo=${NOME^^}          # uppercase
minuscolo=${NOME,,}          # lowercase
sottostirnga=${NOME:0:3}     # slice [0:3]
sostituzione=${NOME/l/L}     # prima occorrenza
tutta=${NOME//l/L}           # tutte le occorrenze
default=${VAR:-"predefinito"} # usa default se VAR non definita

# Condizionali
if [ "$ETA" -ge 18 ]; then
    echo "adulto"
elif [ "$ETA" -eq 0 ]; then
    echo "neonato"
else
    echo "minore"
fi

# Test di file
[ -f "file.txt" ] && echo "file esiste"
[ -d "cartella" ] && echo "directory esiste"
[ -r "file" ] && echo "leggibile"
[ -z "$VAR" ] && echo "variabile vuota"
[ -n "$VAR" ] && echo "variabile non vuota"

# Cicli
for i in {1..10}; do echo $i; done
for f in *.txt; do echo "File: $f"; done
for arg in "$@"; do echo "$arg"; done

while read -r riga; do
    echo "Riga: $riga"
done < file.txt

# Funzioni
backup() {
    local sorgente="$1"
    local destinazione="$2"
    cp -r "$sorgente" "$destinazione/backup_$(date +%Y%m%d_%H%M%S)"
    echo "Backup completato"
}

backup "/dati" "/backup"

# Process substitution e piping
cat file.txt | grep "pattern" | sort | uniq -c | sort -rn | head -10

# Cattura output
output=$(ls -la)
numero_file=$(ls | wc -l)

# Array
arr=("a" "b" "c")
echo "${arr[0]}"          # primo elemento
echo "${arr[@]}"          # tutti
echo "${#arr[@]}"         # lunghezza
arr+=("d")               # append

# Heredoc
cat <<EOF > output.txt
Riga 1
Riga 2 con $NOME
EOF
```

---

# CONCETTI TRASVERSALI

## Design Patterns fondamentali

### Creazionali
**Singleton** — una sola istanza in tutta l'applicazione
```python
class Singleton:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

**Factory** — crea oggetti senza specificare la classe concreta
```python
def crea_animale(tipo: str) -> Animale:
    if tipo == "cane": return Cane()
    if tipo == "gatto": return Gatto()
    raise ValueError(f"Tipo sconosciuto: {tipo}")
```

**Builder** — costruzione passo-passo di oggetti complessi
```python
class QueryBuilder:
    def __init__(self): self._query = []
    def select(self, *cols): self._query.append(f"SELECT {','.join(cols)}"); return self
    def from_(self, t): self._query.append(f"FROM {t}"); return self
    def where(self, c): self._query.append(f"WHERE {c}"); return self
    def build(self): return " ".join(self._query)
```

### Strutturali
**Decorator** — aggiunge comportamento senza modificare la classe
**Adapter** — converte interfaccia incompatibile
**Facade** — interfaccia semplificata per sistema complesso

### Comportamentali
**Observer** — notifica automatica agli iscritti quando cambia stato
**Strategy** — intercambia algoritmi a runtime
**Command** — incapsula richiesta come oggetto (undo/redo)

## Clean Code — principi

**SOLID:**
- **S**ingle Responsibility: ogni classe/funzione fa una cosa sola
- **O**pen/Closed: aperto per estensione, chiuso per modifica
- **L**iskov Substitution: le sottoclassi devono sostituire le superclassi
- **I**nterface Segregation: interfacce specifiche, non generiche
- **D**ependency Inversion: dipendi da astrazioni, non da implementazioni

**DRY** — Don't Repeat Yourself: ogni conoscenza ha una rappresentazione unica
**KISS** — Keep It Simple, Stupid: la semplicità è preferibile alla complessità
**YAGNI** — You Aren't Gonna Need It: non aggiungere funzionalità non richieste

## Testing

```python
# pytest
def test_somma():
    assert somma(2, 3) == 5
    assert somma(-1, 1) == 0
    assert somma(0, 0) == 0

def test_errore():
    with pytest.raises(ZeroDivisionError):
        1 / 0

# Mock
from unittest.mock import Mock, patch

def test_con_mock():
    db = Mock()
    db.trova.return_value = {"id": 1, "nome": "Alice"}
    risultato = servizio.ottieni_utente(1, db)
    db.trova.assert_called_once_with(1)

# Test parametrizzato
@pytest.mark.parametrize("input,expected", [
    (2, 4), (3, 9), (0, 0), (-2, 4)
])
def test_quadrato(input, expected):
    assert quadrato(input) == expected
```

## Algoritmi fondamentali

```python
# Ricerca binaria — O(log n)
def ricerca_binaria(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: left = mid + 1
        else: right = mid - 1
    return -1

# Quicksort — O(n log n) medio
def quicksort(arr):
    if len(arr) <= 1: return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + mid + quicksort(right)

# BFS su grafo
from collections import deque
def bfs(grafo, start):
    visitati, coda = set(), deque([start])
    visitati.add(start)
    while coda:
        nodo = coda.popleft()
        for vicino in grafo[nodo]:
            if vicino not in visitati:
                visitati.add(vicino)
                coda.append(vicino)
```
