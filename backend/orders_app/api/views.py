from django.db.models import Q
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders_app.api.permissions import OrderPermission
from orders_app.api.serializers import OrderSerializer
from orders_app.models import Order


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderPermission]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(
            Q(customer_user=user) | Q(business_user=user)
        )
        return queryset.select_related(
            'customer_user', 'business_user', 'offer_detail'
        ).order_by('-created_at')


class OrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status=Order.IN_PROGRESS,
        ).count()
        return Response({'order_count': count})


class CompletedOrderCountView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, business_user_id):
        count = Order.objects.filter(
            business_user_id=business_user_id,
            status=Order.COMPLETED,
        ).count()
        return Response({'completed_order_count': count})
