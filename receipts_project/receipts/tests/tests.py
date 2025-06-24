from typing import Any
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timezone as dt_timezone

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
            "date": timezone.now().isoformat(),
            "total_amount": "100.00",
            "description": "Test"
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class TransactionDetailAPITests(AuthenticatedAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        from ..models import Transaction
        self.tx = Transaction.objects.create(
            date=timezone.now(),
            total_amount=50.0,
            description="Init"
        )

    def test_get_transaction_detail(self) -> None:
        url = reverse("tx-detail", args=[self.tx.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_transaction(self) -> None:
        url = reverse("tx-detail", args=[self.tx.pk])
        data = {
            "date": timezone.now().isoformat(),
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
        from ..models import Transaction
        self.tx = Transaction.objects.create(
            date=timezone.now(),
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
        response = self.client.post(url, {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProductDetailAPITests(AuthenticatedAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        from ..models import Transaction, Product
        self.tx = Transaction.objects.create(
            date=timezone.now(),
            total_amount=10.0,
            description="Init",
        )
        self.product = Product.objects.create(
            name="Prod",
            price=1.0,
            transaction=self.tx,
        )

    def test_get_product_detail(self) -> None:
        url = reverse("prod-detail", args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product(self) -> None:
        url = reverse("prod-detail", args=[self.product.pk])
        data: dict[str, Any] = {
            "name": "Updated",
            "price": "2.50",
            "transaction": self.tx.pk,
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_product(self) -> None:
        url = reverse("prod-detail", args=[self.product.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class UserUpdateAPITests(AuthenticatedAPITestCase):
    def test_update_username_success(self) -> None:
        url = reverse("user-update")
        response = self.client.patch(url, {"username": "newname"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newname")

class ChangePasswordAPITests(AuthenticatedAPITestCase):
    def test_change_password_success(self) -> None:
        url = reverse("change-password")
        response = self.client.post(
            url,
            {"password": "NewStrongPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass123"))

    def test_change_password_missing(self) -> None:
        url = reverse("change-password")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CalendarAPITests(AuthenticatedAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        from django.utils import timezone
        from ..models import Transaction

        Transaction.objects.create(
            date=timezone.datetime(2024, 1, 1, 10, 0, tzinfo=dt_timezone.utc),
            total_amount=10.0,
            description="Jan1",
        )
        Transaction.objects.create(
            date=timezone.datetime(2024, 1, 2, 10, 0, tzinfo=dt_timezone.utc),
            total_amount=20.0,
            description="Jan2",
        )
        Transaction.objects.create(
            date=timezone.datetime(2024, 2, 1, 10, 0, tzinfo=dt_timezone.utc),
            total_amount=30.0,
            description="Feb1",
        )

def test_daily_totals(self) -> None:
    response = self.client.get(
        "/calendar/daily/",
        {"year": 2024, "month": 1},
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    result = {int(k): v for k, v in response.json().items()}
    self.assertEqual(result, {1: 10.0, 2: 20.0})

def test_monthly_totals(self) -> None:
    response = self.client.get(
        "/calendar/monthly/",
        {"year": 2024},
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    result = {int(k): v for k, v in response.json().items()}
    self.assertEqual(result, {1: 30.0, 2: 30.0})