flask-project

# Run application
flask run

# To run in debug mode 

export FLASK_ENV=development
flask run

### Run

Before run the Application, create models and create database with run:

```
python3 models.py
python3 generatedb.py
```

# App running on
http://127.0.0.1:5000/


# Flask-Login
# lezione https://unive.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=ad582be6-088e-4820-b886-ad0c00b19878

# Tutorato
# https://unive.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=6632cdc0-bf10-44a0-abeb-ad1300820204

# Tema 2 Appunti

Calendario di slot orari (es 1h 30min)
Per ogni slot ci deve essere una politica di controllo degli accessi
Per esempio in ogni slot possono entrare max 10 persone contemporaneamnte

Definire delle policy, ad esempio non è possibile prenotare più di 3 volte a settimana per poter permettere a tutti di prenotare 

Contact tracing, tenere traccia sotrico prenotazioni ultima settimana (trigger)

Definire dei ruoi e politiche di autorizzazione

Transazioni

