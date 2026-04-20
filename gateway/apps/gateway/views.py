import requests
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)

TIMEOUT = 30


def _proxy_request(request, target_url, path=''):
    url = f"{target_url.rstrip('/')}/{path.lstrip('/')}"
    if request.META.get('QUERY_STRING'):
        url += f"?{request.META['QUERY_STRING']}"

    headers = {}
    for key in ['HTTP_AUTHORIZATION', 'HTTP_X_USER_ID', 'HTTP_X_USER_EMAIL', 'HTTP_X_USER_ROLE', 'CONTENT_TYPE']:
        val = request.META.get(key)
        if val:
            header_name = key.replace('HTTP_', '').replace('_', '-').title()
            headers[header_name] = val

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.body if request.method in ('POST', 'PUT', 'PATCH') else None,
            timeout=TIMEOUT,
        )
        response = HttpResponse(
            content=resp.content,
            status=resp.status_code,
            content_type=resp.headers.get('Content-Type', 'application/json'),
        )
        return response
    except requests.exceptions.ConnectionError:
        return JsonResponse({'error': f'Service unavailable: {target_url}'}, status=503)
    except requests.exceptions.Timeout:
        return JsonResponse({'error': 'Service timeout'}, status=504)
    except Exception as exc:
        logger.exception(f'Proxy error for {url}: {exc}')
        return JsonResponse({'error': 'Internal gateway error'}, status=500)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({'status': 'ok', 'service': 'gateway'})


class AuthProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.AUTH_SERVICE_URL, f'auth/{path}')


class UserProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.USER_SERVICE_URL, f'users/{path}')


class CartProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.CART_SERVICE_URL, f'cart/{path}')


class OrderProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.ORDER_SERVICE_URL, f'orders/{path}')


class PaymentProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.PAYMENT_SERVICE_URL, f'payments/{path}')


class SearchProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.SEARCH_SERVICE_URL, f'search/{path}')


class ProductProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, service='', path='', **kwargs):
        service_url = settings.PRODUCT_SERVICE_URLS.get(service.lower())
        if not service_url:
            return JsonResponse({'error': f'Unknown product service: {service}'}, status=404)
        return _proxy_request(request, service_url, f'products/{path}')


class RecommendationProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.RECOMMENDATION_SERVICE_URL, f'recommendations/{path}')


class InventoryProxyView(APIView):
    permission_classes = [AllowAny]

    def dispatch(self, request, path='', **kwargs):
        return _proxy_request(request, settings.INVENTORY_SERVICE_URL, f'inventory/{path}')
