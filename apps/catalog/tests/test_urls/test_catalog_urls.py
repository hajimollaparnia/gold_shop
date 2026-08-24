
from urllib.parse import unquote

from django.test import SimpleTestCase
from django.urls import NoReverseMatch, resolve, reverse

from apps.catalog.views import (
    CategoryProductListView,
    ProductDetailView,
    ProductListView,
)


class CatalogURLTests(SimpleTestCase):
    """
    Test URL configuration for the catalog application.

    These tests verify URL names, namespace resolution, reverse URL
    generation, captured parameters, and mapping between URL patterns
    and their corresponding class-based views.
    """

    def test_product_list_url_resolves_to_correct_view(self):
        """
        Verify that the product list URL resolves to ProductListView.
        """

        url = reverse("catalog:product_list")

        resolved = resolve(url)

        self.assertEqual(
            resolved.func.view_class,
            ProductListView,
        )

    def test_product_list_url_has_expected_path(self):
        """
        Verify the generated product list URL.
        """

        self.assertEqual(
            reverse("catalog:product_list"),
            "/catalog/",
        )

    def test_product_detail_url_resolves_to_correct_view(self):
        """
        Verify that a product detail URL resolves to ProductDetailView.
        """

        url = reverse(
            "catalog:product_detail",
            kwargs={
                "slug": "انگشتر-طلای-کلاسیک",
            },
        )

        resolved = resolve(url)

        self.assertEqual(
            resolved.func.view_class,
            ProductDetailView,
        )

    def test_product_detail_url_contains_slug(self):
        """
        Verify that the product slug is correctly included in the
        generated URL after URL decoding.
        """

        slug = "انگشتر-طلای-کلاسیک"

        url = reverse(
            "catalog:product_detail",
            kwargs={
                "slug": slug,
            },
        )

        decoded_url = unquote(url)

        self.assertIn(
            slug,
            decoded_url,
        )

    def test_product_detail_url_passes_slug_argument(self):
        """
        Verify that the product slug is correctly captured by the URL.
        """

        url = reverse(
            "catalog:product_detail",
            kwargs={
                "slug": "gold-ring",
            },
        )

        resolved = resolve(url)

        self.assertEqual(
            resolved.kwargs["slug"],
            "gold-ring",
        )

    def test_category_product_list_url_resolves_to_correct_view(self):
        """
        Verify that the category URL resolves to
        CategoryProductListView.
        """

        url = reverse(
            "catalog:category_product_list",
            kwargs={
                "slug": "انگشتر",
            },
        )

        resolved = resolve(url)

        self.assertEqual(
            resolved.func.view_class,
            CategoryProductListView,
        )

    def test_category_product_list_url_contains_slug(self):
        """
        Verify that the category slug is correctly included in the
        generated URL after URL decoding.
        """

        slug = "انگشتر"

        url = reverse(
            "catalog:category_product_list",
            kwargs={
                "slug": slug,
            },
        )

        decoded_url = unquote(url)

        self.assertIn(
            slug,
            decoded_url,
        )

    def test_category_product_list_url_passes_slug_argument(self):
        """
        Verify that the category slug is correctly captured by the URL.
        """

        url = reverse(
            "catalog:category_product_list",
            kwargs={
                "slug": "rings",
            },
        )

        resolved = resolve(url)

        self.assertEqual(
            resolved.kwargs["slug"],
            "rings",
        )

    def test_catalog_namespace_is_used(self):
        """
        Verify that all catalog URLs use the expected namespace and
        generate the correct public paths.
        """

        self.assertEqual(
            reverse("catalog:product_list"),
            "/catalog/",
        )

        self.assertEqual(
            reverse(
                "catalog:product_detail",
                kwargs={
                    "slug": "gold-ring",
                },
            ),
            "/catalog/product/gold-ring/",
        )

        self.assertEqual(
            reverse(
                "catalog:category_product_list",
                kwargs={
                    "slug": "rings",
                },
            ),
            "/catalog/category/rings/",
        )

    def test_product_detail_url_requires_slug(self):
        """
        Verify that reversing the product detail URL without the
        required slug raises NoReverseMatch.
        """

        with self.assertRaises(NoReverseMatch):
            reverse("catalog:product_detail")

    def test_category_product_list_url_requires_slug(self):
        """
        Verify that reversing the category product list URL without
        the required slug raises NoReverseMatch.
        """

        with self.assertRaises(NoReverseMatch):
            reverse("catalog:category_product_list")

