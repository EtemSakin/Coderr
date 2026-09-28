"""Permissions for profile access."""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow profile changes only for the owning user."""

    def has_permission(self, request, view):
        """Allow reads and restrict writes to the profile owner."""
        if request.method in SAFE_METHODS:
            return True
        return request.user.id == view.kwargs.get('user_id')
