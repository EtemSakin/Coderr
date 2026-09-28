"""Offer API views, filtering, ordering, and permissions."""

from django.db.models import Min
from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
    NumberFilter,
)
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from offers_app.api.pagination import OfferPagination
from offers_app.api.permissions import (
    IsBusinessOrReadOnly,
    IsOfferOwnerOrReadOnly,
)
from offers_app.api.serializers import (
    OfferDetailSerializer,
    OfferListSerializer,
    OfferReadSerializer,
    OfferWriteSerializer,
)
from offers_app.models import Offer, OfferDetail


class OfferFilter(FilterSet):
    """Define supported filtering options for offer lists."""

    creator_id = NumberFilter(field_name='creator_id')
    min_price = NumberFilter(method='filter_min_price')
    max_delivery_time = NumberFilter(method='filter_max_delivery_time')

    class Meta:
        """Bind filters to the offer model."""

        model = Offer
        fields = []

    def filter_min_price(self, queryset, name, value):
        """Keep offers whose cheapest tier meets the minimum price."""
        return queryset.filter(min_price__gte=value)

    def filter_max_delivery_time(self, queryset, name, value):
        """Keep offers deliverable within the requested duration."""
        return queryset.filter(min_delivery_time__lte=value)


class OfferViewSet(viewsets.ModelViewSet):
    """Provide CRUD operations and filtering for offers."""

    queryset = Offer.objects.all()
    serializer_class = OfferWriteSerializer
    permission_classes = [
        IsAuthenticated,
        IsBusinessOrReadOnly,
        IsOfferOwnerOrReadOnly,
    ]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['-updated_at']
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
        'head',
        'options',
    ]

    def get_queryset(self):
        """Return offers annotated with cheapest and fastest tiers."""
        return (
            Offer.objects.select_related('creator')
            .prefetch_related('details')
            .annotate(
                min_price=Min('details__price'),
                min_delivery_time=Min('details__delivery_time_in_days'),
            )
        )

    def get_permissions(self):
        """Allow anonymous listing while protecting all other actions."""
        if self.action == 'list':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Select the serializer matching the current action."""
        if self.action == 'list':
            return OfferListSerializer
        if self.action == 'retrieve':
            return OfferReadSerializer
        return OfferWriteSerializer

    def perform_create(self, serializer):
        """Assign the authenticated business user as offer creator."""
        serializer.save(creator=self.request.user)


class OfferDetailView(generics.RetrieveAPIView):
    """Return a single offer detail by id."""

    queryset = OfferDetail.objects.select_related('offer')
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
