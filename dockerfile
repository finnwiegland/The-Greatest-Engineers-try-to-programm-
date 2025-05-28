# Verwende ein schlankes Python-Image
FROM python:3.11-slim

# Setze Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere requirements.txt und installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den restlichen Code in den Container
COPY . .

# Erstelle das Upload-Verzeichnis, falls noch nicht vorhanden
RUN mkdir -p uploads

# Setze den Startbefehl: Starte FastAPI mit Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
