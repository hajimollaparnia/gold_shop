from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import (
    CouponNotFoundError,
    ExpiredCouponError,
    InactiveCouponError,
    InvalidCouponError,
    CouponUsageLimitError,
    UserCouponUsageLimitError,
    MinimumOrderAmountError,
)
from .serializers import (
    CouponValidateSerializer,
    CouponValidationResponseSerializer,
)
from .services import CouponService


class CouponValidateAPIView(APIView):
    """Validate a coupon against an order amount."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"]
        order_amount = serializer.validated_data["order_amount"]

        try:
            coupon = CouponService.validate_coupon(
                user=request.user,
                code=code,
                order_amount=order_amount,
            )

            discount_amount = CouponService.calculate_discount(
                coupon=coupon,
                order_amount=order_amount,
            )

        except CouponNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except (
            ExpiredCouponError,
            InactiveCouponError,
            InvalidCouponError,
            CouponUsageLimitError,
            UserCouponUsageLimitError,
            MinimumOrderAmountError,
        ) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        final_amount = order_amount - discount_amount

        response_data = {
            "coupon": coupon,
            "discount_amount": discount_amount,
            "final_amount": final_amount,
        }

        response_serializer = CouponValidationResponseSerializer(
            response_data,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )