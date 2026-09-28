from django.shortcuts import get_object_or_404
from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializes the complete order snapshot."""

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """Creates an order from an offer detail id."""

    offer_detail_id = serializers.IntegerField()

    def validate(self, attrs):
        unknown = set(self.initial_data) - {'offer_detail_id'}
        if unknown:
            raise serializers.ValidationError(
                {field: 'This field is not editable.' for field in unknown}
            )
        return attrs

    def create(self, validated_data):
        detail = get_object_or_404(
            OfferDetail.objects.select_related('offer__creator'),
            pk=validated_data['offer_detail_id'],
        )
        return self._create_order(detail)

    def _create_order(self, detail):
        return Order.objects.create(
            customer_user=self.context['request'].user,
            business_user=detail.offer.creator,
            offer_detail=detail,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=list(detail.features),
            offer_type=detail.offer_type,
        )

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class OrderStatusSerializer(serializers.ModelSerializer):
    """Updates only the mutable order status."""

    class Meta:
        model = Order
        fields = ['status']

    def validate(self, attrs):
        unknown = set(self.initial_data) - {'status'}
        if unknown:
            raise serializers.ValidationError(
                {field: 'This field is not editable.' for field in unknown}
            )
        return attrs

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data
