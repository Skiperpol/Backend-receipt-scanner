from typing import Any
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status

class AuthenticatedAPITestCase(APITestCase):
    """
    Bazowa klasa, która tworzy użytkownika i ustawia token auth
    """
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            username="tester",
            email="test@example.com",
            password="password123"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials( # type: ignore
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )


class TransactionAPITests(AuthenticatedAPITestCase):
    def test_list_transactions(self) -> None:
        url = reverse("tx-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_transaction(self) -> None:
        url = reverse("tx-list")
        payload: dict[str, Any] = {
            "total_amount": "100.00",
            "description": "Test"
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TransactionDetailAPITests(AuthenticatedAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        from .models import Transaction
        self.tx = Transaction.objects.create(
            total_amount=50.0,
            description="Init"
        )

    def test_get_transaction_detail(self) -> None:
        url = reverse("tx-detail", args=[self.tx.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_transaction(self) -> None:
        url = reverse("tx-detail", args=[self.tx.pk])
        data: dict[str, Any] = {
            "total_amount": "75.00",
            "description": "Update"
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_transaction(self) -> None:
        url = reverse("tx-detail", args=[self.tx.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ProductAPITests(AuthenticatedAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        from .models import Transaction
        self.tx = Transaction.objects.create(
            total_amount=20.0,
            description="Init"
        )

    def test_list_products(self) -> None:
        url = reverse("prod-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_product(self) -> None:
        url = reverse("prod-list")
        payload: dict[str, Any] = {
            "name": "A",
            "price": "5.00",
            "transaction": self.tx.pk
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ReceiptScanAPITests(AuthenticatedAPITestCase):
    def test_receipt_scan_not_implemented(self) -> None:
        url = reverse("receipt-scan")
        response = self.client.post(url, {}, format="json")
        self.assertIn(
            response.status_code,
            (status.HTTP_501_NOT_IMPLEMENTED, status.HTTP_405_METHOD_NOT_ALLOWED)
        )
