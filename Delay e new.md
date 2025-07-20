---
title: "Delay"
---

# 1. Indice

- [1. Indice](#1-indice)
- [2. Delay](#2-delay)
	- [2.1. Implementazione del nucleo](#21-implementazione-del-nucleo)
- [3. new](#3-new)

<div class="stop"></div>

# 2. Delay

Una funzionalità utile per chi programma è la possibilità di mettere in pausa o comunque poter tener traccia del tempo che passa durante l'esecuzione di un programma.
Ad esempio, in `Unix` esiste la funzione `sleep(x)` che un processo può invocare per "andare a dormire" per `x` secondi.

Quando un processo sta "dormendo" è a tutti gli effetti `bloccato`, ovvero in attesa di un evento che lo sblocchi. In questo caso l'evento è proprio il passaggio del tempo richiesto.

Per realizzare questa funzionalità, il metodo più semplice è quello di impostare un _timer_ affinché venga inviata una richiesta di interruzione con **periodo fisso**.
Questa è la soluzione che attuiamo nel nostro sistema, utilizzando il `timer 0` del _PC AT_, e programmandolo in modo che invii una richiesta ogni `50ms`.

Forniamo inoltre una _primitiva_ `void delay(natl n)` tramite la quale un processo può chiedere di essere sospeso per `n` **cicli del timer**.

La primitiva inserisce il processo in una _coda di **processi sospesi**_, salvando il valore di `n`.
Chiamiamo `driver` (del timer) la _routine_ che va in esecuzione ogni volta che il timer invia una richiesta di interruzione.

Il `driver` dovrà quindi occuparsi di:
- Decrementare `n` opportunamente
- Risvegliare i processi in attesa quando il loro `n == 0`, inserendoli in _coda `pronti`_.

Per capire come vengono gestite le strutture dati che si occupano di questo processo nel nostro sistema, supponiamo di avere tanti processi sospesi `Pi`, ognuno con `ni` cicli di attesa $(0 \le i \le k)$.

Se `k` fosse molto grande, andare a modificare tutti i singoli `ni` risulterebbe in un operazione molto costosa, poiché richiederebbe che il `driver` debba decrementare **tutti i `k` contatori** ad ogni interruzione del timer.

Operativamente quello che facciamo è quindi diverso:
- Manteniamo i processi in attesa in una lista **ordinata** per cicli di attesa crescenti $n_1 \le ... \le n_k$
- Per ogni processo non salviamo il numero di cicli totali che deve attendere, ma **quanti cicli in più rispetto al precedente**.

In altre parole, l'elemento in cima alla lista $r_1$ memorizza $n_1$, gli elementi $r_i$ con $(1 < i \le k)$ memorizzeranno:&emsp;$n_i - n_{i-1}$.

In questo modo il `driver` deve occuparsi di decrementare **_solo l'elemento in testa alla lista_**.
Quando questo elemento avrà il contatore a $0$, allora sposteremo i primi $k$ elementi con contatore nullo nella lista `pronti`, reinserendovi anche il processo in `esecuzione`, per poi chiamare lo `schedulatore()`.

Facciamo un esempio:
<div class="grid2">
<div class="">

```cpp
// P1
delay(10);		// P1 inserito come primo con t = 10
// P2
delay(15);		// P2 inserito come secondo con t = 15 - 10 = 5
// P3
delay(12);		// P3 inserito come secondo con t = 12 - 10 = 2
				// P2 aggiornato come terzo con t = 5-2 = 3
// P4
delay(11);		// P4 inserito come secondo con t = 11 - 10 = 1
				// P3 aggiornato come terzo con t = 2 - 1 = 1
				// P2 rimane invariato
```
</div>
<div class="">

Ipotizzando di fare tutto nello stesso ciclo di clock:

Situazione precedente a `P4`:
$$
\text{sospesi} \to \boxed{\text{10} \atop \text{P1}} \to \boxed{\text{2} \atop \text{P3}} \to \boxed{\text{3} \atop \text{P2}}
$$

Situazione successiva a `P4`:
$$
\text{sospesi} \to \boxed{\text{10} \atop \text{P1}} \to \boxed{\text{1} \atop \text{P4}} \to \boxed{\text{1} \atop \text{P3}} \to \boxed{\text{3} \atop \text{P2}}
$$
</div>
</div>

## 2.1. Implementazione del nucleo

La lista dei processi è così definita all'interno del file `sistema.cpp`:
```cpp
struct richiesta {
	/// tempo di attesa aggiuntivo rispetto alla richiesta precedente
	natl d_attesa;
	/// puntatore alla richiesta successiva
	richiesta* p_rich;
	/// descrittore del processo che ha effettuato la richiesta
	des_proc* pp;
};
richiesta* sospesi;
```

Ogni elemento della lista, oltre al puntatore `p_rich` necessario per realizzare la lista, contiene:
- `pp` : _puntatore al descrittore_ del processo sospeso
- `d_attesa`: tempo di attesa aggiuntivo rispetto alla richiesta precedente.

La variabile globale `sospesi` punta _**alla testa della lista**_.

Vediamo l'implementazione di `inserimento_lista_attesa`:
```cpp
void inserimento_lista_attesa(richiesta* p) {
    richiesta *r, *precedente;

    r = sospesi;
    precedente = nullptr;

    // Cerco tra quali elementi dovrò inserire p
    while (r != nullptr && p->d_attesa > r->d_attesa) {
        // Ogni elemento che passo, rimuovo l'attesa da p
        p->d_attesa -= r->d_attesa;
        precedente = r;
        r = r->p_rich;
    }

    p->p_rich = r;
    if (precedente != nullptr)
        precedente->p_rich = p;
    else
        sospesi = p;

    // Aggiorno l'attesa del successivo in relazione a quello appena inserito
    if (r != nullptr)
        r->d_attesa -= p->d_attesa;
}
```

Alla lista accedono due _routine_ di sistema:

<div class="p">

`delay()`
</div>

È una normale primitiva di sistema con un gate nella `IDT` e una parte scritta in `assembly`:

<div class="grid2">
<div class="top">
<div class="p">

`sistema.s`
</div>

```x86asm
; ...
carica_gate TIPO_D  a_delay LIV_UTENTE
; ...
.extern c_delay
a_delay:
	.cfi_startproc
	.cfi_def_cfa_offset 40
	.cfi_offset rip, -40
	.cfi_offset rsp, -16
	call salva_stato
	call c_delay
	call carica_stato
	iretq
	.cfi_endproc
```
</div>
<div class="top">
<div class="p">

`sistema.cpp`
</div>

```cpp
extern "C" void c_delay(natl n) {
	// caso particolare:
    // se n è 0 non facciamo niente
	if (!n)
		return;

	richiesta* p = new richiesta;
	p->d_attesa = n;
	p->pp = esecuzione;

	inserimento_lista_attesa(p);
	schedulatore();
}
```
</div>
</div>

<div class="p">

`driver` del timer
</div>

Segue sostanzialmente lo stesso schema di una primitiva, ma va in esecuzione per effetto di una **richiesta di interruzione** e non per una istruzione `int`.

<div class="grid2">
<div class="top">

`sistema.s`
```x86asm
.extern c_driver_td
driver_td:
	.cfi_startproc
	.cfi_def_cfa_offset 40
	.cfi_offset rip, -40
	.cfi_offset rsp, -16
	call salva_stato
	call c_driver_td
    ; Aggiungiamo il segnale all'APIC
	call apic_send_EOI
	call carica_stato
	iretq
	.cfi_endproc
```
</div>
<div class="top">

`sistema.cpp`
```cpp
extern "C" void c_driver_td(void) {
    inspronti();

	if (sospesi != nullptr) {
        sospesi->d_attesa--;
	}

	while (sospesi != nullptr && sospesi->d_attesa == 0) {
        inserimento_lista(pronti, sospesi->pp);
		richiesta* p = sospesi;
		sospesi = sospesi->p_rich;
		delete p;
	}

	schedulatore();
}
```

</div>
</div>

Un'altra sostanziale differenza rispetto alle normali primitive, è che _nessuno esegue attivamente il `driver`_.
Infatti il processo che lo esegue **non lo ha fatto volontariamente**, ma è stato interrotto dall'evento. È persino probabile che il processo non sia nemmeno interessato a ciò che il `driver` deve fare.

# 3. new

L'operatore `new` effettua una ricerca in memoria `heap` di uno spazio sufficente a caricare la struttura/oggetto desiderato.

L'operatore `new` che utilizziamo nel nostro ambiente utilizza una funzione di `libce` che gestisce una zona della memoria di sistema usata come **_`heap`_**.

L'`heap` consiste in una sezione di `MB` della memoria dedicati.
Nel programma di `bootstrap`, viene inizializzato e utilizzata dai vari caricamenti dei processori (`8bit`, `16bit` e successivamente `32bit`).
Quando tutti sono stati caricati correttamente, la memoria viene liberata, e rimane disponibile per altri processi.

Mentre per la modalità sistema gli accessi all'`heap` sono atomici, in quanto le _interruzioni_ sono **disabilitate**, per quanto riguarda invece la modalità `utente`, poiché le _interruzioni_ sono qui attive, l'accesso ad esso rientra nel problema della **mutua esclusione**, risolvibile con un semaforo.

Nel nostro nucleo gli operatori di `new` e `delete` si limitano a richiamare in modo appropriato gli _overload_ di `operator new` e `operator delete` forniti dalla `libce`. Questi si limitano ad usare in maniera opportuna `alloc()`, `alloc_aligned()` e `dealloc()`.

```cpp
/* libce.h */
void *operator new(size_t s);
void *operator new(size_t, std::align_val_t a);
void operator delete(void *p);
```
```cpp
/* bare/new.cpp */
void* operator new(size_t s) {
	return alloc(s);
}
```
```cpp
/* bare/new_alligned.cpp */
void* operator new(size_t s, std::align_val_t a) {
	return alloc_aligned(s, a);
}
```
```cpp
/* bare/delete.cpp */
void operator delete(void *p) {
	dealloc(p);
}
```