from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Logitech', 'logo': 'https://placehold.co/200x100?text=Logitech', 'website': 'https://logitech.com'},
    {'name': 'Razer', 'logo': 'https://placehold.co/200x100?text=Razer', 'website': 'https://razer.com'},
    {'name': 'SteelSeries', 'logo': 'https://placehold.co/200x100?text=SteelSeries', 'website': 'https://steelseries.com'},
    {'name': 'Corsair', 'logo': 'https://placehold.co/200x100?text=Corsair', 'website': 'https://corsair.com'},
    {'name': 'ASUS', 'logo': 'https://placehold.co/200x100?text=ASUS', 'website': 'https://asus.com'},
    {'name': 'Glorious', 'logo': 'https://placehold.co/200x100?text=Glorious', 'website': 'https://pcgamingrace.com'},
]

CATEGORIES = [
    {'name': 'Gaming Mice', 'description': 'High-performance gaming mice'},
    {'name': 'Wireless Mice', 'description': 'Wireless and Bluetooth mice'},
    {'name': 'Office Mice', 'description': 'Ergonomic office mice'},
    {'name': 'Trackballs', 'description': 'Trackball pointing devices'},
]

PRODUCTS = [
    ('Logitech G Pro X Superlight 2', 'Logitech', 'Gaming Mice', 159.99, 'Wireless, 95g, HERO 25K sensor'),
    ('Logitech MX Master 3S', 'Logitech', 'Wireless Mice', 99.99, 'Wireless, 8000DPI, MagSpeed scroll'),
    ('Razer DeathAdder V3 Pro', 'Razer', 'Gaming Mice', 149.99, 'Wireless, 63g, Focus Pro 30K'),
    ('Razer Basilisk V3 Pro', 'Razer', 'Gaming Mice', 159.99, 'Wireless, 11 buttons, Razer HyperScroll'),
    ('SteelSeries Rival 650', 'SteelSeries', 'Gaming Mice', 79.99, 'Wireless, dual sensor, RGB'),
    ('SteelSeries Aerox 5 Wireless', 'SteelSeries', 'Gaming Mice', 129.99, 'Wireless, 74g, TrueMove Air'),
    ('Corsair Dark Core RGB Pro', 'Corsair', 'Gaming Mice', 79.99, 'Wireless, 18000DPI, hyper-polling'),
    ('ASUS ROG Gladius III', 'ASUS', 'Gaming Mice', 79.99, 'Wired, 19000DPI, hotswap switches'),
    ('Glorious Model O Wireless', 'Glorious', 'Gaming Mice', 79.99, 'Wireless, 69g, Bambo sensor'),
    ('Logitech G305 Lightspeed', 'Logitech', 'Gaming Mice', 39.99, 'Wireless, Hero 12K, 99g'),
    ('Logitech MX Anywhere 3', 'Logitech', 'Office Mice', 59.99, 'Compact wireless, any surface'),
    ('Razer Pro Click', 'Razer', 'Office Mice', 99.99, 'Wireless, ergonomic, silent clicks'),
]


class Command(BaseCommand):
    help = 'Seed mouse products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding mouse products...')
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
            sku = f'MOUSE-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(10, 200),
                'specifications': {'dpi': random.choice(['12000', '16000', '19000', '25600', '30000']), 'connection': random.choice(['Wired', 'Wireless', 'Both']), 'weight': f'{random.randint(60, 130)}g', 'buttons': random.randint(5, 11)},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Mouse', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 20})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 400)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(19.99, 159.99), 2)
            sku = f'MOUSE-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Mouse {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 100),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Mouse+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 200)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} mouse products. Total: {Product.objects.count()}'))
