from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Auth Service API",
        default_version='v1',
        description="Authentication and Authorization Service",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def health_check(request):
    return JsonResponse({"status": "ok", "service": "auth-service"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('auth/', include('apps.authentication.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
