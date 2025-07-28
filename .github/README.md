# Automazione Statistiche Q&A

Questo sistema automatizza l'aggiornamento delle statistiche delle domande e risposte nel README principale.

## 🔧 Come Funziona

### 1. GitHub Action
Il file `.github/workflows/update-qa-stats.yml` contiene un workflow che:

- **Si attiva automaticamente** quando:
  - Modifichi il file `Domande e Risposte.md`
  - Ogni lunedì alle 6:00 AM
  - Manualmente dal tab "Actions" di GitHub

- **Calcola le statistiche** analizzando:
  - Tutte le righe che iniziano con `### Domanda X.Y`
  - Quelle che contengono `(answered)` per le risposte complete

- **Aggiorna il README** sostituendo il placeholder:
  ```markdown
  <!-- QA_PERCENTAGE -->!-- /QA_PERCENTAGE -->
  ```

### 2. Script di Test Locale
Il file `test-qa-stats.sh` permette di testare il calcolo localmente:

```bash
./test-qa-stats.sh
```

I risultati vengono salvati in `.github/json/qa-stats-test.json` per l'analisi.

## 📊 Statistiche Attuali

- **Domande totali:** 111
- **Domande con risposta:** 56
- **Percentuale completamento:** 50.5%

## 🚀 Come Aggiungere Nuove Domande

1. **Aggiungi una nuova domanda** in `Domande e Risposte.md`:
   ```markdown
   ### Domanda X.Y
   Testo della domanda...
   ```

2. **Quando completi la risposta**, aggiungi `(answered)`:
   ```markdown
   ### Domanda X.Y (answered)
   Testo della domanda...
   
   **Risposta:**
   Testo della risposta completa...
   ```

3. **Committa e pusha** - la GitHub Action aggiornerà automaticamente le statistiche!

## 🔍 Monitoraggio

- Visualizza l'esecuzione delle GitHub Actions nella tab **"Actions"** del repository
- I commit automatici hanno il prefisso `🤖`
- Le statistiche sono archiviate in `.github/json/qa-stats.json`
- In caso di errori, controlla i log nella sezione Actions

## 🛠️ Risoluzione Problemi

**Se la percentuale non si aggiorna:**
1. Verifica che i placeholder `<!-- QA_PERCENTAGE -->` siano presenti nel README
2. Controlla che le domande abbiano il formato corretto `### Domanda X.Y`
3. Assicurati che `(answered)` sia presente nelle domande completate
4. Controlla i logs nella tab Actions di GitHub

**Test manuale:**
```bash
# Conta domande totali
grep -c "^### Domanda [0-9]*\.[0-9]*" "Domande e Risposte.md"

# Conta domande con risposta
grep -c "^### Domanda [0-9]*\.[0-9]*.*\(answered\)" "Domande e Risposte.md"
```
