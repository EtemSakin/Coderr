from rest_framework.permissions import BasePermission, SAFE_METHODS

from auth_app.models import User


class ReviewPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.method == 'POST':
            return request.user.type == User.CUSTOMER
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer_id == request.user.id
