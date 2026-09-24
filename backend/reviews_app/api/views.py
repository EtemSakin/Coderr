from django.db.models import Avg
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import Profile, User
from offers_app.models import Offer
from reviews_app.api.permissions import ReviewPermission
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
    """Provides CRUD operations, filtering and ordering for reviews."""

    queryset = Review.objects.select_related('reviewer', 'business_user')
    serializer_class = ReviewSerializer
    permission_classes = [ReviewPermission]
    pagination_class = None
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class BaseInfoView(APIView):
    """Returns aggregated marketplace statistics."""

    permission_classes = [AllowAny]

    def get(self, request):
        average_rating = Review.objects.aggregate(
            value=Avg('rating')
        )['value'] or 0
        data = {
            'offer_count': Offer.objects.count(),
            'review_count': Review.objects.count(),
            'business_profile_count': Profile.objects.filter(
                user__type=User.BUSINESS
            ).count(),
            'average_rating': round(average_rating, 1),
        }
        return Response(data)
