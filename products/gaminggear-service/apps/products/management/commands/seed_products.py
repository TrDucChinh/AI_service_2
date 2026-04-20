from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Razer', 'logo': 'https://placehold.co/200x100?text=Razer', 'website': 'https://razer.com'},
    {'name': 'SteelSeries', 'logo': 'https://placehold.co/200x100?text=SteelSeries', 'website': 'https://steelseries.com'},
    {'name': 'HyperX', 'logo': 'https://placehold.co/200x100?text=HyperX', 'website': 'https://hyperx.com'},
    {'name': 'ASTRO', 'logo': 'https://placehold.co/200x100?text=ASTRO', 'website': 'https://astrogaming.com'},
    {'name': 'Corsair', 'logo': 'https://placehold.co/200x100?text=Corsair', 'website': 'https://corsair.com'},
    {'name': 'Secretlab', 'logo': 'https://placehold.co/200x100?text=Secretlab', 'website': 'https://secretlab.co'},
]

CATEGORIES = [
    {'name': 'Gaming Headsets', 'description': 'Immersive gaming headsets'},
    {'name': 'Gaming Chairs', 'description': 'Ergonomic gaming chairs'},
    {'name': 'Gaming Mousepads', 'description': 'Large gaming mousepads'},
    {'name': 'Controllers', 'description': 'Gaming controllers'},
    {'name': 'Gaming Desks', 'description': 'Gaming desks and setups'},
]

PRODUCTS = [
    ('Razer BlackShark V2 Pro', 'Razer', 'Gaming Headsets', 179.99, 'Wireless, 50mm drivers, THX Spatial'),
    ('SteelSeries Arctis Nova Pro', 'SteelSeries', 'Gaming Headsets', 249.99, 'Wireless, dual-wireless, ANC'),
    ('HyperX Cloud Alpha Wireless', 'HyperX', 'Gaming Headsets', 199.99, 'Wireless, 300hr battery, dual chamber'),
    ('ASTRO A50 Gen 4', 'ASTRO', 'Gaming Headsets', 299.99, 'Wireless, Dolby, 15hr battery'),
    ('Corsair HS80 RGB Wireless', 'Corsair', 'Gaming Headsets', 129.99, 'Wireless, Dolby Atmos, USB-A'),
    ('Secretlab TITAN Evo 2022', 'Secretlab', 'Gaming Chairs', 549.00, 'Ergonomic, lumbar support, XL sizes'),
    ('Secretlab OMEGA 2022', 'Secretlab', 'Gaming Chairs', 449.00, 'Classic gaming chair, 4D armrests'),
    ('Corsair HS35 Stereo', 'Corsair', 'Gaming Headsets', 39.99, 'Wired, custom-tuned 50mm, flexible mic'),
    ('Razer Gigantus V2 3XL', 'Razer', 'Gaming Mousepads', 49.99, '1220x610mm, micro-textured cloth'),
    ('SteelSeries QcK Heavy XXL', 'SteelSeries', 'Gaming Mousepads', 49.99, '900x300mm, thick 6mm, cloth'),
    ('Razer Wolverine V2 Chroma', 'Razer', 'Controllers', 99.99, 'Wired Xbox controller, remappable'),
    ('HyperX Clutch Wireless', 'HyperX', 'Controllers', 69.99, 'Wireless, Android/PC, 2.4GHz'),
]


class Command(BaseCommand):
    help = 'Seed gaming gear products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding gaming gear products...')
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
            sku = f'GEAR-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(5, 100),
                'specifications': {'connection': random.choice(['Wired', 'Wireless', 'Both']), 'compatibility': random.choice(['PC', 'PS5', 'Xbox', 'Multi-platform']), 'rgb': random.choice([True, False])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Gaming', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 10})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 300)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(29.99, 549.99), 2)
            sku = f'GEAR-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Gaming Gear {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 80),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=GamingGear+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 150)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} gaming gear products. Total: {Product.objects.count()}'))
