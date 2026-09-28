from django.db import transaction
from django.db.models import Min
from rest_framework import serializers

from auth_app.models import User
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializes a single offer pricing tier."""

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


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serializes an offer detail as an id and API link."""

    url = serializers.HyperlinkedIdentityField(view_name='offer-detail')

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


class OfferUserSerializer(serializers.ModelSerializer):
    """Serializes the public identity of an offer creator."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferReadSerializer(serializers.ModelSerializer):
    """Provides the common read representation of an offer."""

    user = serializers.PrimaryKeyRelatedField(
        source='creator',
        read_only=True,
    )
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
        ]

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


class OfferListSerializer(OfferReadSerializer):
    """Adds creator details to the offer list representation."""

    user_details = OfferUserSerializer(source='creator', read_only=True)

    class Meta(OfferReadSerializer.Meta):
        fields = OfferReadSerializer.Meta.fields + ['user_details']


class OfferWriteSerializer(serializers.ModelSerializer):
    """Creates and updates offers together with their pricing tiers."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        detail_types = [item.get('offer_type') for item in value]
        if None in detail_types or len(detail_types) != len(set(detail_types)):
            raise serializers.ValidationError(
                'Each detail requires a unique offer_type.'
            )
        expected = {
            OfferDetail.BASIC,
            OfferDetail.STANDARD,
            OfferDetail.PREMIUM,
        }
        if self.instance is None and set(detail_types) != expected:
            raise serializers.ValidationError(
                'Basic, standard and premium details are required.'
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        self._create_details(offer, details_data)
        return offer

    def _create_details(self, offer, details_data):
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data is not None:
            self._update_details(instance, details_data)
        return instance

    def _update_details(self, instance, details_data):
        for detail_data in details_data:
            offer_type = detail_data.pop('offer_type')
            OfferDetail.objects.update_or_create(
                offer=instance,
                offer_type=offer_type,
                defaults=detail_data,
            )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['details'] = OfferDetailSerializer(
            instance.details.all(),
            many=True,
        ).data
        return data
