from django.db import models

class Transaction(models.Model):
    date: models.DateTimeField = models.DateTimeField()
    total_amount: models.DecimalField = models.DecimalField(max_digits=10, decimal_places=2)
    description: models.CharField = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.total_amount} PLN" # type: ignore


class Product(models.Model):
    name: models.CharField = models.CharField(max_length=100)
    price: models.DecimalField = models.DecimalField(max_digits=8, decimal_places=2)
    transaction: models.ForeignKey = models.ForeignKey(
        Transaction,
        related_name="products",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
