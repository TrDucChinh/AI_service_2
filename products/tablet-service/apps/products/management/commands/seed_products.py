"""Seed command for tablet products."""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Apple', 'logo': 'https://placehold.co/200x100?text=Apple', 'website': 'https://apple.com'},
    {'name': 'Samsung', 'logo': 'https://placehold.co/200x100?text=Samsung', 'website': 'https://samsung.com'},
    {'name': 'Microsoft', 'logo': 'https://placehold.co/200x100?text=Microsoft', 'website': 'https://microsoft.com'},
    {'name': 'Lenovo', 'logo': 'https://placehold.co/200x100?text=Lenovo', 'website': 'https://lenovo.com'},
    {'name': 'Amazon', 'logo': 'https://placehold.co/200x100?text=Amazon', 'website': 'https://amazon.com'},
]

CATEGORIES = [
    {'name': 'iPad & Apple Tablets', 'description': 'Apple iPad lineup', 'slug': 'ipad-apple-tablets'},
    {'name': 'Android Tablets', 'description': 'Android-based tablets', 'slug': 'android-tablets'},
    {'name': 'Windows Tablets', 'description': 'Windows-based tablets', 'slug': 'windows-tablets'},
    {'name': 'Kids Tablets', 'description': 'Tablets for children', 'slug': 'kids-tablets'},
]

PRODUCTS = [
    ('Apple iPad Pro 12.9"', 'Apple', 'iPad & Apple Tablets', 1099.99),
    ('Apple iPad Air 5th Gen', 'Apple', 'iPad & Apple Tablets', 749.99),
    ('Apple iPad Mini 6', 'Apple', 'iPad & Apple Tablets', 499.99),
    ('Samsung Galaxy Tab S9 Ultra', 'Samsung', 'Android Tablets', 1199.99),
    ('Samsung Galaxy Tab S9', 'Samsung', 'Android Tablets', 799.99),
    ('Microsoft Surface Pro 9', 'Microsoft', 'Windows Tablets', 999.99),
    ('Lenovo Tab P12 Pro', 'Lenovo', 'Android Tablets', 599.99),
    ('Amazon Fire HD 10', 'Amazon', 'Android Tablets', 149.99),
    ('Amazon Fire HD 8 Kids', 'Amazon', 'Kids Tablets', 139.99),
]


class Command(BaseCommand):
    help = 'Seed the database with sample tablet products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding tablet products...')
        brand_objs = {}
        for b in BRANDS:
            brand, _ = Brand.objects.get_or_create(name=b['name'], defaults={'logo': b['logo'], 'website': b['website']})
            brand_objs[b['name']] = brand

        cat_objs = {}
        for c in CATEGORIES:
            cat, _ = Category.objects.get_or_create(slug=c['slug'], defaults={'name': c['name'], 'description': c['description']})
            cat_objs[c['name']] = cat

        created_count = 0
        for i, (name, brand_name, cat_name, price) in enumerate(PRODUCTS):
            sku = f'TABLET-{i+1:04d}'
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name, 'brand': brand_objs.get(brand_name),
                    'category': cat_objs.get(cat_name),
                    'description': f'{name} - premium tablet experience',
                    'price': Decimal(str(price)),
                    'sale_price': Decimal(str(round(price * 0.9, 2))) if random.random() > 0.6 else None,
                    'stock': random.randint(5, 50),
                    'specifications': {'display': random.choice(['10.9"', '11"', '12.4"', '12.9"']), 'storage': random.choice(['64GB', '128GB', '256GB', '512GB']), 'connectivity': '5G + WiFi'}
                }
            )
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Tablet+{i+1}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 300)})

        for i in range(max(0, 50 - Product.objects.count())):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(99.99, 1299.99), 2)
            sku = f'TABLET-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={'name': f'{brand.name} Tablet {i+100}', 'brand': brand, 'category': cat, 'description': f'Tablet from {brand.name}', 'price': Decimal(str(price)), 'stock': random.randint(0, 30), 'specifications': {'display': '10.9"', 'storage': '128GB'}}
            )
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Tablet', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} tablet products. Total: {Product.objects.count()}'))
