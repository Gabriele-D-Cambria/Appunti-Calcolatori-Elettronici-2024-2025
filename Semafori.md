# 1. Indice

- [1. Indice](#1-indice)
- [2. Semafori](#2-semafori)
	- [2.1. Esempio - Mutua Esclusione](#21-esempio---mutua-esclusione)
	- [2.2. Esempio - Sincronizzazione](#22-esempio---sincronizzazione)
	- [2.3. Comandi Semafori e Gettoni](#23-comandi-semafori-e-gettoni)
	- [2.4. Realizzazione dei semafori](#24-realizzazione-dei-semafori)
	- [2.5. Utilizzo Debugger](#25-utilizzo-debugger)


# 2. Semafori

Per quanto riguarda la condivisione della memoria, nel nostro sistema i processi `utente`:
- **Condividono**: le sezioni `.text`, `.data`, `.bus` del modulo `utente` e lo `heap`.
- **Non condividono**: la _pila utente_

Questo tipo di condivisione può essere ottenuta evitando di rimpiazzare la parte di memoria condivisa quando si salta da un processo ad un altro.

Un sistema del genere ha senso se **i processi appartengono tutti allo stesso utente** e **fanno parte di un’unica applicazione**, che l'utente ha deciso di strutturare in più attività concorrenti. 
Da ora in poi ci limiteremo a considerare _<u>**solo questo caso**</u>_.

L'utente che scrive un'applicazione strutturata su più processi concorrenti deve affrontare dei problemi molto simili a quelli già affrontati a livello `sistema`.

In particolare, anche l'utente deve affrontare il problema dell'_**interferenza**_:
Infatti, mentre un processo sta eseguendo delle modifiche su una struttura dati comune, un altro processo potrebbe inserirsi e cominciare anche lui a modificare la stessa struttura dati e se l'utente non scrive il codice con attenzione, questo può causare malfunzionamenti, come abbiamo visto.

Si noti che, mentre nel codice di `sistema` abbiamo risolto il problema ricorrendo all'_atomicità_, realizzata **disabilitando le interruzioni** mentre il codice è in esecuzione, qui non possiamo fare la stessa cosa, in quanto **_le interruzioni devono restare abilitate_** mentre il è in eseuzione il codice `utente`.

Definiamo quindi due problemi quando ci sono più attività che vogliono essere eseguite in contemporanea:
- **Mutua esclusione**: l'ordine nel quale eseguiamo le varie attività non è rilevante.
  Un esempio pratico è la gestione del bagno durante un'esame.
  Non possono infatti esserci più studenti nello stesso momento in bagno, ed è necessario che uno torni poiché possa andare il prossimo.
  Tuttavia non è importante che uno studente vada prima di un altro.

- **Sincronizzazione**: alcune attività devono comunque essere eseguite prima di altre.
  Un caso comune è quello in cui un processo produce dei dati e li scrive in un buffer intermedio, da cui in altro processo li preleva per svolgere ulteriori elaborazioni.
  In questo caso, finché il primo processo non ha prodotto i dati, il secondo non deve andare in esecuzione leggendoli.
  Allo stesso tempo chi scrive deve assicurarsi che l'altro ha letto correttamente tutti i dati, poiché li andrebbe a sovrascrivere.

Per risolvere i problemi di _mutua esclusione_ e _sincronizzazione_, si suppone di avere delle scatore, chiamate _**semafori**_ che possono contenere degli oggetti, chiamati _**gettoni**_, tutti uguali.
Questo nome fu dato da _Dijkstra_ in relazione al fatto che nella prima formulazione ogni _semaforo_ poteva assumere solo due stati:
- "Rosso" $\to$ nessun _gettone_
- "Verde" $\to$ un _gettone_ presente

Nei _semafori_ possono essere eseguite solo due operazioni con i gettoni: **Inserimento** e **Prelievo**.
Per quanto riguarda l'inserimento, non è necessario che il processo che insersce il gettone lo abbia precedentemente prelevato da qualche parte, può infatti  crearlo sul momento.
Nel caso invece del prelievo del gettone, se queto non è presente, il processo **deve aspettare che qualcun altro ne inserisca uno**, entrando in uno stato di attesa dove _<u>non può fare nient’altro</u>_

## 2.1. Esempio - Mutua Esclusione

Supponiamo adesso di dover risolvere un problema di _**mutua esclusione**_.

Abbiamo:
- Persone `P1`, ..., `Pn`
- Azioni `A1`, ..., `An`

Vogliamo che le azioni _<u>**non possano mai essere eseguite contemporaneamente**</u>_.

Per risolvere questo problema è sufficente avere **un semaforo** che inizialmente contiene **un gettone** e imporre la regola che:
> _**"Solo chi ha il gettone può compiere una delle azioni. Al termine dell'azione è obbligatorio reinserire il gettone"**_

In questo modo, se una persona vuole compiere un'azione _deve prendere il gettone_, svuotando la scatola.
Se una seconda persona volesse compiere un'altra azione troverà quindi il **semaforo vuoto** e quindi dovrà attendere che la prima termini la sua.

L'attesa del gettone nella scatola vuota è quello che avevamo precedentemente chiamato come stato `bloccato` delle procedure.

Possiamo notare come in casi come questo può avvenire _preemption_.
Quando un processo riesce finalmente a recuperare il _gettone_, torna nella pila `pronti`, ed è quasi certo che abbia una priorità più elevata del processo attualmente in `esecuzione`, forzandone lo scambio.

## 2.2. Esempio - Sincronizzazione

Supponiamo invece un problema di **_sincronizzazione_**.

Abbiamo due persone:
- `Pa` che deve compiere l'azione `A`
- `Pb` che deve compiere l'azione `B`.

Vogliamo inoltre che **l'azione `B` venga eseguita sempre dopo l'azione `A`**.

È sufficiente in questo caso utilizzare due _semafori_:
- Una che eviti che `A` e `B` avvengano in contemporanea, inizializzata con `1 gettone`
- Una che indichi che `A` è stata eseguita e che `B` ancora no, inizializzata _**vuota**_

Operativamente questo significa che:
1. `Pa` **deve lasciare un gettone nel secondo semaforo** dopo aver eseguito l'azione `A`.
2. Prima di eseguire l'azione `B`, `Pb` deve **prendere un gettone dal secondo semaforo**.

Se `Pa` arriva per primo alla scatola, vi lascia il gettone così che `Pb` possa prenderlo e proseguire. 
Se invece arriva per primo `Pb`, troverà la scatola vuota e dovrà aspettare che `Pa` vi inserisca un gettone.

In entrambi i casi **_l'azione `B` non potrà essere eseguita se prima non è finita l'azione `A`_**.

## 2.3. Comandi Semafori e Gettoni

I comandi per creare i _semafori_ (scatole) e gestirli nella nostra macchina sono:
```cpp
/**
 * Crea un nuovo semaforo con n gettoni
 * @param n : numero gettoni
 * @return identificatore (0xFFFFFFFF se non è stato possibile crearlo)
 */
sem = sem_ini(n);     
/**
 * Prende un gettone. Blocca il processo se il semaforo è vuoto
 * @param sem : numero del semaforo
 */
sem_wait(sem);
/**
 * Inserisce un gettone, risvegliando uno dei processi bloccati in attesa
 * @param sem: numero del semaforo 
 */
sem_signal(sem);
```

Uno _snippet_ di codice per la soluzione dei problemi:
<div class="grid2">
<div class="top">
<div class="p">

**_Mutua Esclusione_**
</div>

```cpp
natl mutex = sem_ini(1);
sem_wait(sem);
A_i();        // Azioni di A_i
sem_signal(sem);
```

</div>
<div class="top">
<div class="p">

**_Sincronizzazione_**
</div>

```cpp
natl mutex = sem_ini(1);
natl sync = sem_ini(0);

void A(){
    sem_wait(mutex);
    // ...
    sem_signal(sync);
    sem_signal(mutex);
}

void B(){
    sem_wait(sync);
    sem_wait(mutex);
    // ...
    sem_signal(mutex);
}
```
</div>
</div>

Nei casi di sincronizzazione, si può arrivare a sviluppare semafori che hanno funzionamento molto simile a quello degli _handshake_.
Riprendiamo infatti il caso dei due utenti che utilizzano un _buffer_ per comunicare:
- Il primo vi può scrivere solo quando il secondo ha già letto
- Il secondo può leggerlo solo quando il primo ha finito di scrivere

Quello che faremo è implementare qualcosa molto simile all'_handshake_ `dav_`/`rfd`:
```cpp
natl S1 = sem_ini(1);
natl S2 = sem_ini(0);
void scrittura(){
    sem_wait(S1);
    // corpo
    sem_signal(S2);
}
void lettura(){
    sem_wait(S2);
    // corpo
    sem_signal(S1);
}
```

## 2.4. Realizzazione dei semafori

Per realizzare i semafori prevediamo la seguente struttura dati **definita nel codice `sistema`**:
```cpp
struct des_sem {
	/// se >= 0, numero di gettoni contenuti;
	/// se < 0, il valore assoluto è il numero di processi in coda
	int counter;
	/// coda di processi bloccati sul semaforo
	des_proc* pointer;
};
```

Dove:
- `counter`: conta i _gettoni_ contenuti nel _semaforo_ (se $\ge$ a 0).
    Gli permettiamo di andare sotto zero, indicando il numero di _processi_ in attesa a quel _semaforo_.

- `pointer`: è la _coda_ dei _processi_ in attesa al _semaforo_, ordinati per precedenza decrescente (come lo è la coda `pronti`).
    Verrano rimessi in coda `pronti` quando riceveranno il _gettone_, per effetto di `sem_signal()`

Come tutte le primitive, anche `sem_ini()`, `sem_wait()` e `sem_signal()` sono invocate tramite una istruzione `INT`, con tutte le conseguenze che abbiamo visto fin'ora.

Possiamo vedere di seguito la parte `C++` della primitiva `sem_ini()`:
```cpp
des_sem array_dess[MAX_SEM * 2];

extern "C" void c_sem_ini(int v){
    natl i = alloca_sem();
    if(i != 0xFFFFFFFF)
        array_dess[i].counter = val;
    esecuzione->contesto[I_RAX] = i;
}
```

Per l'allocazione dei _semafori_ riserviamo **un array di strutture `des_sem`**, chiamato `array_dess`.
Ogni volta che l'utente ci chiede un nuovo _semaforo_, quello che facciamo è limitarci ad utilizzare una nuova struttura dall'_array_.

In questo modo, l'_array_ ci permette di risalire facilmente alla struttura `des_sem` corretta durante la ricerca dell'identificatore del semaforo passato nelle _primitive_ `sem_wait()` e `sem_signal()`. 

Come vedremo, anche il modulo `io` utilizza dei _semafori_.
Per evitare che l'utente possa erroneamente usare i _semafori_ allocati dal modulo `io`, i _semafori_ vengono idealmente distinti in
- `utente`: sono quelli che si trovano nelle prime `MAX_SEM` posizioni dell'_array_
- `sistema`: sono i rimanenti

La funzione `alloca_sem()` allocherà quindi un indice appartenente ad una delle due parti dell'array, in base al **livello di privilegio** che il processo aveva quando ha invocato la primitiva (nella _pila sistema_). 

Vediamo ora la parte `C++` della primitiva `sem_wait()`:
```cpp
extern "C" void c_sem_wait(natl sem){
    // una primitiva non deve mai fidarsi dei parametri
    if (!sem_valido(sem)) {
		flog(LOG_WARN, "sem_wait: semaforo errato: %u", sem);
		c_abort_p();
		return;
	}

	des_sem* s = &array_dess[sem];
	s->counter--;

	if (s->counter < 0) {
		inserimento_lista(s->pointer, esecuzione);
		schedulatore();
	}
}
```

Nel caso di _semaforo_ senza _gettoni_, il processo attualmente in esecuzione viene inserito nella _coda del semaforo_ e ne viene scelto un altro invocando la funzione `schedulatore()`. 
Questa non fa altro che estrarre dalla _coda `pronti`_ il processo a più alta priorità e lo fa puntare dalla variabile `esecuzione`.
In questo modo, la _routine_ `carica_stato` (che verrà eseguita subito dopo) farà saltare al nuovo processo, di fatto bloccando il precedente.

Vediamo infine la parte `C++` della primitiva `sem_signal()`:
```cpp
extern "C" void c_sem_signal(natl sem)
{
	// una primitiva non deve mai fidarsi dei parametri
	if (!sem_valido(sem)) {
		flog(LOG_WARN, "sem_signal: semaforo errato: %u", sem);
		c_abort_p();
		return;
	}

	des_sem* s = &array_dess[sem];
	s->counter++;

	if (s->counter <= 0) {
		des_proc* lavoro = rimozione_lista(s->pointer);
		inspronti();	// preemption
		inserimento_lista(pronti, lavoro);
		schedulatore();	// preemption
	}
}
```

Se ci sono _processi_ in coda sul semaforo, la primitiva ne estrae quello a priorità più alta attraverso la funzione `rimozione_lista()`. 

A questo punto la primitiva deve scegliere quale processo deve proseguire, tra quello in esecuzione e quello appena estratto. 

La cosa più semplice è di inserire entrambi i processi in coda pronti e lasciar scegliere alla funzione `schedulatore()`.

Sia la `sem_wait()` che la `sem_signal()`, prima di usare `sem`, controllano che questo sia **un valido identificatore di semaforo**, ovvero che sia stato precedentemente restituito da una `sem_ini()` **_per il livello corretto_**, e terminare forzatamente il processo in caso contrario. 

## 2.5. Utilizzo Debugger

Le estensioni del debugger che abbiamo nella nostra macchina `QEMU` contengono anche alcuni comandi relativi ai semafori:
- `sem`: mostra lo stato di tutti i semafori allocati
- `sem waiting`: mostra lo stato di tutti i semafori la cui coda non è vuota.
  È eseguito automaticamente ogni volta che il _debugger_ riacquisisce controllo.

Lo stato dei semafori è mostrato nella forma: `{counter, lista_processi}`.