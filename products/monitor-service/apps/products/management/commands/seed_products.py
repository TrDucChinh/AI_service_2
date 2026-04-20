from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'LG', 'logo': 'https://placehold.co/200x100?text=LG', 'website': 'https://lg.com'},
    {'name': 'Samsung', 'logo': 'https://placehold.co/200x100?text=Samsung', 'website': 'https://samsung.com'},
    {'name': 'Dell', 'logo': 'https://placehold.co/200x100?text=Dell', 'website': 'https://dell.com'},
    {'name': 'ASUS', 'logo': 'https://placehold.co/200x100?text=ASUS', 'website': 'https://asus.com'},
    {'name': 'BenQ', 'logo': 'https://placehold.co/200x100?text=BenQ', 'website': 'https://benq.com'},
    {'name': 'AOC', 'logo': 'https://placehold.co/200x100?text=AOC', 'website': 'https://aoc.com'},
]

CATEGORIES = [
    {'name': 'Gaming Monitors', 'description': 'High refresh rate gaming monitors'},
    {'name': 'Professional Monitors', 'description': 'Color-accurate professional monitors'},
    {'name': 'Ultrawide Monitors', 'description': 'Ultrawide curved monitors'},
    {'name': 'Budget Monitors', 'description': 'Affordable everyday monitors'},
    {'name': '4K Monitors', 'description': 'Ultra HD 4K resolution monitors'},
]

PRODUCTS = [
    ('LG 27GP850-B', 'LG', 'Gaming Monitors', 349.99, '27" QHD, 165Hz, 1ms, Nano IPS'),
    ('LG 34WP65C-B', 'LG', 'Ultrawide Monitors', 449.99, '34" UltraWide QHD, VA, 160Hz'),
    ('Samsung Odyssey G7 32"', 'Samsung', 'Gaming Monitors', 599.99, 'QHD, 240Hz, 1ms VESA DisplayHDR'),
    ('Samsung ViewFinity S8', 'Samsung', 'Professional Monitors', 799.99, '4K, USB-C, Thunderbolt 4'),
    ('Dell S2722DGM', 'Dell', 'Gaming Monitors', 279.99, '27" QHD, 165Hz, AMD FreeSync'),
    ('Dell UltraSharp U2723QE', 'Dell', 'Professional Monitors', 699.99, '27" 4K, IPS Black, USB-C 90W'),
    ('ASUS ROG Swift PG279QM', 'ASUS', 'Gaming Monitors', 699.99, '27" QHD, 240Hz, G-Sync'),
    ('ASUS ProArt PA279CRV', 'ASUS', 'Professional Monitors', 499.99, '27" 4K, 98% DCI-P3, USB-C'),
    ('BenQ EX2780Q', 'BenQ', 'Gaming Monitors', 399.99, '27" QHD, 144Hz, HDRi'),
    ('AOC 24G2', 'AOC', 'Gaming Monitors', 199.99, '24" FHD, 144Hz, 1ms, IPS'),
    ('AOC U28P2A', 'AOC', '4K Monitors', 349.99, '28" 4K, 60Hz, USB-C, IPS'),
    ('LG 27UK850-W', 'LG', '4K Monitors', 449.99, '27" 4K, HDR, USB-C, IPS'),
]


class Command(BaseCommand):
    help = 'Seed monitor products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding monitor products...')
        brand_objs = {}
        for b in BRANDS:
            brand, _ = Brand.objects.get_or_create(name=b['name'], defaults={'logo': b['logo'], 'website': b['website']})
            brand_objs[b['name']] = brand

        cat_objs = {}
        for c in CATEGORIES:
            cat, _ = Category.objects.get_or_create(slug=slugify(c['name']), defaults={'name': c['name'], 'description': c['description']})
            cat_objs[c['name']] = cat

        created_count = 0
        for i, (name, brand_name, cat_name, price, desc) in enumerate(PRODUCTS):
            sku = f'MON-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(5, 80),
                'specifications': {'size': random.choice(['24"', '27"', '32"', '34"']), 'resolution': random.choice(['1920x1080', '2560x1440', '3840x2160']), 'refresh_rate': random.choice(['60Hz', '144Hz', '165Hz', '240Hz']), 'panel': random.choice(['IPS', 'VA', 'TN'])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Monitor', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 10})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 200)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(149.99, 799.99), 2)
            sku = f'MON-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Monitor {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 50),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Monitor+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} monitor products. Total: {Product.objects.count()}'))
