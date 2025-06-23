# Backend Receipt Scanner

Projekt zawiera prosty backend API napisany w Django i Django REST Framework, umożliwiający przechowywanie transakcji oraz skanowanie paragonów za pomocą OCR.

## Zawartość repozytorium

- `receipts_project/` – główny projekt Django wraz z aplikacją `receipts`.
- `receipts_project/ocr/` – przykładowe informacje o elementach paragonu.
- `receipts_project/receipts/management/` – komenda `seed_data` do generowania przykładowych danych.

## Wymagania

- Python 3.10+
- Pakiety: `Django`, `djangorestframework`, `dj-rest-auth`, `django-allauth`, `django-cors-headers`, `easyocr`, `opencv-python`, `rapidfuzz`, `numpy`.

Instalację można wykonać wirtualnym środowisku:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Uruchomienie

1. Wejdź do katalogu `receipts_project`.
2. Wykonaj migracje bazy danych:
   ```bash
   python manage.py migrate
   ```
3. (Opcjonalnie) Dodaj przykładowe dane:
   ```bash
   python manage.py seed_data
   ```
4. Uruchom serwer developerski:
   ```bash
   python manage.py runserver
   ```

Aplikacja będzie dostępna pod adresem `http://127.0.0.1:8000/`.

## Najważniejsze endpointy

Wybrane ścieżki API znajdują się w pliku `receipts/urls.py`:

```python
urlpatterns = [
    path("transactions/", TransactionListAPI.as_view(), name="tx-list"),
    path("transactions/<int:pk>/", TransactionDetailAPI.as_view(), name="tx-detail"),
    path("products/", ProductListAPI.as_view(), name="prod-list"),
    path("products/<int:pk>/", ProductDetailAPI.as_view(), name="prod-detail"),
    path("receipts/scan/", ReceiptScanAPI.as_view(), name="receipt-scan"),
    path("auth/user/", UserUpdateAPI.as_view(), name="user-update"),
    path("auth/password/", ChangePasswordAPI.as_view(), name="change-password"),
    path('api/calendar/<str:period>/', CalendarAPI.as_view()),
]
```

Dostęp do większości zasobów wymaga uwierzytelnienia tokenem (`TokenAuthentication`).

## Testy

Pakiet testów jednostkowych znajduje się w `receipts/tests.py`. Uruchomienie:

```bash
python manage.py test
```

## Struktura aplikacji

- `models.py` – definicje modeli `Transaction` i `Product`.
- `serializers.py` – serializery REST.
- `views.py` – logika endpointów API (w tym skaner OCR `ReceiptScanAPI`).
- `management/commands/seed_data.py` – komenda do wypełnienia bazy przykładowymi danymi.
- `ocr.py` – parser paragonów wykorzystujący EasyOCR i OpenCV.

## Uwagi

Parser paragonów znajduje się w `receipts/ocr.py` i obsługuje podział obrazu na sekcje oraz ekstrakcję danych z poszczególnych fragmentów paragonu.

## Licencja

Projekt udostępniony do celów edukacyjnych.