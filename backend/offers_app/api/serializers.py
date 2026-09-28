"""Serializers for offers and their pricing tiers."""

from django.db import transaction
from django.db.models import Min
from rest_framework import serializers

from auth_app.models import User
from offers_app.models import Offer, OfferDetail


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serialize a single offer pricing tier."""

    class Meta:
        """Expose all fields belonging to one pricing tier."""

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
        """Require offer features to be represented as a list."""
        if not isinstance(value, list):
            raise serializers.ValidationError('Features must be a list.')
        return value


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """Serialize an offer detail as an id and API link."""

    url = serializers.HyperlinkedIdentityField(view_name='offer-detail')

    class Meta:
        """Expose the detail id and generated hyperlink."""

        model = OfferDetail
        fields = ['id', 'url']


class OfferUserSerializer(serializers.ModelSerializer):
    """Serialize the public identity of an offer creator."""

    class Meta:
        """Expose the creator fields required by offer lists."""

        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferReadSerializer(serializers.ModelSerializer):
    """Provide the common read representation of an offer."""

    user = serializers.PrimaryKeyRelatedField(
        source='creator',
        read_only=True,
    )
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        """Expose offer data and calculated summary values."""

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
        """Return the cheapest pricing tier."""
        value = getattr(obj, 'min_price', None)
        if value is not None:
            return value
        return obj.details.aggregate(value=Min('price'))['value']

    def get_min_delivery_time(self, obj):
        """Return the shortest delivery time among pricing tiers."""
        value = getattr(obj, 'min_delivery_time', None)
        if value is not None:
            return value
        field = 'delivery_time_in_days'
        return obj.details.aggregate(value=Min(field))['value']


class OfferListSerializer(OfferReadSerializer):
    """Add creator details to the offer list representation."""

    user_details = OfferUserSerializer(source='creator', read_only=True)

    class Meta(OfferReadSerializer.Meta):
        """Extend the read representation with creator details."""

        fields = OfferReadSerializer.Meta.fields + ['user_details']


class OfferWriteSerializer(serializers.ModelSerializer):
    """Create and update offers together with their pricing tiers."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        """Expose fields accepted when writing offers."""

        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details']
        read_only_fields = ['id']

    def validate_details(self, value):
        """Validate tier uniqueness and required tiers on creation."""
        detail_types = [item.get('offer_type') for item in value]
        self._validate_unique_types(detail_types)
        self._validate_create_types(detail_types)
        return value

    def _validate_unique_types(self, detail_types):
        """Reject missing or duplicate offer types."""
        unique_types = len(detail_types) == len(set(detail_types))
        if None in detail_types or not unique_types:
            raise serializers.ValidationError(
                'Each detail requires a unique offer_type.'
            )

    def _validate_create_types(self, detail_types):
        """Require all three offer types when creating an offer."""
        expected = {
            OfferDetail.BASIC,
            OfferDetail.STANDARD,
            OfferDetail.PREMIUM,
        }
        if self.instance is None and set(detail_types) != expected:
            raise serializers.ValidationError(
                'Basic, standard and premium details are required.'
            )

    @transaction.atomic
    def create(self, validated_data):
        """Create an offer and its nested pricing tiers atomically."""
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(**validated_data)
        self._create_details(offer, details_data)
        return offer

    def _create_details(self, offer, details_data):
        """Create each pricing tier belonging to an offer."""
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update offer fields and any submitted pricing tiers."""
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data is not None:
            self._update_details(instance, details_data)
        return instance

    def _update_details(self, instance, details_data):
        """Update pricing tiers by their stable offer type."""
        for detail_data in details_data:
            offer_type = detail_data.pop('offer_type')
            OfferDetail.objects.update_or_create(
                offer=instance,
                offer_type=offer_type,
                defaults=detail_data,
            )

    def to_representation(self, instance):
        """Return all pricing tiers after create or update."""
        data = super().to_representation(instance)
        data['details'] = OfferDetailSerializer(
            instance.details.all(),
            many=True,
        ).data
        return data
