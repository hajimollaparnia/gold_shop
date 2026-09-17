from django.urls import path

from .views import (
    WishlistClearAPIView,
    WishlistDetailAPIView,
    WishlistItemCreateAPIView,
    WishlistItemDeleteAPIView,
)


app_name = "wishlist"

urlpatterns = [
    path(
        "",
        WishlistDetailAPIView.as_view(),
        name="detail",
    ),
    path(
        "items/",
        WishlistItemCreateAPIView.as_view(),
        name="item-create",
    ),
    path(
        "items/<int:item_id>/delete/",
        WishlistItemDeleteAPIView.as_view(),
        name="item-delete",
    ),
    path(
        "clear/",
        WishlistClearAPIView.as_view(),
        name="clear",
    ),
]