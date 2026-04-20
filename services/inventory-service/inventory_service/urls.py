from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path('inventory/', include('apps.inventory.urls')),
    path('health/', lambda r: JsonResponse({'status': 'ok'})),
]
