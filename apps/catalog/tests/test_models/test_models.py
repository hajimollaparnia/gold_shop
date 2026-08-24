import pytest
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
)


# ============================================================
# Category
# ============================================================


@pytest.mark.django_db
class TestCategoryModel:
    """Test category behavior, hierarchy, constraints, and slugs."""

    def test_str_returns_category_name(self):
        category = Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
        )

        assert str(category) == "انگشتر"

    def test_slug_is_generated_when_missing(self):
        category = Category.objects.create(
            name="گردنبند طلا",
        )

        assert category.slug == "گردنبند-طلا"

    def test_parent_child_relationship(self):
        parent = Category.objects.create(
            name="طلا",
            slug="طلا",
        )

        child = Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
            parent=parent,
        )

        assert child.parent == parent
        assert child in parent.children.all()

    def test_category_name_is_unique_per_parent(self):
        parent = Category.objects.create(
            name="طلا",
            slug="طلا",
        )

        Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
            parent=parent,
        )

        with pytest.raises(IntegrityError):
            Category.objects.create(
                name="انگشتر",
                slug="انگشتر-دوم",
                parent=parent,
            )

    def test_same_category_name_is_allowed_under_different_parents(self):
        first_parent = Category.objects.create(
            name="طلا",
            slug="طلا",
        )

        second_parent = Category.objects.create(
            name="جواهرات",
            slug="جواهرات",
        )

        first_child = Category.objects.create(
            name="انگشتر",
            slug="انگشتر-طلا",
            parent=first_parent,
        )

        second_child = Category.objects.create(
            name="انگشتر",
            slug="انگشتر-جواهرات",
            parent=second_parent,
        )

        assert first_child.pk != second_child.pk

    def test_category_with_products_cannot_be_deleted(self):
        category = Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
        )

        Product.objects.create(
            category=category,
            name="انگشتر طلای کلاسیک",
            slug="انگشتر-طلای-کلاسیک",
            sku="RNG-001",
            weight="2.500",
            purity=750,
        )

        with pytest.raises(ProtectedError):
            category.delete()


# ============================================================
# Brand
# ============================================================


@pytest.mark.django_db
class TestBrandModel:
    """Test brand behavior and slug generation."""

    def test_str_returns_brand_name(self):
        brand = Brand.objects.create(
            name="SVG Gold",
            slug="svg-gold",
        )

        assert str(brand) == "SVG Gold"

    def test_slug_is_generated_when_missing(self):
        brand = Brand.objects.create(
            name="برند طلای ایرانی",
        )

        assert brand.slug == "برند-طلای-ایرانی"

    def test_brand_name_must_be_unique(self):
        Brand.objects.create(
            name="SVG Gold",
            slug="svg-gold",
        )

        with pytest.raises(IntegrityError):
            Brand.objects.create(
                name="SVG Gold",
                slug="svg-gold-2",
            )


# ============================================================
# Product Attribute
# ============================================================


@pytest.mark.django_db
class TestProductAttributeModel:
    """Test reusable product attribute definitions."""

    def test_str_returns_attribute_name(self):
        attribute = ProductAttribute.objects.create(
            name="سایز",
            slug="سایز",
        )

        assert str(attribute) == "سایز"

    def test_slug_is_generated_when_missing(self):
        attribute = ProductAttribute.objects.create(
            name="نوع قفل",
        )

        assert attribute.slug == "نوع-قفل"

    def test_attribute_name_must_be_unique(self):
        ProductAttribute.objects.create(
            name="سایز",
            slug="سایز",
        )

        with pytest.raises(IntegrityError):
            ProductAttribute.objects.create(
                name="سایز",
                slug="سایز-دوم",
            )


# ============================================================
# Product Attribute Value
# ============================================================


@pytest.mark.django_db
class TestProductAttributeValueModel:
    """Test attribute values and their constraints."""

    @pytest.fixture
    def attribute(self):
        return ProductAttribute.objects.create(
            name="سایز",
            slug="سایز",
        )

    def test_str_returns_attribute_and_value(
        self,
        attribute,
    ):
        value = ProductAttributeValue.objects.create(
            attribute=attribute,
            value="18",
            slug="18",
        )

        assert str(value) == "سایز: 18"

    def test_slug_is_generated_when_missing(
        self,
        attribute,
    ):
        value = ProductAttributeValue.objects.create(
            attribute=attribute,
            value="18",
        )

        assert value.slug == "18"

    def test_same_value_cannot_be_duplicated_for_same_attribute(
        self,
        attribute,
    ):
        ProductAttributeValue.objects.create(
            attribute=attribute,
            value="18",
            slug="18",
        )

        with pytest.raises(IntegrityError):
            ProductAttributeValue.objects.create(
                attribute=attribute,
                value="18",
                slug="18-duplicate",
            )

    def test_same_value_is_allowed_for_different_attributes(self):
        size_attribute = ProductAttribute.objects.create(
            name="سایز",
            slug="سایز",
        )

        length_attribute = ProductAttribute.objects.create(
            name="طول",
            slug="طول",
        )

        size_value = ProductAttributeValue.objects.create(
            attribute=size_attribute,
            value="18",
            slug="سایز-18",
        )

        length_value = ProductAttributeValue.objects.create(
            attribute=length_attribute,
            value="18",
            slug="طول-18",
        )

        assert size_value.pk != length_value.pk


# ============================================================
# Product
# ============================================================


@pytest.mark.django_db
class TestProductModel:
    """Test product identity, slugs, constraints, and relationships."""

    @pytest.fixture
    def category(self):
        return Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
        )

    def test_str_returns_product_name(self, category):
        product = Product.objects.create(
            category=category,
            name="انگشتر طلای کلاسیک",
            slug="انگشتر-طلای-کلاسیک",
            sku="RNG-001",
            weight="2.500",
            purity=750,
        )

        assert str(product) == "انگشتر طلای کلاسیک"

    def test_slug_is_generated_when_missing(self, category):
        product = Product.objects.create(
            category=category,
            name="پلاک طلای قلب",
            sku="PND-001",
            weight="1.500",
            purity=750,
        )

        assert product.slug == "پلاک-طلای-قلب"

    def test_sku_must_be_unique(self, category):
        Product.objects.create(
            category=category,
            name="محصول اول",
            slug="محصول-اول",
            sku="SKU-001",
            weight="2.000",
            purity=750,
        )

        with pytest.raises(IntegrityError):
            Product.objects.create(
                category=category,
                name="محصول دوم",
                slug="محصول-دوم",
                sku="SKU-001",
                weight="3.000",
                purity=750,
            )

    def test_slug_must_be_unique(self, category):
        Product.objects.create(
            category=category,
            name="محصول اول",
            slug="محصول-یکسان",
            sku="SKU-001",
            weight="2.000",
            purity=750,
        )

        with pytest.raises(IntegrityError):
            Product.objects.create(
                category=category,
                name="محصول دوم",
                slug="محصول-یکسان",
                sku="SKU-002",
                weight="3.000",
                purity=750,
            )

    def test_weight_must_be_positive(self, category):
        with pytest.raises(IntegrityError):
            Product.objects.create(
                category=category,
                name="محصول نامعتبر",
                slug="محصول-نامعتبر",
                sku="INVALID-001",
                weight="0.000",
                purity=750,
            )

    def test_purity_must_be_positive(self, category):
        with pytest.raises(IntegrityError):
            Product.objects.create(
                category=category,
                name="محصول نامعتبر",
                slug="محصول-نامعتبر",
                sku="INVALID-002",
                weight="2.000",
                purity=0,
            )

    def test_product_can_be_inactive(self, category):
        product = Product.objects.create(
            category=category,
            name="محصول غیرفعال",
            slug="محصول-غیرفعال",
            sku="INACTIVE-001",
            weight="2.000",
            purity=750,
            is_active=False,
        )

        assert product.is_active is False

    def test_default_stock_is_zero(self, category):
        product = Product.objects.create(
            category=category,
            name="محصول جدید",
            slug="محصول-جدید",
            sku="NEW-001",
            weight="2.000",
            purity=750,
        )

        assert product.stock_quantity == 0


# ============================================================
# Product Variant
# ============================================================


@pytest.mark.django_db
class TestProductVariantModel:
    """Test product variant behavior and attribute relationships."""

    @pytest.fixture
    def product(self):
        category = Category.objects.create(
            name="انگشتر",
            slug="انگشتر",
        )

        return Product.objects.create(
            category=category,
            name="انگشتر طلای کلاسیک",
            slug="انگشتر-طلای-کلاسیک",
            sku="RNG-001",
            weight="2.500",
            purity=750,
        )

    @pytest.fixture
    def attribute_value(self):
        attribute = ProductAttribute.objects.create(
            name="سایز",
            slug="سایز",
        )

        return ProductAttributeValue.objects.create(
            attribute=attribute,
            value="18",
            slug="18",
        )

    def test_str_returns_product_and_sku(self, product):
        variant = ProductVariant.objects.create(
            product=product,
            sku="RNG-001-V1",
            weight="2.600",
            stock_quantity=2,
        )

        assert str(variant) == (
            "انگشتر طلای کلاسیک - RNG-001-V1"
        )

    def test_variant_sku_must_be_unique(self, product):
        ProductVariant.objects.create(
            product=product,
            sku="VARIANT-001",
            weight="2.500",
        )

        with pytest.raises(IntegrityError):
            ProductVariant.objects.create(
                product=product,
                sku="VARIANT-001",
                weight="2.600",
            )

    def test_variant_can_have_attributes(
        self,
        product,
        attribute_value,
    ):
        variant = ProductVariant.objects.create(
            product=product,
            sku="RNG-001-V1",
            weight="2.600",
            stock_quantity=2,
        )

        variant.attributes.add(attribute_value)

        assert variant.attributes.filter(
            pk=attribute_value.pk,
        ).exists()

    def test_variant_default_stock_is_zero(self, product):
        variant = ProductVariant.objects.create(
            product=product,
            sku="RNG-001-V1",
            weight="2.600",
        )

        assert variant.stock_quantity == 0


# ============================================================
# Product Image
# ============================================================


@pytest.mark.django_db
class TestProductImageModel:
    """Test product image relationships and representation."""

    @pytest.fixture
    def product(self):
        category = Category.objects.create(
            name="پلاک",
            slug="پلاک",
        )

        return Product.objects.create(
            category=category,
            name="پلاک طلای قلب",
            slug="پلاک-طلای-قلب",
            sku="PND-001",
            weight="1.500",
            purity=750,
        )

    def test_str_returns_product_and_image_id(
        self,
        product,
    ):
        image = ProductImage.objects.create(
            product=product,
            image="catalog/products/heart.webp",
        )

        assert str(image) == (
            f"{product.name} - Image #{image.pk}"
        )

    def test_multiple_images_can_belong_to_product(
        self,
        product,
    ):
        first_image = ProductImage.objects.create(
            product=product,
            image="catalog/products/heart-1.webp",
        )

        second_image = ProductImage.objects.create(
            product=product,
            image="catalog/products/heart-2.webp",
        )

        assert product.images.count() == 2
        assert first_image in product.images.all()
        assert second_image in product.images.all()