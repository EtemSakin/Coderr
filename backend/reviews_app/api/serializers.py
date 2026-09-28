"""Serializers for review creation and updates."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    """Serialize reviews and validate review-specific rules."""

    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(type=User.BUSINESS)
    )
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        """Expose all review fields used by the API."""

        model = Review
        fields = [
            'id',
            'reviewer',
            'business_user',
            'rating',
            'description',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

    def validate(self, attrs):
        """Reject duplicate reviews during creation."""
        if self.instance:
            return attrs
        if self._review_exists(attrs['business_user']):
            raise serializers.ValidationError(
                {'detail': 'You have already reviewed this business user.'}
            )
        return attrs

    def _review_exists(self, business_user):
        """Return whether the current user already reviewed the business."""
        reviewer = self.context['request'].user
        return Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user,
        ).exists()


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Update only rating and description on an existing review."""

    class Meta:
        """Expose the two editable review fields."""

        model = Review
        fields = ['rating', 'description']

    def validate(self, attrs):
        """Reject fields that must remain immutable on a review."""
        unknown = set(self.initial_data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError(
                {field: 'This field is not editable.' for field in unknown}
            )
        return attrs

    def to_representation(self, instance):
        """Return the complete review after an update."""
        return ReviewSerializer(instance, context=self.context).data
