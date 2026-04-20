import time
import jwt
import logging
from django.conf import settings
from django.http import JsonResponse
from collections import defaultdict

logger = logging.getLogger(__name__)

# ── Route access policy ────────────────────────────────────────────────────────
# Routes the JWT must be present and valid for (any authenticated role)
AUTHENTICATED_PREFIXES = [
    '/api/users/',
    '/api/cart/',
    '/api/orders/',
    '/api/payments/',
]

# Routes only ADMIN or STAFF may write to
STAFF_WRITE_PREFIXES = [
    '/api/orders/',      # status updates, etc.
]

# Routes only ADMIN may write to (create/update/delete products, manage users)
ADMIN_WRITE_PREFIXES = [
    '/api/auth/users/',
    '/api/auth/roles/',
]

# Read-only (GET) access is public for these
PUBLIC_GET_PREFIXES = [
    '/api/products/',
    '/api/search/',
    '/api/recommendations/',
    '/api/inventory/',
]

# Completely public (any method, no token required)
PUBLIC_PATHS = [
    '/api/auth/register/',
    '/api/auth/login/',
    '/api/auth/refresh/',
    '/api/auth/verify/',
    '/health/',
    '/api/auth/register',
    '/api/auth/login',
    '/api/auth/refresh',
    '/api/auth/verify',
    '/health',
    '/api/ai/health/',
    '/api/ai/health',
]

# Paths where write ops (POST/PUT/PATCH/DELETE) require admin or staff
PRODUCT_WRITE_REQUIRES_STAFF = True

SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

# ── In-memory rate limit store ─────────────────────────────────────────────────
_rate_limit_store = defaultdict(list)


class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration_ms = (time.time() - start) * 1000
        logger.info(
            '[%s] %s %s → %d (%.1fms) user=%s role=%s',
            request.META.get('REMOTE_ADDR', '-'),
            request.method,
            request.path,
            response.status_code,
            duration_ms,
            request.META.get('HTTP_X_USER_ID', '-'),
            request.META.get('HTTP_X_USER_ROLE', '-'),
        )
        return response


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.window = getattr(settings, 'RATE_LIMIT_WINDOW', 60)

    def __call__(self, request):
        ip = self._get_ip(request)
        now = time.time()
        window_start = now - self.window
        _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if t > window_start]
        if len(_rate_limit_store[ip]) >= self.max_requests:
            return JsonResponse(
                {'error': 'Rate limit exceeded. Try again later.', 'retry_after': self.window},
                status=429,
            )
        _rate_limit_store[ip].append(now)
        return self.get_response(request)

    def _get_ip(self, request):
        forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        return forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR', '0.0.0.0')


class JWTValidationMiddleware:
    """
    Sprint 11: Full RBAC enforcement at the gateway level.

    Policy:
      - Public paths  → no token needed
      - GET on products/search → no token needed
      - /api/users, /api/cart, /api/orders, /api/payments → must be authenticated
      - Write ops on /api/products/* → staff or admin
      - Write ops on /api/auth/users, /api/auth/roles → admin only
      - Admin dashboard paths → admin only
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        method = request.method

        # 1. Always allow public paths
        if any(path == p or path.startswith(p.rstrip('/') + '/') for p in PUBLIC_PATHS):
            return self.get_response(request)

        # 2. Public GET on products and search
        if method in SAFE_METHODS and any(path.startswith(p) for p in PUBLIC_GET_PREFIXES):
            # Still parse token if present so downstream gets user context
            self._try_inject_user(request)
            return self.get_response(request)

        # 3. All other paths: require valid JWT
        auth_result = self._validate_jwt(request)
        if auth_result is not None:
            return auth_result  # 401 error response

        role = request.META.get('HTTP_X_USER_ROLE', 'customer')

        # 4. RBAC: product write ops require staff or admin
        if any(path.startswith(p) for p in ['/api/products/']):
            if method not in SAFE_METHODS and role not in ('admin', 'staff'):
                return JsonResponse(
                    {'error': 'Forbidden: staff or admin role required to modify products.'},
                    status=403,
                )

        # 5. RBAC: admin-only write paths
        if any(path.startswith(p) for p in ADMIN_WRITE_PREFIXES):
            if method not in SAFE_METHODS and role != 'admin':
                return JsonResponse(
                    {'error': 'Forbidden: admin role required.'},
                    status=403,
                )

        # 6. RBAC: authenticated paths are open to any valid user
        return self.get_response(request)

    def _validate_jwt(self, request):
        """Decode JWT, inject user headers. Returns error JsonResponse or None."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': 'Authentication required. Provide a Bearer token.'}, status=401)

        token = auth_header.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            request.META['HTTP_X_USER_ID'] = str(payload.get('user_id', ''))
            request.META['HTTP_X_USER_EMAIL'] = str(payload.get('email', ''))
            request.META['HTTP_X_USER_ROLE'] = str(payload.get('role', 'customer'))
            request.META['HTTP_X_USERNAME'] = str(payload.get('username', ''))
            return None
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token has expired. Please login again.'}, status=401)
        except jwt.InvalidTokenError as exc:
            return JsonResponse({'error': f'Invalid token: {exc}'}, status=401)

    def _try_inject_user(self, request):
        """Optionally inject user context from token if present (no error if missing)."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return
        token = auth_header.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            request.META['HTTP_X_USER_ID'] = str(payload.get('user_id', ''))
            request.META['HTTP_X_USER_EMAIL'] = str(payload.get('email', ''))
            request.META['HTTP_X_USER_ROLE'] = str(payload.get('role', 'customer'))
        except jwt.InvalidTokenError:
            pass
