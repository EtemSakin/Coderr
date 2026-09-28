"""Permissions for offer creation and ownership."""

from rest_framework.permissions import BasePermission, SAFE_METHODS

from auth_app.models import User


class IsBusinessOrReadOnly(BasePermission):
    """Allow writes only for authenticated business users."""

    def has_permission(self, request, view):
        """Allow safe methods and restrict writes to business users."""
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.type == User.BUSINESS
        )


class IsOfferOwnerOrReadOnly(BasePermission):
    """Allow offer changes only for the offer owner."""

    def has_object_permission(self, request, view, obj):
        """Allow reads and restrict object writes to the creator."""
        if request.method in SAFE_METHODS:
            return True
        return obj.creator_id == request.user.id
