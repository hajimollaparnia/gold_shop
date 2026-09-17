"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("catalog/", include("apps.catalog.urls")),
    path("api/inventory/", include("apps.inventory.urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/v1/cart/", include("apps.cart.urls")),
    path(
    "api/v1/coupons/",
    include("apps.coupons.urls"),
    ),
    path(
    "api/v1/wishlist/",
    include("apps.wishlist.urls"),
    ),

]