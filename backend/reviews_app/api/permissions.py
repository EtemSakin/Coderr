"""Permissions for review creation and ownership."""

from rest_framework.permissions import BasePermission, SAFE_METHODS

from auth_app.models import User


class ReviewPermission(BasePermission):
    """Enforce review creation and ownership permissions."""

    def has_permission(self, request, view):
        """Allow reads and restrict creation to customer accounts."""
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            return request.user.type == User.CUSTOMER
        return True

    def has_object_permission(self, request, view, obj):
        """Allow reads and restrict writes to the review author."""
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer_id == request.user.id
