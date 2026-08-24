from django.urls import path

from . import views


app_name = "catalog"


urlpatterns = [
    # Product listing endpoint.
    path(
        "",
        views.ProductListView.as_view(),
        name="product_list",
    ),

    # Product detail endpoint.
    path(
        "product/<str:slug>/",
        views.ProductDetailView.as_view(),
        name="product_detail",
    ),

    # Category-specific product listing endpoint.
    path(
        "category/<str:slug>/",
        views.CategoryProductListView.as_view(),
        name="category_product_list",
    ),
]