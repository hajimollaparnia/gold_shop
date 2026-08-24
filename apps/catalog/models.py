from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify

from decimal import Decimal


class Category(models.Model):
    """
    Represents a hierarchical product category in the gold shop catalog.

    Categories support parent-child relationships, allowing the catalog
    to represent multiple levels of classification without requiring
    separate models for each category depth.
    """

    name = models.CharField(
        max_length=150,
        verbose_name="نام دسته‌بندی",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        blank=True,
        null=True,
        verbose_name="دسته‌بندی والد",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="ترتیب نمایش",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["display_order", "name"]

        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_category_name_per_parent",
            ),
        ]

    def __str__(self):
        """Return the category name for administrative and debugging output."""

        return self.name

    def save(self, *args, **kwargs):
        """
        Persist the category and generate a Unicode-compatible slug when
        a slug has not been explicitly provided.
        """

        if not self.slug:
            self.slug = slugify(
                self.name,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


class Brand(models.Model):
    """
    Represents a reusable product brand within the catalog.

    Brands are modeled independently from products so they can be reused
    across the catalog and later support filtering, landing pages,
    and dedicated SEO content.
    """

    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="نام برند",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    logo = models.ImageField(
        upload_to="catalog/brands/",
        blank=True,
        null=True,
        verbose_name="لوگو",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ["name"]

    def __str__(self):
        """Return the brand name for administrative and debugging output."""

        return self.name

    def save(self, *args, **kwargs):
        """
        Persist the brand and generate a Unicode-compatible slug when
        a slug has not been explicitly provided.
        """

        if not self.slug:
            self.slug = slugify(
                self.name,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


class ProductAttribute(models.Model):
    """
    Defines a reusable product attribute.

    Attributes are separated from products so new characteristics can
    be introduced without changing the Product database schema.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="نام ویژگی",
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "ویژگی محصول"
        verbose_name_plural = "ویژگی‌های محصول"
        ordering = ["name"]

    def __str__(self):
        """Return the attribute name for administrative and debugging output."""

        return self.name

    def save(self, *args, **kwargs):
        """
        Persist the attribute and generate its slug when necessary.
        """

        if not self.slug:
            self.slug = slugify(
                self.name,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Represents a gold product in the store catalog.

    The model contains stable product identity and physical catalog data.
    Dynamic pricing, inventory movements, reservations, and transactional
    pricing snapshots are intentionally handled by dedicated domains.
    """

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
        verbose_name="دسته‌بندی",
    )

    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="products",
        blank=True,
        null=True,
        db_index=True,
        verbose_name="برند",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="نام محصول",
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    sku = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name="کد محصول",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    # Physical gold weight is stored with milligram-level precision.
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[
            MinValueValidator(Decimal("0.001")),
        ],
        verbose_name="وزن (گرم)",
    )

    # Gold purity is stored numerically to support pricing calculations.
    purity = models.PositiveSmallIntegerField(
        default=750,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="عیار",
    )

    class GoldColor(models.TextChoices):
        """Supported gold colors used for catalog classification."""

        YELLOW = "yellow", "طلای زرد"
        WHITE = "white", "طلای سفید"
        ROSE = "rose", "رزگلد"

    color = models.CharField(
        max_length=20,
        choices=GoldColor.choices,
        default=GoldColor.YELLOW,
        verbose_name="رنگ طلا",
    )

    # Legacy catalog stock is retained temporarily until the dedicated
    # inventory domain becomes the source of truth for stock management.
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="محصول ویژه",
    )

    is_bestseller = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="پرفروش",
    )

    is_new = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="محصول جدید",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(weight__gt=0),
                name="product_weight_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(purity__gt=0),
                name="product_purity_positive",
            ),
        ]

        indexes = [
            models.Index(
                fields=["category", "is_active"],
                name="product_category_active_idx",
            ),
            models.Index(
                fields=["brand", "is_active"],
                name="product_brand_active_idx",
            ),
            models.Index(
                fields=["is_active", "-created_at"],
                name="product_active_created_idx",
            ),
        ]

    def __str__(self):
        """Return the product name for administrative and debugging output."""

        return self.name

    def save(self, *args, **kwargs):
        """
        Persist the product and generate a Unicode-compatible slug when
        a slug has not been explicitly provided.
        """

        if not self.slug:
            self.slug = slugify(
                self.name,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


class ProductAttributeValue(models.Model):
    """
    Represents a concrete value belonging to a reusable product attribute.

    Attribute values provide structured options such as ring size,
    chain length, or clasp type and can be assigned to product variants.
    """

    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE,
        related_name="values",
        verbose_name="ویژگی",
    )

    value = models.CharField(
        max_length=150,
        verbose_name="مقدار",
    )

    slug = models.SlugField(
        max_length=180,
        allow_unicode=True,
        verbose_name="اسلاگ",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    class Meta:
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی"
        ordering = ["value"]

        constraints = [
            models.UniqueConstraint(
                fields=["attribute", "value"],
                name="unique_attribute_value",
            ),
        ]

    def __str__(self):
        """Return a readable representation of the attribute value."""

        return f"{self.attribute.name}: {self.value}"

    def save(self, *args, **kwargs):
        """
        Persist the attribute value and generate its slug when necessary.
        """

        if not self.slug:
            self.slug = slugify(
                self.value,
                allow_unicode=True,
            )

        super().save(*args, **kwargs)


class ProductVariant(models.Model):
    """
    Represents a purchasable variation of a catalog product.

    Variants support product configurations such as different ring sizes,
    chain lengths, or other selectable attributes while maintaining
    independent SKU, weight, and inventory information.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
        verbose_name="محصول",
    )

    sku = models.CharField(
        max_length=80,
        unique=True,
        db_index=True,
        verbose_name="کد SKU",
    )

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(Decimal("0.001")),
        ],
        verbose_name="وزن (گرم)",
    )

    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="موجودی",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="فعال",
    )

    attributes = models.ManyToManyField(
        ProductAttributeValue,
        blank=True,
        related_name="variants",
        verbose_name="ویژگی‌ها",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی",
    )

    class Meta:
        verbose_name = "تنوع محصول"
        verbose_name_plural = "تنوع‌های محصول"
        ordering = ["product", "sku"]

        indexes = [
            models.Index(
                fields=["product", "is_active"],
                name="variant_product_active_idx",
            ),
        ]

    def __str__(self):
        """Return a readable representation of the product variant."""

        return f"{self.product.name} - {self.sku}"


class ProductImage(models.Model):
    """
    Represents an image associated with a catalog product.

    A dedicated image model allows each product to have multiple images
    while supporting explicit display ordering, SEO-friendly alt text,
    and primary-image selection.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="محصول",
    )

    image = models.ImageField(
        upload_to="catalog/products/",
        verbose_name="تصویر",
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="متن جایگزین تصویر",
    )

    display_order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name="ترتیب نمایش",
    )

    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="تصویر اصلی",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
    )

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصولات"
        ordering = ["display_order", "-created_at"]

        indexes = [
            models.Index(
                fields=["product", "is_primary"],
                name="image_product_primary_idx",
            ),
        ]

    def __str__(self):
        """Return a readable representation of the product image."""

        return f"{self.product.name} - Image #{self.pk}"