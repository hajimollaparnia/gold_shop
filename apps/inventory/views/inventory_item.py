from rest_framework import generics
from rest_framework.permissions import IsAdminUser

from apps.inventory.models import InventoryItem
from apps.inventory.serializers.inventory_item import InventoryItemSerializer


class InventoryItemListView(generics.ListAPIView):
    """
    Return a list of inventory items.

    Inventory data is restricted to admin users because stock levels
    are internal business information.
    """

    queryset = (
        InventoryItem.objects
        .select_related("product", "variant")
        .all()
    )

    serializer_class = InventoryItemSerializer
    permission_classes = (IsAdminUser,)


class InventoryItemDetailView(generics.RetrieveAPIView):
    """
    Return details of a single inventory item.

    Inventory data is restricted to admin users.
    """

    queryset = (
        InventoryItem.objects
        .select_related("product", "variant")
        .all()
    )

    serializer_class = InventoryItemSerializer
    permission_classes = (IsAdminUser,)