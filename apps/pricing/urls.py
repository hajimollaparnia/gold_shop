from django.urls import path

from apps.pricing.views import (
    CurrentGoldPriceAPIView,
    current_gold_price_fragment,
)

app_name = "pricing"

urlpatterns = [
    path(
        "market-price/",
        CurrentGoldPriceAPIView.as_view(),
        name="current-gold-price",
    ),
    path(
        "market-price/fragment/",
        current_gold_price_fragment,
        name="current-gold-price-fragment",
    ),
]