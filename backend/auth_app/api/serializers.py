"""Serializers for authentication and marketplace profiles."""

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from auth_app.models import Profile


User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate and create new marketplace users."""

    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        """Define fields accepted during registration."""

        model = User
        fields = [
            'username',
            'email',
            'password',
            'repeated_password',
            'type',
        ]

    def validate_email(self, value):
        """Reject email addresses that are already registered."""
        queryset = User.objects.filter(email__iexact=value)
        if queryset.exists():
            raise serializers.ValidationError(
                'This email address is already in use.'
            )
        return value

    def validate(self, attrs):
        """Ensure both supplied passwords match."""
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        return attrs

    def create(self, validated_data):
        """Create the user together with an empty profile."""
        validated_data.pop('repeated_password')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Validate username and password credentials."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the supplied credentials."""
        user = authenticate(
            username=attrs['username'],
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError(
                {'detail': 'Invalid credentials.'}
            )
        attrs['user'] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize profile data together with selected user fields."""

    user = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', required=False, allow_blank=True
    )
    last_name = serializers.CharField(
        source='user.last_name', required=False, allow_blank=True
    )
    email = serializers.EmailField(source='user.email', required=False)
    type = serializers.CharField(source='user.type', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        """Define the flattened profile representation."""

        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'email',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'created_at',
        ]

    def validate_email(self, value):
        """Reject an email address used by another account."""
        queryset = User.objects.filter(email__iexact=value)
        if self.instance is not None:
            queryset = queryset.exclude(pk=self.instance.user_id)
        if queryset.exists():
            raise serializers.ValidationError(
                'This email address is already in use.'
            )
        return value

    def update(self, instance, validated_data):
        """Update user fields and profile fields in one request."""
        user_data = validated_data.pop('user', {})
        if user_data:
            for field, value in user_data.items():
                setattr(instance.user, field, value)
            instance.user.save(update_fields=user_data.keys())
        return super().update(instance, validated_data)


class BusinessProfileSerializer(ProfileSerializer):
    """Serialize the public business profile list representation."""

    class Meta(ProfileSerializer.Meta):
        """Expose fields required by business profile listings."""

        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
        ]


class CustomerProfileSerializer(ProfileSerializer):
    """Serialize the compact customer profile list representation."""

    class Meta(ProfileSerializer.Meta):
        """Expose fields required by customer profile listings."""

        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'type',
        ]
