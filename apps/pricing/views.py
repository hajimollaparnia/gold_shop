from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pricing.selectors import get_active_gold_price
from apps.pricing.serializers import MarketPriceSerializer


class CurrentGoldPriceAPIView(APIView):
    """
    Return the currently active 18K gold market price.
    """

    def get(self, request):
        market_price = get_active_gold_price()

        if market_price is None:
            return Response(
                {
                    "detail": "Gold price is currently unavailable.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MarketPriceSerializer(market_price)

        return Response(serializer.data)


def current_gold_price_fragment(request):
    """
    Render the current 18K gold price as an HTML fragment.
    """
    price = get_active_gold_price()

    return render(
        request,
        "pricing/_gold_price.html",
        {"price": price},
    )