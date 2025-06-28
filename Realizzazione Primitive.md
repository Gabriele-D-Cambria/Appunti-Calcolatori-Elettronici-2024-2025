<link rel="stylesheet" type="text/css" href="./stilePersonalizzato.css">

# 1. Indice

- [1. Indice](#1-indice)
- [2. Reaizzazione Primitive](#2-reaizzazione-primitive)
- [3. Meccanismo di chiamata](#3-meccanismo-di-chiamata)
- [4. Scrivere una primitiva](#4-scrivere-una-primitiva)
  - [4.1. Funzioni di supporto](#41-funzioni-di-supporto)


# 2. Reaizzazione Primitive

Le primitive del nostro sitema devono lavorare su un insieme di strutture dati globali, come **descrittori di processo** e **code dei processi**.

Dobbiamo però chiederci cosa succederebbe se, mentre una primitiva sta lavorando su una di queste strutture `S`, una _interruzione_ (di qualsiasi tipo) causasse un salto ad un'altra primitiva che cerca di accedere alla medesima `S`?

Pensiamo, per esempio, ad una primitiva che sta cercando di inserire un nuovo `des_proc *d1`, nella coda `pronti` (supponiamo in testa).

Per eseguire questa operazione la primitiva esegue due operazioni:
- Copiare `pronti` in `d1->puntatore`
- Scrivere `d1` in `pronti`.

Supponiamo a questo punto che, tra la prima e la seconda scrittura, il processore salti ad un'altra _routine di sistema_ per effetto di una interruzione.
Questa nuova _routine_ cerca anch'essa di inserire un altro `des_proc *d2` in testa alla coda `pronti`.

Questa seconda primitiva copierà quindi `pronti` in `d2->puntatore` e appenderà `d2` in testa a `pronti`.

Al termine della seconda primitiva si ritornerà quindi alla prima, che proseguirà dal punto in cui si era interrotta.
Il problema che sorge è che in questo momento la primitiva appenderà `d1` in testa a `pronti`, **cancellando quanto vi aveva scritto la seconda**, poiché nella `pronti` salvata in `d1->puntatore` non è presente `d2`.

Perciò l'effetto è che il `des_proc* d2` **non è più puntato da niente**.

Chiaramente non vogliamo che quanto appena descritto possa accadere, ma questo è solo uno degli infiniti problemi che si potrebbero presentare
<small>(si pensi, per esempio, ad una `salva_stato` interrotta da un’altra `salva_stato`)</small>.

Più in generale, quello che abbiamo descritto è un problema di **_interferenza tra due flussi_** di esecuzione che lavorano **su una stessa struttura dati**.
La causa di queste _interferenze_ è dovuta alle _interruzioni_, poiché rende visibili ad altri processi gli **stati inconsistenti** dovute a **espressioni non atomiche**.

Infatti, quando si provano ad eseguire più istruzioni che singolarmente possono essere considerate _atomiche_ (poiché i vari _stati inconsistenti_ che comportano vengono risolti al termine della loro esecuzione), a casusa delle interruzioni è possibile per un altro processo inserirsi tra queste espressioni.

In generale, noi vogliamo che ogni struttura dati si trovi in uno **stato consistente**.
<small>(Per esempio, una lista è in uno _stato consistente_ se tutti e soli i suoi elementi sono raggiungibili dalla testa)</small>

In un sistema che _non prevede interruzioni_, le operazioni che manipolano le strutture dati vengono scritte assumendo che <u>la struttura dati si trovi sempre in uno stato consistente quando l'operazione inizia</u>, e assicurandosi di **portarla in un nuovo stato consistente alla fine dell'operazione**.
Nel mezzo dell'operazione, però, sono ammessi delle transizioni temporanee della struttura dati attraverso **stati non consistenti**.
Ripensiamo all'operazione di inserimento in testa alla coda `pronti` eseguita dalla prima primitiva:
&emsp;Subito dopo la copia di pronti in `d1->puntatore`, la lista **non è in uno stato consistente**, in quanto `d1` ne fa concettualmente parte, ma non è ancora puntato da `pronti`.

Questo stato inconsistente non è un problema in un sistema senza _interruzioni_, in quanto non è osservabile da nessun’altra operazione sulla _coda_.

In presenza di _interruzioni_, però, lo stato inconsistente diventa improvvisamente visibile da un’altra operazione, che era stata scritta assumendo che ciò non potesse mai accadere, e che dunque non è
preparata per affrontare la situazione.

Abbiamo a disposizione principalmente due modi per evitare i malfunzionamenti causati dalle _interferenze_:
1. Scrivere tutte le routine in modo da **tener conto di tutti i modi in cui queste si possono mescolare**, in modo che funzionino in ogni caso.
   <small>(possibile e anzi desiderabile, ma molto complesso)</small>;
2. Prevenire a priori l'interferenza, **eliminando tutte le sorgenti di interruzione durante l'esecuzione delle primitive**, o almeno delle loro parti critiche.

Per l'intera durata di tutte primitive del modulo `sistema` della nostra macchina adotteremo la <u>seconda soluzione</u>, Rilasseremo solo nel modulo `io`.
<small>(Da considerare che alcuni testi d’esame considerano il caso di rilassamento anche nel modulo sistema.)</small>

In particolare per quanto riguarda `sistema`, tutti i _gate_ saranno del tipo `interrupt`, con **disabilitazione automatica** delle _interruzioni esterne mascherabili_.
Durante la scrittura delle primitive, staremo inoltre attenti a non causare _eccezioni_ e **a non chiaramare altre primitive tramite `int`**.

Utilizzando questi accorgimenti, le nostre _primitive_ gireranno in un contesto **atomico**: <u>una volta iniziate saranno portate a compimento, senza che niente le possa interrompere</u>.

Diventeranno in questo modo molto simili alle singole istruzioni di linguaggio macchina, la cui _atomiticà_ è garantita dal processore.
Si noti che in molti sistemi reali l'_atomicità_ viene considerata un prezzo troppo alto da pagare e viene rilassata in vari modi, come ad esempio in `Linux`.

# 3. Meccanismo di chiamata

A livello `Assembler`, invocare una primitiva non è come invocare una semplice funzione, proprio perché è necessario passare attraverso un _gate_ con una istruzione `INT`.

Tuttavia è possibile utilizzare le _routine_ a livello del `C++` come una qualunque funzione, per maggior comodità dell'utente.

Ricordando che il _gate_ di una primitiva è così formato:
```cpp
P = 1               // bit presenza //
L = SISTEMA         // livello di privilegio della routine //
DPL = UTENTE        // livello di privilegio necessario //
ROUTINE = &routine  // indirizzo della routine //
I/T = INTERRUPT     // disabilita le interruzioni esterne //
```

Le routine avranno quindi tutte **lo stesso formato**.
Nel file `sistema.cpp` avremo:
```cpp
//...
extern "C" returnType c_primitiva_i(/*Parametri Formali*/);
//...
```
Nel file `sistema.s` avremo invece il corpo della primitiva e la sua "gemella" in `assembler`:

```x86asm
    .global a_primitiva_i
a_primitiva_i:
    CALL salva_stato
    CALL c_primitiva;
    CALL carica_stato
    IRETQ

; ...

    .global c_primitiva_i
c_primitiva_i:
    pushq %rbp
    movq %rsp, %rbp
    ; ...
    
    ; Usa i parametri attuali in
    ; %rdi, %rsi, etc...
    
    ; ...
    leave
    ret
```

</div>
<div class="top">
<div class="p">

</div>

</div>
</div>

Per permettere l'invocazione di una primitiva esistono nel nostro modulo `sistema` delle _label_ globali che chiamano i gate della `IDT`.
L'utente potrà quindi chiamare:
<div class="grid3">
<div class="top">
<div class="p">

`sys.h`
</div>

```cpp
//...
extern "C" returnType primitiva_i(/*parametri formali*/);
//...
```

Tendenzialmente è inutile che restituiscano risultato, poiché verrebbe sovrascritto nella `carica_stato`.
Il metodo corretto per propagare nuovi risultati alla fine dell'esecuzione è sfruttare il contesto del processo, in particolare `contesto[I_RAX]`.

</div>
<div class="top">
<div class="p">

`utente.cpp`
</div>

```cpp
#include <sys.h>
//...
void corpo(int a)
{
    //...
    primitiva_i(/*parametri attuali*/);
    //...
}
```
Esegue:
```x86asm
; Passo i parametri nei registri adeguati
; %rdi, %rsi, ...

CALL primitiva_i
```
</div>
<div class="top">
<div class="p">

`utente.s`
</div>

```x86asm
    .global primitiva_i
primitiva_i:
    INT $tipo_i
    RET
```
</div>
</div>

# 4. Scrivere una primitiva

Per scrivere una primitiva dobbiamo eseguire una serie di passaggi, alcuni obbligati altri semplicemente utili.

Il primo passaggio utile (ma non necessario) è creare una nuova **costante** nel file `costanti.h` così da potervi riferire per nome e non per valore:
```cpp
// ...
#define TIPO_I  0x29    /// inutile
// ...
```

A questo punto il primo passaggi obbligatorio è inserirla nel `sys.h`:
```cpp
// ...
extern "C" int inutile(int a, int b);
// ...
```

Adesso l'utente può dichiararne il corpo e successivamente utilizzarla.

Vediamo quindi come aggiungerla:

Nel file `utente.s` aggiungiamo le _stab_:
```x86asm
; ...
    .global inutile
inutile:
    .cfi_startproc      ; per il debugger
    int $TIPO_I
    RET
    .cfi_endproc        ; per il debugger
; ...
```

Definiamo e descriviamo quindi la funzione:
<div class="grid2">
<div class="top">
<div class="p">

`sistema.s`

</div>

```x86asm
;...

; Aggiungiamo alla tabella IDT
init_idt:
    ;...
    carica_gate TIPO_I  a_inutile   LIV_UTENTE
    ;...
```
```x86asm
; ...
.extern c_inutile
a_inutile:
    CALL salva_stato
    CALL c_inutile
    CALL carica_stato
    IRETQ

;...
```

</div>
<div class="top">
<div class="p">

`sistema.cpp`
</div>

```cpp
// ...
extern "C" void c_inutile(int a, int b){
    // Nella variabile esecuzione c'è ancora l'id del processo che l'ha invocata
    // Inoltre nel puntatore di processo si trova il processo che stava eseguendo
    int r = a + b + esecuzione->precedenza;

    // Per restituire r non possiamo fare return, ma scriviamo:
    esecuzione->contesto[I_RAX] = r;
}
```
</div>
</div>


L'utente a questo punto può utilizzare la nuova primitiva nel file `utente.cpp`:
```cpp
#include<all.h>

int main(){
    printf("inutile(2,3) = %d\n", inutile(2,3));
    pause();
    terminate_p();
}
```
> inutile(2, 3) = 1028

## 4.1. Funzioni di supporto

Le seguenti funzioni sono già definite in `sistema.cpp` e possono essere utilizzare nel definire nuove _primitive_:

- `desc_proc* nuovo_des_p(natl id)`: resituisce un puntatore al descrittore del processo di identificatore `id` (`nullptr` se non esiste)

- `void schedulatore()`: sceglie il prossimo processo da mettere in esecuzione, cambiando il valore della variabile `esecuzione`

- `void inserimento_lista(des_proc*& p_lista, des_proc* p_elem)`: Inserisce `p_elem` nella _lista_ `p_lista`, mantenendo l’ordinamento basato sul campo precedenza. 
    Se la _lista_ contiene altri elementi che hanno la stessa precedenza del nuovo, il nuovo viene inserito **come ultimo** tra questi.

- `des_proc* rimozione_lista(des_proc*& p_lista)`: Estrae l’elemento **in testa** alla `p_lista` e ne restituisce un puntatore (`nullptr` se la lista è vuota).

- `void inspronti()`: Inserisce il `des_proc` puntato da esecuzione in testa alla coda pronti senza effettuare controlli sulla priorità.

- `void c_abort_p()`: Distrugge il processo puntato da `esecuzione` e chiama `schedulatore()`