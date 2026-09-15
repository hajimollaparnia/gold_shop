from django.urls import path

from .views import (
    PaymentInitializeAPIView,
    PaymentReceiptUploadAPIView,
)

app_name = "payments"

urlpatterns = [
    path(
        "orders/<int:order_id>/initialize/",
        PaymentInitializeAPIView.as_view(),
        name="initialize",
    ),
    path(
        "<int:payment_id>/receipt/",
        PaymentReceiptUploadAPIView.as_view(),
        name="upload-receipt",
    ),
]