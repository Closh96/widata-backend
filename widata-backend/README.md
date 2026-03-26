# WiData Backend — IoT Sensor API

Backend REST API sviluppata in Flask per raccogliere, salvare e analizzare misure 
provenienti da sensori IoT. Progetto realizzato come prova pratica per il 
secondo step di selezione WiData.

---

## Tecnologie utilizzate

- Python 3.11+
- Flask 3.1.0
- Flask-SQLAlchemy 3.1.1
- SQLite
- PyTest + pytest-flask
- Docker + docker-compose

---

## Struttura del progetto
```
widata-backend/
  app/
    __init__.py       # factory function, configurazione Flask e DB
    models.py         # modelli SQLAlchemy (Measure, Metric)
    routes.py         # endpoint REST API
    stats.py          # calcolo statistiche (min, max, avg, count)
  tests/
    test_api.py       # test automatici con PyTest
  run.py              # entry point dell'applicazione
  requirements.txt    # dipendenze Python
  Dockerfile          # istruzioni per il container
  docker-compose.yml  # orchestrazione del container
```

---

## Avvio del progetto

### Con Docker (consigliato)

Assicurarsi di avere Docker Desktop installato e in esecuzione, poi lanciare:
```bash
docker-compose up --build
```

L'API sarà disponibile su: http://localhost:8000

### Senza Docker (sviluppo locale)
```bash
pip install -r requirements.txt
python run.py
```

---

## Esecuzione dei test con PyTest

Assicurarsi di essere nella cartella del progetto, poi lanciare:
```bash
python -m pytest tests/ -v
```
Con -v viene mostrato il dettaglio di ogni test eseguito.

Output atteso: 6 test PASSED

---

## Endpoints API

### POST /measures
Riceve e salva una misurazione da un sensore.

Payload:
```json
{
    "sensor_id": "sensor-123",
    "timestamp": "2026-03-23T10:15:30Z",
    "metrics": {
        "temperature": 22.4,
        "humidity": 45.2
    }
}
```

Risposta (201):
```json
{
    "id": 1,
    "message": "Misura salvata"
}
```

---

### GET /measures
Restituisce lo storico di tutte le misure salvate.

Filtro opzionale per sensore:

    GET /measures?sensor_id=sensor-123

Risposta (200):
```json
[
    {
        "id": 1,
        "sensor_id": "sensor-123",
        "timestamp": "2026-03-23T10:15:30",
        "metrics": {
            "temperature": 22.4,
            "humidity": 45.2
        }
    }
]
```

---

### GET /stats
Restituisce statistiche (min, max, avg, count) sulle metriche raccolte.

Filtri opzionali:

    GET /stats?sensor_id=sensor-123
    GET /stats?metric=temperature
    GET /stats?sensor_id=sensor-123&metric=temperature

Risposta (200):
```json
{
    "temperature": {
        "avg": 22.4,
        "count": 1,
        "max": 22.4,
        "min": 22.4
    },
    "humidity": {
        "avg": 45.2,
        "count": 1,
        "max": 45.2,
        "min": 45.2
    }
}
```

---

## Esempi con curl

Inviare una misura:
```bash
curl -X POST http://localhost:8000/measures \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor-123",
    "timestamp": "2026-03-23T10:15:30Z",
    "metrics": { "temperature": 22.4, "humidity": 45.2 }
  }'
```

Recuperare lo storico:
```bash
curl http://localhost:8000/measures
```

Recuperare lo storico di un sensore specifico:
```bash
curl http://localhost:8000/measures?sensor_id=sensor-123
```

Consultare le statistiche:
```bash
curl http://localhost:8000/stats
```

Statistiche filtrate:
```bash
curl "http://localhost:8000/stats?sensor_id=sensor-123&metric=temperature"
```

---

## Scelte tecniche e trade-off

**Database — SQLite**
Ho approfondito i vari database, cercato di capire quale fosse il migliore e
alla fine ho scelto SQLite per semplicità di setup: non ha bisogno di un server separato. 
È perfetto per progetti piccoli, prototipi e prove tecniche come questa. 

Con più tempo, approfondirei PostgreSQL e migrerei lì, essendo un database vero e proprio che 
gira come un server separato. Supporta molte connessioni contemporanee ed è molto 
più veloce con grandi quantità di dati. Lo svantaggio è che richiede installazione 
e configurazione extra, poichè nel nostro docker-compose.yml avremmo dovuto aggiungere 
un secondo container solo per il database.

Un'altra alternativa sarebbe potuta essere MySQL, Meno potente di PostgreSQL ma 
comunque valido per un contesto come questo.

MongoDB sarebbe stato interessante per il nostro caso perché le metriche sono già 
in formato JSON, ma avrebbe richiesto una libreria diversa e un approccio completamente 
diverso alla modellazione dei dati.


**ORM — Flask-SQLAlchemy**
Facendo varie ricerce, per rendere il codice più leggibile e veloce da sviluppare, 
mi sono imbattuto negli ORM, che mi permettono di lavorare con un database relazionale 
utilizzando oggetti del linguaggio invece di scrivere query SQL direttamente.

Come ORM ho deciso di usare SQLAlchemy (che appare nel sito ufficiale di Flask come estensione) 
invece di query SQL grezze per tre motivi: 
il codice è più leggibile e manutenibile (definendo le tabelle come classi Python tramite i modelli); 
gestisce automaticamente la connessione al database; 
in un contesto lavorativo si eviterebbe il rischio di un possibile attacco dove un utente 
malintenzionato può mandare dati costruiti apposta per manipolare le query.

SQLAlchemy avrebbe funzionato anche senza la parte Flask, ma richiedeva più 
configurazione manuale per integrarlo con esso.


**Struttura dati — due tabelle separate (Measure e Metric)**
Il primo istinto era di creare una tabella con colonne fisse con Sensor-A e Sensor-B.
Però le metriche sono variabili e ogni sensore può mandare metriche diverse con nomi diversi. 
Se domani arrivasse un sensore che manda co2_level e noise_db, dovrei modificare la struttura 
del database aggiungendo nuove colonne. Così invece aggiungo semplicemente una riga 
in Metric e la struttura del database non cambia mai.


**Factory function per Flask**
Con un'app globale avrebbe funzionato, ma l'app verrebbe creata una volta sola al momento dell'import 
con una configurazione fissa. Non potrei creare una versione diversa per i test senza modificare il file.
Controllando la documentazione ufficiale ho notato che con create_app(), 
ogni volta che la funzione viene chiamata, costruisce e restituisce una nuova istanza dell'app 
con la configurazione che desidero. Il vantaggio è che se in futuro volessi aggiungere 
una configurazione di produzione, basterebbe aggiungere un parametro senza toccare nulla del resto del codice.

---

## Cosa migliorerei con più tempo

- Migrare da SQLite a PostgreSQL per un uso in produzione
- Aggiungere paginazione al GET /measures perchè con molti dati diventerebbe pesante
- Aggiungere autenticazione alle API (es. API key per i sensori)
- Aggiungere filtri per range temporale (es. misure delle ultime 24 ore)