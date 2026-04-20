"""Seed command for mobile/smartphone products."""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Apple', 'logo': 'https://placehold.co/200x100?text=Apple', 'website': 'https://apple.com'},
    {'name': 'Samsung', 'logo': 'https://placehold.co/200x100?text=Samsung', 'website': 'https://samsung.com'},
    {'name': 'Google', 'logo': 'https://placehold.co/200x100?text=Google', 'website': 'https://store.google.com'},
    {'name': 'OnePlus', 'logo': 'https://placehold.co/200x100?text=OnePlus', 'website': 'https://oneplus.com'},
    {'name': 'Xiaomi', 'logo': 'https://placehold.co/200x100?text=Xiaomi', 'website': 'https://mi.com'},
    {'name': 'Sony', 'logo': 'https://placehold.co/200x100?text=Sony', 'website': 'https://sony.com'},
    {'name': 'Motorola', 'logo': 'https://placehold.co/200x100?text=Motorola', 'website': 'https://motorola.com'},
    {'name': 'Nokia', 'logo': 'https://placehold.co/200x100?text=Nokia', 'website': 'https://nokia.com'},
]

CATEGORIES = [
    {'name': 'Flagship Phones', 'description': 'Top-of-the-line smartphones'},
    {'name': 'Mid-Range Phones', 'description': 'Best value smartphones'},
    {'name': 'Budget Phones', 'description': 'Affordable smartphones'},
    {'name': 'Foldable Phones', 'description': 'Foldable smartphones'},
    {'name': 'Rugged Phones', 'description': 'Tough and durable smartphones'},
]

MOBILE_PRODUCTS = [
    ('iPhone 15 Pro', 'Apple', 'Flagship Phones', 999.99),
    ('iPhone 15', 'Apple', 'Flagship Phones', 799.99),
    ('iPhone 14', 'Apple', 'Mid-Range Phones', 699.99),
    ('Samsung Galaxy S24 Ultra', 'Samsung', 'Flagship Phones', 1199.99),
    ('Samsung Galaxy S24', 'Samsung', 'Flagship Phones', 799.99),
    ('Samsung Galaxy A54', 'Samsung', 'Mid-Range Phones', 449.99),
    ('Samsung Galaxy Z Fold 5', 'Samsung', 'Foldable Phones', 1799.99),
    ('Google Pixel 8 Pro', 'Google', 'Flagship Phones', 999.99),
    ('Google Pixel 8', 'Google', 'Flagship Phones', 699.99),
    ('Google Pixel 7a', 'Google', 'Mid-Range Phones', 499.99),
    ('OnePlus 12', 'OnePlus', 'Flagship Phones', 799.99),
    ('OnePlus Nord 3', 'OnePlus', 'Mid-Range Phones', 449.99),
    ('Xiaomi 14 Pro', 'Xiaomi', 'Flagship Phones', 899.99),
    ('Xiaomi Redmi Note 12', 'Xiaomi', 'Budget Phones', 249.99),
    ('Sony Xperia 1 V', 'Sony', 'Flagship Phones', 1299.99),
    ('Motorola Edge 40 Pro', 'Motorola', 'Flagship Phones', 799.99),
    ('Motorola Moto G84', 'Motorola', 'Budget Phones', 299.99),
    ('Nokia G60', 'Nokia', 'Budget Phones', 349.99),
]


class Command(BaseCommand):
    help = 'Seed the database with sample mobile products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding mobile products...')
        brand_objs = {}
        for b in BRANDS:
            brand, _ = Brand.objects.get_or_create(name=b['name'], defaults={'logo': b['logo'], 'website': b['website']})
            brand_objs[b['name']] = brand

        cat_objs = {}
        for c in CATEGORIES:
            slug = slugify(c['name'])
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': c['name'], 'description': c['description']})
            cat_objs[c['name']] = cat

        created_count = 0
        for i, (name, brand_name, cat_name, price) in enumerate(MOBILE_PRODUCTS):
            sku = f'MOBILE-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            specs = {
                'processor': random.choice(['Apple A17', 'Snapdragon 8 Gen 3', 'Tensor G3', 'Dimensity 9300']),
                'ram': random.choice(['8GB', '12GB', '16GB']),
                'storage': random.choice(['128GB', '256GB', '512GB', '1TB']),
                'display': random.choice(['6.1"', '6.4"', '6.7"', '6.8"']),
                'battery': random.choice(['4000mAh', '4500mAh', '5000mAh']),
                'camera': random.choice(['48MP', '50MP', '108MP', '200MP']),
                'os': random.choice(['iOS 17', 'Android 14', 'Android 13']),
            }
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name, 'brand': brand_objs.get(brand_name),
                    'category': cat_objs.get(cat_name),
                    'description': f'Latest {name} smartphone with cutting-edge features',
                    'price': Decimal(str(price)),
                    'sale_price': Decimal(str(sale)) if sale else None,
                    'stock': random.randint(5, 100),
                    'specifications': specs,
                }
            )
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Phone', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 500)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(199.99, 1299.99), 2)
            sku = f'MOBILE-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': f'{brand.name} Phone Model {i+100}', 'brand': brand, 'category': cat,
                    'description': f'Smartphone from {brand.name}',
                    'price': Decimal(str(price)), 'stock': random.randint(0, 50),
                    'specifications': {'ram': '8GB', 'storage': '128GB'},
                }
            )
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Phone+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 200)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} new mobile products. Total: {Product.objects.count()}'))
