from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Logitech', 'logo': 'https://placehold.co/200x100?text=Logitech', 'website': 'https://logitech.com'},
    {'name': 'Corsair', 'logo': 'https://placehold.co/200x100?text=Corsair', 'website': 'https://corsair.com'},
    {'name': 'Razer', 'logo': 'https://placehold.co/200x100?text=Razer', 'website': 'https://razer.com'},
    {'name': 'SteelSeries', 'logo': 'https://placehold.co/200x100?text=SteelSeries', 'website': 'https://steelseries.com'},
    {'name': 'Keychron', 'logo': 'https://placehold.co/200x100?text=Keychron', 'website': 'https://keychron.com'},
    {'name': 'Ducky', 'logo': 'https://placehold.co/200x100?text=Ducky', 'website': 'https://duckychannel.com'},
]

CATEGORIES = [
    {'name': 'Mechanical Keyboards', 'description': 'Mechanical switch keyboards'},
    {'name': 'Gaming Keyboards', 'description': 'Keyboards designed for gaming'},
    {'name': 'Wireless Keyboards', 'description': 'Wireless and Bluetooth keyboards'},
    {'name': 'Compact Keyboards', 'description': '60% and 75% compact keyboards'},
    {'name': 'Office Keyboards', 'description': 'Quiet keyboards for office use'},
]

PRODUCTS = [
    ('Logitech G Pro X TKL', 'Logitech', 'Gaming Keyboards', 149.99, 'Tenkeyless, hotswap, RGB, GX switches'),
    ('Logitech MX Keys', 'Logitech', 'Wireless Keyboards', 109.99, 'Backlit, multi-device, USB-C'),
    ('Corsair K70 RGB Pro', 'Corsair', 'Mechanical Keyboards', 159.99, 'Full-size, Cherry MX, per-key RGB'),
    ('Corsair K65 Plus Wireless', 'Corsair', 'Wireless Keyboards', 149.99, '75% wireless, hotswap, RGB'),
    ('Razer BlackWidow V4 Pro', 'Razer', 'Gaming Keyboards', 229.99, 'Full-size, Yellow/Green switches, RGB'),
    ('Razer Huntsman Mini', 'Razer', 'Compact Keyboards', 99.99, '60%, optical switches, PBT keycaps'),
    ('SteelSeries Apex Pro', 'SteelSeries', 'Gaming Keyboards', 199.99, 'Full-size, OmniPoint 2.0, OLED display'),
    ('Keychron Q1 Pro', 'Keychron', 'Mechanical Keyboards', 199.99, '75%, aluminum, wireless, hotswap'),
    ('Keychron K2 V2', 'Keychron', 'Wireless Keyboards', 89.99, '75%, RGB, Bluetooth 5.1, hotswap'),
    ('Ducky One 3', 'Ducky', 'Mechanical Keyboards', 119.99, 'Full-size, Cherry MX, PBT keycaps'),
    ('Ducky Mecha Mini', 'Ducky', 'Compact Keyboards', 109.99, '60%, Cherry MX, RGB, doubleshot PBT'),
    ('Logitech G512 Carbon', 'Logitech', 'Gaming Keyboards', 79.99, 'Full-size, GX Brown switches, RGB'),
]


class Command(BaseCommand):
    help = 'Seed keyboard products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding keyboard products...')
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
            sku = f'KB-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(10, 150),
                'specifications': {'switch': random.choice(['Cherry MX Red', 'Cherry MX Brown', 'Razer Yellow', 'Optical']), 'layout': random.choice(['Full', 'TKL', '75%', '65%', '60%']), 'connection': random.choice(['Wired', 'Wireless', 'Both']), 'rgb': random.choice([True, False])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Keyboard', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 15})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 300)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(29.99, 229.99), 2)
            sku = f'KB-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Keyboard {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 100),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Keyboard+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 150)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} keyboard products. Total: {Product.objects.count()}'))
