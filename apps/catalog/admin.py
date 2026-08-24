
from django.contrib import admin
from django.db.models import Count, QuerySet

from .models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
    ProductVariant,
)


# =============================================================================
# Category Admin
# =============================================================================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Administrative configuration for hierarchical product categories.

    Provides an optimized interface for managing category structure,
    activation state, ordering, searching, and SEO-friendly slugs.
    """

    list_display = (
        "name",
        "parent",
        "is_active",
        "display_order",
        "product_count",
        "created_at",
    )

    list_filter = (
        "is_active",
        "parent",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    ordering = (
        "display_order",
        "name",
    )

    list_editable = (
        "is_active",
        "display_order",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "parent",
    )

    list_per_page = 50

    def get_queryset(self, request):
        """
        Optimize category listing and expose product counts.
        """

        return (
            super()
            .get_queryset(request)
            .select_related("parent")
            .annotate(
                product_count=Count(
                    "products",
                    distinct=True,
                )
            )
        )

    @admin.display(
        description="تعداد محصولات",
        ordering="product_count",
    )
    def product_count(self, obj):
        """Return the number of products assigned to the category."""

        return obj.product_count


# =============================================================================
# Brand Admin
# =============================================================================


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """
    Administrative configuration for catalog brands.

    Centralizes brand management and provides efficient tools for
    searching, filtering, ordering, activation, and maintaining
    brand metadata and logos.
    """

    list_display = (
        "name",
        "is_active",
        "product_count",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
        "description",
    )

    ordering = (
        "name",
    )

    list_editable = (
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 50

    fieldsets = (
        (
            "اطلاعات برند",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                    "logo",
                ),
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_active",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        """
        Optimize brand listing and expose product counts.
        """

        return (
            super()
            .get_queryset(request)
            .annotate(
                product_count=Count(
                    "products",
                    distinct=True,
                )
            )
        )

    @admin.display(
        description="تعداد محصولات",
        ordering="product_count",
    )
    def product_count(self, obj):
        """Return the number of products assigned to the brand."""

        return obj.product_count


# =============================================================================
# Product Image Inline
# =============================================================================


class ProductImageInline(admin.TabularInline):
    """
    Inline administration interface for product images.

    Enables administrators to upload, order, and designate primary
    product images directly from the product administration page.
    """

    model = ProductImage

    extra = 1

    fields = (
        "image",
        "alt_text",
        "display_order",
        "is_primary",
    )

    ordering = (
        "display_order",
        "-created_at",
    )

    readonly_fields = (
        "created_at",
    )

    show_change_link = True


# =============================================================================
# Product Variant Inline
# =============================================================================


class ProductVariantInline(admin.TabularInline):
    """
    Inline administration interface for product variants.

    Allows all purchasable variations of a product to be maintained
    directly within the parent product administration workflow.
    """

    model = ProductVariant

    extra = 1

    fields = (
        "sku",
        "weight",
        "stock_quantity",
        "is_active",
        "attributes",
    )

    filter_horizontal = (
        "attributes",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    show_change_link = True


# =============================================================================
# Product Admin
# =============================================================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Administrative configuration for gold shop products.

    The interface is structured around the complete catalog workflow:
    product identification, classification, gold specifications,
    inventory management, merchandising flags, related media,
    and product variants.
    """

    list_display = (
        "name",
        "sku",
        "category",
        "brand",
        "weight",
        "purity",
        "color",
        "stock_quantity",
        "is_active",
        "is_featured",
        "is_bestseller",
        "is_new",
        "created_at",
    )

    list_filter = (
        "category",
        "brand",
        "purity",
        "color",
        "is_active",
        "is_featured",
        "is_bestseller",
        "is_new",
    )

    search_fields = (
        "name",
        "sku",
        "slug",
        "brand__name",
        "description",
    )

    ordering = (
        "-created_at",
    )

    list_editable = (
        "stock_quantity",
        "is_active",
        "is_featured",
        "is_bestseller",
        "is_new",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "category",
        "brand",
    )

    list_per_page = 50

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "name",
                    "slug",
                    "sku",
                    "category",
                    "brand",
                    "description",
                ),
            },
        ),
        (
            "مشخصات طلا",
            {
                "fields": (
                    "weight",
                    "purity",
                    "color",
                ),
            },
        ),
        (
            "موجودی و وضعیت فروش",
            {
                "fields": (
                    "stock_quantity",
                    "is_active",
                    "is_featured",
                    "is_bestseller",
                    "is_new",
                ),
            },
        ),
        (
            "اطلاعات سیستمی",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    inlines = (
        ProductImageInline,
        ProductVariantInline,
    )

    actions = (
        "activate_products",
        "deactivate_products",
        "mark_as_featured",
        "remove_from_featured",
        "mark_as_bestseller",
        "remove_from_bestseller",
    )

    def get_queryset(self, request):
        """
        Optimize product administration queries.

        Related category and brand objects are loaded in the same query
        to avoid unnecessary database round trips in the admin list.
        """

        return (
            super()
            .get_queryset(request)
            .select_related(
                "category",
                "brand",
            )
        )

    @admin.action(description="فعال کردن محصولات انتخاب‌شده")
    def activate_products(self, request, queryset: QuerySet):
        """Activate selected products."""

        updated = queryset.update(is_active=True)

        if request is not None:
            self.message_user(
                request,
                f"{updated} محصول فعال شد.",
            )

    @admin.action(description="غیرفعال کردن محصولات انتخاب‌شده")
    def deactivate_products(self, request, queryset: QuerySet):
        """Deactivate selected products."""

        updated = queryset.update(is_active=False)

        if request is not None:
            self.message_user(
                request,
                f"{updated} محصول غیرفعال شد.",
            )

    @admin.action(description="علامت‌گذاری به‌عنوان محصول ویژه")
    def mark_as_featured(self, request, queryset: QuerySet):
        """Mark selected products as featured."""

        updated = queryset.update(is_featured=True)

        if request is not None:
            self.message_user(
                request,
                f"{updated} محصول به‌عنوان محصول ویژه علامت‌گذاری شد.",
            )

    @admin.action(description="حذف از محصولات ویژه")
    def remove_from_featured(self, request, queryset: QuerySet):
        """Remove selected products from featured products."""

        updated = queryset.update(is_featured=False)

        if request is not None:
            self.message_user(
                request,
                f"{updated} محصول از محصولات ویژه حذف شد.",
            )

    @admin.action(description="علامت‌گذاری به‌عنوان پرفروش")
    def mark_as_bestseller(self, request, queryset: QuerySet):
        """Mark selected products as bestsellers."""

        updated = queryset.update(is_bestseller=True)

        if request is not None:
            self.message_user(
                request,
                f"{updated} محصول به‌عنوان پرفروش علامت‌گذاری شد.",
            )

    @admin.action(description="حذف از محصولات پرفروش")
    def remove_from_bestseller(self, request, queryset: QuerySet):
        """Remove selected products from bestsellers."""

        updated = queryset.update(is_bestseller=False)

        if request is not None:
            self.message_user(
                request,
                f"{updated} محصول از محصولات پرفروش حذف شد.",
            )


# =============================================================================
# Product Image Admin
# =============================================================================


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Administrative configuration for product images.

    Provides an independent management interface for reviewing,
    searching, ordering, and maintaining product media.
    """

    list_display = (
        "product",
        "display_order",
        "is_primary",
        "created_at",
    )

    list_filter = (
        "is_primary",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "alt_text",
    )

    ordering = (
        "product",
        "display_order",
    )

    list_editable = (
        "display_order",
        "is_primary",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "product",
    )

    list_per_page = 50

    def get_queryset(self, request):
        """
        Optimize product image administration queries.
        """

        return (
            super()
            .get_queryset(request)
            .select_related("product")
        )


# =============================================================================
# Product Attribute Admin
# =============================================================================


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """
    Administrative configuration for reusable product attributes.

    Provides centralized management for attribute definitions such as
    ring size, chain length, lock type, and other catalog properties.
    """

    list_display = (
        "name",
        "is_active",
        "value_count",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    ordering = (
        "name",
    )

    list_editable = (
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 50

    def get_queryset(self, request):
        """
        Optimize attribute listing and expose value counts.
        """

        return (
            super()
            .get_queryset(request)
            .annotate(
                value_count=Count(
                    "values",
                    distinct=True,
                )
            )
        )

    @admin.display(
        description="تعداد مقادیر",
        ordering="value_count",
    )
    def value_count(self, obj):
        """Return the number of values defined for the attribute."""

        return obj.value_count


# =============================================================================
# Product Attribute Value Admin
# =============================================================================


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    """
    Administrative configuration for product attribute values.

    Keeps individual attribute values structured under their parent
    attribute while providing efficient search, filtering, and status
    management.
    """

    list_display = (
        "value",
        "attribute",
        "is_active",
    )

    list_filter = (
        "attribute",
        "is_active",
    )

    search_fields = (
        "value",
        "slug",
        "attribute__name",
    )

    ordering = (
        "attribute",
        "value",
    )

    list_editable = (
        "is_active",
    )

    prepopulated_fields = {
        "slug": ("value",),
    }

    autocomplete_fields = (
        "attribute",
    )

    list_per_page = 50

    def get_queryset(self, request):
        """
        Optimize attribute value administration queries.
        """

        return (
            super()
            .get_queryset(request)
            .select_related("attribute")
        )


# =============================================================================
# Product Variant Admin
# =============================================================================


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    """
    Administrative configuration for product variants.

    Provides direct management of variant SKU, inventory, physical
    specifications, attributes, and activation state.
    """

    list_display = (
        "sku",
        "product",
        "weight",
        "stock_quantity",
        "is_active",
        "attribute_count",
        "created_at",
    )

    list_filter = (
        "is_active",
        "product__category",
    )

    search_fields = (
        "sku",
        "product__name",
        "product__sku",
    )

    ordering = (
        "product",
        "sku",
    )

    list_editable = (
        "stock_quantity",
        "is_active",
    )

    filter_horizontal = (
        "attributes",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    autocomplete_fields = (
        "product",
    )

    list_per_page = 50

    def get_queryset(self, request):
        """
        Optimize variant administration queries and attribute counts.
        """

        return (
            super()
            .get_queryset(request)
            .select_related(
                "product",
                "product__category",
            )
            .prefetch_related("attributes")
            .annotate(
                attribute_count=Count(
                    "attributes",
                    distinct=True,
                )
            )
        )

    @admin.display(
        description="تعداد ویژگی‌ها",
        ordering="attribute_count",
    )
    def attribute_count(self, obj):
        """Return the number of attributes assigned to the variant."""

        return obj.attribute_count

