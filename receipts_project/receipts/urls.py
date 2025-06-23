from django.urls import path
from .views import (
    TransactionListAPI, TransactionDetailAPI,
    ProductListAPI, ProductDetailAPI,
    ReceiptScanAPI, UserUpdateAPI, ChangePasswordAPI, CalendarAPI
)

urlpatterns = [
    path("transactions/", TransactionListAPI.as_view(), name="tx-list"),
    path("transactions/<int:pk>/", TransactionDetailAPI.as_view(), name="tx-detail"),
    path("products/", ProductListAPI.as_view(), name="prod-list"),
    path("products/<int:pk>/", ProductDetailAPI.as_view(), name="prod-detail"),
    path("receipts/scan/", ReceiptScanAPI.as_view(), name="receipt-scan"),
    path("auth/user/", UserUpdateAPI.as_view(), name="user-update"),    
    path("auth/password/", ChangePasswordAPI.as_view(), name="change-password"), 
    path('calendar/<str:period>/', CalendarAPI.as_view()),
]
