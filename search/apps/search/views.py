import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

logger = logging.getLogger(__name__)
TIMEOUT = 5


def _search_service(service_name, service_url, query, min_price=None, max_price=None):
    try:
        params = {'search': query, 'page': 1, 'page_size': 20}
        if min_price:
            params['min_price'] = min_price
        if max_price:
            params['max_price'] = max_price
        resp = requests.get(f"{service_url.rstrip('/')}/products/", params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            data = resp.json()
            results = data.get('results', data) if isinstance(data, dict) else data
            if not isinstance(results, list):
                results = []
            return service_name, [
                {
                    'service': service_name,
                    'id': p.get('id'),
                    'name': p.get('name', ''),
                    'price': p.get('current_price') or p.get('price', 0),
                    'sale_price': p.get('sale_price'),
                    'brand': p.get('brand_name', ''),
                    'category': p.get('category_name', ''),
                    'image': p.get('primary_image', ''),
                    'rating': p.get('rating', {}).get('average_rating') if isinstance(p.get('rating'), dict) else None,
                    'stock': p.get('stock', 0),
                    'sku': p.get('sku', ''),
                }
                for p in results
                if query.lower() in p.get('name', '').lower() or query.lower() in p.get('description', '').lower()
            ]
    except Exception as exc:
        logger.warning(f'Search failed for {service_name}: {exc}')
    return service_name, []


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return JsonResponse({'status': 'ok', 'service': 'search'})


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({'error': 'Query parameter "q" is required.'}, status=400)

        service_filter = request.GET.get('service')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))

        services = settings.PRODUCT_SERVICES
        if service_filter and service_filter in services:
            services = {service_filter: services[service_filter]}

        all_results = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = {
                executor.submit(_search_service, name, url, query, min_price, max_price): name
                for name, url in services.items()
            }
            for future in as_completed(futures):
                _, results = future.result()
                all_results.extend(results)

        # Sort by rating desc, then name
        all_results.sort(key=lambda x: (-(float(x['rating']) if x['rating'] else 0), x['name']))

        total = len(all_results)
        start = (page - 1) * limit
        paginated = all_results[start:start + limit]

        return JsonResponse({
            'query': query,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit,
            'results': paginated,
        })
