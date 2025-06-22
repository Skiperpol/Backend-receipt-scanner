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
                "total_amount": Decimal("-129.99"),
                "description": "Zakupy spożywcze",
                "products": [
                    {"name": "Chleb", "price": Decimal("-4.50")},
                    {"name": "Mleko", "price": Decimal("-3.20")},
                    {"name": "Masło", "price": Decimal("-7.30")},
                ],
            },
            {
                "total_amount": Decimal("-320.00"),
                "description": "Zakupy elektronika",
                "products": [
                    {"name": "Słuchawki", "price": Decimal("-199.99")},
                    {"name": "Kabel USB-C", "price": Decimal("-19.99")},
                ],
            },
            {
                "total_amount": Decimal("-65.40"),
                "description": "Apteka",
                "products": [
                    {"name": "Witamina C", "price": Decimal("-14.50")},
                    {"name": "Ibuprofen", "price": Decimal("-8.90")},
                    {"name": "Maseczki", "price": Decimal("-20.00")},
                ],
            },
            {
                "total_amount": Decimal("1000.40"),
                "description": "Sklep internetowy",
                "products": [
                    {"name": "Hosting", "price": Decimal("200.00")},
                    {"name": "Projekt graficzny", "price": Decimal("400.00")},
                    {"name": "Programowanie", "price": Decimal("400.40")},
                ],
            },
        ]

        for entry in data:
            transaction = Transaction.objects.create(
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
