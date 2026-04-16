# Matematica — Concetti Fondamentali

## Aritmetica e algebra di base

### Operazioni fondamentali
- **Addizione**: a + b (commutativa, associativa)
- **Sottrazione**: a − b
- **Moltiplicazione**: a × b (commutativa, associativa, distributiva)
- **Divisione**: a ÷ b (b ≠ 0)

**Priorità delle operazioni (PEMDAS/BODMAS):**
1. Parentesi
2. Esponenti
3. Moltiplicazione e Divisione (da sinistra a destra)
4. Addizione e Sottrazione (da sinistra a destra)

Esempio: 2 + 3 × 4 = 2 + 12 = 14 (NON 20)

### Frazioni
- **Forma**: numeratore/denominatore
- **Semplificazione**: dividere entrambi per il MCD
- **Addizione**: mettere a denominatore comune → a/b + c/d = (ad + bc)/(bd)
- **Moltiplicazione**: a/b × c/d = ac/bd
- **Divisione**: a/b ÷ c/d = a/b × d/c

### Percentuali
- X% di N = (X/100) × N
- Aumento del X%: N × (1 + X/100)
- Riduzione del X%: N × (1 − X/100)
- Per trovare la percentuale di variazione: ((nuovo − vecchio) / vecchio) × 100

### Potenze e radici
- a^n = a × a × ... × a (n volte)
- a^0 = 1 (per a ≠ 0)
- a^(-n) = 1/a^n
- a^(m/n) = ⁿ√(a^m)
- √a × √b = √(ab)
- Proprietà: a^m × a^n = a^(m+n) — a^m / a^n = a^(m−n) — (a^m)^n = a^(mn)

### Logaritmi
- log_b(x) = y significa b^y = x
- log(x) = log_10(x) — logaritmo decimale
- ln(x) = log_e(x) — logaritmo naturale (e ≈ 2.718)
- **Proprietà:**
  - log(ab) = log(a) + log(b)
  - log(a/b) = log(a) − log(b)
  - log(a^n) = n × log(a)
  - log_b(b) = 1 — log_b(1) = 0

---

## Algebra

### Equazioni di primo grado
Forma: ax + b = 0 → x = −b/a

Esempio: 2x + 6 = 0 → x = −3

**Sistemi di equazioni:**
```
2x + y = 5
x − y = 1
```
Metodo di sostituzione: dalla seconda, x = 1 + y → 2(1+y) + y = 5 → y = 1, x = 2

### Equazioni di secondo grado
Forma: ax² + bx + c = 0

**Formula quadratica:** x = (−b ± √(b² − 4ac)) / 2a

**Discriminante Δ = b² − 4ac:**
- Δ > 0: due soluzioni reali distinte
- Δ = 0: una soluzione reale doppia
- Δ < 0: nessuna soluzione reale (due complesse)

**Esempio:** x² − 5x + 6 = 0 → Δ = 25 − 24 = 1 → x = (5 ± 1)/2 → x₁ = 3, x₂ = 2

### Prodotti notevoli
- (a + b)² = a² + 2ab + b²
- (a − b)² = a² − 2ab + b²
- (a + b)(a − b) = a² − b²
- (a + b)³ = a³ + 3a²b + 3ab² + b³

### Disequazioni
- ax + b > 0 → x > −b/a (se a > 0), x < −b/a (se a < 0)
- Attenzione: moltiplicare o dividere per un numero negativo **inverte** il verso

### Funzioni
Una funzione f: A → B associa ad ogni elemento di A uno e un solo elemento di B.
- **Dominio**: insieme dei valori di x ammissibili
- **Codominio**: insieme dei valori possibili di f(x)
- **Immagine**: insieme dei valori effettivamente assunti
- **Funzione inversa**: f⁻¹ tale che f⁻¹(f(x)) = x

**Tipi di funzione:**
| Tipo | Formula | Caratteristica |
|---|---|---|
| Costante | f(x) = k | Retta orizzontale |
| Lineare | f(x) = mx + b | Retta con pendenza m |
| Quadratica | f(x) = ax² + bx + c | Parabola |
| Esponenziale | f(x) = a^x | Crescita/decrescita rapida |
| Logaritmica | f(x) = log(x) | Inversa dell'esponenziale |
| Trigonometrica | sin, cos, tan | Periodiche |

---

## Geometria

### Figure piane
| Figura | Perimetro | Area |
|---|---|---|
| Quadrato (lato a) | 4a | a² |
| Rettangolo (b×h) | 2(b+h) | b×h |
| Triangolo | a+b+c | (base × altezza)/2 |
| Cerchio (raggio r) | 2πr | πr² |
| Trapezio | a+b+c+d | ((b₁+b₂)×h)/2 |

### Figure solide
| Solido | Volume | Superficie |
|---|---|---|
| Cubo (lato a) | a³ | 6a² |
| Parallelepipedo (l,w,h) | l×w×h | 2(lw+lh+wh) |
| Sfera (raggio r) | (4/3)πr³ | 4πr² |
| Cilindro (r,h) | πr²h | 2πr(r+h) |
| Cono (r,h) | (1/3)πr²h | πr(r+l), l=√(r²+h²) |

### Teorema di Pitagora
In un triangolo rettangolo: a² + b² = c²
(a, b = cateti; c = ipotenusa)

**Terne pitagoriche comuni:** (3,4,5) — (5,12,13) — (8,15,17) — (7,24,25)

### Trigonometria
In un triangolo rettangolo con angolo θ:
- sin(θ) = opposto/ipotenusa
- cos(θ) = adiacente/ipotenusa
- tan(θ) = opposto/adiacente = sin/cos

**Valori fondamentali:**
| Angolo | 0° | 30° | 45° | 60° | 90° |
|---|---|---|---|---|---|
| sin | 0 | 1/2 | √2/2 | √3/2 | 1 |
| cos | 1 | √3/2 | √2/2 | 1/2 | 0 |
| tan | 0 | √3/3 | 1 | √3 | ∞ |

**Identità fondamentali:**
- sin²(θ) + cos²(θ) = 1
- tan(θ) = sin(θ)/cos(θ)
- sin(2θ) = 2sin(θ)cos(θ)
- cos(2θ) = cos²(θ) − sin²(θ)

---

## Analisi matematica

### Limiti
Il limite di f(x) per x → a è L se f(x) si avvicina a L quanto si vuole avvicinando x ad a.

**Notazione:** lim(x→a) f(x) = L

**Limiti notevoli:**
- lim(x→0) sin(x)/x = 1
- lim(x→0) (1 + x)^(1/x) = e
- lim(x→∞) (1 + 1/x)^x = e
- lim(x→∞) ln(x)/x = 0

**Forme indeterminate:** 0/0, ∞/∞, 0×∞, ∞−∞, 0^0, 1^∞, ∞^0

### Derivate
La derivata f'(x) misura la velocità di cambiamento di f in un punto. Geometricamente è la pendenza della tangente alla curva.

**Derivate fondamentali:**
| Funzione | Derivata |
|---|---|
| c (costante) | 0 |
| x^n | n·x^(n−1) |
| e^x | e^x |
| ln(x) | 1/x |
| sin(x) | cos(x) |
| cos(x) | −sin(x) |
| tan(x) | 1/cos²(x) |

**Regole di derivazione:**
- Somma: (f + g)' = f' + g'
- Prodotto: (f·g)' = f'g + fg'
- Quoziente: (f/g)' = (f'g − fg') / g²
- Catena (chain rule): (f(g(x)))' = f'(g(x)) · g'(x)

**Applicazioni:**
- Massimi e minimi: f'(x) = 0 (punto stazionario), f''(x) < 0 (massimo), f''(x) > 0 (minimo)
- Tangente alla curva in x₀: y − f(x₀) = f'(x₀)(x − x₀)

### Integrali
L'integrale definito ∫[a,b] f(x)dx rappresenta l'area sotto la curva di f tra a e b.

**Integrali fondamentali:**
| Funzione | Integrale |
|---|---|
| x^n (n≠−1) | x^(n+1)/(n+1) + C |
| 1/x | ln|x| + C |
| e^x | e^x + C |
| sin(x) | −cos(x) + C |
| cos(x) | sin(x) + C |

**Teorema fondamentale del calcolo:**
∫[a,b] f(x)dx = F(b) − F(a), dove F' = f

---

## Statistica e probabilità

### Statistica descrittiva

**Misure di posizione (dati: x₁, x₂, ..., xₙ):**
- **Media aritmetica**: μ = (x₁ + x₂ + ... + xₙ) / n
- **Mediana**: valore centrale dopo aver ordinato i dati
- **Moda**: valore che appare più frequentemente

**Misure di dispersione:**
- **Varianza**: σ² = Σ(xᵢ − μ)² / n
- **Deviazione standard**: σ = √(varianza) — misura quanto i dati si discostano dalla media
- **Range**: max − min

**Esempio:** dati = [2, 4, 4, 6, 8]
- Media = 24/5 = 4.8
- Mediana = 4 (valore centrale)
- Varianza = [(2−4.8)² + (4−4.8)² + (4−4.8)² + (6−4.8)² + (8−4.8)²]/5 = 3.76
- Dev. standard = √3.76 ≈ 1.94

### Probabilità
La probabilità di un evento A è P(A) = casi favorevoli / casi totali (per eventi equiprobabili).

**Proprietà:**
- 0 ≤ P(A) ≤ 1
- P(spazio campionario) = 1
- P(non A) = 1 − P(A)
- P(A o B) = P(A) + P(B) − P(A e B)
- P(A e B) = P(A) × P(B) se A e B sono indipendenti

**Distribuzione normale (Gaussiana):**
- Simmetrica attorno alla media μ
- 68% dei dati entro ±1σ dalla media
- 95% dei dati entro ±2σ dalla media
- 99.7% dei dati entro ±3σ dalla media

**Probabilità condizionata:**
P(A|B) = P(A e B) / P(B) — probabilità di A dato che B è avvenuto

**Teorema di Bayes:**
P(A|B) = P(B|A) × P(A) / P(B)

### Combinatoria
- **Permutazioni** di n oggetti: n! = n × (n−1) × ... × 1
- **Permutazioni di k tra n**: P(n,k) = n! / (n−k)!
- **Combinazioni di k tra n** (senza ripetizione): C(n,k) = n! / (k! × (n−k)!)

---

## Algebra lineare (base)

### Vettori
Un vettore ha modulo (lunghezza) e direzione.
- v = (x, y) in 2D; v = (x, y, z) in 3D
- Modulo: |v| = √(x² + y²)
- Addizione: (a,b) + (c,d) = (a+c, b+d)
- Prodotto scalare: (a,b)·(c,d) = ac + bd

### Matrici
Una matrice m×n ha m righe e n colonne.

**Operazioni:**
- Addizione: elemento per elemento (stessa dimensione)
- Moltiplicazione scalare: k × M = scala ogni elemento
- Prodotto tra matrici: A(m×n) × B(n×p) = C(m×p)

**Matrice identità I:** 1 sulla diagonale, 0 altrove. A × I = A.

**Determinante (matrice 2×2):**
det([[a,b],[c,d]]) = ad − bc

Il determinante è 0 se e solo se la matrice è singolare (non invertibile).

**Applicazioni:** sistemi lineari, trasformazioni geometriche, machine learning (regressione, reti neurali).

---

## Logica matematica

### Connettivi logici
| Simbolo | Nome | Significato |
|---|---|---|
| ¬ | NOT | negazione |
| ∧ | AND | congiunzione |
| ∨ | OR | disgiunzione |
| → | IMPLICA | se...allora |
| ↔ | IFF | se e solo se |

### Quantificatori
- ∀x P(x) — "per ogni x, P(x) è vera"
- ∃x P(x) — "esiste almeno un x per cui P(x) è vera"

### Tecniche di dimostrazione
- **Dimostrazione diretta**: A → B, si assume A e si dimostra B
- **Dimostrazione per contraddizione (reductio ad absurdum)**: si assume ¬B e si arriva a una contraddizione
- **Dimostrazione per induzione**: si dimostra il caso base, poi si dimostra che se vale per n vale per n+1
- **Dimostrazione per controesempio**: per negare ∀x P(x), basta trovare un x per cui P(x) è falsa
