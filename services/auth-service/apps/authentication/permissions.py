from rest_framework.permissions import BasePermission
from functools import wraps
from rest_framework.exceptions import PermissionDenied


class IsAdminUser(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role_name == 'admin'
        )


class IsStaffUser(BasePermission):
    """Allow access to admin or staff users."""

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role_name in ('admin', 'staff')
        )


class IsCustomerUser(BasePermission):
    """Allow access to any authenticated user."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


def require_role(*roles):
    """Decorator factory to require specific roles on view functions."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                raise PermissionDenied("Authentication required.")
            if request.user.role_name not in roles:
                raise PermissionDenied(f"Role '{request.user.role_name}' not allowed. Required: {roles}")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
