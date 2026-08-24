
from decimal import Decimal

from django.db import connection
from django.test import TestCase
from django.urls import reverse

from apps.catalog.models import (
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
)
from apps.catalog.views import (
    CategoryProductListView,
    ProductDetailView,
    ProductListView,
)


class CatalogViewTestMixin:
    """
    Provide reusable test data for catalog view tests.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Create shared catalog data once for the test class.
        """

        cls.category = Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
            is_active=True,
        )

        cls.other_category = Category.objects.create(
            name="گردنبند",
            slug="گردنبند",
            is_active=True,
        )

        cls.inactive_category = Category.objects.create(
            name="دسته غیرفعال",
            slug="دسته-غیرفعال",
            is_active=False,
        )

        cls.product = Product.objects.create(
            category=cls.category,
            name="انگشتر طلای کلاسیک",
            slug="انگشتر-طلای-کلاسیک",
            sku="RNG-1001",
            description="محصول تستی",
            weight=Decimal("2.850"),
            purity=750,
            color="yellow",
            stock_quantity=5,
            is_active=True,
        )

        cls.second_product = Product.objects.create(
            category=cls.category,
            name="انگشتر طلای سفید",
            slug="انگشتر-طلای-سفید",
            sku="RNG-1002",
            description="محصول تستی دوم",
            weight=Decimal("3.100"),
            purity=750,
            color="white",
            stock_quantity=3,
            is_active=True,
        )

        cls.other_category_product = Product.objects.create(
            category=cls.other_category,
            name="گردنبند طلای ظریف",
            slug="گردنبند-طلای-ظریف",
            sku="NCK-1001",
            description="محصول دسته دیگر",
            weight=Decimal("4.200"),
            purity=750,
            color="yellow",
            stock_quantity=2,
            is_active=True,
        )

        cls.inactive_product = Product.objects.create(
            category=cls.category,
            name="محصول غیرفعال",
            slug="محصول-غیرفعال",
            sku="INACTIVE-1001",
            description="نباید در کاتالوگ نمایش داده شود.",
            weight=Decimal("2.000"),
            purity=750,
            color="yellow",
            stock_quantity=1,
            is_active=False,
        )

        cls.attribute = ProductAttribute.objects.create(
            name="سایز",
            slug="سایز",
            is_active=True,
        )

        cls.attribute_value = ProductAttributeValue.objects.create(
            attribute=cls.attribute,
            value="18",
            slug="سایز-18",
            is_active=True,
        )

        cls.image = ProductImage.objects.create(
            product=cls.product,
            image="catalog/products/test-image.webp",
            alt_text="تصویر انگشتر تستی",
            display_order=1,
            is_primary=True,
        )

        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            sku="RNG-1001-V1",
            weight=Decimal("2.900"),
            stock_quantity=2,
            is_active=True,
        )

        cls.variant.attributes.add(cls.attribute_value)


class ProductListViewTests(CatalogViewTestMixin, TestCase):
    """
    Test the public product listing view.
    """

    def test_product_list_view_returns_success(self):
        """
        Verify that the product listing page returns HTTP 200.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_product_list_view_uses_correct_template(self):
        """
        Verify that the product listing view uses the expected template.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        self.assertTemplateUsed(
            response,
            "catalog/product_list.html",
        )

    def test_product_list_view_uses_correct_view_class(self):
        """
        Verify that the resolved URL uses ProductListView.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        self.assertIsInstance(
            response.context["view"],
            ProductListView,
        )

    def test_product_list_contains_only_active_products(self):
        """
        Verify that inactive products are excluded from the public catalog.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        products = response.context["products"]

        self.assertIn(
            self.product,
            products,
        )

        self.assertIn(
            self.second_product,
            products,
        )

        self.assertNotIn(
            self.inactive_product,
            products,
        )

    def test_product_list_contains_products_from_multiple_categories(self):
        """
        Verify that the general product listing is not restricted to
        a single category.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        products = response.context["products"]

        self.assertIn(
            self.product,
            products,
        )

        self.assertIn(
            self.other_category_product,
            products,
        )

    def test_product_list_context_name_is_products(self):
        """
        Verify that products are exposed through the expected context key.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        self.assertIn(
            "products",
            response.context,
        )

    def test_product_list_prefetches_images(self):
        """
        Verify that product images are available without requiring
        additional database queries for each product.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        product = next(
            product
            for product in response.context["products"]
            if product.pk == self.product.pk
        )

        with self.assertNumQueries(0):
            images = list(product.images.all())

        self.assertEqual(
            images,
            [self.image],
        )

    def test_product_list_prefetches_variants(self):
        """
        Verify that product variants are prefetched.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        product = next(
            product
            for product in response.context["products"]
            if product.pk == self.product.pk
        )

        with self.assertNumQueries(0):
            variants = list(product.variants.all())

        self.assertEqual(
            variants,
            [self.variant],
        )

    def test_product_list_prefetches_variant_attributes(self):
        """
        Verify that variant attributes and their parent attributes
        are prefetched.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        product = next(
            product
            for product in response.context["products"]
            if product.pk == self.product.pk
        )

        variant = product.variants.all()[0]

        with self.assertNumQueries(0):
            attributes = list(
                variant.attributes.all()
            )

        self.assertEqual(
            attributes,
            [self.attribute_value],
        )

        with self.assertNumQueries(0):
            attribute_name = variant.attributes.all()[0].attribute.name

        self.assertEqual(
            attribute_name,
            "سایز",
        )

    def test_product_list_is_paginated(self):
        """
        Verify that the product listing uses the configured pagination size.
        """

        response = self.client.get(
            reverse("catalog:product_list")
        )

        self.assertEqual(
            response.context["paginator"].per_page,
            24,
        )


class ProductDetailViewTests(CatalogViewTestMixin, TestCase):
    """
    Test the public product detail view.
    """

    def test_product_detail_returns_success(self):
        """
        Verify that an active product detail page returns HTTP 200.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.product.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_product_detail_uses_correct_template(self):
        """
        Verify that the product detail view uses the expected template.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.product.slug,
                },
            )
        )

        self.assertTemplateUsed(
            response,
            "catalog/product_detail.html",
        )

    def test_product_detail_returns_requested_product(self):
        """
        Verify that the requested active product is exposed as product
        in the template context.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.product.slug,
                },
            )
        )

        self.assertEqual(
            response.context["product"],
            self.product,
        )

    def test_product_detail_uses_correct_view_class(self):
        """
        Verify that the resolved detail page uses ProductDetailView.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.product.slug,
                },
            )
        )

        self.assertIsInstance(
            response.context["view"],
            ProductDetailView,
        )

    def test_inactive_product_detail_returns_404(self):
        """
        Verify that inactive products cannot be accessed publicly.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.inactive_product.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_nonexistent_product_detail_returns_404(self):
        """
        Verify that a nonexistent product slug returns HTTP 404.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": "product-does-not-exist",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_product_detail_prefetches_images(self):
        """
        Verify that product images are prefetched on the detail page.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.product.slug,
                },
            )
        )

        product = response.context["product"]

        with self.assertNumQueries(0):
            images = list(product.images.all())

        self.assertEqual(
            images,
            [self.image],
        )

    def test_product_detail_prefetches_variants(self):
        """
        Verify that product variants are prefetched on the detail page.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.product.slug,
                },
            )
        )

        product = response.context["product"]

        with self.assertNumQueries(0):
            variants = list(product.variants.all())

        self.assertEqual(
            variants,
            [self.variant],
        )

    def test_product_detail_prefetches_variant_attributes(self):
        """
        Verify that variant attributes are prefetched on the detail page.
        """

        response = self.client.get(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": self.product.slug,
                },
            )
        )

        product = response.context["product"]
        variant = product.variants.all()[0]

        with self.assertNumQueries(0):
            attribute_value = variant.attributes.all()[0]

        self.assertEqual(
            attribute_value,
            self.attribute_value,
        )

        with self.assertNumQueries(0):
            attribute_name = attribute_value.attribute.name

        self.assertEqual(
            attribute_name,
            "سایز",
        )


class CategoryProductListViewTests(CatalogViewTestMixin, TestCase):
    """
    Test the category-specific product listing view.
    """

    def test_category_product_list_returns_success(self):
        """
        Verify that an active category page returns HTTP 200.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_category_product_list_uses_correct_template(self):
        """
        Verify that the category listing uses the expected template.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        self.assertTemplateUsed(
            response,
            "catalog/product_list.html",
        )

    def test_category_product_list_uses_correct_view_class(self):
        """
        Verify that the category listing uses CategoryProductListView.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        self.assertIsInstance(
            response.context["view"],
            CategoryProductListView,
        )

    def test_category_product_list_contains_only_products_from_category(self):
        """
        Verify that only products belonging to the requested category
        are exposed.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        products = response.context["products"]

        self.assertIn(
            self.product,
            products,
        )

        self.assertIn(
            self.second_product,
            products,
        )

        self.assertNotIn(
            self.other_category_product,
            products,
        )

    def test_category_product_list_excludes_inactive_products(self):
        """
        Verify that inactive products are excluded from category pages.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        products = response.context["products"]

        self.assertNotIn(
            self.inactive_product,
            products,
        )

    def test_category_context_contains_requested_category(self):
        """
        Verify that the validated category is available in the context.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        self.assertEqual(
            response.context["category"],
            self.category,
        )

    def test_nonexistent_category_returns_404(self):
        """
        Verify that a nonexistent category returns HTTP 404.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": "category-does-not-exist",
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_inactive_category_returns_404(self):
        """
        Verify that inactive categories cannot be accessed publicly.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.inactive_category.slug,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_category_product_list_is_paginated(self):
        """
        Verify that category product listings use the configured
        pagination size.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        self.assertEqual(
            response.context["paginator"].per_page,
            24,
        )

    def test_category_product_list_prefetches_images(self):
        """
        Verify that category product images are prefetched.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        product = next(
            product
            for product in response.context["products"]
            if product.pk == self.product.pk
        )

        with self.assertNumQueries(0):
            images = list(product.images.all())

        self.assertEqual(
            images,
            [self.image],
        )

    def test_category_product_list_prefetches_variants(self):
        """
        Verify that category product variants are prefetched.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        product = next(
            product
            for product in response.context["products"]
            if product.pk == self.product.pk
        )

        with self.assertNumQueries(0):
            variants = list(product.variants.all())

        self.assertEqual(
            variants,
            [self.variant],
        )

    def test_category_product_list_prefetches_variant_attributes(self):
        """
        Verify that category product variant attributes are prefetched.
        """

        response = self.client.get(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": self.category.slug,
                },
            )
        )

        product = next(
            product
            for product in response.context["products"]
            if product.pk == self.product.pk
        )

        variant = product.variants.all()[0]

        with self.assertNumQueries(0):
            attribute_value = variant.attributes.all()[0]

        self.assertEqual(
            attribute_value,
            self.attribute_value,
        )

        with self.assertNumQueries(0):
            attribute_name = attribute_value.attribute.name

        self.assertEqual(
            attribute_name,
            "سایز",
        )

