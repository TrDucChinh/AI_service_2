from django.urls import path, include

urlpatterns = [
    path('notifications/', include('apps.notifications.urls')),
    path('health/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
]
