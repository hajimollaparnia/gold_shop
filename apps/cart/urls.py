from django.urls import path

from .views import (
    CartClearAPIView,
    CartDetailAPIView,
    CartItemCreateAPIView,
    CartItemDeleteAPIView,
    CartItemUpdateAPIView,
)

app_name = "cart"

urlpatterns = [
    path(
        "",
        CartDetailAPIView.as_view(),
        name="detail",
    ),
    path(
        "items/",
        CartItemCreateAPIView.as_view(),
        name="item-create",
    ),
    path(
        "items/<int:item_id>/",
        CartItemUpdateAPIView.as_view(),
        name="item-update",
    ),
    path(
        "items/<int:item_id>/delete/",
        CartItemDeleteAPIView.as_view(),
        name="item-delete",
    ),
    path(
        "clear/",
        CartClearAPIView.as_view(),
        name="clear",
    ),
]