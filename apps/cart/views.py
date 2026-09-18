from drf_spectacular.utils import OpenApiResponse, extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import (
    CartItemNotFoundError,
    InvalidCartQuantityError,
    ProductNotFoundError,
    ProductVariantNotFoundError,
)
from .selectors import CartSelector
from .serializers import (
    AddCartItemSerializer,
    CartItemSerializer,
    CartSerializer,
    UpdateCartItemSerializer,
)
from .services import CartService


class CartDetailAPIView(APIView):
    """Return the authenticated user's shopping cart."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        summary="Retrieve shopping cart",
        responses={
            200: CartSerializer,
        },
    )
    def get(self, request):
        cart = CartSelector.get_cart_for_user(request.user)

        if cart is None:
            cart = CartService.get_or_create_cart(request.user)

        return Response(
            CartSerializer(cart).data,
            status=status.HTTP_200_OK,
        )


class CartItemCreateAPIView(APIView):
    """Add a product or variant to the authenticated user's cart."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        summary="Add item to cart",
        request=AddCartItemSerializer,
        responses={
            201: CartItemSerializer,
            400: OpenApiResponse(
                description="Invalid cart quantity.",
            ),
            404: OpenApiResponse(
                description="Product or product variant not found.",
            ),
        },
    )
    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = CartService.add_item(
                user=request.user,
                product_id=serializer.validated_data["product_id"],
                quantity=serializer.validated_data["quantity"],
                variant_id=serializer.validated_data.get("variant_id"),
            )
        except ProductNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ProductVariantNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InvalidCartQuantityError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemUpdateAPIView(APIView):
    """Update the quantity of an existing cart item."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        summary="Update cart item",
        request=UpdateCartItemSerializer,
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(
                description="Invalid cart quantity.",
            ),
            404: OpenApiResponse(
                description="Cart item not found.",
            ),
        },
    )
    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = CartService.update_item(
                user=request.user,
                item_id=item_id,
                quantity=serializer.validated_data["quantity"],
            )
        except CartItemNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )
        except InvalidCartQuantityError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_200_OK,
        )


class CartItemDeleteAPIView(APIView):
    """Remove an item from the authenticated user's cart."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        summary="Remove cart item",
        request=None,
        responses={
            204: OpenApiResponse(
                description="Cart item removed successfully.",
            ),
            404: OpenApiResponse(
                description="Cart item not found.",
            ),
        },
    )
    def delete(self, request, item_id):
        try:
            CartService.remove_item(
                user=request.user,
                item_id=item_id,
            )
        except CartItemNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearAPIView(APIView):
    """Remove all items from the authenticated user's cart."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Cart"],
        summary="Clear shopping cart",
        request=None,
        responses={
            204: OpenApiResponse(
                description="Shopping cart cleared successfully.",
            ),
        },
    )
    def delete(self, request):
        CartService.clear_cart(request.user)

        return Response(status=status.HTTP_204_NO_CONTENT)