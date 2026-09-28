"""Order API views and order counters."""

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.models import User
from orders_app.api.permissions import OrderPermission
from orders_app.api.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    OrderStatusSerializer,
)
from orders_app.models import Order


class OrderViewSet(viewsets.ModelViewSet):
    """Provide order listing, creation, retrieval, updates and deletion."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermission]
    pagination_class = None
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        """Return orders visible to the current action and user."""
        if self.action in ('partial_update', 'destroy'):
            queryset = Order.objects.all()
        else:
            user = self.request.user
            queryset = Order.objects.filter(
                Q(customer_user=user) | Q(business_user=user)
            )
        return queryset.select_related(
            'customer_user', 'business_user', 'offer_detail'
        ).order_by('-created_at')

    def get_serializer_class(self):
        """Select the serializer matching the current order action."""
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'partial_update':
            return OrderStatusSerializer
        return OrderSerializer


class OrderCountView(APIView):
    """Return the number of in-progress orders for a business."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Count in-progress orders after validating the business id."""
        business = get_object_or_404(
            User,
            pk=business_user_id,
            type=User.BUSINESS,
        )
        count = Order.objects.filter(
            business_user=business,
            status=Order.IN_PROGRESS,
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    """Return the number of completed orders for a business."""

    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """Count completed orders after validating the business id."""
        business = get_object_or_404(
            User,
            pk=business_user_id,
            type=User.BUSINESS,
        )
        count = Order.objects.filter(
            business_user=business,
            status=Order.COMPLETED,
        ).count()
        return Response({'completed_order_count': count})
