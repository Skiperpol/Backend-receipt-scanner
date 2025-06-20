from typing import Any
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction, Product
from .serializers import TransactionSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.password_validation import validate_password
from rest_framework.permissions import IsAuthenticated

class UserUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        new_username = request.data.get("username")
        if new_username:
            user.username = new_username
            user.save()
            return Response({"username": user.username})
        return Response({"detail": "No username provided"}, status=400)


class ChangePasswordAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        new_password = request.data.get("password")
        if not new_password:
            return Response({"detail": "No password provided"}, status=400)
        try:
            validate_password(new_password, user=request.user)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)
        request.user.set_password(new_password)
        request.user.save()
        return Response({"detail": "Password changed"})

class TransactionListAPI(APIView):
    def get(self, request: Request) -> Response:
        qs = Transaction.objects.all()
        serializer = TransactionSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TransactionDetailAPI(APIView):
    def get(self, request: Request, pk: int) -> Response:
        tx = Transaction.objects.get(pk=pk)
        serializer = TransactionSerializer(tx)
        return Response(serializer.data)

    def put(self, request: Request, pk: int) -> Response:
        tx = Transaction.objects.get(pk=pk)
        serializer = TransactionSerializer(tx, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, pk: int) -> Response:
        tx = Transaction.objects.get(pk=pk)
        tx.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListAPI(APIView):
    def get(self, request: Request) -> Response:
        qs = Product.objects.all()
        serializer = ProductSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailAPI(APIView):
    def get(self, request: Request, pk: int) -> Response:
        prod = Product.objects.get(pk=pk)
        serializer = ProductSerializer(prod)
        return Response(serializer.data)

    def put(self, request: Request, pk: int) -> Response:
        prod = Product.objects.get(pk=pk)
        serializer = ProductSerializer(prod, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request: Request, pk: int) -> Response:
        prod = Product.objects.get(pk=pk)
        prod.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReceiptScanAPI(APIView):
    def post(self, request: Request) -> Response:
        return Response({"detail": "Not implemented"}, status=status.HTTP_501_NOT_IMPLEMENTED)