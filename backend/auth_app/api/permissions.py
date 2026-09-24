from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allows profile changes only for the owning user."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.id == view.kwargs.get('user_id')
