from drf_spectacular.utils import OpenApiResponse, extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import (
    ProductNotFoundError,
    ProductVariantNotFoundError,
    WishlistItemAlreadyExistsError,
    WishlistItemNotFoundError,
)
from .serializers import (
    AddWishlistItemSerializer,
    WishlistItemSerializer,
    WishlistSerializer,
)
from .services import WishlistService


class WishlistDetailAPIView(APIView):
    """Return the authenticated user's wishlist."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Wishlist"],
        summary="Retrieve user's wishlist",
        responses={
            200: WishlistSerializer,
        },
    )
    def get(self, request):
        wishlist = WishlistService.get_wishlist(request.user)

        if wishlist is None:
            wishlist = WishlistService.get_or_create_wishlist(
                request.user,
            )

        return Response(
            WishlistSerializer(wishlist).data,
            status=status.HTTP_200_OK,
        )


class WishlistItemCreateAPIView(APIView):
    """Add a product or variant to the user's wishlist."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Wishlist"],
        summary="Add item to wishlist",
        request=AddWishlistItemSerializer,
        responses={
            201: WishlistItemSerializer,
            400: OpenApiResponse(
                description="Wishlist item already exists.",
            ),
            404: OpenApiResponse(
                description="Product or product variant not found.",
            ),
        },
    )
    def post(self, request):
        serializer = AddWishlistItemSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        try:
            item = WishlistService.add_item(
                user=request.user,
                product_id=serializer.validated_data["product_id"],
                variant_id=serializer.validated_data.get("variant_id"),
            )

        except (
            ProductNotFoundError,
            ProductVariantNotFoundError,
        ) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except WishlistItemAlreadyExistsError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            WishlistItemSerializer(item).data,
            status=status.HTTP_201_CREATED,
        )


class WishlistItemDeleteAPIView(APIView):
    """Remove an item from the authenticated user's wishlist."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Wishlist"],
        summary="Remove item from wishlist",
        request=None,
        responses={
            204: OpenApiResponse(
                description="Wishlist item removed successfully.",
            ),
            404: OpenApiResponse(
                description="Wishlist item not found.",
            ),
        },
    )
    def delete(self, request, item_id):
        try:
            WishlistService.remove_item(
                user=request.user,
                item_id=item_id,
            )

        except WishlistItemNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


class WishlistClearAPIView(APIView):
    """Remove all items from the authenticated user's wishlist."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Wishlist"],
        summary="Clear wishlist",
        request=None,
        responses={
            204: OpenApiResponse(
                description="Wishlist cleared successfully.",
            ),
        },
    )
    def delete(self, request):
        WishlistService.clear_wishlist(request.user)

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )