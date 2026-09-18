from drf_spectacular.utils import OpenApiResponse, extend_schema

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import (
    ProductNotFoundError,
    ProductVariantNotFoundError,
    ReviewAlreadyExistsError,
    ReviewNotFoundError,
)
from .serializers import CreateReviewSerializer, ReviewSerializer
from .services import ReviewService


class ReviewCreateAPIView(APIView):
    """Create a product review for the authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reviews"],
        summary="Create product review",
        request=CreateReviewSerializer,
        responses={
            201: ReviewSerializer,
            400: OpenApiResponse(
                description="Review already exists for this product.",
            ),
            404: OpenApiResponse(
                description="Product or product variant not found.",
            ),
        },
    )
    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            review = ReviewService.create_review(
                user=request.user,
                product_id=serializer.validated_data["product_id"],
                variant_id=serializer.validated_data.get("variant_id"),
                rating=serializer.validated_data["rating"],
                title=serializer.validated_data.get("title", ""),
                comment=serializer.validated_data.get("comment", ""),
            )

        except (
            ProductNotFoundError,
            ProductVariantNotFoundError,
        ) as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ReviewAlreadyExistsError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            ReviewSerializer(review).data,
            status=status.HTTP_201_CREATED,
        )


class ReviewDeleteAPIView(APIView):
    """Delete a review owned by the authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Reviews"],
        summary="Delete product review",
        request=None,
        responses={
            204: OpenApiResponse(
                description="Review deleted successfully.",
            ),
            404: OpenApiResponse(
                description="Review not found.",
            ),
        },
    )
    def delete(self, request, review_id):
        try:
            ReviewService.delete_review(
                user=request.user,
                review_id=review_id,
            )

        except ReviewNotFoundError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )