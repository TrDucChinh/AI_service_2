import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response

logger = logging.getLogger(__name__)

CACHE_TTL = 300  # 5 minutes


class RecommendationsView(APIView):
    """
    GET /recommendations/?product_id=<id>&service=<service>&limit=<n>
    Returns products from the same category/brand as the given product.
    """
    permission_classes = []

    def get(self, request):
        product_id = request.query_params.get('product_id')
        service = request.query_params.get('service', 'laptop')
        limit = int(request.query_params.get('limit', 6))

        if not product_id:
            return Response({'error': 'product_id is required'}, status=400)

        cache_key = f'reco:{service}:{product_id}:{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        service_url = settings.PRODUCT_SERVICE_URLS.get(service)
        if not service_url:
            return Response({'error': f'Unknown service: {service}'}, status=400)

        try:
            detail_resp = requests.get(f'{service_url}/products/{product_id}/', timeout=5)
            if detail_resp.status_code != 200:
                return Response({'results': [], 'count': 0})

            product = detail_resp.json()
            brand = product.get('brand', '')
            category = product.get('category', '')

            params = {'page_size': limit + 1}
            if brand:
                params['brand'] = brand
            elif category:
                params['category'] = category

            list_resp = requests.get(f'{service_url}/products/', params=params, timeout=5)
            candidates = list_resp.json().get('results', []) if list_resp.status_code == 200 else []
            recommendations = [p for p in candidates if str(p.get('id')) != str(product_id)][:limit]

            result = {'results': recommendations, 'count': len(recommendations), 'source_service': service}
            cache.set(cache_key, result, CACHE_TTL)
            return Response(result)
        except Exception as exc:
            logger.error('Recommendation fetch failed: %s', exc)
            return Response({'results': [], 'count': 0})


class CrossServiceRecommendationsView(APIView):
    """
    GET /recommendations/cross/?category=<cat>&limit=<n>
    Fetches top-rated products matching a category from all services.
    """
    permission_classes = []

    def get(self, request):
        category = request.query_params.get('category', '')
        limit = int(request.query_params.get('limit', 4))

        cache_key = f'reco:cross:{category}:{limit}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        all_products = []
        service_urls = settings.PRODUCT_SERVICE_URLS

        def fetch(svc_name, url):
            try:
                params = {'page_size': limit}
                if category:
                    params['category'] = category
                r = requests.get(f'{url}/products/', params=params, timeout=4)
                if r.status_code == 200:
                    return r.json().get('results', [])
            except Exception:
                pass
            return []

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(fetch, name, url): name for name, url in service_urls.items()}
            for future in as_completed(futures):
                all_products.extend(future.result())

        all_products.sort(key=lambda p: float(p.get('rating', 0) or 0), reverse=True)
        top = all_products[:limit]
        result = {'results': top, 'count': len(top)}
        cache.set(cache_key, result, CACHE_TTL)
        return Response(result)
