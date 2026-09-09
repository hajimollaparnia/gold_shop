from django.urls import path

from .views import (
    OrderCancelView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
)


app_name = "orders"


urlpatterns = [
    # List authenticated user's orders.
    path(
        "",
        OrderListView.as_view(),
        name="order-list",
    ),

    # Create a new order.
    path(
        "create/",
        OrderCreateView.as_view(),
        name="order-create",
    ),

    # Cancel an existing order.
    path(
        "<int:pk>/cancel/",
        OrderCancelView.as_view(),
        name="order-cancel",
    ),

    # Retrieve a single authenticated user's order.
    path(
        "<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),
]