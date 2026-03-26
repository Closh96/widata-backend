# Dockerfile

# Partiamo da un'immagine Python ufficiale leggera
FROM python:3.11-slim

# Creiamo la cartella di lavoro dentro il container
WORKDIR /app

# Prima copiamo solo requirements.txt e installiamo le dipendenze.
# Questo sfrutta il "layer caching" di Docker: se non cambia requirements.txt,
# Docker non reinstalla tutto ogni volta che cambi il codice.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ora copiamo tutto il resto del codice
COPY . .

# La porta su cui gira Flask
EXPOSE 8000

# Comando per avviare l'app
CMD ["python", "run.py"]