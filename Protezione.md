# 1. Indice

- [1. Indice](#1-indice)
- [2. Protezione](#2-protezione)
  - [2.1. Disponibilità della memoria](#21-disponibilità-della-memoria)
  - [2.2. Passaggi tra contesti](#22-passaggi-tra-contesti)


# 2. Protezione

Fin'ora i programmmi che abbiamo scritto e quelli degli esempi, hanno sempre avuto **il pieno controllo di tutta la macchina `QEMU`**.
I programmi avevano a disposizione infatti **tutto lo spazio di I/O** e **tutto lo spazio di memoria**.

Nella realtà questa situazione è possibile solo qualora eseguissimo un unico programma alla volta, così come veniva fatto con i primi calcolatori, quando un calcolatore occupava l’area di una palestra, ed una Università poteva averne uno o forse due.

I primi _calcolatori_ venivano infatti usati in modalità `batch`:  
Gli utenti, ricercatori o studenti, preparavano i programmi a casa su fogli di carta scrivendoli in `linguaggio macchina` o in `FORTRAN`.
Portavano poi i loro fogli al centro di calcolo, dove alcuni impiegati potevano trascriverli su nastro o su schede perforate.
Ogni pacco di schede, contenente il programma di un utente, rappresentava un _job_.
L’utente consegnava poi il suo _job_ agli operatori del calcolatore e in un secondo momento sarebbe dovuto ritornare a ritirare i risultati, tipicamente sotto forma di un tabulato stampato su carta.

Gli operatori erano **gli unici** ad avere accesso alla sala del calcolatore, e aspettavano di avere un mazzo (`batch`) di _job_ e poi lo caricavano sul lettore di schede.

Questo eseguiva i _job_ **uno alla volta**. Quando il primo _job_ terminava, veniva caricato automaticamente il successivo.
In questi sistemi era quindi importante cercare di massimizzare il numero di _job_ completati ogni ora, così da sfruttare il costosissimo processore nel modo più efficiente possibile.

Supponiamo però ora che un _job1_ debba caricare una serie di dati da un nastro magnetico **a controllo di programma**.
Il nastro magnetico va però riavvolto, operazione che richiede diversi secondi. Il costosissimo processore viene così sprecato in un banale ciclo di istruzioni che legge ripetutamente i registri del controllore del nastro, per attendere che il nastro raggiunga la posizione desiderata.
La "vera" elaborazione del _job1_, quella che ha davvero bisogno delle piene capacità della **CPU**, comincerà infatti solo quando **tutti i dati saranno stati letti**.

Per gli operatori del calcolatore sarebbe molto meglio se il controllore del nastro fosse programmato per inviare _una richiesta di interruzione dopo il riavvolgimento_.
In questo modo, durante il tempo di riavvolgimento, si potrebbe utilizzare la **CPU** per cominciare ad eseguire il prossimo _job_ del `batch`.
All’arrivo della richiesta di interruzione si potrebbe poi ritornare al _job1_.

Potremmo quindi pensare di utilizzare due _routine_:
1. `Routine1`: avvia il riavvolgimento del nastro e cede il controllo ad un altro _job_
2. `Routine2`: (da associare alle richieste di interruzione provenienti dal controllore del nastro) restituisce il controllo al job che aveva invocato la `Routine1`

Questa soluzione, che poi sarà quella che vedremo più avanti, presenta però dei problemi legati alla natura dei _job_:
1. Costringere l'utente 1 a scrivere il programma tramite _routine_ invece di dialogare direttamente con il controllore
1. Costringere l'utente 2 a non disattivare le interruzioni

Un'opzione potrebbe essere controllare manualmente i _job_ consegnati per verificare che non disattivino le interruzioni né eseguano processi all'I/O direttamente da programma.
Tuttavia questa operazione è estremamente difficile e potenzialmente impossibile, in quanto il programmatore può utilizzare metodi più o meno complessi per mascherare le sue azioni.

Sono quindi state apportate delle modifiche sull'**hardware** per imporre al processore che **_alcune operazioni sono vietate in determinati contesti_**.
Per risolvere il primo problema creiamo una distinzione del contesto nel quale la **CPU** sta operando, differenziando tra:
- Contesto `utente`
- Contesto `sistema`

Andremo quindi a **vietare le istruzioni di `IN`, `OUT`, `CLI`, `STI` per il _contesto `utente`_**, permettendole solamente quando ci si trova nel _contesto `sistema`_.

Dovremo quindi solamente far capire al processore **in quale contesto si trova** (cosa relativamente semplice poiché si tratta di due contesti).
È infatti sufficente fornire un singolo `bit` al processore che se settato indica il _contesto sistema_, se resettato invece si trova nel _contesto utente_.
Questo bit si trova nel registro chiamato `CS` (_Code Selector_).

In questo modo il processore, qual'ora trovi una delle operazioni "vietate", andrà a prima a controllare il contesto nel quale si trova prima di eseguirla eventualmente _vietandone l'esecuzione_.


L'idea generale di questo nuovo sistema è quindi la seguente:
1. All'accensione, tramite il _bootstrap_, si inizializza il processore a livello `sistema`
2. Quando viene inizializzato un _job_ si passa a livello `utente`
3. Quando viene generata un'iterruzione esterna, si torna al livello `sistema`
4. Gestita l'interruzione esterna, si torna al _job_ nel livello `utente`

Per far funzionare ciò dobbiamo quindi _togliere agli utenti la possibilità di poter sfruttare le interruzioni_, permettendo loro però di poter comunque chiamare le _routine_ e utilizzarle.

Uno dei modi per poterlo fare è quello di **sfruttare le eccezioni**: permetteremo all'utente di utilizzare una determinata eccezione (non modificabile nella memoria), salvando in un registro quale routine si vuole chiamare.

La _intel_ ha adottato un sistema diverso, introducendo un nuovo operando assembler `INT $tipo` che fa da _gate_ per chiamare la _routine_ (_primitiva di sistema_) e passare in modalità `sistema`.
`$tipo` è un numero tra `0` e `255`, ed ha lo stesso significato del tipo delle eccezioni e delle interruzioni esterne.

Per fare il passaggio inverso da `sistema` a `utente` l'**unica istruzione utilizzabile** è la `IRETQ`, chiamata alla fine della _routine_.

## 2.1. Disponibilità della memoria

In tutto questo contesto va però _ridefinita la porzione di memoria concessa all'utente_.
Se infatti avesse a disposizione tutta la memoria il'utente potrebbe:
- Modificare le _routine_ a suo piacimento
- Modificare la tabella `IDT` e rimuovere le routine presenti

Rendendo inutile la separazione dei contesti.

Dobbiamo quindi trovare un modo per _vietare certi indirizzi_.
Parleremo più avanti della _paginazione_, per ora facciamo invece una semplificazione:
Immaginiamo dunque di avere un registro nel processore che contiene **l'ultimo indirizzo valido di memoria utilizzabile dagli utenti**.
Ogni qualvolta che il processore effettuerà un accesso in memoria, prima controllerà il contesto e, nel caso fosse nel _contesto utente_, controllerà che l'indirizzo desiderato sia **_maggiore o uguale_** a quello contenuto nel registro.

Da ora in poi chiameremo `M1` la parte di memoria ad indirizzi inferiori al limite (_system-only_), e `M2` la rimanente.
Il registro contenente l'indirizzo di separazione viene inizializzato tramite il programma di _bootstrap_, lo stesso che carica `IDT` e il corpo delle varie _orutine_ e strutture dati

## 2.2. Passaggi tra contesti

Il livello di privilegio può essere cambiato solo in due modi:
<div class="flexbox" markdown="1">

| Operazione         | Livello di privilegio    |
| ------------------ | ------------------------ |
| _gate_ della `IDT` | `utente` $\to$ `sistema` |
| Istruzione `IRETQ` | `sistema` $\to$ `utente` |

</div>

Ai _gate_ della `IDT` si può passare tramite tre operazioni:
- _Eccezioni_
- _Interruzioni_
- Operazione `INT`

Ogni _gate_ della `IDT` occupa `16Byte` e contiene le segueni informazioni:
- Il puntatore alla `Routine` a cui saltare (`8 Byte`)

- `P` (_Presenza_): indica se la riga contiene bit significativi

- `I/T`: indica se il _gate_ è di tipo _Interrupt_ (azzera `IF`) o _Trap_ (mantiene `IF` invariato).

- `L` (_Livello_): indica il _livello di privilegio_ al quale portare il processore **dopo** aver passato il _gate_. Nel nostro caso sarà sempre settato a `sistema`.<!--  -->

- `DPL` (_Descriptor Privilege Level_): specifica il **livello di privilegio minimo** che deve avere il processore **prima** di passare il gate. Può vietare l'utilizzo di alcuni gate attraverso l'istruzione `INT` generando un'_eccezione di protezione_ `13`. 
  I programmatori di sistema possono settarlo come:
   - `sistema`: nei _gate_ delle _interruzioni esterne_, così che possano essere attraversati solo da codice protetto
   - `utente`: nei _gate_ delle _primitive_, per permetterne l'utilizzo da parte degli utenti

La `IDT` viene inizializzata tramite il programma di _bootstrap_, in particolare utilizzando l'istruzione `LIDTR` che carica l'indirizzo della `IDT` nel registro `IDTR` che il processore utilizza per accedere ala tabella e allocando `IDT` nella memoria `M1`.
Per non permettere la modifica di `IDT` da parte dell'utente l'istruzione `LIDTR` è anch'essa **vietata** nel contesto _utente_.

Quando il processore accede all'`IDT` accadono questi passaggi:

1. Innanzitutto il processore si procura il _tipo_ dell'interruzione
   - In caso di _eccezione_ il tipo è implicito;
   - In caso di _interruzione **esterna**_, riceve il tipo dall'`APIC`;
   - In caso di _interruzione **software**_ è l'argomento specificato nell'istruzione `INT $tipo`.

2. Verifica se il bit `P` associato al tipo è zero, generando un'eccezione di _gate non presente_ `11` in caso positivo, negli altri casi procede.

3. Se sta gestendo una _interruzione software_ o `int3`, confronta il livello corrente con il campo `DPL` del gate.
   Se il livello corrente è meno privilegiato di `DPL` si genera una _eccezione di protezione_ `13`.

4. Altrimenti, confronta `CS` con `L`.
   Se `L` è **inferiore**, si genera ancora un'_eccezione di protezione_ `13`. 
   Questo perché attraverso la `IDT` **<u>non è possibile abbassare il livello di privilegio</u>** ma solamente mantenerlo o aumentarlo.

5. Negli altri casi, il processore salva in un registro di appoggio (chiamiamolo `SRSP`) il contenuto corrente di `RSP`

6. Se `CS` è diverso da `L` esegue un _cambio di pila_ (_pila sistema/utente_ nel nostro caso), caricando un nuovo valore in `RSP`
   <small>(vedremo più avanti dove si trova questo valore)</small>

7. Salva in pila `5 long word`. In ordine:
   - [0] `SS`: `1 long word` non significativa (rimasuglio della segmentazione, ...)
   - [1] `SRSP`: pila salvata al passo 5. Nel caso di cambio pila è quella `utente`, altrimenti punta alla pila `sistema` stessa
   - [2] `RFLAGS`: registro dei flag
   - [3] `CS`: vecchio valore del `CS` da ripristinare successivamente
   - [4] `RIP`: indirizzo della prima istruzione da eseguire all'uscita del gate. Nel caso di interruzioni software `INT $tipo` questo contiene l'istruzione immediatamente successiva

8. Il processore poi azzera:
   - `TF` in ogni caso;
   - `IF` solo se il gate è di tipo _Interrupt_.

9. Salta infine all'indirizzo della _routine_ puntata dal gate.

Le interruzioni di protezione sono progetatte per poter **solamente _mantenere o alzare_** il _livello di privilegio_.

Il cambio di pila è **_necessario_**, è ha due motivazioni:
- Il processore deve garantire di poter scrivere le 5 `long word` senza sovrascrivere altre cose, e non può quindi fidarsi di `RSP` che è completamente a servizio dell'utente.
- Queste informazioni sono salvate nella memoria di sistema, in modo che l’utente **non le possa corrompere**.
  In particolare, è bene che l’utente non possa modificare il valore salvato di `CS`.

Quando si chiama la `IRETQ` per tornare indietro, si effettua un'accesso alla _pila di sistema_:
1. Confronta il valore corrente di `CS` con quello salvato in pila, generando un _eccezione di protezione_ `13` qualora quello salvato fosse più **alto**;
2. Ripristina i valori di `RIP`, `CS`, `RFLAGS` e `RSP` leggendo i corrispondenti valori dalla pila.

La `IRETQ` è progettata per poter **solamente _abbassare_** il _livello di privilegio_.

Nei primi processori _intel_ ogni _job_ aveva un proprio **segmento** di un registro chiamato `TSS`, che indicava la pila a disposizione del _job_.
Per identificare la _pila sistema_ si accedeva prima ad un'altro registro, `TR` (_Task Register_), che indicava quale segmento era associato a quel _job_.

