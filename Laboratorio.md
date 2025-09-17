---
title: "Laboratorio"
---

# 1. Indice

- [1. Indice](#1-indice)
- [2. Compilare File](#2-compilare-file)
- [3. Prologo ed Epilogo](#3-prologo-ed-epilogo)
- [4. Assembler intelx86 - `64bit`](#4-assembler-intelx86---64bit)
- [5. _Mangling_ e Differenze C - C++](#5-mangling-e-differenze-c---c)
  - [5.1. Struttura](#51-struttura)
- [6. QEMU](#6-qemu)
  - [6.1. Utilizzo HD macchina](#61-utilizzo-hd-macchina)
  - [6.2. Eccezioni](#62-eccezioni)

<div class="stop"></div>

# 2. Compilare File

Siamo abituati a compilare tramite il comando: 
```bash
gcc nomeEseguibile -o fileDaCompilare.cpp
```
Questo comando esegue compilazione e linking.
Per poter eseguire compilazione e linking in due momenti diversi si possono utilizzare i seguenti comandi:
```bash
# Compilazione (valida anche per file .s)
gcc -c main.c -o main.o

# Linking
gcc file.o -o eseguibile
```

Per poter visualizzare il contenuto del file `.o` generato dalla compilazione si può utilizzare il seguente comando: 
```bash
objdump -d fileOggetto.o
```

# 3. Prologo ed Epilogo

Quando si compila un file `.c` o `.cpp` prima di tradurre il codice dal `main` e dalle varie funzioni vanno inseriti due pezzi di codice chiamati **prologo** ed **epilogo**.

Entrambe le sezioni sono **indispensabili** affinché il processore possa eseguire il programma in maniera corretta.
Concretamente si occupano infatti di inizializzare/gestire correttamente lo spazio dedicato ad una funzione nella pila tramite i registri `%rbp` e `%rsp`.

Quando un programma viene eseguito il registro `%rsp` punta **alla prima locazione di memoria dedicata**, mentre `%rbp` punta al **primo indirizzo _fuori_** dalla locazione di memoria.
Il prologo si occupa di allocare la memoria necessaria per salvare tutte le variabili di una determinata funzione.
Per fare ciò la struttura è la seguente:
```x86asm
; Prologo
PUSHq %rbp                       ; Salvo la vecchia ultima locazione, mi servirà per tornarci nell'epilogo
MOVq %rsp, %rbp                  ; La vecchia prima locazione è la nuova ultima locazione
SUBq $spazioNecessario, %rsp     ; La nuova prima locazione si trova X byte indietro rispetto a quella attuale
```

Dove per `$spazioNecessario` si intende uno spazio multiplo di `8Byte`.

L'epilogo invece fa la stessa cosa ma in ordine inverso.
I passaggi sono i seguenti:
```x86asm
; Epilogo
MOVq %rbp, %rsi
POPq %rbp

; --- Sono condensati nel seguente comando --- ;

LEAVE
```

# 4. Assembler intelx86 - `64bit`

Nell'assembelr a `64bit` esistono delle regole sui registri "sporcabili" dai programmmi che il compilatore segue.

<div class="flexbox index" style="margin-bottom: 0px; padding-bottom: 16px" markdown="1">

| Registro | Descrizione                             | Stato di utilizzo                                 |
| -------- | --------------------------------------- | ------------------------------------------------- |
| `%rax`   | Usato per i valori di ritorno           | **Utilizzabile**                                  |
| `%rbx`   | Generalmente salvato dal chiamato       | Non tipicamente utilizzabile                      |
| `%rcx`   | Comunemente usato per i contatori       | **Utilizzabile**                                  |
| `%rdx`   | Spesso usato per operazioni I/O         | **Utilizzabile**                                  |
| `%rsi`   | Tipicamente salvato dal chiamato        | Non tipicamente utilizzabile                      |
| `%rdi`   | Spesso usato per operazioni su stringhe | Non tipicamente utilizzabile                      |
| `%rbp`   | Puntatore base per il frame dello stack | <u><strong><em>Non utilizzabile</em></strong></u> |
| `%rsp`   | Puntatore dello stack                   | <u><strong><em>Non utilizzabile</em></strong></u> |
| `%r8`    | Registro utilizzabile                   | **Utilizzabile**                                  |
| `%r9`    | Registro utilizzabile                   | **Utilizzabile**                                  |
| `%r10`   | Registro utilizzabile                   | **Utilizzabile**                                  |
| `%r11`   | Registro utilizzabile                   | **Utilizzabile**                                  |
| `%r12`   | Tipicamente salvato dal chiamato        | Non tipicamente utilizzabile                      |
| `%r13`   | Tipicamente salvato dal chiamato        | Non tipicamente utilizzabile                      |
| `%r14`   | Tipicamente salvato dal chiamato        | Non tipicamente utilizzabile                      |
| `%r15`   | Tipicamente salvato dal chiamato        | Non tipicamente utilizzabile                      |

</div>


# 5. _Mangling_ e Differenze C - C++

In `C`, se volessi utilizzare una funzione scritta in assembly nel mio file `.c`, è sufficente che i file rispettino questo standard:
<div class="grid2">
<div class="top">

```cpp
extern int funzione();
```
</div>
<div class="top">

```x86asm
.global funzione

funzione:
    NOP
    ...
    RET
```
</div>
</div>

Infatti in `C` le funzioni sono definite univocamente dal loro nome.

In `C++` la cosa è diversa, infatti esiste l'_overloading_ delle funzioni, che non sono più univocamente definite dal nome, ma anche dal tipo/ordine/numero di parametri

In `C++` si utilizza quindi questa sintassi

<div class="grid2">
<div class="top">

```cpp
extern int funzione();
```
</div>
<div class="top">

```x86asm
.global _ZXnome

_ZXnome:
    NOP
    ...
    RET
```
</div>
</div>


Infatti si utilizza un comando del seguente tipo:
```x86asm
_Zn(nome)(tipi input)
```

`n` indica il numero di caratteri dal quale è formato il nome
Per tipi di input si intendono:
- `i` $\to$ `int`
- `c` $\to$ `char`
- $\cdots$
- `P(elemento)` $\to$ `puntatore a elemento`
- `R(elemento)` $\to$ `riferimento`
- `E` puntatore `this`
- `C1` indica il costruttore
- Nel caso di tipi definiti dall'utente si utilizza la stessa regola che per il nome della funzione

Nel caso di metodi annidati, invece di `_Zn(nomeFunzione)` si utilizza `_ZN(nomeClasse)n(nomeFunzione)`:

<div class="grid2">
<div class="top">

```cpp
class cl{
    cl(int);
    // ...
    void elab1();
}
```
</div>
<div class="top">

```x86asm
; cl::elab1
.global _ZN2cl5elab1E

; cl::cl
.global _ZN2clC1i
```

</div>
</div>


Per verificare la sintassi di un nome è possibile utilizzare il comando `c++filt _Z....`

Nel caso in cui si volesse passare come parametro due volte lo stesso tipo definito dall'utente, si utilizza `S(n)_`.
Questo comando ripete il tipo defiito dall'utente.
`n` indica quale dei vari tipi già dichiarati va ripetuto (si omette per il primo, 0 per il secondo, 1 peer il terzo, ...):
```bash
c++filt _Z5somma4caso5puntoS_
c++filt _Z5somma4caso5puntoS0_
c++filt _Z5somma4casoP5puntoS0_
```
> somma(caso, punto caso) <br>
> somma(caso, punto, punto)

## 5.1. Struttura

<div class="grid2">
<div class="top">
<p class="p">Passaggio Struttura</p>

```cpp
struct st{
    int x;
    int y;
}

extern int somma_struttura(st struttura);
```

Il file assembly diventa così:
```x86asm
.global _Z15somma_struttura2st

;
; args:
;   - st struttura: %rdi
; return:
;   %rax
;   |000000000000000|
;   +---------------+  <- %rsp
;   |   a   |   b   |
;   +---------------+  <- %rbp  (base pointer)
;   |fffffffffffffff|
;

.set struttura, -8
.set freccia_a, 0
.set freccia_b, 4

_Z15somma_struttura2st:
    ; Prologo
    PUSH %RPB
    MOVq %RSP, %RBP
    SUB $8, %RSP

    ; Corpo
    MOVq %rdi, struttura(%rbp)

    MOVl struttura+freccia_a(%rbp), %eax
    addl struttura+freccia_b(%rbp), %eax


    ; Epilogo
    LEAVE

    RET

```
</div>
<div class="top">
<p class="p">Passaggio Struttura per puntatore</p>

```cpp
struct st{
    int x;
    int y;
}

extern int somma_struttura(st* struttura);
```

Il file assembly diventa così:
```x86asm
.global _Z18somma_struttura_ptP2st

;
; args:
;   - st* struttura: %rdi
; return:
;   struttura->a + struttura->b 
;   %rax
;   |000000000000000|
;   +---------------+  <- %rsp                              +---------------+
;   | st* struttura |   ----------------------------------> |   a   |   b   |
;   +---------------+  <- %rbp  (base pointer)              +---------------+
;   |fffffffffffffff|
;

.set struttura_pt, -8
.set freccia_a, 0
.set freccia_b, 4

_Z15somma_struttura2st:
    ; Prologo
    PUSH %RPB
    MOVq %RSP, %RBP
    SUB $8, %RSP

    ; Corpo
    MOVq %rdi, struttura_pt(%rbp)

    MOVq struttura_pt(%rbp), %rsi

    MOVl freccia_a(%rsi), %eax
    ADDl freccia_b(%rsi), %eax


    ; Epilogo
    LEAVE

    RET

```
</div>
</div>

# 6. QEMU

È una macchina virtuale che emula un sistema basato su _Intelx86_ a `64bit` **senza bootloader**.
L'unico programma che è conservato in memoria della macchina dobbiamo caricarlo noi.

Per fare ciò ci posizioniamo nella cartella contenente i file che si desidera caricare.
Possono essere file `.cpp`, `.c` e `.s`.

Viene poi eseguito il comando `compile`.
Dopo aver eseguito l'esecuzione _compile_ in maniera corretta, è possibile avviare `QEMU` tramite il comando `boot`.

Nel caso in cui volessimo effettuare del _debug_ del codice dobbiamo _bootare_ la macchina con il comando `boot -g`, e successivamente, _da un nuovo terminale_, eseguire il comando `debug`.

## 6.1. Utilizzo HD macchina 

La macchina `QEMU` utilizza un _HD_ virtuale salvato nella cartella `CE/share/hd.img`.

Nel caso volessimo svuotare l'_HD_ il comando per farlo è il seguente:
```bash
truncate -s 20971520 ~/CE/share/hd.img
```

Per visualizzarne invece il contenuto il comando è il seguente:
```bash
hexdump -C ~/CE/share/hd.img | less
```

## 6.2. Eccezioni

Come abbiamo già visto nella parte teorica non possono essere chiamate dall'utente, ma vengono generate quando si verificano certe cose.

Si dividono in tre tipi:
- `Fault`: l'`IP` punta all'istruzione stessa che genera l'eccezione, e prova a rieseguirla dopo la _routine_
- `Trap`: l'`IP` punta all'istruzione successiva a quella che genera l'eccezione
- `Abort`

