from django.urls import path

from .views import CouponValidateAPIView


app_name = "coupons"

urlpatterns = [
    path(
        "validate/",
        CouponValidateAPIView.as_view(),
        name="validate",
    ),
]