from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .models import Transaction, Product
from .serializers import TransactionSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from django.db.models.functions import TruncDay, TruncMonth
from django.db.models import Sum
from .ocr import ReceiptParser
from rest_framework.parsers import MultiPartParser, FormParser
import numpy as np
import cv2
import traceback

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
        print("request.data:", request.data)
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
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "Brak pliku 'image' w żądaniu"},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_bytes = image_file.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return Response(
                {"detail": "Nie udało się zdekodować obrazu"},
                status=status.HTTP_400_BAD_REQUEST
            )

        parser = ReceiptParser()
        try:
            parser.load_image_from_np_ndarray(img)
            parser.run()
        except ValueError as ve:
            print("ValueError:", ve)
            traceback.print_exc()
            return Response(
                {"detail": f"Błąd danych: {str(ve)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            print("Inny błąd:", e)
            traceback.print_exc()
            return Response(
                {"detail": f"Błąd parsowania: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        parsed = parser.to_json()

        if 'total' in parsed:
            parsed['total'] = -abs(parsed['total'])

        for item in parsed.get('items', []):
            item['price'] = -abs(item.get('price', 0))

        return Response(parsed, status=status.HTTP_200_OK)
    
class CalendarAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, period: str):
        try:
            year = int(request.query_params.get('year', 0))
        except ValueError:
            return JsonResponse({'detail': 'Invalid year'}, status=status.HTTP_400_BAD_REQUEST)

        if period == 'daily':
            try:
                month = int(request.query_params.get('month', 0))
            except ValueError:
                return JsonResponse({'detail': 'Invalid month'}, status=status.HTTP_400_BAD_REQUEST)
            qs = Transaction.objects.filter(date__year=year, date__month=month)
            data = (
                qs.annotate(day=TruncDay('date'))
                  .values('day')
                  .annotate(total=Sum('total_amount'))
                  .order_by('day')
            )
            result = {entry['day'].day: float(entry['total'] or 0) for entry in data}
        elif period == 'monthly':
            qs = Transaction.objects.filter(date__year=year)
            data = (
                qs.annotate(month=TruncMonth('date'))
                  .values('month')
                  .annotate(total=Sum('total_amount'))
                  .order_by('month')
            )
            result = {entry['month'].month: float(entry['total'] or 0) for entry in data}
        else:
            return JsonResponse({'detail': 'Unsupported period'}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(result, safe=True)