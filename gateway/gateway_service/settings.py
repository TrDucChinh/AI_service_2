import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-gateway-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'apps.gateway',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.gateway.middleware.LoggingMiddleware',
    'apps.gateway.middleware.RateLimitMiddleware',
    'apps.gateway.middleware.JWTValidationMiddleware',
]

ROOT_URLCONF = 'gateway_service.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'gateway_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'gateway.sqlite3'),
    }
}

# Service URLs
AUTH_SERVICE_URL = config('AUTH_SERVICE_URL', default='http://auth-service:8001')
USER_SERVICE_URL = config('USER_SERVICE_URL', default='http://user-service:8002')
CART_SERVICE_URL = config('CART_SERVICE_URL', default='http://cart-service:8003')
ORDER_SERVICE_URL = config('ORDER_SERVICE_URL', default='http://order-service:8004')
PAYMENT_SERVICE_URL = config('PAYMENT_SERVICE_URL', default='http://payment-service:8005')
SEARCH_SERVICE_URL = config('SEARCH_SERVICE_URL', default='http://search-service:8025')
NOTIFICATION_SERVICE_URL = config('NOTIFICATION_SERVICE_URL', default='http://notification-service:8026')
RECOMMENDATION_SERVICE_URL = config('RECOMMENDATION_SERVICE_URL', default='http://recommendation-service:8027')
INVENTORY_SERVICE_URL = config('INVENTORY_SERVICE_URL', default='http://inventory-service:8028')

PRODUCT_SERVICE_URLS = {
    'laptop': config('LAPTOP_SERVICE_URL', default='http://laptop-service:8010'),
    'mobile': config('MOBILE_SERVICE_URL', default='http://mobile-service:8011'),
    'tablet': config('TABLET_SERVICE_URL', default='http://tablet-service:8012'),
    'audio': config('AUDIO_SERVICE_URL', default='http://audio-service:8013'),
    'accessory': config('ACCESSORY_SERVICE_URL', default='http://accessory-service:8014'),
    'smartwatch': config('SMARTWATCH_SERVICE_URL', default='http://smartwatch-service:8015'),
    'camera': config('CAMERA_SERVICE_URL', default='http://camera-service:8016'),
    'monitor': config('MONITOR_SERVICE_URL', default='http://monitor-service:8017'),
    'keyboard': config('KEYBOARD_SERVICE_URL', default='http://keyboard-service:8018'),
    'mouse': config('MOUSE_SERVICE_URL', default='http://mouse-service:8019'),
    'printer': config('PRINTER_SERVICE_URL', default='http://printer-service:8020'),
    'networking': config('NETWORKING_SERVICE_URL', default='http://networking-service:8021'),
    'storage': config('STORAGE_SERVICE_URL', default='http://storage-service:8022'),
    'component': config('COMPONENT_SERVICE_URL', default='http://component-service:8023'),
    'gaminggear': config('GAMINGGEAR_SERVICE_URL', default='http://gaminggear-service:8024'),
}

JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='your-super-secret-jwt-key-change-in-production')
JWT_ALGORITHM = config('JWT_ALGORITHM', default='HS256')

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']

RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
