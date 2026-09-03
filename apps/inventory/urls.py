from django.urls import path

from apps.inventory.views.inventory_item import (
    InventoryItemDetailView,
    InventoryItemListView,
)
from apps.inventory.views.reservation import (
    ReservationCommitView,
    ReservationReleaseView,
    ReservationReserveView,
)
from apps.inventory.views.stock import (
    StockAdjustView,
    StockDecreaseView,
    StockIncreaseView,
)


app_name = "inventory"


urlpatterns = [
    path(
        "items/",
        InventoryItemListView.as_view(),
        name="inventory-item-list",
    ),
    path(
        "items/<int:pk>/",
        InventoryItemDetailView.as_view(),
        name="inventory-item-detail",
    ),
    path(
        "stock/increase/",
        StockIncreaseView.as_view(),
        name="stock-increase",
    ),
    path(
        "stock/decrease/",
        StockDecreaseView.as_view(),
        name="stock-decrease",
    ),
    path(
        "stock/adjust/",
        StockAdjustView.as_view(),
        name="stock-adjust",
    ),
    path(
        "reservations/reserve/",
        ReservationReserveView.as_view(),
        name="reservation-reserve",
    ),
    path(
        "reservations/release/",
        ReservationReleaseView.as_view(),
        name="reservation-release",
    ),
    path(
        "reservations/commit/",
        ReservationCommitView.as_view(),
        name="reservation-commit",
    ),
]