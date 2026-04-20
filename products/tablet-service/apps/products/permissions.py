from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        role = request.META.get('HTTP_X_USER_ROLE', '')
        return role in ('admin', 'staff')


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.META.get('HTTP_X_USER_ROLE', '') == 'admin'


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.META.get('HTTP_X_USER_ROLE', '') in ('admin', 'staff')
