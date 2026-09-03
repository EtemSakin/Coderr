from rest_framework.permissions import BasePermission, SAFE_METHODS

from auth_app.models import User


class IsBusinessOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.type == User.BUSINESS
        )


class IsOfferOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.creator_id == request.user.id
