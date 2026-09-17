from django.urls import path

from .views import (
    ReviewCreateAPIView,
    ReviewDeleteAPIView,
)


app_name = "reviews"

urlpatterns = [
    path(
        "",
        ReviewCreateAPIView.as_view(),
        name="create",
    ),
    path(
        "<int:review_id>/delete/",
        ReviewDeleteAPIView.as_view(),
        name="delete",
    ),
]