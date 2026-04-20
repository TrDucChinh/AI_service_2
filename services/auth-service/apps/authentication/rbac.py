"""
RBAC (Role-Based Access Control) utilities for the auth service.
"""
from rest_framework.permissions import BasePermission
from functools import wraps
from rest_framework.exceptions import PermissionDenied


def require_role(*roles):
    """
    Decorator factory to require specific roles.
    Usage:
        @require_role('admin', 'staff')
        def my_view(request, *args, **kwargs):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                raise PermissionDenied("Authentication required.")

            user_role = getattr(request.user, 'role_name', None)
            if user_role not in roles:
                raise PermissionDenied(
                    f"Access denied. Required roles: {roles}. Your role: {user_role}"
                )
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class IsAdminUser(BasePermission):
    message = "Admin role required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role_name', '') == 'admin'
        )


class IsStaffUser(BasePermission):
    message = "Staff or Admin role required."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role_name', '') in ('admin', 'staff')
        )


class IsCustomerUser(BasePermission):
    message = "Authentication required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


def get_jwt_payload_extra(user):
    """Return extra claims to add to JWT payload."""
    return {
        'role': user.role_name,
        'email': user.email,
        'username': user.username,
    }
