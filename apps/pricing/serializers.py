from rest_framework import serializers

from apps.pricing.models import MarketPrice


class MarketPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketPrice
        fields = (
            "asset",
            "purity",
            "buy_price",
            "sell_price",
            "currency",
            "effective_at",
        )