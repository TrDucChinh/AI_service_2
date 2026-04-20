#!/usr/bin/env python3
"""
Run this script to generate all remaining product service files.
Usage: python infra/setup_product_services.py
"""
import os
import shutil
import sys

# Script runs from the project root
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOBILE_SRC = os.path.join(BASE, 'products', 'mobile-service')

SERVICES = [
    ('tablet', 8012, 'product_tablet'),
    ('audio', 8013, 'product_audio'),
    ('accessory', 8014, 'product_accessory'),
    ('smartwatch', 8015, 'product_smartwatch'),
    ('camera', 8016, 'product_camera'),
    ('monitor', 8017, 'product_monitor'),
    ('keyboard', 8018, 'product_keyboard'),
    ('mouse', 8019, 'product_mouse'),
    ('printer', 8020, 'product_printer'),
    ('networking', 8021, 'product_networking'),
    ('storage', 8022, 'product_storage'),
    ('component', 8023, 'product_component'),
    ('gaminggear', 8024, 'product_gaminggear'),
]

FILES_TO_COPY = [
    ('apps/products/models.py', 'apps/products/models.py'),
    ('apps/products/serializers.py', 'apps/products/serializers.py'),
    ('apps/products/views.py', 'apps/products/views.py'),
    ('apps/products/urls.py', 'apps/products/urls.py'),
    ('apps/products/filters.py', 'apps/products/filters.py'),
    ('apps/products/permissions.py', 'apps/products/permissions.py'),
    ('apps/products/admin.py', 'apps/products/admin.py'),
    ('apps/products/apps.py', 'apps/products/apps.py'),
]


def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


def create_service(name, port, db):
    module = f'{name}_service'
    svc_dir = os.path.join(BASE, 'products', f'{name}-service')
    print(f'  Creating {name}-service...')

    # Create directories
    for d in [
        svc_dir, os.path.join(svc_dir, module), os.path.join(svc_dir, 'apps'),
        os.path.join(svc_dir, 'apps', 'products'),
        os.path.join(svc_dir, 'apps', 'products', 'management'),
        os.path.join(svc_dir, 'apps', 'products', 'management', 'commands'),
    ]:
        os.makedirs(d, exist_ok=True)

    # manage.py
    manage_path = os.path.join(svc_dir, 'manage.py')
    if not os.path.exists(manage_path):
        write_file(manage_path, f'''#!/usr/bin/env python
import os, sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{module}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
''')

    # requirements.txt
    req_path = os.path.join(svc_dir, 'requirements.txt')
    if not os.path.exists(req_path):
        write_file(req_path, '''Django==4.2.9
djangorestframework==3.14.0
psycopg2-binary==2.9.9
django-cors-headers==4.3.1
python-decouple==3.8
Pillow==10.2.0
drf-yasg==1.21.7
django-filter==23.5
django-redis==5.4.0
redis==5.0.1
''')

    # Dockerfile
    dockerfile_path = os.path.join(svc_dir, 'Dockerfile')
    if not os.path.exists(dockerfile_path):
        write_file(dockerfile_path, f'''FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE {port}
CMD ["python", "manage.py", "runserver", "0.0.0.0:{port}"]
''')

    # module files
    write_file(os.path.join(svc_dir, module, '__init__.py'), '')

    write_file(os.path.join(svc_dir, module, 'settings.py'), f'''import os
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
''')

    write_file(os.path.join(svc_dir, module, 'urls.py'), f'''from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({{"status": "ok", "service": "{name}-service"}})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check),
    path('products/', include('apps.products.urls')),
]
''')

    write_file(os.path.join(svc_dir, module, 'wsgi.py'), f'''import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{module}.settings')
application = get_wsgi_application()
''')

    # apps __init__
    write_file(os.path.join(svc_dir, 'apps', '__init__.py'), '')
    write_file(os.path.join(svc_dir, 'apps', 'products', '__init__.py'), '')

    # Copy product app files from mobile-service
    for src_rel, dst_rel in FILES_TO_COPY:
        src = os.path.join(MOBILE_SRC, src_rel.replace('/', os.sep))
        dst = os.path.join(svc_dir, dst_rel.replace('/', os.sep))
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            print(f'    WARNING: Source not found: {src}')

    # management init files
    write_file(os.path.join(svc_dir, 'apps', 'products', 'management', '__init__.py'), '')
    write_file(os.path.join(svc_dir, 'apps', 'products', 'management', 'commands', '__init__.py'), '')

    # seed command
    name_title = name.title()
    name_upper = name.upper()
    write_file(os.path.join(svc_dir, 'apps', 'products', 'management', 'commands', 'seed_products.py'), f'''"""Seed command for {name} products."""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {{'name': '{name_title} Brand A', 'logo': 'https://placehold.co/200x100?text=BrandA', 'website': 'https://example.com/a'}},
    {{'name': '{name_title} Brand B', 'logo': 'https://placehold.co/200x100?text=BrandB', 'website': 'https://example.com/b'}},
    {{'name': '{name_title} Brand C', 'logo': 'https://placehold.co/200x100?text=BrandC', 'website': 'https://example.com/c'}},
    {{'name': '{name_title} Brand D', 'logo': 'https://placehold.co/200x100?text=BrandD', 'website': 'https://example.com/d'}},
]

CATEGORIES = [
    {{'name': 'Premium {name_title}', 'description': 'Premium {name} products', 'slug': 'premium-{name}'}},
    {{'name': 'Standard {name_title}', 'description': 'Standard {name} products', 'slug': 'standard-{name}'}},
    {{'name': 'Budget {name_title}', 'description': 'Budget {name} products', 'slug': 'budget-{name}'}},
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
            cat, _ = Category.objects.get_or_create(
                slug=c['slug'],
                defaults={{'name': c['name'], 'description': c['description']}}
            )
            cat_objs[c['name']] = cat

        created_count = 0
        for i in range(50):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(19.99, 1499.99), 2)
            sale = round(price * 0.85, 2) if random.random() > 0.5 else None
            sku = f'{name_upper}-{{i+1:04d}}'

            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={{
                    'name': f'{{brand.name}} {name_title} {{i+1}}',
                    'brand': brand,
                    'category': cat,
                    'description': f'Quality {name} product - Model {{i+1}}',
                    'price': Decimal(str(price)),
                    'sale_price': Decimal(str(sale)) if sale else None,
                    'stock': random.randint(0, 200),
                    'is_active': True,
                    'specifications': {{'model': f'MOD-{{i+1}}', 'warranty': '1 year', 'color': random.choice(['Black', 'White', 'Silver', 'Blue'])}},
                }}
            )
            if created:
                created_count += 1
                ProductImage.objects.create(
                    product=product,
                    image=f'https://placehold.co/800x600?text={name_title}+{{i+1}}',
                    is_primary=True,
                    alt_text=f'{{product.name}} main image'
                )
                Inventory.objects.get_or_create(
                    product=product,
                    defaults={{'quantity': product.stock, 'reserved_qty': 0, 'low_stock_threshold': 10}}
                )
                Rating.objects.get_or_create(
                    product=product,
                    defaults={{'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 200)}}
                )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {{created_count}} new {name} products. Total: {{Product.objects.count()}}'
        ))
''')

    print(f'    Done {name}-service')


if __name__ == '__main__':
    print('Setting up product services...')
    for name, port, db in SERVICES:
        create_service(name, port, db)
    print('All product services created!')
