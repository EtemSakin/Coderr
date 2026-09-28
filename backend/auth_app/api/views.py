from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from auth_app.api.permissions import IsProfileOwnerOrReadOnly
from auth_app.api.serializers import (
    BusinessProfileSerializer,
    CustomerProfileSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)
from auth_app.models import Profile, User


def auth_response_data(user, token):
    return {
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
    }


class RegistrationView(generics.GenericAPIView):
    """Registers a user and returns an authentication token."""

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            auth_response_data(user, token),
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """Authenticates a user and returns an authentication token."""

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response(auth_response_data(user, token))


class ProfileView(generics.GenericAPIView):
    """Reads profiles and updates the authenticated user's profile."""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrReadOnly]

    def get_profile(self, user_id):
        queryset = Profile.objects.select_related('user')
        return get_object_or_404(queryset, user_id=user_id)

    def get(self, request, user_id):
        profile = self.get_profile(user_id)
        return Response(self.get_serializer(profile).data)

    def patch(self, request, user_id):
        profile = self.get_profile(user_id)
        serializer = self.get_serializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BusinessProfileListView(generics.ListAPIView):
    """Lists profiles belonging to business users."""

    serializer_class = BusinessProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.select_related('user').filter(
        user__type=User.BUSINESS
    )


class CustomerProfileListView(generics.ListAPIView):
    """Lists profiles belonging to customer users."""

    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.select_related('user').filter(
        user__type=User.CUSTOMER
    )
