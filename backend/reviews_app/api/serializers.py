from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews_app.models import Review


User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.PrimaryKeyRelatedField(read_only=True)
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(type=User.BUSINESS)
    )
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
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
        if self.instance:
            self._reject_business_change(attrs)
            return attrs
        if self._review_exists(attrs['business_user']):
            raise serializers.ValidationError(
                {'detail': 'You have already reviewed this business user.'}
            )
        return attrs

    def _reject_business_change(self, attrs):
        if 'business_user' in attrs:
            raise serializers.ValidationError(
                {'business_user': 'This field cannot be changed.'}
            )

    def _review_exists(self, business_user):
        reviewer = self.context['request'].user
        return Review.objects.filter(
            reviewer=reviewer,
            business_user=business_user,
        ).exists()
