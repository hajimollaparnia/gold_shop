"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

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
    path(
    "api/v1/reviews/",
    include("apps.reviews.urls"),
),
path(
    "api/v1/notifications/",
    include("apps.notifications.urls"),
),


]