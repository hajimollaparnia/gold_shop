
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import MarketPrice, PriceSnapshot, PricingRule


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for managing live and historical market prices.

    Provides filtering, searching, sorting, bulk activation/deactivation,
    and structured fieldsets for efficient price management.
    """

    list_display = (
        "asset_display",
        "purity",
        "buy_price_display",
        "sell_price_display",
        "currency_display",
        "provider_display",
        "status_display",
        "effective_at",
    )

    list_filter = (
        "asset",
        "purity",
        "currency",
        "provider",
        "is_active",
    )

    search_fields = (
        "source",
    )

    ordering = (
        "-effective_at",
        "-id",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    date_hierarchy = "effective_at"

    list_per_page = 50

    # Provides bulk operations for quickly activating or deactivating
    # multiple market price records from the admin list view.
    actions = (
        "activate_selected",
        "deactivate_selected",
    )

    fieldsets = (
        (
            _("اطلاعات بازار"),
            {
                "fields": (
                    "asset",
                    "purity",
                    "currency",
                )
            },
        ),
        (
            _("قیمت‌های بازار"),
            {
                "fields": (
                    "buy_price",
                    "sell_price",
                )
            },
        ),
        (
            _("منبع قیمت"),
            {
                "fields": (
                    "provider",
                    "source",
                )
            },
        ),
        (
            _("وضعیت قیمت"),
            {
                "fields": (
                    "is_active",
                    "effective_at",
                )
            },
        ),
        (
            _("اطلاعات سیستمی"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(
        description="دارایی",
        ordering="asset",
    )
    def asset_display(self, obj):
        """Return the human-readable asset label."""
        return obj.get_asset_display()

    @admin.display(
        description="قیمت خرید",
        ordering="buy_price",
    )
    def buy_price_display(self, obj):
        """Format the market buy price as a readable Rial amount."""
        return f"{obj.buy_price:,.0f} ریال"

    @admin.display(
        description="قیمت فروش",
        ordering="sell_price",
    )
    def sell_price_display(self, obj):
        """Format the market sell price as a readable Rial amount."""
        return f"{obj.sell_price:,.0f} ریال"

    @admin.display(
        description="ارز",
        ordering="currency",
    )
    def currency_display(self, obj):
        """Return the human-readable currency label."""
        return obj.get_currency_display()

    @admin.display(
        description="ارائه‌دهنده",
        ordering="provider",
    )
    def provider_display(self, obj):
        """Return the human-readable price provider label."""
        return obj.get_provider_display()

    @admin.display(
        description="فعال",
        boolean=True,
        ordering="is_active",
    )
    def status_display(self, obj):
        """Display the active state using Django Admin's boolean indicator."""
        return obj.is_active

    @admin.action(description="فعال‌سازی قیمت‌های انتخاب‌شده")
    def activate_selected(self, request, queryset):
        """
        Activate all selected market prices in a single database operation.
        """
        updated = queryset.update(is_active=True)

        self.message_user(
            request,
            f"{updated} قیمت با موفقیت فعال شد.",
        )

    @admin.action(description="غیرفعال‌سازی قیمت‌های انتخاب‌شده")
    def deactivate_selected(self, request, queryset):
        """
        Deactivate all selected market prices in a single database operation.
        """
        updated = queryset.update(is_active=False)

        self.message_user(
            request,
            f"{updated} قیمت با موفقیت غیرفعال شد.",
        )


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for managing pricing rules.

    Pricing rules define the making fee, seller profit, tax, additional
    charges, and validity period used by the pricing engine.
    """

    list_display = (
        "name",
        "making_fee_display",
        "profit_display",
        "tax_rate_display",
        "other_charge_display",
        "is_active",
        "effective_from",
        "effective_until",
    )

    list_filter = (
        "making_fee_type",
        "profit_type",
        "is_active",
    )

    search_fields = (
        "name",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 50

    fieldsets = (
        (
            _("اطلاعات قانون قیمت‌گذاری"),
            {
                "fields": (
                    "name",
                    "is_active",
                )
            },
        ),
        (
            _("اجرت ساخت"),
            {
                "fields": (
                    "making_fee_type",
                    "making_fee_value",
                )
            },
        ),
        (
            _("سود فروشنده"),
            {
                "fields": (
                    "profit_type",
                    "profit_value",
                )
            },
        ),
        (
            _("مالیات و هزینه‌های اضافی"),
            {
                "fields": (
                    "tax_rate",
                    "other_charge",
                )
            },
        ),
        (
            _("بازه زمانی اعتبار"),
            {
                "fields": (
                    "effective_from",
                    "effective_until",
                )
            },
        ),
        (
            _("اطلاعات سیستمی"),
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="اجرت ساخت")
    def making_fee_display(self, obj):
        """Format the making fee according to its configured calculation type."""
        if obj.making_fee_type == "percentage":
            return f"{obj.making_fee_value}%"

        return f"{obj.making_fee_value:,.0f} ریال"

    @admin.display(description="سود فروشنده")
    def profit_display(self, obj):
        """Format the seller profit according to its configured calculation type."""
        if obj.profit_type == "percentage":
            return f"{obj.profit_value}%"

        return f"{obj.profit_value:,.0f} ریال"

    @admin.display(description="مالیات")
    def tax_rate_display(self, obj):
        """Format the configured tax rate as a percentage."""
        return f"{obj.tax_rate}%"

    @admin.display(description="هزینه اضافی")
    def other_charge_display(self, obj):
        """Format additional charges as a readable Rial amount."""
        return f"{obj.other_charge:,.0f} ریال"


@admin.register(PriceSnapshot)
class PriceSnapshotAdmin(admin.ModelAdmin):
    """
    Read-only Django Admin configuration for calculated price snapshots.

    Snapshots represent immutable records of pricing calculations and are
    intentionally protected from manual creation, modification, or deletion.
    """

    list_display = (
        "id",
        "market_price_display",
        "weight",
        "purity",
        "subtotal_display",
        "discount_display",
        "final_price_display",
        "currency_display",
        "calculated_at",
    )

    list_filter = (
        "currency",
        "purity",
    )

    search_fields = (
        "id",
    )

    ordering = (
        "-calculated_at",
        "-id",
    )

    # Snapshot values are calculation results and must remain immutable
    # after creation to preserve the integrity of historical pricing data.
    readonly_fields = (
        "market_price",
        "weight",
        "purity",
        "gold_value",
        "making_charge",
        "profit",
        "tax",
        "other_charges",
        "discount",
        "subtotal",
        "final_price",
        "currency",
        "calculated_at",
        "created_at",
    )

    list_per_page = 50

    fieldsets = (
        (
            _("اطلاعات پایه"),
            {
                "fields": (
                    "market_price",
                    "weight",
                    "purity",
                    "currency",
                )
            },
        ),
        (
            _("جزئیات محاسبه"),
            {
                "fields": (
                    "gold_value",
                    "making_charge",
                    "profit",
                    "tax",
                    "other_charges",
                    "discount",
                )
            },
        ),
        (
            _("نتیجه نهایی"),
            {
                "fields": (
                    "subtotal",
                    "final_price",
                )
            },
        ),
        (
            _("اطلاعات سیستمی"),
            {
                "fields": (
                    "calculated_at",
                    "created_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="قیمت بازار")
    def market_price_display(self, obj):
        """Format the referenced market price as a readable Rial amount."""
        return f"{obj.market_price:,.0f} ریال"

    @admin.display(description="مبلغ اولیه")
    def subtotal_display(self, obj):
        """Format the calculated subtotal as a readable Rial amount."""
        return f"{obj.subtotal:,.0f} ریال"

    @admin.display(description="تخفیف")
    def discount_display(self, obj):
        """Format the applied discount as a readable Rial amount."""
        return f"{obj.discount:,.0f} ریال"

    @admin.display(description="قیمت نهایی")
    def final_price_display(self, obj):
        """Format the final calculated price as a readable Rial amount."""
        return f"{obj.final_price:,.0f} ریال"

    @admin.display(description="ارز")
    def currency_display(self, obj):
        """Return the human-readable currency label."""
        return obj.get_currency_display()

    def has_add_permission(self, request):
        """
        Prevent manual creation of price snapshots through Django Admin.

        Snapshots should only be generated by the pricing service.
        """
        return False

    def has_change_permission(self, request, obj=None):
        """
        Prevent manual modification of existing price snapshots.

        Historical calculation results must remain immutable.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Prevent deletion of price snapshots through Django Admin.

        This protects historical pricing and audit information.
        """
        return False

