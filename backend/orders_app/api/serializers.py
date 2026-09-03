from rest_framework import serializers

from offers_app.models import OfferDetail
from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        source='offer_detail',
        queryset=OfferDetail.objects.select_related('offer__creator'),
        write_only=True,
        required=False,
    )

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
            'status',
            'created_at',
            'updated_at',
            'offer_detail_id',
        ]
        read_only_fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        if self.instance is None and 'offer_detail' not in attrs:
            raise serializers.ValidationError(
                {'offer_detail_id': 'This field is required.'}
            )
        if self.instance is not None and 'offer_detail' in attrs:
            raise serializers.ValidationError(
                {'offer_detail_id': 'This field cannot be changed.'}
            )
        return attrs

    def validate_status(self, value):
        if self.instance is None:
            raise serializers.ValidationError(
                'Status cannot be set when creating an order.'
            )
        return value

    def create(self, validated_data):
        detail = validated_data.pop('offer_detail')
        user = self.context['request'].user
        return Order.objects.create(
            customer_user=user,
            business_user=detail.offer.creator,
            offer_detail=detail,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=list(detail.features),
        )
