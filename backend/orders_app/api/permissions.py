from rest_framework.permissions import BasePermission

from auth_app.models import User


class OrderPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method == 'POST':
            return user.is_authenticated and user.type == User.CUSTOMER
        if request.method == 'PATCH':
            return user.is_authenticated and user.type == User.BUSINESS
        if request.method == 'DELETE':
            return user.is_authenticated and user.is_staff
        return user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH':
            return obj.business_user_id == request.user.id
        if request.method == 'DELETE':
            return request.user.is_staff
        user_id = request.user.id
        return user_id in (obj.customer_user_id, obj.business_user_id)
