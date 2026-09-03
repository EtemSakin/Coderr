from django.db.models import Min
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        ]
        read_only_fields = ['id']

    def validate_features(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Features must be a list.')
        return value


class OfferSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    details = OfferDetailSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'creator',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
        ]
        read_only_fields = ['id', 'creator', 'created_at', 'updated_at']

    def get_min_price(self, obj):
        value = getattr(obj, 'min_price', None)
        if value is not None:
            return value
        return obj.details.aggregate(value=Min('price'))['value']

    def get_min_delivery_time(self, obj):
        value = getattr(obj, 'min_delivery_time', None)
        if value is not None:
            return value
        field = 'delivery_time_in_days'
        return obj.details.aggregate(value=Min(field))['value']

    def validate_details(self, value):
        detail_types = [item['offer_type'] for item in value]
        expected = {
            OfferDetail.BASIC,
            OfferDetail.STANDARD,
            OfferDetail.PREMIUM,
        }
        if len(detail_types) != 3 or set(detail_types) != expected:
            raise serializers.ValidationError(
                'Basic, standard and premium details are required.'
            )
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        self._create_details(offer, details_data)
        return offer

    def _create_details(self, offer, details_data):
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data is not None:
            self._update_details(instance, details_data)
        return instance

    def _update_details(self, instance, details_data):
        current = {item.offer_type: item for item in instance.details.all()}
        for detail_data in details_data:
            detail = current[detail_data['offer_type']]
            for field, value in detail_data.items():
                setattr(detail, field, value)
            detail.save()
