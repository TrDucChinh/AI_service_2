"""
Script to generate all remaining product service files.
Run this script once to create all the missing files for the 13 remaining product services.
"""
import os
import shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SERVICES = [
    # (name, port, db_name, description)
    ('tablet', 8012, 'product_tablet', 'Tablet Product Service'),
    ('audio', 8013, 'product_audio', 'Audio Product Service'),
    ('accessory', 8014, 'product_accessory', 'Accessory Product Service'),
    ('smartwatch', 8015, 'product_smartwatch', 'Smartwatch Product Service'),
    ('camera', 8016, 'product_camera', 'Camera Product Service'),
    ('monitor', 8017, 'product_monitor', 'Monitor Product Service'),
    ('keyboard', 8018, 'product_keyboard', 'Keyboard Product Service'),
    ('mouse', 8019, 'product_mouse', 'Mouse Product Service'),
    ('printer', 8020, 'product_printer', 'Printer Product Service'),
    ('networking', 8021, 'product_networking', 'Networking Product Service'),
    ('storage', 8022, 'product_storage', 'Storage Product Service'),
    ('component', 8023, 'product_component', 'Component Product Service'),
    ('gaminggear', 8024, 'product_gaminggear', 'Gaming Gear Product Service'),
]

# Template for settings.py
SETTINGS_TEMPLATE = '''import os
from decouple import config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_NAME = '{name}'
SERVICE_PORT = {port}
SECRET_KEY = config('DJANGO_SECRET_KEY', default='django-insecure-{name}-service-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'rest_framework', 'corsheaders', 'drf_yasg', 'django_filters', 'apps.products',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', 'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{module}.urls'
TEMPLATES = [{{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True,
    'OPTIONS': {{'context_processors': ['django.template.context_processors.debug',
    'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages']}}}}]

WSGI_APPLICATION = '{module}.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('POSTGRES_DB', default='{db}'),
        'USER': config('POSTGRES_USER', default='postgres'),
        'PASSWORD': config('POSTGRES_PASSWORD', default='postgres'),
        'HOST': config('POSTGRES_HOST', default='postgres'),
        'PORT': config('POSTGRES_PORT', default='5432'),
    }}
}}

REST_FRAMEWORK = {{
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend', 'rest_framework.filters.SearchFilter', 'rest_framework.filters.OrderingFilter'],
}}

CACHES = {{'default': {{'BACKEND': 'django_redis.cache.RedisCache', 'LOCATION': config('REDIS_URL', default='redis://redis:6379/0'), 'OPTIONS': {{'CLIENT_CLASS': 'django_redis.client.DefaultClient'}}, 'TIMEOUT': 300}}}}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
'''

URLS_TEMPLATE = '''from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(openapi.Info(title="{title}", default_version='v1', description="{desc}"), public=True, permission_classes=(permissions.AllowAny,))

def health_check(request):
    return JsonResponse({{"status": "ok", "service": "{name}-service"}})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('products/', include('apps.products.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
'''

WSGI_TEMPLATE = '''import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{module}.settings')
application = get_wsgi_application()
'''

MANAGE_TEMPLATE = '''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{module}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''

SEED_TEMPLATE = '''"""Seed command for {name} products."""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {{'name': 'Brand A', 'logo': 'https://placehold.co/200x100?text=BrandA', 'website': 'https://brandA.com'}},
    {{'name': 'Brand B', 'logo': 'https://placehold.co/200x100?text=BrandB', 'website': 'https://brandB.com'}},
    {{'name': 'Brand C', 'logo': 'https://placehold.co/200x100?text=BrandC', 'website': 'https://brandC.com'}},
    {{'name': 'Brand D', 'logo': 'https://placehold.co/200x100?text=BrandD', 'website': 'https://brandD.com'}},
    {{'name': 'Brand E', 'logo': 'https://placehold.co/200x100?text=BrandE', 'website': 'https://brandE.com'}},
]

CATEGORIES = [
    {{'name': '{name_title} Category A', 'description': 'Category A for {name} products'}},
    {{'name': '{name_title} Category B', 'description': 'Category B for {name} products'}},
    {{'name': '{name_title} Category C', 'description': 'Category C for {name} products'}},
]


class Command(BaseCommand):
    help = 'Seed the database with sample {name} products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding {name} products...')
        brand_objs = {{}}
        for b in BRANDS:
            brand, _ = Brand.objects.get_or_create(name=b['name'], defaults={{'logo': b['logo'], 'website': b['website']}})
            brand_objs[b['name']] = brand

        cat_objs = {{}}
        for c in CATEGORIES:
            slug = slugify(c['name'])
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={{'name': c['name'], 'description': c['description']}})
            cat_objs[c['name']] = cat

        created_count = 0
        for i in range(50):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(29.99, 999.99), 2)
            sale = round(price * 0.85, 2) if random.random() > 0.5 else None
            sku = f'{name_upper}-PROD-{{i+1:04d}}'

            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={{
                    'name': f'{{brand.name}} {name_title} Model {{i+1}}',
                    'brand': brand,
                    'category': cat,
                    'description': f'High-quality {name} product from {{brand.name}}',
                    'price': Decimal(str(price)),
                    'sale_price': Decimal(str(sale)) if sale else None,
                    'stock': random.randint(0, 100),
                    'is_active': True,
                    'specifications': {{'model': f'Model-{{i+1}}', 'warranty': '1 year'}},
                }}
            )
            if created:
                created_count += 1
                ProductImage.objects.create(
                    product=product,
                    image=f'https://placehold.co/800x600?text={{brand.name}}+{name_title}+{{i+1}}',
                    is_primary=True,
                    alt_text=f'{{product.name}} - Main Image'
                )
                Inventory.objects.get_or_create(product=product, defaults={{'quantity': product.stock, 'reserved_qty': 0, 'low_stock_threshold': 5}})
                Rating.objects.get_or_create(product=product, defaults={{'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 150)}})

        self.stdout.write(self.style.SUCCESS(f'Seeded {{created_count}} new {name} products. Total: {{Product.objects.count()}}'))
'''

# Files to copy from mobile-service (they're all identical)
COPY_FILES = [
    'apps/products/models.py',
    'apps/products/serializers.py',
    'apps/products/views.py',
    'apps/products/urls.py',
    'apps/products/filters.py',
    'apps/products/permissions.py',
    'apps/products/admin.py',
    'apps/products/apps.py',
]

mobile_src = os.path.join(BASE, 'products', 'mobile-service')


def create_service(name, port, db, desc):
    module = f'{name}_service'
    svc_dir = os.path.join(BASE, 'products', f'{name}-service')

    # Create directories
    dirs = [
        svc_dir,
        os.path.join(svc_dir, module),
        os.path.join(svc_dir, 'apps'),
        os.path.join(svc_dir, 'apps', 'products'),
        os.path.join(svc_dir, 'apps', 'products', 'management'),
        os.path.join(svc_dir, 'apps', 'products', 'management', 'commands'),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

    # Write manage.py
    if not os.path.exists(os.path.join(svc_dir, 'manage.py')):
        with open(os.path.join(svc_dir, 'manage.py'), 'w') as f:
            f.write(MANAGE_TEMPLATE.format(module=module))

    # Write module __init__.py
    with open(os.path.join(svc_dir, module, '__init__.py'), 'w') as f:
        f.write('')

    # Write settings.py
    with open(os.path.join(svc_dir, module, 'settings.py'), 'w') as f:
        f.write(SETTINGS_TEMPLATE.format(name=name, port=port, module=module, db=db))

    # Write urls.py
    title = f'{name.title()} Service API'
    with open(os.path.join(svc_dir, module, 'urls.py'), 'w') as f:
        f.write(URLS_TEMPLATE.format(name=name, title=title, desc=desc, module=module))

    # Write wsgi.py
    with open(os.path.join(svc_dir, module, 'wsgi.py'), 'w') as f:
        f.write(WSGI_TEMPLATE.format(module=module))

    # Write apps __init__.py
    with open(os.path.join(svc_dir, 'apps', '__init__.py'), 'w') as f:
        f.write('')

    # Copy product app files from mobile-service
    for rel_path in COPY_FILES:
        src = os.path.join(mobile_src, rel_path.replace('/', os.sep))
        dst = os.path.join(svc_dir, rel_path.replace('/', os.sep))
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # Write products __init__.py
    with open(os.path.join(svc_dir, 'apps', 'products', '__init__.py'), 'w') as f:
        f.write('')

    # Write management __init__.py files
    with open(os.path.join(svc_dir, 'apps', 'products', 'management', '__init__.py'), 'w') as f:
        f.write('')
    with open(os.path.join(svc_dir, 'apps', 'products', 'management', 'commands', '__init__.py'), 'w') as f:
        f.write('')

    # Write seed command
    name_upper = name.upper()
    name_title = name.title()
    with open(os.path.join(svc_dir, 'apps', 'products', 'management', 'commands', 'seed_products.py'), 'w') as f:
        f.write(SEED_TEMPLATE.format(
            name=name, name_title=name_title, name_upper=name_upper
        ))

    print(f'  Created {name}-service')


if __name__ == '__main__':
    print('Generating product services...')
    for name, port, db, desc in SERVICES:
        create_service(name, port, db, desc)
    print('Done!')
