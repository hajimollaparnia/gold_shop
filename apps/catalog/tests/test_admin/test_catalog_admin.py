from django.contrib import admin
from django.test import RequestFactory, TestCase

from apps.catalog.admin import (
    BrandAdmin,
    CategoryAdmin,
    ProductAdmin,
    ProductAttributeAdmin,
    ProductAttributeValueAdmin,
    ProductImageAdmin,
    ProductVariantAdmin,
    ProductImageInline,
    ProductVariantInline,
)
from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
)


class CatalogAdminTestMixin:
    """
    Shared test utilities for catalog admin tests.
    """

    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def get_request(self):
        """
        Return a request object suitable for ModelAdmin methods.
        """

        request = self.factory.get("/admin/")
        request.user = None
        return request


# =============================================================================
# Admin Registration Tests
# =============================================================================


class AdminRegistrationTests(TestCase):
    """
    Verify that all catalog models are correctly registered
    with Django's admin site.
    """

    def test_category_is_registered(self):
        self.assertIsInstance(
            admin.site._registry[Category],
            CategoryAdmin,
        )

    def test_brand_is_registered(self):
        self.assertIsInstance(
            admin.site._registry[Brand],
            BrandAdmin,
        )

    def test_product_is_registered(self):
        self.assertIsInstance(
            admin.site._registry[Product],
            ProductAdmin,
        )

    def test_product_image_is_registered(self):
        self.assertIsInstance(
            admin.site._registry[ProductImage],
            ProductImageAdmin,
        )

    def test_product_attribute_is_registered(self):
        self.assertIsInstance(
            admin.site._registry[ProductAttribute],
            ProductAttributeAdmin,
        )

    def test_product_attribute_value_is_registered(self):
        self.assertIsInstance(
            admin.site._registry[ProductAttributeValue],
            ProductAttributeValueAdmin,
        )

    def test_product_variant_is_registered(self):
        self.assertIsInstance(
            admin.site._registry[ProductVariant],
            ProductVariantAdmin,
        )


# =============================================================================
# Category Admin Tests
# =============================================================================


class CategoryAdminTests(CatalogAdminTestMixin, TestCase):
    """
    Verify CategoryAdmin configuration and queryset behavior.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.parent = Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
            is_active=True,
        )

        cls.child = Category.objects.create(
            name="انگشتر طلا",
            slug="انگشتر-طلا",
            parent=cls.parent,
            is_active=True,
        )

        cls.product = Product.objects.create(
            name="انگشتر کلاسیک",
            slug="انگشتر-کلاسیک",
            sku="RING-001",
            category=cls.parent,
            weight=2,
            purity=18,
            stock_quantity=5,
        )

    def get_admin(self):
        return CategoryAdmin(Category, admin.site)

    def test_list_display_contains_product_count(self):
        admin_instance = self.get_admin()

        self.assertIn(
            "product_count",
            admin_instance.list_display,
        )

    def test_product_count_returns_correct_value(self):
        admin_instance = self.get_admin()

        request = self.get_request()

        category = (
            admin_instance
            .get_queryset(request)
            .get(pk=self.parent.pk)
        )

        self.assertEqual(
            admin_instance.product_count(category),
            1,
        )

    def test_queryset_uses_product_count_annotation(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "product_count",
            queryset.query.annotations,
        )

    def test_queryset_selects_parent(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "parent",
            queryset.query.select_related,
        )

    def test_parent_is_autocomplete_field(self):
        admin_instance = self.get_admin()

        self.assertIn(
            "parent",
            admin_instance.autocomplete_fields,
        )

    def test_list_per_page_is_50(self):
        admin_instance = self.get_admin()

        self.assertEqual(
            admin_instance.list_per_page,
            50,
        )


# =============================================================================
# Brand Admin Tests
# =============================================================================


class BrandAdminTests(CatalogAdminTestMixin, TestCase):
    """
    Verify BrandAdmin configuration and queryset behavior.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.brand = Brand.objects.create(
            name="برند طلایی",
            slug="brand-gold",
            is_active=True,
        )

        cls.category = Category.objects.create(
            name="گردنبند",
            slug="گردنبند",
        )

        cls.product = Product.objects.create(
            name="گردنبند طلا",
            slug="gold-necklace",
            sku="NECK-001",
            category=cls.category,
            brand=cls.brand,
            weight=3,
            purity=18,
        )

    def get_admin(self):
        return BrandAdmin(Brand, admin.site)

    def test_product_count_returns_correct_value(self):
        admin_instance = self.get_admin()

        brand = (
            admin_instance
            .get_queryset(self.get_request())
            .get(pk=self.brand.pk)
        )

        self.assertEqual(
            admin_instance.product_count(brand),
            1,
        )

    def test_queryset_contains_product_count_annotation(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "product_count",
            queryset.query.annotations,
        )

    def test_list_display_contains_product_count(self):
        admin_instance = self.get_admin()

        self.assertIn(
            "product_count",
            admin_instance.list_display,
        )


# =============================================================================
# Product Admin Tests
# =============================================================================


class ProductAdminTests(CatalogAdminTestMixin, TestCase):
    """
    Verify ProductAdmin configuration, queryset optimization,
    bulk actions, and inline administration.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.category = Category.objects.create(
            name="دستبند",
            slug="دستبند",
        )

        cls.brand = Brand.objects.create(
            name="برند تست",
            slug="test-brand",
        )

        cls.product_one = Product.objects.create(
            name="دستبند اول",
            slug="bracelet-one",
            sku="BR-001",
            category=cls.category,
            brand=cls.brand,
            weight=4,
            purity=18,
            stock_quantity=10,
        )

        cls.product_two = Product.objects.create(
            name="دستبند دوم",
            slug="bracelet-two",
            sku="BR-002",
            category=cls.category,
            brand=cls.brand,
            weight=5,
            purity=18,
            stock_quantity=5,
        )

    def get_admin(self):
        return ProductAdmin(Product, admin.site)

    def get_queryset(self):
        return Product.objects.filter(
            pk__in=[
                self.product_one.pk,
                self.product_two.pk,
            ]
        )

    def test_queryset_selects_category_and_brand(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "category",
            queryset.query.select_related,
        )

        self.assertIn(
            "brand",
            queryset.query.select_related,
        )

    def test_category_and_brand_are_autocomplete_fields(self):
        admin_instance = self.get_admin()

        self.assertIn(
            "category",
            admin_instance.autocomplete_fields,
        )

        self.assertIn(
            "brand",
            admin_instance.autocomplete_fields,
        )

    def test_product_inlines_are_configured(self):
        admin_instance = self.get_admin()

        self.assertIn(
            ProductImageInline,
            admin_instance.inlines,
        )

        self.assertIn(
            ProductVariantInline,
            admin_instance.inlines,
        )

    def test_activate_products_action(self):
        self.product_one.is_active = False
        self.product_one.save(update_fields=["is_active"])

        admin_instance = self.get_admin()

        queryset = Product.objects.filter(
            pk=self.product_one.pk,
        )

        admin_instance.activate_products(
            None,
            queryset,
        )

        self.product_one.refresh_from_db()

        self.assertTrue(
            self.product_one.is_active,
        )

    def test_deactivate_products_action(self):
        admin_instance = self.get_admin()

        queryset = Product.objects.filter(
            pk=self.product_one.pk,
        )

        admin_instance.deactivate_products(
            None,
            queryset,
        )

        self.product_one.refresh_from_db()

        self.assertFalse(
            self.product_one.is_active,
        )

    def test_mark_as_featured_action(self):
        admin_instance = self.get_admin()

        queryset = Product.objects.filter(
            pk=self.product_one.pk,
        )

        admin_instance.mark_as_featured(
            None,
            queryset,
        )

        self.product_one.refresh_from_db()

        self.assertTrue(
            self.product_one.is_featured,
        )

    def test_remove_from_featured_action(self):
        self.product_one.is_featured = True
        self.product_one.save(update_fields=["is_featured"])

        admin_instance = self.get_admin()

        queryset = Product.objects.filter(
            pk=self.product_one.pk,
        )

        admin_instance.remove_from_featured(
            None,
            queryset,
        )

        self.product_one.refresh_from_db()

        self.assertFalse(
            self.product_one.is_featured,
        )

    def test_mark_as_bestseller_action(self):
        admin_instance = self.get_admin()

        queryset = Product.objects.filter(
            pk=self.product_one.pk,
        )

        admin_instance.mark_as_bestseller(
            None,
            queryset,
        )

        self.product_one.refresh_from_db()

        self.assertTrue(
            self.product_one.is_bestseller,
        )

    def test_remove_from_bestseller_action(self):
        self.product_one.is_bestseller = True
        self.product_one.save(update_fields=["is_bestseller"])

        admin_instance = self.get_admin()

        queryset = Product.objects.filter(
            pk=self.product_one.pk,
        )

        admin_instance.remove_from_bestseller(
            None,
            queryset,
        )

        self.product_one.refresh_from_db()

        self.assertFalse(
            self.product_one.is_bestseller,
        )

    def test_all_product_actions_are_registered(self):
        admin_instance = self.get_admin()

        expected_actions = {
            "activate_products",
            "deactivate_products",
            "mark_as_featured",
            "remove_from_featured",
            "mark_as_bestseller",
            "remove_from_bestseller",
        }

        self.assertEqual(
            set(admin_instance.actions),
            expected_actions,
        )


# =============================================================================
# Product Image Admin Tests
# =============================================================================


class ProductImageAdminTests(CatalogAdminTestMixin, TestCase):
    """
    Verify ProductImageAdmin configuration and queryset optimization.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.category = Category.objects.create(
            name="گوشواره",
            slug="گوشواره",
        )

        cls.product = Product.objects.create(
            name="گوشواره طلا",
            slug="gold-earring",
            sku="EAR-001",
            category=cls.category,
            weight=2,
            purity=18,
        )

        cls.image = ProductImage.objects.create(
            product=cls.product,
            alt_text="تصویر گوشواره",
            display_order=1,
            is_primary=True,
        )

    def get_admin(self):
        return ProductImageAdmin(
            ProductImage,
            admin.site,
        )

    def test_queryset_selects_product(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "product",
            queryset.query.select_related,
        )

    def test_product_is_autocomplete_field(self):
        admin_instance = self.get_admin()

        self.assertIn(
            "product",
            admin_instance.autocomplete_fields,
        )


# =============================================================================
# Product Attribute Admin Tests
# =============================================================================


class ProductAttributeAdminTests(CatalogAdminTestMixin, TestCase):
    """
    Verify ProductAttributeAdmin configuration and value counts.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.attribute = ProductAttribute.objects.create(
            name="سایز",
            slug="size",
            is_active=True,
        )

        ProductAttributeValue.objects.create(
            attribute=cls.attribute,
            value="18",
            slug="18",
        )

        ProductAttributeValue.objects.create(
            attribute=cls.attribute,
            value="20",
            slug="20",
        )

    def get_admin(self):
        return ProductAttributeAdmin(
            ProductAttribute,
            admin.site,
        )

    def test_value_count_returns_correct_value(self):
        admin_instance = self.get_admin()

        attribute = (
            admin_instance
            .get_queryset(self.get_request())
            .get(pk=self.attribute.pk)
        )

        self.assertEqual(
            admin_instance.value_count(attribute),
            2,
        )

    def test_queryset_contains_value_count_annotation(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "value_count",
            queryset.query.annotations,
        )


# =============================================================================
# Product Attribute Value Admin Tests
# =============================================================================


class ProductAttributeValueAdminTests(CatalogAdminTestMixin, TestCase):
    """
    Verify ProductAttributeValueAdmin queryset optimization.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.attribute = ProductAttribute.objects.create(
            name="طول زنجیر",
            slug="chain-length",
        )

        cls.value = ProductAttributeValue.objects.create(
            attribute=cls.attribute,
            value="45 سانتی‌متر",
            slug="45-cm",
        )

    def get_admin(self):
        return ProductAttributeValueAdmin(
            ProductAttributeValue,
            admin.site,
        )

    def test_queryset_selects_attribute(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "attribute",
            queryset.query.select_related,
        )

    def test_attribute_is_autocomplete_field(self):
        admin_instance = self.get_admin()

        self.assertIn(
            "attribute",
            admin_instance.autocomplete_fields,
        )


# =============================================================================
# Product Variant Admin Tests
# =============================================================================


class ProductVariantAdminTests(CatalogAdminTestMixin, TestCase):
    """
    Verify ProductVariantAdmin configuration, annotations,
    relationships, and attribute counts.
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.category = Category.objects.create(
            name="انگشتر",
            slug="rings",
        )

        cls.product = Product.objects.create(
            name="انگشتر تست",
            slug="test-ring",
            sku="RING-100",
            category=cls.category,
            weight=3,
            purity=18,
        )

        cls.attribute = ProductAttribute.objects.create(
            name="سایز انگشتر",
            slug="ring-size",
        )

        cls.attribute_value = ProductAttributeValue.objects.create(
            attribute=cls.attribute,
            value="18",
            slug="ring-size-18",
        )

        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            sku="RING-100-18",
            weight=3,
            stock_quantity=4,
        )

        cls.variant.attributes.add(
            cls.attribute_value,
        )

    def get_admin(self):
        return ProductVariantAdmin(
            ProductVariant,
            admin.site,
        )

    def test_queryset_selects_product(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "product",
            queryset.query.select_related,
        )

    def test_queryset_selects_product_category(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        select_related = queryset.query.select_related

        self.assertIn("product", select_related)
        self.assertIn("category", select_related["product"])
    def test_queryset_contains_attribute_count_annotation(self):
        admin_instance = self.get_admin()

        queryset = admin_instance.get_queryset(
            self.get_request(),
        )

        self.assertIn(
            "attribute_count",
            queryset.query.annotations,
        )

    def test_attribute_count_returns_correct_value(self):
        admin_instance = self.get_admin()

        variant = (
            admin_instance
            .get_queryset(self.get_request())
            .get(pk=self.variant.pk)
        )

        self.assertEqual(
            admin_instance.attribute_count(variant),
            1,
        )

    def test_product_is_autocomplete_field(self):
        admin_instance = self.get_admin()

        self.assertIn(
            "product",
            admin_instance.autocomplete_fields,
        )


# =============================================================================
# Inline Admin Tests
# =============================================================================


class ProductInlineAdminTests(TestCase):
    """
    Verify product inline administration configuration.
    """

    def test_product_image_inline_model(self):
        self.assertIs(
            ProductImageInline.model,
            ProductImage,
        )

    def test_product_variant_inline_model(self):
        self.assertIs(
            ProductVariantInline.model,
            ProductVariant,
        )

    def test_product_image_inline_has_change_link(self):
        self.assertTrue(
            ProductImageInline.show_change_link,
        )

    def test_product_variant_inline_has_change_link(self):
        self.assertTrue(
            ProductVariantInline.show_change_link,
        )

    def test_product_variant_inline_uses_filter_horizontal(self):
        self.assertIn(
            "attributes",
            ProductVariantInline.filter_horizontal,
        )