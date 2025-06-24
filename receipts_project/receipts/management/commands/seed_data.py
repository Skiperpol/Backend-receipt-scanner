from datetime import datetime
from django.core.management.base import BaseCommand
from decimal import Decimal
from receipts.models import Transaction, Product


class Command(BaseCommand):
    help = "Dodaje przykładowe transakcje i produkty"

    def handle(self, *args, **kwargs):

        self.stdout.write(self.style.ERROR("Usuwam stare dane..."))
        Product.objects.all().delete()
        Transaction.objects.all().delete()

        self.stdout.write(self.style.WARNING("Dodaję nowe transakcje i produkty..."))

        data = [
            {
                "date": "01:06:2025 09:15",
                "total_amount": Decimal("-129.99"),
                "description": "Zakupy spożywcze",
                "products": [
                    {"name": "Chleb", "price": Decimal("-4.50")},
                    {"name": "Mleko", "price": Decimal("-3.20")},
                    {"name": "Masło", "price": Decimal("-7.30")},
                ],
            },
            {
                "date": "03:06:2025 14:00",
                "total_amount": Decimal("-320.00"),
                "description": "Zakupy elektronika",
                "products": [
                    {"name": "Słuchawki", "price": Decimal("-199.99")},
                    {"name": "Kabel USB-C", "price": Decimal("-19.99")},
                ],
            },
            {
                "date": "05:06:2025 11:30",
                "total_amount": Decimal("-65.40"),
                "description": "Apteka",
                "products": [
                    {"name": "Witamina C", "price": Decimal("-14.50")},
                    {"name": "Ibuprofen", "price": Decimal("-8.90")},
                    {"name": "Maseczki", "price": Decimal("-20.00")},
                ],
            },
            {
                "date": "07:06:2025 16:45",
                "total_amount": Decimal("1000.40"),
                "description": "Sklep internetowy",
                "products": [
                    {"name": "Hosting", "price": Decimal("200.00")},
                    {"name": "Projekt graficzny", "price": Decimal("400.00")},
                    {"name": "Programowanie", "price": Decimal("400.40")},
                ],
            },
            {
                "date": "10:06:2025 08:00",
                "total_amount": Decimal("-2500.00"),
                "description": "Czynsz za mieszkanie",
                "products": [
                    {"name": "Czynsz miesięczny", "price": Decimal("-2500.00")},
                ],
            },
            {
                "date": "12:06:2025 12:15",
                "total_amount": Decimal("-450.75"),
                "description": "Rachunki za media",
                "products": [
                    {"name": "Prąd", "price": Decimal("-150.25")},
                    {"name": "Gaz", "price": Decimal("-100.00")},
                    {"name": "Woda", "price": Decimal("-200.50")},
                ],
            },
            {
                "date": "15:06:2025 19:30",
                "total_amount": Decimal("-120.00"),
                "description": "Abonament streaming",
                "products": [
                    {"name": "Netflix", "price": Decimal("-50.00")},
                    {"name": "Spotify", "price": Decimal("-20.00")},
                    {"name": "HBO Max", "price": Decimal("-50.00")},
                ],
            },
            {
                "date": "18:06:2025 07:45",
                "total_amount": Decimal("5500.00"),
                "description": "Wypłata miesięczna",
                "products": [
                    {"name": "Pensja podstawowa", "price": Decimal("5000.00")},
                    {"name": "Premia", "price": Decimal("500.00")},
                ],
            },
            {
                "date": "20:06:2025 13:20",
                "total_amount": Decimal("-89.99"),
                "description": "Zakupy odzieżowe",
                "products": [
                    {"name": "Koszula", "price": Decimal("-29.99")},
                    {"name": "Spodnie", "price": Decimal("-60.00")},
                ],
            },
            {
                "date": "22:06:2025 17:10",
                "total_amount": Decimal("-15.00"),
                "description": "Transport publiczny",
                "products": [
                    {"name": "Bilet miesięczny", "price": Decimal("-15.00")},
                ],
            },
        ]

        for entry in data:
            dt = datetime.strptime(entry["date"], "%d:%m:%Y %H:%M")
            transaction = Transaction.objects.create(
                date=dt,
                total_amount=entry["total_amount"],
                description=entry["description"]
            )
            for prod in entry["products"]:
                Product.objects.create(
                    name=prod["name"],
                    price=prod["price"],
                    transaction=transaction
                )

        self.stdout.write(self.style.SUCCESS("Przykładowe dane zostały dodane."))
