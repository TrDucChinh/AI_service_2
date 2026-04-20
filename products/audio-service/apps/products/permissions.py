from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Admin users can do any request, others can only read.
    Uses X-User-Role header set by gateway.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        role = request.META.get('HTTP_X_USER_ROLE', '')
        return role in ('admin', 'staff')


class IsAdminUser(BasePermission):
    """Only admin users have access."""

    def has_permission(self, request, view):
        role = request.META.get('HTTP_X_USER_ROLE', '')
        return role == 'admin'


class IsStaffUser(BasePermission):
    """Admin and staff users have access."""

    def has_permission(self, request, view):
        role = request.META.get('HTTP_X_USER_ROLE', '')
        return role in ('admin', 'staff')
