from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Apple', 'logo': 'https://placehold.co/200x100?text=Apple', 'website': 'https://apple.com'},
    {'name': 'Samsung', 'logo': 'https://placehold.co/200x100?text=Samsung', 'website': 'https://samsung.com'},
    {'name': 'Garmin', 'logo': 'https://placehold.co/200x100?text=Garmin', 'website': 'https://garmin.com'},
    {'name': 'Fitbit', 'logo': 'https://placehold.co/200x100?text=Fitbit', 'website': 'https://fitbit.com'},
    {'name': 'Fossil', 'logo': 'https://placehold.co/200x100?text=Fossil', 'website': 'https://fossil.com'},
    {'name': 'Amazfit', 'logo': 'https://placehold.co/200x100?text=Amazfit', 'website': 'https://amazfit.com'},
]

CATEGORIES = [
    {'name': 'Fitness Trackers', 'description': 'Activity and fitness tracking bands'},
    {'name': 'Smartwatches', 'description': 'Full-featured smartwatches'},
    {'name': 'Sport Watches', 'description': 'GPS sport and outdoor watches'},
    {'name': 'Fashion Smartwatches', 'description': 'Stylish fashion smartwatches'},
]

PRODUCTS = [
    ('Apple Watch Series 9', 'Apple', 'Smartwatches', 399.99, 'GPS, Always-On Retina display, 45mm'),
    ('Apple Watch Ultra 2', 'Apple', 'Sport Watches', 799.99, 'Titanium case, 49mm, Alpine Loop'),
    ('Samsung Galaxy Watch 6', 'Samsung', 'Smartwatches', 299.99, '44mm, BioActive Sensor, Wear OS'),
    ('Samsung Galaxy Watch 6 Classic', 'Samsung', 'Smartwatches', 349.99, '47mm, Rotating Bezel'),
    ('Garmin Forerunner 965', 'Garmin', 'Sport Watches', 599.99, 'AMOLED, GPS, Training Readiness'),
    ('Garmin Fenix 7X Solar', 'Garmin', 'Sport Watches', 799.99, 'Solar charging, 51mm, Multi-GNSS'),
    ('Garmin Venu 3', 'Garmin', 'Fitness Trackers', 449.99, 'AMOLED, Sleep Coach, 45mm'),
    ('Fitbit Sense 2', 'Fitbit', 'Fitness Trackers', 249.99, 'ECG app, EDA sensor, 6-day battery'),
    ('Fitbit Charge 6', 'Fitbit', 'Fitness Trackers', 159.99, 'GPS, Google Maps, YouTube Music'),
    ('Fossil Gen 6', 'Fossil', 'Fashion Smartwatches', 295.00, '44mm, Wear OS, 1-day battery'),
    ('Amazfit GTR 4', 'Amazfit', 'Smartwatches', 199.99, 'AMOLED, 14-day battery, GPS'),
    ('Amazfit T-Rex 2', 'Amazfit', 'Sport Watches', 219.99, 'Military-grade, 10ATM, GPS'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample smartwatch products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding smartwatch products...')
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
            sku = f'WATCH-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(5, 100),
                'specifications': {'display': random.choice(['AMOLED', 'LCD', 'MIP']), 'battery': f'{random.randint(18, 21)}h GPS', 'water_resistance': f'{random.randint(3, 10)}ATM', 'os': random.choice(['Wear OS', 'watchOS', 'Garmin OS', 'FitbitOS'])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Watch', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 10})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 200)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(99.99, 799.99), 2)
            sku = f'WATCH-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Smartwatch Model {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 50),
                'specifications': {'battery': f'{random.randint(1, 14)} days'},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Watch+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} smartwatch products. Total: {Product.objects.count()}'))
