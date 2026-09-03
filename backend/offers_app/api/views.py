from django.db.models import Min
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    NumberFilter,
)
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny

from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import (
    IsBusinessOrReadOnly,
    IsOfferOwnerOrReadOnly,
)
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferSerializer,
)
from offers_app.models import Offer, OfferDetail


class OfferFilter(FilterSet):
    creator_id = NumberFilter(field_name='creator_id')
    max_delivery_time = NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = []

    def filter_max_delivery_time(self, queryset, name, value):
        return queryset.filter(min_delivery_time__lte=value)


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsBusinessOrReadOnly, IsOfferOwnerOrReadOnly]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']

    def get_queryset(self):
        return (
            Offer.objects.select_related('creator')
            .prefetch_related('details')
            .annotate(
                min_price=Min('details__price'),
                min_delivery_time=Min('details__delivery_time_in_days'),
            )
        )

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class OfferDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.select_related('offer')
    serializer_class = OfferDetailSerializer
    permission_classes = [AllowAny]
