from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Samsung', 'logo': 'https://placehold.co/200x100?text=Samsung', 'website': 'https://samsung.com'},
    {'name': 'Western Digital', 'logo': 'https://placehold.co/200x100?text=WD', 'website': 'https://westerndigital.com'},
    {'name': 'Seagate', 'logo': 'https://placehold.co/200x100?text=Seagate', 'website': 'https://seagate.com'},
    {'name': 'SanDisk', 'logo': 'https://placehold.co/200x100?text=SanDisk', 'website': 'https://sandisk.com'},
    {'name': 'Crucial', 'logo': 'https://placehold.co/200x100?text=Crucial', 'website': 'https://crucial.com'},
]

CATEGORIES = [
    {'name': 'NVMe SSDs', 'description': 'High-speed NVMe solid state drives'},
    {'name': 'SATA SSDs', 'description': 'SATA solid state drives'},
    {'name': 'Hard Drives', 'description': 'Traditional hard disk drives'},
    {'name': 'External Drives', 'description': 'Portable and desktop external drives'},
    {'name': 'USB Flash Drives', 'description': 'USB flash storage'},
    {'name': 'Memory Cards', 'description': 'SD, microSD memory cards'},
]

PRODUCTS = [
    ('Samsung 990 Pro 2TB NVMe', 'Samsung', 'NVMe SSDs', 179.99, 'PCIe 4.0, 7450MB/s read, 2TB'),
    ('Samsung 870 EVO 1TB SATA', 'Samsung', 'SATA SSDs', 89.99, 'SATA III, 560MB/s, 1TB'),
    ('WD Black SN850X 2TB', 'Western Digital', 'NVMe SSDs', 159.99, 'PCIe 4.0, 7300MB/s, 2TB'),
    ('WD Blue 4TB HDD', 'Western Digital', 'Hard Drives', 89.99, '5400RPM, SATA, 64MB cache'),
    ('Seagate Barracuda 2TB', 'Seagate', 'Hard Drives', 54.99, '7200RPM, SATA, 256MB cache'),
    ('Seagate Expansion 4TB External', 'Seagate', 'External Drives', 89.99, 'USB 3.0, portable, 4TB'),
    ('SanDisk Extreme Pro 2TB External', 'SanDisk', 'External Drives', 219.99, 'USB 3.2, 2000MB/s, rugged'),
    ('Crucial P3 Plus 2TB NVMe', 'Crucial', 'NVMe SSDs', 99.99, 'PCIe 4.0, 5000MB/s, 2TB'),
    ('Crucial MX500 1TB SATA', 'Crucial', 'SATA SSDs', 74.99, 'SATA III, 560MB/s, 1TB'),
    ('Samsung T7 Shield 2TB', 'Samsung', 'External Drives', 169.99, 'USB 3.2 Gen2, 1050MB/s, rugged'),
    ('SanDisk Ultra 256GB USB', 'SanDisk', 'USB Flash Drives', 29.99, 'USB 3.0, 130MB/s, 256GB'),
    ('Samsung PRO Plus 256GB microSD', 'Samsung', 'Memory Cards', 39.99, 'UHS-I, 180MB/s, Class 10'),
]


class Command(BaseCommand):
    help = 'Seed storage products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding storage products...')
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
            sku = f'STG-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(20, 200),
                'specifications': {'capacity': random.choice(['256GB', '512GB', '1TB', '2TB', '4TB']), 'interface': random.choice(['PCIe 4.0', 'SATA III', 'USB 3.0', 'USB 3.2']), 'read_speed': f'{random.randint(500, 7500)}MB/s'},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Storage', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 20})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(4.0, 5.0), 2), 'total_reviews': random.randint(0, 500)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(19.99, 299.99), 2)
            sku = f'STG-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Storage {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 100),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Storage+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 200)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} storage products. Total: {Product.objects.count()}'))
