from django.db.models import Prefetch
from django.http import Http404
from django.views.generic import DetailView, ListView

from .models import (
    Category,
    Product,
    ProductImage,
    ProductVariant,
)


class ProductListView(ListView):
    """
    Display active products available in the public catalog.

    The queryset is optimized for catalog listing pages by loading
    single-valued relationships with ``select_related`` and collection
    relationships with optimized ``prefetch_related`` queries.

    Only active products are exposed through the public catalog.
    """

    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        """
        Return an optimized queryset of active catalog products.

        ``select_related`` prevents additional queries for the product
        category, while ``prefetch_related`` efficiently loads product
        images and variants.

        Variant attributes are prefetched together to prevent N+1
        queries when variant attributes are rendered in the template.
        """

        image_queryset = (
            ProductImage.objects
            .only(
                "id",
                "product_id",
                "image",
                "alt_text",
                "display_order",
                "is_primary",
            )
            .order_by(
                "display_order",
                "-created_at",
            )
        )

        variant_queryset = (
            ProductVariant.objects
            .prefetch_related(
                "attributes__attribute",
            )
            .only(
                "id",
                "product_id",
                "sku",
                "weight",
                "stock_quantity",
                "is_active",
                "created_at",
                "updated_at",
            )
            .order_by("sku")
        )

        return (
            Product.objects
            .filter(
                is_active=True,
            )
            .select_related(
                "category",
            )
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=image_queryset,
                ),
                Prefetch(
                    "variants",
                    queryset=variant_queryset,
                ),
            )
            .order_by("-created_at")
        )


class ProductDetailView(DetailView):
    """
    Display the public detail page of a single active product.

    Inactive products are intentionally excluded from the public
    catalog and therefore cannot be accessed through their detail URL.
    """

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """
        Return an optimized queryset for the product detail page.

        Related category, images, variants, and variant attributes
        are loaded efficiently to minimize database round trips.
        """

        image_queryset = (
            ProductImage.objects
            .only(
                "id",
                "product_id",
                "image",
                "alt_text",
                "display_order",
                "is_primary",
            )
            .order_by(
                "display_order",
                "-created_at",
            )
        )

        variant_queryset = (
            ProductVariant.objects
            .prefetch_related(
                "attributes__attribute",
            )
            .only(
                "id",
                "product_id",
                "sku",
                "weight",
                "stock_quantity",
                "is_active",
                "created_at",
                "updated_at",
            )
            .order_by("sku")
        )

        return (
            Product.objects
            .filter(
                is_active=True,
            )
            .select_related(
                "category",
            )
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=image_queryset,
                ),
                Prefetch(
                    "variants",
                    queryset=variant_queryset,
                ),
            )
        )


class CategoryProductListView(ListView):
    """
    Display active products belonging to an active category.

    Category validation and product filtering are performed at the
    database level so inactive or nonexistent categories are not
    exposed through the public catalog.
    """

    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 24

    def get_category(self):
        """
        Return the requested active category.

        Raises ``Http404`` when the category does not exist or is
        inactive, preventing invalid category pages from rendering.

        The result is cached on the view instance so multiple calls
        during the same request do not trigger duplicate queries.
        """

        if hasattr(self, "_category"):
            return self._category

        try:
            self._category = Category.objects.get(
                slug=self.kwargs["slug"],
                is_active=True,
            )
        except Category.DoesNotExist as exc:
            raise Http404(
                "Category does not exist or is inactive."
            ) from exc

        return self._category

    def get_queryset(self):
        """
        Return an optimized queryset of products for the category.

        Products are filtered by the already validated category object,
        while related catalog data is loaded efficiently to prevent
        N+1 database queries.
        """

        category = self.get_category()

        image_queryset = (
            ProductImage.objects
            .only(
                "id",
                "product_id",
                "image",
                "alt_text",
                "display_order",
                "is_primary",
            )
            .order_by(
                "display_order",
                "-created_at",
            )
        )

        variant_queryset = (
            ProductVariant.objects
            .prefetch_related(
                "attributes__attribute",
            )
            .only(
                "id",
                "product_id",
                "sku",
                "weight",
                "stock_quantity",
                "is_active",
                "created_at",
                "updated_at",
            )
            .order_by("sku")
        )

        return (
            Product.objects
            .filter(
                category=category,
                is_active=True,
            )
            .select_related(
                "category",
            )
            .prefetch_related(
                Prefetch(
                    "images",
                    queryset=image_queryset,
                ),
                Prefetch(
                    "variants",
                    queryset=variant_queryset,
                ),
            )
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        """
        Add the validated active category to the template context.

        The category is retrieved through the cached ``get_category``
        method so no additional database query is performed.
        """

        context = super().get_context_data(**kwargs)
        context["category"] = self.get_category()

        return context