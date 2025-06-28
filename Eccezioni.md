<link rel="stylesheet" type="text/css" href="./assets/style.css">

# 1. Indice

- [1. Indice](#1-indice)
- [2. Eccezioni](#2-eccezioni)
  - [2.1. Eccezione di Debug `int3`](#21-eccezione-di-debug-int3)
  - [2.2. Gestione Eccezioni](#22-gestione-eccezioni)


# 2. Eccezioni

Avevamo già discusso di come il processore possa mascherare le interruzioni in arrivo tramite `INTR`.
Esistono quindi alti tipi di interruzioni inviate tramite fili `NMI` che non possono essere mascherate e sono sempre immediatamente eseguite.

Sulle `NMI` viaggiano tra le altre cose le _**eccezioni**_.
Le eccezioni, quando vengono _sollevate_, sono quindi gestite immediatamente attraverso _routine_.

Le _routine_ delle eccezioni sono anch'esse salvate nella `IDT`, in particolare nelle **prime 32 entrate**.
I tipi delle eccezioni sono **fissi e impliciti**, consultabili nel manuale del processore.

Alcune famose sono:
- `0`: **Divisione per zero**
- `1`: **Single-Step**: viene avviato se il flag `TF` è settato.
  Il processore genererà quindi un'eccezione alla fine di ogni operazione eseguita.
- `3`: **Eccezione di debug** (istruzione `int3`)

## 2.1. Eccezione di Debug `int3`

È grazie a questa che il _debugger_ riesce a controllare il flusso del programma sul quale è eseguito.
Quando il _debugger_ inserisce un `breakpoint` in un indirizzo, quello che fa operativamente è sostituire il primo byte a quell'indirizzo con il valore `0xcc`, salvando il byte significativo.

Tramite il segnale di `continue` il debugger rilascia il controllo al programma, che eseguirà finché non farà la _fetch_ dell'eccezione.
Il controllo torna quindi al _debugger_, che opererà finché il programmatore non restituirà il controllo al programma.

Prima di permettere al programmatore di agire sul codice, il debugger **reinserisce il vecchio valore** dove aveva salvato `0xcc`, e setta il bit `TF` così da generare un'eccezione di _single-step_.
Il programma eseguirà quindi l'operazione dove era stato chiamato il breakpoint per poi dare controllo nuovamente al _debugger_, che reinserirà il valore `0xcc` così da mantenere il `breakpoint` per le successive iterazioni.
Il _debugger_ resetta quindi `TF` e restituisce per l'ultima volta il controllo al flusso principale

## 2.2. Gestione Eccezioni

Mentre le interruzioni possono accedere solo tra un'istruzione e la successiva, le eccezioni possono essere sollevate **in un momento qualunque di un'istruzione** (lettura, decodifica, esecuzione).

Il loro sollevamento può quindi generare comportamenti diversi da quelli delle interruzioni, che quindi vanno gestiti opportunamente.

Il primo dilemma riguarda come far variare lo stato del processore quando durante un istruzione viene sollevata un'eccezione.
Il secondo riguarda invece come riprendere l'esecuzione del programma.

Le eccezioni sono classificabili in tre gruppi, ognuno dei quali ha comportamenti diversi:
<div class="flexbox"><span class="">

| Tipo    | Quando viene generata                             | Indirizzo salvato                             | Scopo/Effetto                                                                           |
| ------- | ------------------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------- |
| `Fault` | Durante l'esecuzione di un'istruzione             | Indirizzo dell'istruzione che stava eseguendo | La routine dovrebbe sistemare il problema per poter rieseguire l'istruzione             |
| `Trap`  | Tra l'esecuzione di un'istruzione e la successiva | Indirizzo dell'istruzione successiva          | -                                                                                       |
| `Abort` | In qualsiasi momento                              | -                                             | Gestisce errori particolarmente gravi, tipicamente causa lo spegnimento del calcolatore |

</span></div>

Non siamo costretti ad utilizzare le eccezioni fornite dal processore o dalle librerie, ma possiamo scriverne di nostre:
<div class="grid2">
<div class="top">

```cpp
#include <libce.h>

extern "C" void a_divPerZero();
extern "C" void c_divPerZero(natq rip) {
    printf("Divisione per 0, all'indirizzo %lx!\n", rip);
}

int main() {
    int b = 0;
    gate_init(0, a_divPerZero);
    /*
    *  Inizializzo la riga 0 della IDT(DivisionPerZeroFault)
    *  con la mia funzione
    */

    int a = 3 / b;
}
```
</div>
<div class="top">

```x86asm
  .global divPerZero
divPerZero:
    NOP
    MOVq (%rsp), %rdi
    CALL c_divPerZero
    IRETq

```
</div>
</div>

