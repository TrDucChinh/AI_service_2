from django.urls import path, include
from django.http import JsonResponse

urlpatterns = [
    path('recommendations/', include('apps.recommendations.urls')),
    path('health/', lambda r: JsonResponse({'status': 'ok'})),
]
