from rest_framework import filters, viewsets

from reviews_app.api.permissions import ReviewPermission
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
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
