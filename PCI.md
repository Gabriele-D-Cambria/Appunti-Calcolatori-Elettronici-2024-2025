# 1. Indice

- [1. Indice](#1-indice)
- [2. Bus PCI](#2-bus-pci)
  - [2.1. Spazio di Configurazione](#21-spazio-di-configurazione)
  - [2.2. Gestione Interruzioni](#22-gestione-interruzioni)
  - [2.3. Il bus nel `PC AT`](#23-il-bus-nel-pc-at)

# 2. Bus PCI

Il _bus_ `PCI` (_Peripheral Component Interconnect_) è uno standard per i _bus_ introdotto da _Intel_.

La maggior parte dei _computer_ dell'epoca (come oggi) erano **espandibili**, ovvero potevano essere inserite delle _schede di espansione_ indipendenti da _IBM_ per aggiungere funzionalità al sistema.

Tuttavia questa possibilità genera dei problemi, specialmente in un mercato dove non era presente il coordinamento tra i vari produttori di schede.
Poteva infatti capitare che due schede diverse facessero riferimento agli stessi indirizzi di memoria, e che quindi quegli indirizzamenti fossero **sovrapposti**.
Questo problema si propagava anche in come venivano scritti i _driver_, che non erano quindi più in grado di distinguere se la scheda desiderata era effettivamente inserita, se si trattava di una scheda diversa oppure se non ci fosse installato nulla.

Dal momento che il `PC AT` era costruito con parti _standard_, il suo bus venne chiamato **ISA** (_Industry Standard Architecture_).
Questo _bus_ era però molto limitato e descriveva tutti i limiti del `PC AT`.

Nel 1992 la _Intel_ propose lo _standard_ **_Peripheral Component Interconnect_**, all'epoca a `32bit`, valido **per qualsiasi tipo di processore, non solo Intel**.
Nei _computer_ moderni si utilizza un'evoluzione del `PCI`, ovvero il `PCIexpress`, molto più complesso ma comunque compatibile con il precedente. Purtroppo non vedremo il `PCIexpress` in questo corso.

Lo standard `PCI` stabilisce:
- Quali sono i collegamenti del bus
- Il protocollo che le schede devono usare per comunicare.

Lo standard definisce inoltre **tre spazi di indirizzamento**: _spazio di memoria_, _spazio di I/O_ e _spazio di configurazione_.

I primi due spazi sono completamente analoghi a quelli che già conosciamo e sono quelli che il _software_ **deve utilizzare per dialogare con le periferiche connesse al bus**.

Per garantire il vincolo che i _registri_ delle _periferiche_ non occupino indirizzi sovrapposti si introducono due regole:
> Le _periferiche_ che rispettano lo standard **non possono scegliere autonomamente gli indirizzi dei propri registri**, ma devono contenere dei _**comparatori programmabili**_ in modo che questi indirizzi _siano impostati dal software della macchina_.
>
> Il _software_ può impostare questi comparatori all’avvio del sistema, tramite il nuovo _spazio di configurazione_.

Lo _spazio di configurazione_ è fatto in modo da poter accedere a dei **registri di configurazione** che ogni _periferica_ <u>deve avere per rispettare lo _standard_ in modo **univoco** e **senza conflitti</u>**.

Tramite questi registri il software di avvio (`PCI BIOS`) può scoprire quali periferiche sono connesse al bus.
Non solo, capisce anche di quanti indirizzi hanno bisogno e programma di conseguenza i comparatori affinché non ci siano _sovrapposizioni_.

La struttura che permette al _bus_ di essere indipendente dal processore è quella del _ponte ospite-PCI_ (detto _North-Gate_), un dispositivo che fa da tramite tra il _bus locale_ (quello dove risiede la **CPU**) e il _bus PCI_.

Lo standard `PCI` non prevede infatti un unico _bus_, bensì un **_albero di bus_**, che ha come radice il _bus_ collegato al _ponte ospite-PCI_. Ogni _bus_ è collegato all'albero tramite **ponti PCI-PCI**.
Per ogni albero si possono avere fino ad un massimo di 256 _bus_. Ogni _bus_ può inoltre collegare fino a **32 dispositivi**, ciascuno contenente **da 1 a 8 funzioni** (audio, video, ...).
Alcune funzioni possono persino fare da ponte verso altri tipi di _bus_, formando _ponti `PCI-ISA`_, _ponti `PCI-ATA`_, _ponti `PCI-USB`_, ...

<figure class="80">
<img class="40" src="./images/PCI/Esempio Architettura.png">
<figcaption>

Esempio di architettura con _bus_ `PCI`.
</figcaption>
</figure>

Le operazioni (lettura, scrittura, ...) sul _bus_ `PCI` sono dette **transazioni**.
Le _transazioni_ sono iniziate da un dispositivo _iniziatore_ che cerca di operare su un altro dispositivo _obiettivo_, e seguono il `clock`.

Lo standard permette a **qualsiasi dispositivo di essere _iniziatore_ o _obiettivo_ in transazioni diverse**.
Questo meccanismo permette il meccanismo di _accesso diretto alla memoria_ di cui parleremo in seguito.

Immaginiamo per ora (per semplicità) che **l'unico _iniziatore_ sia il _ponte ospite-PCI_**, che inizia le _transazioni_ sul bus `PCI` per tradurre le operazioni analoghe avviate sul _bus_ locale.

Le transazioni si svolgono in più fasi:
- **Fase di Indirizzamento**: dopo che l'_iniziatore_ specifica il tipo di operazione e l'indirizzo del primo byte da leggere/scrivere, **tutti i dispositivi che hanno registri nello spazio** confrontano queste informazioni con il contenuto dei loro comparatori.
  Al più uno troverà una corrispondenza, e quello diventerà l'_obiettivo_ della transazione.
- **Fase/i di Scambio di Dati**: Avviene quindi il trasferimento dei dati dall'_iniziatore_ all'_obiettivo_ (_scrittura_) o dall'_obiettivo_ all'_iniziatore_ (_lettura_).

I principali collegamenti del bus sono i seguenti: <small>(`#` indica gli attivi bassi)</small>

<div class="flexbox index" markdown="1">

| Nome       |   Iniziatore    |    Obiettivo    |                                                                                                   Ruolo                                                                                                    |
| ---------- | :-------------: | :-------------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| `FRAME#`   |     uscita      |    ingresso     |                                                                            Delimita l'inizio e il termine di ogni _transazione_                                                                            |
| `DEVSEL#`  |    ingresso     |     uscita      |                                                   Segnale attivato dall'obiettivo che **riconosce uno dei propri indirizzi** durante l'_indirizzamento_                                                    |
| `C[3:0]`   |     uscita      |    ingresso     |                                                                      Codificano il tipo di operazione nell'indirizzamento (`C[3:0]`)                                                                       |
| `BE#[3:0]` |     uscita      |    ingresso     |                                                                     Fungono da _byte-enabler_ nelle fasi di trasferimento (`BE#[3:0]`)                                                                     |
| `AD[31:0]` | ingresso/uscita | ingresso/uscita |                                             Codificano l'indirizzo nella _fase di indirizzamento_. <br> Trasportano i dati nelle _fasi di trasferimento dati_                                              |
| `TRDY#`    |    ingresso     |     uscita      |                                                                          (_target ready_), _Handshake_ nelle fasi di scambio dati                                                                          |
| `IRDY#`    |     uscita      |    ingresso     |                                                                        (_initiator ready_), _Handshake_ nelle fasi di scambio dati                                                                         |
| `STOP#`    |    ingresso     |     uscita      |                                                                              Serve a terminare prematuramente una transazione                                                                              |
| `CLK`      |    ingresso     |    ingresso     | Segnale di `clock`, tutti i dispositivi campionano i loro segnali in ingresso sul suo **fronte di salita**. <br>È molto più lento di quello della **CPU** (all'inizio era `33MHz` poi è passato a `64MHz`) |

</div>

Alcuni esempi di _temporizzazioni_:
<div class="grid2">
<div class="top">
<figure class="100">
<img class="80" src="./images/PCI/Transazione read.png">
<figcaption>

Lettura con 4 fasi di trasferimento dati.
</figcaption>
</figure>


</div>
<div class="top">

<figure class="100">
<img class="80" src="./images/PCI/Transazione write.png">
<figcaption>

Scrittura con 4 fasi di trasferimento dati.
</figcaption>
</figure>
</div>
</div>

Segue il seguente protocollo:
- L'_iniziatore_ pilota `C[3:0]` e `AD[31:0]` con il tipo di operazione e l'indirizzo iniziale del trasferimento
- Attiva `FRAME#` per segnalare l'inizio di una _transazione_
- Se un dispositivo riconosce il tipo di operazione e l'indirizzo attiva `DEVSEL#`
- Se nessuno lo attiva entro un certo numero di `clock`, l'inizializzatore termina l'operazione con un errore
- Altrimenti si prosegue con le fasi di trasferimento dati.

Nelle **operazioni di lettura**:
- L'_obiettivo_ pilota le linee `AD[31:0]` e segnala la loro validità tramite la linea `TRDY#`.
- Attende quindi che l'_iniziatore_ segnali di aver ricevuto i dati attivando `IRDY#`.
- Viceversa, l'_iniziatore_ era in attesa di `TRDY#` e quando lo trova attivo campiona `AD[31:0]` e una volta pronto attiva `IRDY#`.

Nelle scritture invece avviene l'opposto:
- L'_iniziatore_ pilota le linee `AD[31:0]` e `BE#[3:0]` per poi attivare `IRDY#` quando è pronto,
- Attende quindi che l'_obiettivo_ segnali che le linee sono valide tramite `TRDY#`.
- Viceversa, l'_obiettivo_ era in attesa di `IRDY#`, e quando lo trova attivo campiona `AD[31:0]` e `BE#[3:0]` e una volta pronto attiva `TRDY#`.

Ogni fase dati trasferisce **al più `4Byte` allineati naturalmente**.
Ciascuna fase si conclude quando sia `IRDY#` che `TRDY#` sono **attivi sullo stesso fronte di salita del clock**.

Il riutilizzo delle stesse linee per scopi diversi riduce i costi a scapito però della velocità di trasferimento. Fortunatamente, la possibilità di eseguire **più fasi dati** con _una singola fase di indirizzamento_ ci fa recuperaro un po' di velocità. È infatti sufficiente che l'_iniziatore_ mantenga `FRAME#` attivo quando lo è anche `IRDY#`.

L'_obiettivo_ può inoltre **attivare** `STOP#` per terminare forzatamente la transazione.



## 2.1. Spazio di Configurazione

Lo standard `PCI` prevede uno spazio di configurazione di `4 Byte` (_64 parole_) per ogni _funzione_. In questo spazio ciascuna funzione rende accessibili i propri registri di configurazione.

Un indirizzo nello _spazio di configurazione_ è composto da tre parti:
- `bus|8bit`: codice identificativo del _bus_
- `device|5bit`: dipende dalla posizione dove una scheda è fisicamente inserita
- `function|3bit`: indica la funzione del _device_

Il _bus_ più vicino alla **CPU** ha il codice `0`, gli altri vengono assegnati in maniera dinamica.

<div class="grid2">
<div class="">

Le funzioni rendono accessibili i loro registri di configurazione secondo lo schema sulla destra.

Non tutti i registri devono essere sempre presenti, ma, tranne per il ponte _ospite-PCI_, tutte le funzioni devono avere i seguenti registri:
- `Vendor ID`: (_lettura_) un codice che identifica il produttore della funzione.
  È assegnato ad ogni produttore da una autorità centrale (`PCI SIG`).
  L'_Intel_ ha come `ID: 8086`

- `Device ID`: (_lettura_) un codice che identifica la funzione.
  È assegnato dal produttore

- `Command`:  (_lettura_/_scrittura_) permette di abilitare o disabilitare varie capacità della funzione (vedere sotto);

- `Status`: (_lettura_) descrive alcune capacità della funzione, più lo stato di alcuni eventi, per lo più legati al verificarsi di errori

- `Revision ID`: (_lettura_) numero di revisione della funzione, assegnato dal produttore;

- `Class Code`: (_lettura_) un codice che identifica in modo generico il tipo di funzione;

- `Header Type`: (_lettura_) tipo di header; deve essere `0` per tutte le funzioni che non siano _ponti PCI-PCI_ o _ponti PCI-CardBus_.

In particolare, del registro `Command` ci interessano solo i bit `0`, `1` e `2`. Questi bit si occupano di:
- Abilitare la funzione nella _risposta alle transazioni_ nello spazio di `I/O` (`0`) e di `memoria` (`1`).
- Abilitare la funzione a comportarsi da _bus master_ qualore ne abbia la capacità (`2`)

Questi bit valgono di _default_ zero, ed è il _software di inizializzazione_ che deve settarli a 1 dopo aver assegnato alla funzione gli indirizzi necessari nei corrispondenti spazi, qualora questi corrispondano. 
Se ad esempio una funzione non ha registri nello spazio di `I/O` il suo bit `0` non sarà scrivibile.

</div>
<div class="">

<figure class="100">
<img class="80" src="./images/PCI/Registri Funzione.png">
<figcaption>

I registri con sfondo grigio sono obbligatori.
</figcaption>
</figure>
</div>
</div>

Nella nostra macchina il _ponte ospite-PCI_ è collegato come se fosse una periferica che esprime dei registri nello spazio di `I/O`:
- `CAP` (_Configuration Address Port_) (indirizzo `0xCF8`): permette di accedere allo _spazio di configurazione_, inserendo le 3 informazioni fondamentali e l'_offset_ di parola (`{bus, device, funzione, offset}`). Il ponte si preparerà quindi alla transazione

<img class="50" src="./images/PCI/Resgistro CAP.png">


- `CDP` (_Configuration Data Port_) (indirizzo `0xCFC`): permette di accedere alla parola selezionata tramite `CAP`.
  Se l'operazione è di lettura e nessun dispositivo risponde alla transazione il ponte restituisce **il valore `0xFFFF` al processore**.

Questi due registri possono essere usati per accedere allo spazio di configurazione in modo simile a come facciamo per la **memoria video**.
Per recuperare il risultato dell'operazione `IN/OUT` si utilizza `CDP`.

Lo scopo principale della fase di configurazione dei dispositivi è quello di **assegnare indirizzi univoci negli spazi di `I/O` e/o di `memoria`**.

Una volta che `CAP` è stato impostato, il _ponte ospite-PCI_ tradurrà le letture e le scritture in `CDP` in corrispondenti transizioni nello _spazio di configurazione_.

Prima di impostare `CAP` però il ponte attiverà l'uscita `IDSEL`, che è un entrata, presente in ogni _slot di espansione_, che è necessario attivare per poter trasmettere il numero della funzione e l'_offset_ della parola che contiene il registro (oltre ai _byte enable_ relativi al registro).

Un vincolo presente in tutti i dispositivi è che **la funzione `0` deve essere sempre presente**. In questo modo si permette allo _spazio di configurazione_  di essere accessibile già all'avvio del sistema.

Il costruttore di un blocco, oltre a deciderne la locazione, l'organizzazione interna e i _blocchi di indirizzi_ all'interno dei quali rendere disponibili i registri specifici della funzione, deve prevedere un `BAR` _Base Address Register_ nello spazio di configurazione.

<div class="grid2">
<div class="top">
<figure class="100">
<img class="75" src="./images/PCI/BAR memoria.png">
<figcaption>

`BAR` di **memoria**, $b \ge 4$
</figcaption>
</figure>
</div>
<div class="top">
<figure class="100">
<img class="75" src="./images/PCI/BAR io.png">
<figcaption>

`BAR` di **I/O**, $b \ge 2$
</figcaption>
</figure>
</div>
</div>

La dimensione del blocco è $2^b$ dove $b$ è il numero di bit **non scrivibili** utilizzati per fornire al _software di inizializzazione_ indicazioni sul tipo di blocco e sulla sua dimensione.
In particolare il bit `0` serve a capire se il blocco è pensato per lo spazio di `I/O` (`1`) o di `memoria` (`0`).
Si può scoprire il suo valore provando a scrivere tutti `1` nel `BAR` e rileggendo il risultato, per vedere quanti sono stati effettivamente scritti.

I blocchi possono essere assegnati solo a regioni allineate naturalmente alla loro dimensione.
Il _software di inizializzazione_ sceglierà quindi la regione e ne scriverà il numero nei bit scrivibili del `BAR`, così che contenga l'indirizzo di partenza del blocco.

Dopo aver assegnato una regione il _software di inizializzazione_ setterà il bit `0` o `1` del registro `ComMand`.
Da quel momento in poi la funzione **risponderà alle transazioni i cui indirizzi cadono in quella regione**.

Nella macchina `QEMU` l'inizializzazione è fatta dal `PCI BIOS`, e viene completata prima che il vostro _software_ parta.
Noi ci limiteremo ad accettare le impostazioni del `BIOS`, perciò tutto quello che ci serve è **sapere quali indirizzi il `BIOS` ha assegnato ai vari blocchi**, e possiamo farlo leggendo i `BAR`.

## 2.2. Gestione Interruzioni

I dispositivi `PCI` possono generare richieste di _interruzioni_, ma lo standard non prevede dettagli a riguardo.

Ogni dispositivo ha fino a quattro piedini in uscita per le richieste di interruzione: `INTA#`, `INTB#`, `INTC#` e `INTD#`.

Ogni funzione può quindi essere collegata ad **al più uno di questi piedini**.
Inoltre, funzioni dello stesso dispositivo possono essere collegate allo stesso piedino.

Il piedino utilizzato deve essere leggibile dal _registro di configurazione_ chiamato `Intr. Pin`, grande `1Byte` e di sola _lettura_.
Se vale `0` indica che la funzione non genera interruzione, `1` che utilizza `INTA#`, `2` che utilizza `INTB#` e così via...

Chi scrive il _software_ però vorrebbe sapere a quale piedino dell'`APIC` ciascuna funzione è collegata, informazione che dipende però dal progettista in quantonon standardizzata.
Questo deve quindi garantire che il `BIOS` scriva qualche informazione nel registro `Intr. line` (`1Byte`, _lettura_/_scrittura_) affinché il _software_ possa ricavare l'informazione.

Nel nostro caso il `BIOS` scrive in `Intr. line` **proprio il numero del piedino** dell'`APIC`, quindi possiamo limitarci a leggere questo registro.


## 2.3. Il bus nel `PC AT`

<div class="grid2">
<div class="">

Nella nostra macchina `QEMU` la struttura del bus è quella a destra.

Abbiamo un unico _bus `PCI`_ e due ponti:
1. Verso il _bus_ `ISA` dove si trovano le vecchie periferiche del `PC AT`, come tastiera e timer
2. Verso il _bus_ `ATA`, dove si trovano gli _HD_

In questa architettura, comune nei primi anni 2000, il _bus ospite-PCI_ veniva chiamato _North Bridge_ e spesso conteneva altre funzioni, come quella di controllare una porizone della memoria.

Inoltre i _ponti PCI-ISA_ e _PCI-ATA_ erano spesso inglobati in un altro dispositivo che svolgeva tutte queste funzioni, chiamato _South Bridge_
</div>
<div class="">
<figure class="100">
<img class="80" src="./images/PCI/Architettura QEMU.png">
<figcaption>

I numero all'interno delle funzioni `PCI` rappresentano `VendorID:DeviceID`
</figcaption>
</figure>
</div>
</div>
