import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def _fetch_service_inventory(service_name, service_url):
    try:
        resp = requests.get(
            f'{service_url}/products/',
            params={'page_size': 200, 'show_inactive': True},
            timeout=5,
        )
        if resp.status_code == 200:
            products = resp.json().get('results', [])
            return service_name, products
    except Exception as exc:
        logger.warning('Failed to fetch inventory from %s: %s', service_name, exc)
    return service_name, []


class InventoryAggregateView(APIView):
    """GET /inventory/ — aggregate inventory summary across all product services."""
    permission_classes = []

    def get(self, request):
        cache_key = 'inventory:aggregate'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        service_urls = settings.PRODUCT_SERVICE_URLS
        threshold = getattr(settings, 'LOW_STOCK_THRESHOLD', 10)
        aggregate = {}

        with ThreadPoolExecutor(max_workers=15) as pool:
            futures = {
                pool.submit(_fetch_service_inventory, name, url): name
                for name, url in service_urls.items()
            }
            for future in as_completed(futures):
                service_name, products = future.result()
                total = len(products)
                out_of_stock = sum(1 for p in products if p.get('stock', 0) == 0)
                low_stock = sum(1 for p in products if 0 < p.get('stock', 0) <= threshold)
                total_units = sum(p.get('stock', 0) for p in products)
                aggregate[service_name] = {
                    'total_products': total,
                    'out_of_stock': out_of_stock,
                    'low_stock': low_stock,
                    'in_stock': total - out_of_stock - low_stock,
                    'total_units': total_units,
                }

        result = {
            'services': aggregate,
            'summary': {
                'total_products': sum(v['total_products'] for v in aggregate.values()),
                'total_out_of_stock': sum(v['out_of_stock'] for v in aggregate.values()),
                'total_low_stock': sum(v['low_stock'] for v in aggregate.values()),
                'total_units': sum(v['total_units'] for v in aggregate.values()),
            },
        }
        cache.set(cache_key, result, 60)
        return Response(result)


class LowStockView(APIView):
    """GET /inventory/low-stock/?threshold=<n> — list all low-stock products."""
    permission_classes = []

    def get(self, request):
        threshold = int(request.query_params.get('threshold', getattr(settings, 'LOW_STOCK_THRESHOLD', 10)))
        service_filter = request.query_params.get('service')

        cache_key = f'inventory:low_stock:{threshold}:{service_filter or "all"}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        service_urls = settings.PRODUCT_SERVICE_URLS
        if service_filter and service_filter in service_urls:
            service_urls = {service_filter: service_urls[service_filter]}

        low_stock_items = []

        with ThreadPoolExecutor(max_workers=15) as pool:
            futures = {
                pool.submit(_fetch_service_inventory, name, url): name
                for name, url in service_urls.items()
            }
            for future in as_completed(futures):
                service_name, products = future.result()
                for p in products:
                    stock = p.get('stock', 0)
                    if 0 <= stock <= threshold:
                        low_stock_items.append({
                            'service': service_name,
                            'id': p.get('id'),
                            'name': p.get('name'),
                            'sku': p.get('sku'),
                            'stock': stock,
                            'price': p.get('current_price') or p.get('price'),
                        })

        low_stock_items.sort(key=lambda x: x['stock'])
        result = {'results': low_stock_items, 'count': len(low_stock_items), 'threshold': threshold}
        cache.set(cache_key, result, 60)
        return Response(result)
