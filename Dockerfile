FROM python:3.10-slim

# Zainstaluj zależności systemowe potrzebne m.in. przez OpenCV, easyocr, torch itp.
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kopiujemy najpierw requirements.txt, by wykorzystać cache warstwy Pythona przy rebuildzie
COPY requirements.txt .

# Aktualizacja pip i instalacja zależności Pythona
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Kopiujemy resztę kodu źródłowego
COPY . .

# Uruchamiamy serwer Django
CMD ["python", "receipts_project/manage.py", "runserver", "0.0.0.0:8000"]
