"""
Custom JWT authentication that validates tokens via the auth service
or directly using the shared JWT secret.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework.authentication import BaseAuthentication
import requests
from django.conf import settings


class GatewayJWTAuthentication(JWTAuthentication):
    """
    Validates JWT tokens using the shared secret.
    Also accepts X-User-Id / X-User-Role headers set by the gateway
    for internal service communication.
    """

    def authenticate(self, request):
        # Check for gateway-forwarded headers (internal communication)
        user_id = request.META.get('HTTP_X_USER_ID')
        user_role = request.META.get('HTTP_X_USER_ROLE')
        user_email = request.META.get('HTTP_X_USER_EMAIL')

        if user_id and user_role:
            # Create a lightweight user object from headers
            return (GatewayUser(user_id, user_role, user_email), None)

        # Fall back to standard JWT
        return super().authenticate(request)


class GatewayUser:
    """A lightweight user object populated from gateway headers."""

    def __init__(self, user_id, role, email=None):
        self.id = int(user_id) if user_id else None
        self.pk = self.id
        self.role_name = role
        self.email = email or ''
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return f"GatewayUser(id={self.id}, role={self.role_name})"
