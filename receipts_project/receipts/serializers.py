from rest_framework import serializers
from .models import Transaction, Product

class ProductSerializer(serializers.ModelSerializer[Product]):
    class Meta:
        model = Product
        fields: list[str] = ["id", "name", "price", "transaction"]


class TransactionSerializer(serializers.ModelSerializer[Transaction]):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Transaction
        fields = ["id", "date", "total_amount", "description", "products"]
        read_only_fields = ("date",)