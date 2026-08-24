from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from apps.catalog.models import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductVariant,
)


class Command(BaseCommand):
    """
    Populate the catalog with a consistent development dataset.

    This command creates the core catalog entities required for local
    development and testing, including categories, brands, attributes,
    products, and product variants.

    The seed operation is idempotent: records are created or updated
    using stable unique identifiers, allowing the command to be executed
    repeatedly without creating duplicate catalog records.

    All operations are wrapped in a single database transaction so that
    a failure during the process rolls back the complete seed operation.
    """

    help = "Populate the catalog with development sample data."

    @transaction.atomic
    def handle(self, *args, **options):
        """
        Execute the complete catalog seed workflow.

        The creation order follows the dependency hierarchy of the catalog:
        categories and brands are created first, followed by attributes,
        products, and finally product variants.
        """

        self.stdout.write(
            self.style.NOTICE(
                "Starting catalog seed operation..."
            )
        )

        categories = self._create_categories()
        brands = self._create_brands()
        attributes = self._create_attributes()

        self._create_products(
            categories=categories,
            brands=brands,
            attributes=attributes,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Catalog seed completed successfully."
            )
        )

    def _create_categories(self):
        """
        Create the hierarchical catalog category structure.

        Returns:
            dict[str, Category]:
                Category objects indexed by their logical Persian names.
        """

        categories = {}

        category_definitions = [
            {
                "name": "انگشتر",
                "slug": "انگشتر",
                "description": "انواع انگشتر طلا",
                "display_order": 1,
            },
            {
                "name": "گردنبند",
                "slug": "گردنبند",
                "description": "انواع گردنبند طلا",
                "display_order": 2,
            },
            {
                "name": "دستبند",
                "slug": "دستبند",
                "description": "انواع دستبند طلا",
                "display_order": 3,
            },
            {
                "name": "گوشواره",
                "slug": "گوشواره",
                "description": "انواع گوشواره طلا",
                "display_order": 4,
            },
            {
                "name": "پلاک",
                "slug": "پلاک",
                "description": "انواع پلاک و آویز طلا",
                "display_order": 5,
            },
        ]

        for data in category_definitions:
            category, _ = Category.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "display_order": data["display_order"],
                    "is_active": True,
                },
            )

            categories[data["name"]] = category

        return categories

    def _create_brands(self):
        """
        Create reusable development brands.

        Returns:
            dict[str, Brand]:
                Brand objects indexed by their stable slug.

        Brands are stored as independent catalog entities and are later
        referenced by Product through a ForeignKey relationship.
        """

        brands = {}

        brand_definitions = [
            {
                "name": "SVG Gold",
                "slug": "svg-gold",
                "description": "برند نمونه فروشگاه برای داده‌های توسعه.",
            },
            {
                "name": "Gold House",
                "slug": "gold-house",
                "description": "برند نمونه برای تست کاتالوگ.",
            },
            {
                "name": "Royal Gold",
                "slug": "royal-gold",
                "description": "برند نمونه محصولات طلا.",
            },
        ]

        for data in brand_definitions:
            brand, _ = Brand.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "is_active": True,
                },
            )

            brands[data["slug"]] = brand

        return brands

    def _create_attributes(self):
        """
        Create reusable product attributes and their values.

        The returned structure provides direct access to both the
        ProductAttribute objects and their associated values, allowing
        variants to be populated without additional database lookups.
        """

        attribute_definitions = {
            "سایز": [
                "16",
                "17",
                "18",
                "19",
                "20",
            ],
            "رنگ": [
                "طلای زرد",
                "طلای سفید",
                "رزگلد",
            ],
            "عیار": [
                "18 عیار",
                "24 عیار",
            ],
        }

        attributes = {}

        for attribute_name, values in attribute_definitions.items():
            attribute, _ = ProductAttribute.objects.update_or_create(
                name=attribute_name,
                defaults={
                    "slug": self._slug_for_attribute(attribute_name),
                    "is_active": True,
                },
            )

            attributes[attribute_name] = {
                "attribute": attribute,
                "values": {},
            }

            for value in values:
                attribute_value, _ = (
                    ProductAttributeValue.objects.update_or_create(
                        attribute=attribute,
                        value=value,
                        defaults={
                            "slug": self._slug_for_value(
                                attribute_name,
                                value,
                            ),
                            "is_active": True,
                        },
                    )
                )

                attributes[attribute_name]["values"][value] = (
                    attribute_value
                )

        return attributes

    def _create_products(self, categories, brands, attributes):
        """
        Create representative gold products and their variants.

        Products are distributed across multiple catalog categories and
        brands so listing, filtering, detail pages, brand relationships,
        and variant-aware functionality can be tested with realistic data.
        """

        products = [
            {
                "category": "انگشتر",
                "brand": "svg-gold",
                "name": "انگشتر طلای کلاسیک",
                "slug": "انگشتر-طلای-کلاسیک",
                "sku": "RNG-1001",
                "description": "انگشتر طلای کلاسیک مناسب استفاده روزمره.",
                "weight": Decimal("2.850"),
                "purity": 750,
                "color": "yellow",
                "stock_quantity": 5,
                "is_featured": True,
                "is_bestseller": True,
                "is_new": True,
            },
            {
                "category": "انگشتر",
                "brand": "gold-house",
                "name": "انگشتر طلای سفید نگین‌دار",
                "slug": "انگشتر-طلای-سفید-نگین-دار",
                "sku": "RNG-1002",
                "description": "انگشتر طلای سفید با طراحی ظریف و مدرن.",
                "weight": Decimal("3.120"),
                "purity": 750,
                "color": "white",
                "stock_quantity": 3,
                "is_featured": True,
                "is_bestseller": False,
                "is_new": True,
            },
            {
                "category": "گردنبند",
                "brand": "royal-gold",
                "name": "گردنبند طلای ظریف",
                "slug": "گردنبند-طلای-ظریف",
                "sku": "NCK-2001",
                "description": "گردنبند طلای ظریف مناسب استفاده روزانه.",
                "weight": Decimal("4.650"),
                "purity": 750,
                "color": "yellow",
                "stock_quantity": 4,
                "is_featured": True,
                "is_bestseller": True,
                "is_new": True,
            },
            {
                "category": "دستبند",
                "brand": "svg-gold",
                "name": "دستبند طلای زنجیری",
                "slug": "دستبند-طلای-زنجیری",
                "sku": "BRL-3001",
                "description": "دستبند طلای زنجیری با طراحی کلاسیک.",
                "weight": Decimal("5.300"),
                "purity": 750,
                "color": "yellow",
                "stock_quantity": 6,
                "is_featured": False,
                "is_bestseller": True,
                "is_new": False,
            },
            {
                "category": "گوشواره",
                "brand": "gold-house",
                "name": "گوشواره طلای رزگلد",
                "slug": "گوشواره-طلای-رزگلد",
                "sku": "EAR-4001",
                "description": "گوشواره طلای رزگلد با طراحی مدرن.",
                "weight": Decimal("2.420"),
                "purity": 750,
                "color": "rose",
                "stock_quantity": 4,
                "is_featured": True,
                "is_bestseller": False,
                "is_new": True,
            },
            {
                "category": "پلاک",
                "brand": "royal-gold",
                "name": "پلاک طلای قلب",
                "slug": "پلاک-طلای-قلب",
                "sku": "PND-5001",
                "description": "پلاک طلای قلب مناسب هدیه.",
                "weight": Decimal("1.950"),
                "purity": 750,
                "color": "yellow",
                "stock_quantity": 8,
                "is_featured": False,
                "is_bestseller": True,
                "is_new": True,
            },
        ]

        for data in products:
            product, _ = Product.objects.update_or_create(
                sku=data["sku"],
                defaults={
                    "category": categories[data["category"]],
                    "brand": brands[data["brand"]],
                    "name": data["name"],
                    "slug": data["slug"],
                    "description": data["description"],
                    "weight": data["weight"],
                    "purity": data["purity"],
                    "color": data["color"],
                    "stock_quantity": data["stock_quantity"],
                    "is_active": True,
                    "is_featured": data["is_featured"],
                    "is_bestseller": data["is_bestseller"],
                    "is_new": data["is_new"],
                },
            )

            self._create_product_variants(
                product=product,
                attributes=attributes,
            )

    def _create_product_variants(self, product, attributes):
        """
        Create representative purchasable variants for a product.

        Ring products receive size-specific variants. Other products
        receive a default variant so the catalog can already be tested
        with variant-aware inventory and purchasing logic.
        """

        if product.category.name == "انگشتر":
            sizes = ["16", "17", "18"]

            for index, size in enumerate(sizes, start=1):
                variant, _ = ProductVariant.objects.update_or_create(
                    sku=f"{product.sku}-V{index}",
                    defaults={
                        "product": product,
                        "weight": product.weight + (
                            Decimal(index) / Decimal("100")
                        ),
                        "stock_quantity": 2,
                        "is_active": True,
                    },
                )

                variant.attributes.set(
                    [
                        attributes["سایز"]["values"][size],
                        attributes["عیار"]["values"]["18 عیار"],
                    ]
                )

        else:
            variant, _ = ProductVariant.objects.update_or_create(
                sku=f"{product.sku}-V1",
                defaults={
                    "product": product,
                    "weight": product.weight,
                    "stock_quantity": product.stock_quantity,
                    "is_active": True,
                },
            )

            variant.attributes.set(
                [
                    attributes["عیار"]["values"]["18 عیار"],
                ]
            )

    @staticmethod
    def _slug_for_attribute(name):
        """
        Generate a Unicode-compatible slug for a product attribute.

        Keeping Persian characters readable is intentional because the
        catalog models support Unicode slugs for SEO-friendly URLs.
        """

        return slugify(
            name,
            allow_unicode=True,
        )

    @staticmethod
    def _slug_for_value(attribute_name, value):
        """
        Generate a deterministic Unicode-compatible slug for an
        attribute value.
        """

        return slugify(
            f"{attribute_name}-{value}",
            allow_unicode=True,
        )