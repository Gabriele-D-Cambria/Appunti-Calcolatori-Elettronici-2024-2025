<link rel="stylesheet" type="text/css" href="./stilePersonalizzato.css">

# 1. Indice

- [1. Indice](#1-indice)
- [2. Sistemi Multiprocesso](#2-sistemi-multiprocesso)
  - [2.1. Processi](#21-processi)
  - [2.2. Contesti](#22-contesti)
  - [2.3. Kernel](#23-kernel)
  - [2.4. Semplice Sistema Multiprocesso](#24-semplice-sistema-multiprocesso)
    - [2.4.1. Scrittura programmi utente](#241-scrittura-programmi-utente)
    - [2.4.2. Avvio sistema](#242-avvio-sistema)
    - [2.4.3. Uso debugger](#243-uso-debugger)
- [3. Descrizione Processi](#3-descrizione-processi)
  - [3.1. Transizione Processi](#31-transizione-processi)
  - [3.2. Creazione nuovo Processo](#32-creazione-nuovo-processo)


# 2. Sistemi Multiprocesso

Per poter introdurre sistemi che possano eseguire più programmi contemporaneamente dobbiamo prima introdurre alcuni concetti.

## 2.1. Processi

Il primo tra i concetti che andiamo a vedere è il **_processo_**.
> Un _**processo**_ è un programma in esecuzione su dei dati di ingresso

Questa esecuzione la possiamo modellare come la sequenza degli stati attraverso il cui il sistema processore+memoria passa eseguendo il programma.

Questa definizione si applica bene ai programmi di tipo _batch_, in cui gli ingressi vengono specificati tutti all'inizio, e il _processo_ prosegue indisturbato dino ad ottenere le uscite.
Tuttavia non è difficile immaginarsi l'estensione di questa definizione ai programmi "interattivi".

L'importante è capire che _programma_ e _processo_ sono due cose <u>completamente distinte</u>, infatti:
- Uno stesso programma piò essere associato a **più processi**;
- Uno stesso processo può eseguire, in sequenza, **più programmi**;
- In generale non è esclusivamente il programma a decidere attraverso quali stati il processo dovrà passare, ma hanno influenze anche i vari segnali di _input_;
- Il programma potrebbe contenere dei cicli, che scrivono le cose da ripetere una sola volta, mentre nel processo vediamo le azioni ripetute tante volte.

## 2.2. Contesti

Per riuscire a realizzare i processi riutilizziamo il concetto che avevamo già utilizzato di **_contesto_**.

In un sistema multiprocesso infatti, il significato di una istruzione _dipende dal processo che la sta eseguendo_.

Se un processo `P1` esegue una istruzione `MOV %rax, 1000` si sta riferendo al "suo" registro `%rax` e al "suo" indirizzo `1000`.
Mentre se la esegue un processo `P2` parlerà di un diverso `%rax` e di un diverso contenuto dell'indirizzo `1000`.

Il _contesto di un processo_ comprenderà quindi:
- Tutta la memoria (`M2`) usata dal processo (la immaginiamo per ora salvata nell'`HD`)
- Una **copia privata** di tutti i registri del processore, salvati in una opportuna struttura dati.

Per cambiare il contesto quando passiamo da un processo all'altro (ovvero quando eseguiamo _swap-out_ e _swap-in_ della memoria) si utilizziamo tecniche _sofware_:
> Ogni volta che si effettua un cambio di processo, andiamo a **salvare in una struttura dati** i valori dei registri e della memoria del processo terminato.
> Successivamente _copiamo i valori precedentemente salvati_ nella struttura dati associata al nuovo processo, rendendolo il **processo corrente** (o **processo attivo**)

Dobbiamo quindi implementare il _software_, in `M1`, che fa queste cose.
Il nome di questo _software_ è `kernel`.

## 2.3. Kernel

<div class="grid2">
<div class="">


Il `kernel` è quindi un software che sta sempre nello spazio di memoria di sistema (`M1`) e può **riacquisire** occasionalmente il controllo del flusso.
Il `kernel` gira infatti a **livello sistema** e può recuperare il controllo del flusso <u>**solamente**</u> tramite i _gate_ della `IDT` (interruzioni esterne, eccezioni, chiamate `int`)
</div>
<div class="">
<figure class="100">
<img class="30" src="./images/Kernel/Livelli di Privilegio e contesti.png">
<figcaption>

Rappresentazione dei livelli di privilegio e contesti
</figcaption>
</figure>
</div>
</div>


Il registro `RIP` del processore si trova **sempre** in uno e uno solo dei processi.
`RIP` **non può** attraversare due processi diversi, se non tramite il cambio di processo effettuato dal `kernel` stesso.

Il `kernel` ha diversi modi per decidere come saltare tra processi, noi ne vedremo uno in questo corso, mentre gli altri verranno esaminati nel corso di **_Sistemi Operativi_**.

Un'altra scelta che il `kernel` deve eseguire è quella di decidere la intravisibilità dei processi, ovvero se si possono interfacciare tra di loro o se sono indipendenti.
In questo corso vedremo un'_implementazione mista_ dove ci sarà sia **una parte della memoria condivisa** sia **una parte privata**.

L'ultima precisazione da fare è che generalemnte tanti processi si riferiscono a diversi programmi, spesso persino di diversi utenti.
Noi vedremo invece <u>esclusivamente</u> l'implementazione di **un unico programma**, di **un unico utente**, che genera _tanti processi_.

## 2.4. Semplice Sistema Multiprocesso

Il sistema che realizzeremo è organizzato in tre moduli:
- `sistema`
- `io`
- `utente`

Ogni modulo è un programma a sé stante, non collegato con gli altri due.

Il modulo `sistema` contiene la realizzazione dei processi, inclusa la _gestione della memoria_ (tramite _memoria virtuale_).
Il modulo `io` contiene le _routine_ di ingresso/uscita che permettono di utilizzare le periferiche collegate al sistema (testiera, video, hd, ...)

Entrambi questi due moduli vengono eseguiti con il processore a **_livello sistema_**, in un contesto privilegiato, mentre `utente` verrà eseguito al _**livello utente**_.

Il ruolo di `sistema` e `io` è quello di fornire un supporto ad `utente`, sotto forma di primitive che possono essere da lui invocate.
In particolare `utente` può **creare più processi** che vengono eseguiti _concorrentemente_.

Il nostro sistema si sviluppa quindi nella _directory_ `nucleo-8.3/`. <small>(versione utilizzata durante la stesura di questi appunti)</small>
Al suo interno troviamo le seguenti _sottodirectory_:
- `sistema/`, `io/` e `utente/`, che contengono **i file sorgenti** dei rispettivi moduli;
- `util/`, che contiene alcuni script di utilità;
- `include/`, che contiene dei file `.h` inclusi dai vari sorgenti;
- `build/`, inizialmente vuota, destinata a contenere i moduli finiti;
- `debug/`, che contiene alcune estensioni per il debugger `gdb`;
- `doc/`, destinata a contenere **la documentazione dei moduli**.

Oltre a queste _sottodirectory_ troviamo anche **due file**:
- `MakeFile`: contiene le istruzioni per il programma `make` del sistema di appoggio.
- `run`: uno script che permette di avviare il sistema su una `VM`

Il `MakeFile` può essere utilizzato per generare la documentazione (se sono installati `Doxygen` e `PAandoc`) lanciando il comando
```x86asmh
make doc
```
Se ha successo si troverà nell'indice `doc/html/index.html`.

Per compilare tutti i moduli si utilizza, **_nella directory_** `nucleo-8.3`:
```x86asmh
make
```

### 2.4.1. Scrittura programmi utente

Si suppone che i moduli `sistema` e `io` cambino raramente e costituiscano il sistema vero e proprio, mentre il modulo `utente`, di volta in volta diverso, rappresenta il programma che l’utente del nostro sistema vuole eseguire.

Per questo motivo la _sottodirectory_ `utente` contiene solo:
- Alcuni file di supporto (`lib.cpp`, `lib.h` e `utente.s`)
- Una _sottodirectory_ `examples/` contenente alcuni esempi di possibili programmi utente.

Un esempio minimo può essere il seguente:
```cpp
#include<all.h>

void main(){
    writeconsole("Hello, world!\n", 14);
    pause();
    // Serve ad evitare che lo shutdown venga eseguito troppo velocemente
    terminate_p();
    // Necessaria poiché il <main> deve chiedere al sistema di poter terminare
}
```
> Hello, world!
> Premere un tasto per continuare

### 2.4.2. Avvio sistema

Una volta costruiti i moduli possiamo avviare il sistema.
La procedura di `boostrap` è la stessa di quella già vista, e può essere avviata tramite lo script `boot`.

I processori _intel_ sono ancora oggi progettati per avviarsi a `16bit` in modalità non protetta.
Via _software_ vengono poi portati in modalità protetta a `32bit`, in generae grazie ad un programma di `bootstrap` nel `BIOS`.
Nel nostro caso sarà l'emulatore stesso ad effettuare questo primo passaggio.

Tocca a noi però portare il processore nella modalità a `64bit`, e questo compito lo facciamo svolgere al programma `boot.bin` che può cedere il controllo al modulo `sistema`.

Il programma `boot.bin` esegue una serie di allocazioni in memoria per permettere il corretto funzionamento della nostra macchina.

Una volta avviato vedremo una nuova finestra che rappresenta il video della _VM_.

Nel terminale dal quale abbiamo lanciato `boot` vedremo tutta una serie di messaggi, che altro non sono che quelli inviati sulla porta seriale della _VM_, che adesso andiamo ad analizzare:

<div class="grid2">
<div class="top">

Le righe 1-15 arrivano dal programma `boot.bin`:
- Nelle righe 4–7 il programma `boot.bin` ci informa del fatto che il `bootloader` precedente (nel nostro caso `QEMU` stesso) ha caricato in
memoria _tre file_, in particolare il file `build/sistema.strip4` all’indirizzo `0x114000`.
- Nelle righe 8–11 ci informa di come sta copiando le sezioni di questo file nella loro destinazione finale.
- La riga 15 ci avverte infine che `boot.bin` ha finito e sta per
saltare all’indirizzo mostrato nella riga 12 (`0x200178`), dove si trova **l’entry point del modulo `sistema`**.

I messaggi successivi arrivano dal modulo `sistema` (con alcuni,
come le righe 45–46, che arrivano dal modulo `io`).

Nella seconda sezione troviamo in particolare:
- Le righe 19–24 contengono informazioni relative alla _memoria virtuale_, che per il momento ignoriamo.
- Nelle righe 36-37 vengono creati i primi processi di sistema
- Alla riga 38 vediamo che viene inizializzato l’`APIC`.
- Nella riga 40 veniamo informati dell'inizializzazione dello _heap di sistema_ (riutilizzando lo spazio occupato da `boot.bin`).

Da questo punto in poi l’inizializzazione prosegue nel _processo_ `main_sistema` (`id 1`) e `main I/O` (`id 2`).

Il processo `main_sistema`:
- Alla riga 41 **attiva il timer**
- Alle righe 42-43 e crea il processo `main_io`
- Le righe 44–53 sono invece relative all’inizializzazione del modulo `io`, eseguita da questo processo.

Quando il processo `main_io` termina, processo `main_sistema` **crea il primo processo utente** (righe 54–55) e gli cede il controllo (riga 56), semplicemente terminando (riga 57).

In questo caso il processo `utente` esegue del codice che verrà eseguito per poi terminare.

Il controllo passa quindi a `dummy` (`id 0`), che si accorge che **non ci sono più processi utente** e quindi _**ordina lo shutdown della macchina `QEMU`**_ (riga 60).
</div>
<div class="top">

```txt
 1 | INF - Boot loader di Calcolatori Elettronici, v1.0
 2 | INF - Memoria totale: 32 MiB, heap: 636 KiB
 3 | INF - Argomenti: /home/giuseppe/CE/lib/ce/boot.bin
 4 | INF - Il boot loader precedente ha caricato 3 moduli:
 5 | INF - - mod[0]: start=114000 end=12f580 file=build/sistema.strip
 6 | INF - - mod[1]: start=130000 end=1414e0 file=build/io.strip
 7 | INF - - mod[2]: start=142000 end=147400 file=build/utente.strip
 8 | INF - Copio mod[0] agli indirizzi specificati nel file ELF:
 9 | INF - - copiati 108560 byte da 114000 a 200000
10 | INF - - copiati 970 byte da 12edb8 a 21bdb8
11 | INF - - azzerati ulteriori 79030 byte
12 | INF - - entry point 200178
13 | INF - Creata finestra sulla memoria centrale: [ 1000, 2000000)
14 | INF - Creata finestra per memory-mapped-IO: [ 2000000, 100000000)
15 | INF - Attivo la modalita’ a 64 bit e cedo il controllo a mod[0]...
16 | INF - Nucleo di Calcolatori Elettronici, v7.1.1
17 | INF - Heap del modulo sistema: [1000, a0000)
18 | INF - Numero di frame: 560 (M1) 7632 (M2)
19 | INF - Suddivisione della memoria virtuale:
20 | INF - - sis/cond [ 0, 8000000000)
21 | INF - - sis/priv [ 8000000000, 10000000000)
22 | INF - - io /cond [ 10000000000, 18000000000)
23 | INF - - usr/cond [ffff800000000000, ffffc00000000000)
24 | INF - - usr/priv [ffffc00000000000, 0)
25 | INF - mappo il modulo I/O:
26 | INF - - segmento sistema read-only mappato a [ 10000000000, 1000000f000)
27 | INF - - segmento sistema read/write mappato a [ 10000010000, 10000031000)
28 | INF - - heap: [ 10000031000, 10000131000)
29 | INF - - entry point: start [io.s:11]
30 | INF - mappo il modulo utente:
31 | INF - - segmento utente read-only mappato a [ffff800000000000, ffff800000005000)
32 | INF - - segmento utente read/write mappato a [ffff800000005000, ffff800000007000)
33 | INF - - heap: [ffff800000007000, ffff800000107000)
34 | INF - - entry point: start [utente.s:10]
35 | INF - Frame liberi: 7059 (M2)
36 | INF - Creato il processo dummy (id = 0)
37 | INF - Creato il processo main_sistema (id = 1)
38 | INF - Inizializzo l’APIC
39 | INF - Cedo il controllo al processo main sistema...
40 | INF 1 Heap del modulo sistema: aggiunto [100000, 200000)
41 | INF 1 Attivo il timer (DELAY=59659)
42 | INF 1 Creo il processo main I/O
43 | INF 1 proc=2 entry=start [io.s:11](1024) prio=1278 liv=0
44 | INF 1 Attendo inizializzazione modulo I/O...
45 | INF 2 Heap del modulo I/O: 100000B [0x10000031000, 0x10000131000)
46 | INF 2 Inizializzo la console (kbd + vid)
47 | INF 2 estern=3 entry=estern_kbd(int) [io.cpp:168](0) prio=1104 (tipo=50) liv=0 irq=1
48 | INF 2 kbd: tastiera inizializzata
49 | INF 2 vid: video inizializzato
50 | INF 2 Inizializzo la gestione dell’hard disk
51 | INF 2 bm: 00:01.1
52 | INF 2 estern=4 entry=estern_hd(int) [io.cpp:509](0) prio=1120 (tipo=60) liv=0 irq=14
53 | INF 2 Processo 2 terminato
54 | INF 1 Creo il processo main utente
55 | INF 1 proc=5 entry=start [utente.s:10](0) prio=1023 liv=3
56 | INF 1 Cedo il controllo al processo main utente...
57 | INF 1 Processo 1 terminato
58 | INF 5 Heap del modulo utente: 100000B [0xffff800000006068, 0xffff800000106068)
59 | INF 5 Processo 5 terminato
60 | INF 0 Shutdown
```
</div>
</div>


Il sistema sul quale lavoriamo è progettato affinché qualsiasi eccezione venga sollevata in modalità utente, resituisce il controllo al modulo sistema, il quale **_termina forzatamente il processo_** e invia alcuni messaggi sul log come il seguente:
```
 1 | WRN 5 Eccezione 13 (errore di protezione), errore 0, RIP inputb [inputb.s:6]
 2 | WRN 5 proc 5: corpo start [utente.s:10](0), livello UTENTE, precedenza 1023
 3 | WRN 5 RIP=inputb [inputb.s:6] CPL=LIV_UTENTE
 4 | WRN 5 RFLAGS=246 [-- -- -- IF -- -- ZF -- PF --, IOPL=SISTEMA]
 5 | WRN 5 RAX= fee000b0 RBX= 0 RCX=fffffffffffffe68 RDX= 60
 6 | WRN 5 RDI= 60 RSI=fffffffffffffe68 RBP=fffffffffffffff0 RSP=ffffffffffffffe8
 7 | WRN 5 R8 =ffff800000106068 R9 = 0 R10= 0 R11= 0
 8 | WRN 5 R12= 0 R13= 0 R14= 0 R15= 0
 9 | WRN 5 backtrace:
10 | WRN 5 > main [utente.cpp:5]
11 | WRN 5 Processo 5 abortito
```

Questi messaggi hanno una struttura generalmente simile tra di loro.

Alla riga 1 viene indicata:
- **_il tipo di eccezione che ha generato lo shutdown del processo_** `Eccezione 13 (errore di protezione)`
- Una descrizione dell'errore `errore 0`
- **_L'istruzione che l'ha sollevata_** `RIP inputb [inputb.b:6]`

Nella seconda riga si hanno informazioni riguardanti il _processo interrotto_ e il livello al quale l'eccezione è stata sollevata `livello UTENTE, precedenza 1023`

Successivamente nelle righe 3-8 è presente **un riepilogo dello stato dei registri al momento dell'eccezione**, utile per il _debug_.

Dalla riga 9 fino alla penultima si ha un _backtrace_ delle chiamate che indica come siamo arrivati al file corrrente, in questo caso passando dal `main` nel file `utente.cpp:5`

L'ultima riga indica l'esito del processo, nel nostro caso sempre _abortito_.


Tutte queste informazioni che ci vengono fornite, sono processate dallo script `util/show_log.pl` a partire dal log inviato dal sistema che contiene _solamente indirizzi numerici_, usando le informazioni di debug contenute nei file della directory `build/`.
Nel caso si voglia vedere il contenuto del log non processato si può usare il comando:
```x86asmh
CERAW=1 boot
```


### 2.4.3. Uso debugger

Anche per quanto riguarda il `debug`, così come per gli `esempiIO`, abbiamo la possibilità di _collegate il debugger_ dalla macchina host e osservare tutto quello che accade nel sistema.

La procedura è quella già vista:
1. Avviamo la _VM_ tramite `boot -g`
2. Da un altro terminale, ci portiamo nella stessa _directory_ e lanciamo `debug`.

In questo caso però lo script, oltre alle estensioni già viste, carica altre estensioni dal file `debug/nucleo.py`, in modo che il _debugger_ mostri informazioni specifiche sullo stato del nucleo.

In particolare, ogni volta che il _debugger_ riacquisisce il controllo, viene mostrato:
- Lo stack delle chiamate (_backtrace_);
- Il file sorgente nell’intorno del punto in cui si trova `%rip`;
- Se il sorgente è `C++`, _i parametri della funzione_ in cui ci troviamo e _tutte le sue variabili locali_;
  Altrimenti se il file è `assembler` vengono mostrati i _registri_ e la _parte superiore della pila_;
- Il numero di processi (`utente`) esistenti e le liste `esecuzione` e `pronti` (ed eventuali altre liste di processi);
- Alcuni dettagli sul processo attualmente in esecuzione;
- Lo _stato di protezione_ della **CPU**.


Oltre ai normali comandi di `gdb`, sono disponibili altri comandi personalizzati per il nostro nuleo.
Alcuni di quesi comandi sono:
- `process list`: mostra una lista di **tutti i processi attivi** (`utente` o `sistema`);
- `process dump id`:  mostra il contenuto (della parte superiore) **della pila sistema del processo `id`** e **il contenuto dell’array `contesto`** del suo descrittore di processo.

Altri comandi disponibili servono ad esaminare altre strutture dati che per il momento non abbiamo ancora introdotto.

Possiamo notare inoltre che il _debugger_ è **preimpostato per caricare i simboli di tutti e tre i moduli**.
È quindi possibile **inserire _breakpoint_ liberamente** nel codice del modulo `sistema`, `utente` e `io`.

# 3. Descrizione Processi

All'esecuzione di ogni processo abbiamo detto che il processore utilizza un diverso `contesto`.

Il `contesto` è una _struttura dati_ salvata in `M2`, ed è formato da:
- `id` : descrittore processo
- **corpo**: contenuto dei registri del processore
- `priorità`: indica il livello di priorità del processo

Sappiamo già che il processore lavora per **stati**.
Anche i _processi_ seguono la stessa logica e, durante la loro vita, si trovano costantenmente in uno degli _stati di esecuzione_.

<figure class="80">
<img class="50" src="./images/Processi/Stati di esecuzione.png">
<figcaption>

Lo schema di riferimento per gli stati dei processi.

</figcaption>
</figure>


I processi devono essere prima di tutto **attivati**, in modo che possano cominciare ad essere eseguiti.
L’attivazione comporta <u>la creazione di tutte le strutture dati necessarie al corretto funzionamento del _processo_</u>.
Queste strutture comprendono due componenti:
- **Descrittore di processo**
- **Pile**

In alcuni sistemi i processi da attivare sono decisi staticamente all’avvio del sistema.
Nel sistema che realizzeremo, descriveremo il caso in cui **i processi possano essere creati dinamicamente da altri processi** (tranne ovviamente il primo processo, che sarà creato dal sistema stesso all’avvio).


Una volta attivato correttamente, il _processo_ si trova quindi nello stato di **pronto**, nel nostro sistema questa lista è rappresentata dalla lista `pronti`.
A questo punto, il processore, tramile la _schedulazione_ e il _dispatch_, porta il _processo_ in **esecuzione**, nel nostro sistema rappresentata dalla variabile `esecuzione`.

È importante capire che _Schedulazione_ e _Dispatch_ <u>sono due cose diverse</u>.
La _schedulazione_  si occupa di gestire l'ordine dei processi pronti all'interno della lista, scegliendo quello che andrà in esecuzione, abbiamo la funzione `sistema` chiamata `schedulatore()` che si occupa di selezionare la testa di `pronti` e inserirla in `esecuzione`.
Il _dispatch_ si occupa invece di tutti i passaggi necessari per far cedere il controllo ad un processo ed assegnarlo ad un altro. Nel nostro sistema questa avviene quando viene chiamata la `CALL carica_stato; IRETQ` all'uscita del _gate_. Infatti queste fanno adesso riferimento al constesto del nuovo processo in `esecuzione`, aggiornando quindi i dati all'interno dei registri con quelli del nuovo processo.

Se un processo si trova in **esecuzione**, il processore sta eseguendo le sue istruzioni.
In questo momento _**il processo ha il controllo del processore**_, e può cambiare nel tempo il suo stato.
Con un solo processore **un solo processo per volta puo trovarsi in esecuzione**.

Mentre si trova in **esecuzione** un processo può chiedere di _terminare_, oppure di _sospendersi_ in attesa di un evento.
Nel primo caso il processo rientra nello stato di **terminazione** (abbiamo la routine `terminate_p()` nella nostra macchina).
Nel secondo invece passa allo stato **bloccato**.
Mentre un processo è bloccato il processore prosegue con un'altro nella coda `pronti`.
Quando l’evento atteso si verifica il processo torna nello stato di  **pronto** (può anche accadere che vada direttamente in esecuzione, anche se ciò non è mostrato esplicitamente in figura)

Nello schema si trova anche la _preemption_, che permette ad un processo di passare dall'**esecuzione** direttamente allo stato **pronto**.

In questo caso il processo non sta attendendo un evento, non è più in esecuzione soltanto perchè un altro processo, per un motivo o per un altro (ad esempio _priorità_) sta occupando il processore durante quello che doveva essere il suo tempo.
Nei sistemi senza _preemption_ un processo può occupare il processore indefinitamente senza lasciare mai il processore agli altri processi, basta che non chieda mai di terminare, che non generi processi a priorità più elevata o che non vada mai nello stato di **bloccato**.

Per quanto riguarda lo _scheduling_ esistono diverse strategie da poter seguire, quella vedremo noi è la _**strategia a priorità fissa**_.
Secondo questa politica, ad ogni processo, al momento della creazione, è assegnata una _**priorità numerica**_. Il nostro sistema si impegna quindi a garantire che, in ogni istante, si trovi **in esecuzione il processo che ha la massima priorità tra tutti quelli pronti**.

Questo ci permette di dover eseguire una azione di `schedulazione()` solo quando un processo passa da:
- **esecuzione** $\to$ **bloccato**: il processore si libera, e dunque dobbiamo mettere in esecuzione il processo a maggiore priorità tra quelli in `pronti`
- **bloccato** $\to$ **pronto**: si genera quando c’è un nuovo processo pronto, che potrebbe avere priorità maggiore di quello attualmente in esecuzione. Per rispettare la regola che abbiamo promesso di garantire potremmo dover fare _preemption_ sul processo in esecuzione.

Dobbiamo inoltre notare che anche quando un processo `P1` ne attiva un altro `P2` ci troviamo in una situazione simile, in quanto il nuovo processo appena creato viene inserito in `pronti`, e potrebbe avere priorità superiore a quello in `esecuzione`.

Quello che ci impegniamo a garantire quindi è che i processi _**non possano attivarne altri a priorità maggiore della propria**_.
Perciò nel nostro sistema <u>non saranno mai necessarie _preemption_</u>.

## 3.1. Transizione Processi

Sottolineamo che l'**_unico modo per transizionare da un processo ad un altro è tramite un gate della `IDT`_**.

Quando si accede ad un _gate_ della `IDT` (tramite _interruzione_, _eccezione_ o `int`), sappiamo che vengono già salvate delle informazioni (`5 long word`):
- [0] Informazioni per noi non rilevanti
- [1] `RSP`: indirizzo della _pila_ al momento del passaggio
- [2] `RFLAGS`: stato dei _flag_ al momento del passaggio
- [3] `CS`: livello precedente all'attraversamento del _gate_
- [4] `RIP`: istruzione dalla quale ripartire

Perciò tutto quello che dovrà fare il _dispatch_ è salvare il contenuto dei registri tramite la _routine_ invocata:
```x86asm
routine_gate:
    CALL salva_stato        ; Macro che salva il contenuto di tutti i registri in pila

    /*
    * corpo routine
    */

    CALL carica_stato       ; Macro che carica il contenuto di tutti i registri dalla pila
    IRETQ

```
<small>(le informazioni complete su `salva_stato` e `carica_stato` si trovano nel file `nucleo-8.3/sistema/sistema.s`)</small>

Inoltre, per capire a quale processo ci stiamo riferendo quando invochiamo `salva_stato` e `carica_stato` utilizziamo come già detto una variabile globale `esecuzione`.
`esecuzione` è implementata come un **puntatore a descrittore di processo** `des_proc*`:
```cpp
struct des_proc {
  /// identificatore numerico del processo
  natw id;
  /// livello di privilegio (LIV_UTENTE o LIV_SISTEMA)
  natw livello;
  /// precedenza nelle code dei processi
  natl precedenza;
  /// indirizzo della base della pila sistema
  vaddr punt_nucleo;
  /// copia dei registri generali del processore
  natq contesto[N_REG];
  /// radice del TRIE del processo (vedere la parte sulla memoria virtuale)
  paddr cr3;

  /// prossimo processo in coda
  des_proc* puntatore;

  /// parametro `f` passato alla `activate_p`/`_pe` che ha creato questo processo
  void (*corpo)(natq);
  /// parametro `a` passato alla `activate_p`/`_pe` che ha creato questo processo
  natq  parametro;
  /// @}
};
```

Lo _scheduler_, che invece identifica e ordina i processi **pronti**, utilizza un'altra variable globale `pronti` che punta ad una lista dove si trovano **tutti** i vari processi.
Poiché la nostra politica è quella di eseguire i processi a priorità maggiore, quando inseriamo i processi in questa lista, lo facciamo **in ordine di priorità**, cosicché il prossimo processo da eseguire sarà sempre quello **in cima alla lista**.

Per quanto riguarda la gestione dello stato **bloccato** vedremo che sarà necessario considerare ogni azione di bloccaggio in maniera diversa.

Le varie operazioni eseguite nel modulo `sistema` (come questa _routine_ stessa), sono **indipendenti dai processi**, che si trovano come congelati durante questo frangente.
<small>(finché la prima cosa nella _routine_ che facciamo è salvarne lo stato, e l'ultima cosa è caricarlo)</small>

Quando entriamo nel _gate_ da un processo `P1` salviamo, tra le varie informazioni, l'indirizzo della pila utilizzata dal processo, nella sezione `rsp` della _pila di sistema di `P1`_.
Facciamo ciò perché il registro `rsp` del processo in questo istante punta proprio alla _pila di sistema di `P1`_.

Quando eseguiamo quindi la `salva_stato`, il registro `rsp` punta **proprio la pila di sistema `P1`** salvata dall'entrata al _gate_.

Ciò significa che, `carica_stato` ripristinerà la _pila di sistema_ del processo `P2`, e la successiva `IRETQ` ripristinerà proprio le istruzioni relative a quel processo, reinserendo il valore della _pila di stack_ di `P2`.

Tutto il necessario per cambiare _processo_ è quindi **cambiare la variabile `esecuzione`** all'interno del _corpo routine_.

Quando viene selezionato il prossimo processo però può avvenire che ci sia un solo processo in esecuzione e che questo vada in **blocco**.
In questo caso la coda `pronti` è vuota, e dovremmo gestire il nostro processore in maniera che faccia comunque qualcosa in attesa il processo in **blocco** torni in **pronti**.

La strategia che adottiamo è quella di inserire un processo `dummy` con priorità **_più bassa di tutte_** (`0`), **_sempre presente in coda_**.
Questo processo consiste in nient'altro che un in un **_ciclo infinito_**, che ha come obiettivo quello di attendere semplicemente che arrivi un nuovo processo significativo nello stato di **pronto**.

## 3.2. Creazione nuovo Processo

Quando viene creato un processo (`activate_p(f, a, prec, livello)`), dobbiamo fare in modo che, quando questo venga selezionato per andare in escuzione lo faccia eseguendo la funzione `f(a)`.

Alla creazione del processo la `activate_p()`, oltre ad inserire un **puntatore al _processo_** in una nuova riga della `proc_table`, ne alloca tutte le strutture dati nella porzione `M1` della memoria:
- **Descrittore di processo** (`desc_proc`)
- _Pila Sistema_

<img class="5" src="./images/Processi/Creazione Processo.png">
<div class="grid2">
<div class="top">
<div class="p">

`desc_proc`
</div>

- `id`: codice identificativo nella `proc_table` del processo

- `livello`: `LIV_UTENTE` per tutti i _processi_ che vogliamo possano essere chiamati ed eseguiti dall'utente.

- `precedenza`: valore di `prec` passato da `activate_p()`

- `punt_nucleo`: punta alla base _pila di sistema_, **_come se fosse vuota_**.
    Questo è necessario per gestire opportunamente le interruzioni quando il processo sarà in operazione a livello `utente`.
    Infatti, in questo caso, la sia _pila sistema_ è <u>sempre vuota</u>.

- `contesto`: contiene il valore dei registri al momento della creazione del processo, quindi sono tutti vuoti, ad eccezione di:
  
  - `contesto[I_RDI]`: parametro `a` passato da `activate_p()`
  
  - `contesto[I_RSI]`: indirizzo della _pila sistema_
</div>
<div class="top">
<div class="p">

_Pila Sistema_
</div>

- `RIP`: funzione `f` passata da `acrivate_p()`

- `CS`: livello di chi è entrato nel _gate_ (solitamente `LIV_UTENTE`)

- `RFLAG`: Registro dei _flag_ completamente **resettato**, tranne per quanto riguarda due flag:
  
  - `IF = 1`: per permettere le interruzioni durante l'esecuzione della _routine_
  
  - `IOPL = sis`, setta la **priorità di sistema** alle periferiche `IO` per vietare l'utilizzo di istruzioni quali `IN`, `OUT`.
    Inoltre modifica il livello di privilegio per bloccare anche le istruzioni `STI` e `CLI`

- `RSP`: `rsp-ini`, vedremo più avanti in cosa consiste

<small>(quando si modifica `RFLAG` tramite `POPF` i flag `IF` e `IOPL` non vengono modificati)</small>
</div>
</div>

Il codice che gestisce tutto questo nella nostra macchina `QEMU` si trova nei file `sistema.cpp` e `sistema.s` nella _directory_ `nucleo-8.3/sistema/`.

