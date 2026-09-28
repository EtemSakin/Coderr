"""Review API views and public marketplace statistics."""

from django.db.models import Avg
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import Profile, User
from offers_app.models import Offer
from reviews_app.api.permissions import ReviewPermission
from reviews_app.api.serializers import (
    ReviewSerializer,
    ReviewUpdateSerializer,
)
from reviews_app.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
    """Provide CRUD operations, filtering and ordering for reviews."""

    queryset = Review.objects.select_related('reviewer', 'business_user')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, ReviewPermission]
    pagination_class = None
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Filter reviews by business or reviewer query parameters."""
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset

    def get_serializer_class(self):
        """Use the restricted serializer for partial updates."""
        if self.action == 'partial_update':
            return ReviewUpdateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        """Assign the authenticated customer as review author."""
        serializer.save(reviewer=self.request.user)


class BaseInfoView(APIView):
    """Return aggregated marketplace statistics."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        """Return the current public platform statistics."""
        return Response(self._statistics_data())

    def _statistics_data(self):
        """Build offer, review, business, and rating statistics."""
        average = Review.objects.aggregate(value=Avg('rating'))['value'] or 0
        business_count = Profile.objects.filter(
            user__type=User.BUSINESS
        ).count()
        return {
            'offer_count': Offer.objects.count(),
            'review_count': Review.objects.count(),
            'business_profile_count': business_count,
            'average_rating': round(average, 1),
        }
