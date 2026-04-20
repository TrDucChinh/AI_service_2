from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Sony', 'logo': 'https://placehold.co/200x100?text=Sony', 'website': 'https://sony.com'},
    {'name': 'Canon', 'logo': 'https://placehold.co/200x100?text=Canon', 'website': 'https://canon.com'},
    {'name': 'Nikon', 'logo': 'https://placehold.co/200x100?text=Nikon', 'website': 'https://nikon.com'},
    {'name': 'Fujifilm', 'logo': 'https://placehold.co/200x100?text=Fujifilm', 'website': 'https://fujifilm.com'},
    {'name': 'Panasonic', 'logo': 'https://placehold.co/200x100?text=Panasonic', 'website': 'https://panasonic.com'},
    {'name': 'GoPro', 'logo': 'https://placehold.co/200x100?text=GoPro', 'website': 'https://gopro.com'},
]

CATEGORIES = [
    {'name': 'Mirrorless Cameras', 'description': 'Compact mirrorless interchangeable lens cameras'},
    {'name': 'DSLR Cameras', 'description': 'Digital single-lens reflex cameras'},
    {'name': 'Point & Shoot', 'description': 'Compact point and shoot cameras'},
    {'name': 'Action Cameras', 'description': 'Rugged action and adventure cameras'},
    {'name': 'Camera Lenses', 'description': 'Interchangeable camera lenses'},
]

PRODUCTS = [
    ('Sony Alpha A7 IV', 'Sony', 'Mirrorless Cameras', 2499.99, '33MP full-frame, 4K60p, IBIS'),
    ('Sony ZV-E10', 'Sony', 'Mirrorless Cameras', 699.99, '24.2MP APS-C, 4K video, vlog'),
    ('Canon EOS R6 Mark II', 'Canon', 'Mirrorless Cameras', 2499.99, '40MP, 4K60p, IBIS, Dual Pixel AF'),
    ('Canon EOS R50', 'Canon', 'Mirrorless Cameras', 679.99, '24.2MP APS-C, 4K30p, compact'),
    ('Nikon Z6 III', 'Nikon', 'Mirrorless Cameras', 1999.99, '24.5MP, 6K ProRes, Z mount'),
    ('Fujifilm X-T5', 'Fujifilm', 'Mirrorless Cameras', 1699.99, '40.2MP APS-C, X-Trans CMOS 5 HR'),
    ('Canon EOS 90D', 'Canon', 'DSLR Cameras', 1199.99, '32.5MP APS-C, 4K, Dual Pixel AF'),
    ('Nikon D780', 'Nikon', 'DSLR Cameras', 2299.99, '24.5MP full-frame, 4K, 51-pt AF'),
    ('Sony RX100 VII', 'Sony', 'Point & Shoot', 1299.99, '20.1MP 1-inch sensor, 4K, Real-time tracking'),
    ('Canon PowerShot G7X III', 'Canon', 'Point & Shoot', 749.99, '20.1MP, 4K, Live streaming'),
    ('GoPro Hero 12 Black', 'GoPro', 'Action Cameras', 399.99, '5.3K60, HyperSmooth 6.0, waterproof'),
    ('GoPro Hero 11 Black', 'GoPro', 'Action Cameras', 299.99, '5.3K60, HyperSmooth 5.0, 10-bit color'),
]


class Command(BaseCommand):
    help = 'Seed camera products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding camera products...')
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
            sku = f'CAM-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(5, 50),
                'specifications': {'megapixels': random.choice(['20MP', '24MP', '33MP', '40MP']), 'video': random.choice(['4K30', '4K60', '6K30']), 'sensor': random.choice(['APS-C', 'Full-frame', '1-inch'])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Camera', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 5})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 150)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(299.99, 2499.99), 2)
            sku = f'CAM-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Camera Model {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 30),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Camera+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} camera products. Total: {Product.objects.count()}'))
