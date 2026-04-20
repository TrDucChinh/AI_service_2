import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-recommendation-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.recommendations',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'recommendation_service.urls'
WSGI_APPLICATION = 'recommendation_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'recommendations.sqlite3'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://redis:6379/3'),
        'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
        'TIMEOUT': 300,
    }
}

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

CORS_ALLOW_ALL_ORIGINS = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
