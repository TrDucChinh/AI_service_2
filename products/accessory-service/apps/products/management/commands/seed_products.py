"""
Seed command for accessory products.
Creates 50 sample products with brands, categories, images, and inventory.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random


BRANDS = [
    {'name': 'Belkin', 'logo': 'https://placehold.co/200x100?text=Belkin', 'website': 'https://belkin.com'},
    {'name': 'Anker', 'logo': 'https://placehold.co/200x100?text=Anker', 'website': 'https://anker.com'},
    {'name': 'Logitech', 'logo': 'https://placehold.co/200x100?text=Logitech', 'website': 'https://logitech.com'},
    {'name': 'Spigen', 'logo': 'https://placehold.co/200x100?text=Spigen', 'website': 'https://spigen.com'},
    {'name': 'Case-Mate', 'logo': 'https://placehold.co/200x100?text=CaseMate', 'website': 'https://case-mate.com'},
    {'name': 'OtterBox', 'logo': 'https://placehold.co/200x100?text=OtterBox', 'website': 'https://otterbox.com'},
    {'name': 'Mophie', 'logo': 'https://placehold.co/200x100?text=Mophie', 'website': 'https://mophie.com'},
    {'name': 'ESR', 'logo': 'https://placehold.co/200x100?text=ESR', 'website': 'https://esrgear.com'},
]

CATEGORIES = [
    {'name': 'Phone Cases', 'description': 'Protective cases for smartphones'},
    {'name': 'Chargers & Cables', 'description': 'Charging accessories and cables'},
    {'name': 'Screen Protectors', 'description': 'Screen protection films and glass'},
    {'name': 'Power Banks', 'description': 'Portable battery packs'},
    {'name': 'Mounts & Stands', 'description': 'Phone and device mounts and stands'},
]

ACCESSORY_PRODUCTS = [
    ('Anker 65W GaN Charger', 'Anker', 'Chargers & Cables', 35.99, '65W compact 3-port GaN charger'),
    ('Anker PowerCore 20000', 'Anker', 'Power Banks', 45.99, '20000mAh portable charger with dual USB-A and USB-C'),
    ('Anker USB-C to Lightning Cable', 'Anker', 'Chargers & Cables', 15.99, 'MFi certified 6ft cable for iPhone'),
    ('Anker USB-C Cable 6ft', 'Anker', 'Chargers & Cables', 12.99, 'Braided USB-C to USB-C cable'),
    ('Belkin BoostCharge Wireless Pad', 'Belkin', 'Chargers & Cables', 29.99, '15W wireless charging pad'),
    ('Belkin MagSafe 3-in-1 Charger', 'Belkin', 'Chargers & Cables', 149.99, 'Charge iPhone, AirPods, and Apple Watch simultaneously'),
    ('Belkin Car Vent Mount Pro', 'Belkin', 'Mounts & Stands', 29.99, 'MagSafe compatible car mount'),
    ('Spigen Tough Armor Case', 'Spigen', 'Phone Cases', 24.99, 'Military-grade protection phone case'),
    ('Spigen Tempered Glass Screen Protector', 'Spigen', 'Screen Protectors', 14.99, 'Tempered glass screen protector 2-pack'),
    ('Spigen Thin Fit Case', 'Spigen', 'Phone Cases', 19.99, 'Ultra-slim hard shell phone case'),
    ('OtterBox Defender Series', 'OtterBox', 'Phone Cases', 49.99, 'Multi-layer rugged protection case'),
    ('OtterBox Commuter Series', 'OtterBox', 'Phone Cases', 39.99, 'Slim dual-layer protection case'),
    ('Case-Mate Blox Case', 'Case-Mate', 'Phone Cases', 34.99, 'Square-edge design phone case'),
    ('Mophie Juice Pack Access', 'Mophie', 'Power Banks', 79.99, 'Battery case with wireless charging'),
    ('Mophie Powerstation Plus', 'Mophie', 'Power Banks', 49.99, '10000mAh portable charger with built-in cables'),
    ('ESR HaloLock Wallet Case', 'ESR', 'Phone Cases', 29.99, 'MagSafe wallet phone case'),
    ('ESR Armorite Screen Protector', 'ESR', 'Screen Protectors', 12.99, 'Tempered glass with edge-to-edge coverage'),
    ('Logitech MX Anywhere 3', 'Logitech', 'Mounts & Stands', 79.99, 'Compact wireless mouse'),
    ('Anker Wireless Charger Stand', 'Anker', 'Chargers & Cables', 19.99, '10W wireless charging stand'),
    ('Belkin Wired Tablet Stand', 'Belkin', 'Mounts & Stands', 34.99, 'Adjustable aluminum tablet stand'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample accessory products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding accessory products...')

        brand_objs = {}
        for b in BRANDS:
            brand, created = Brand.objects.get_or_create(
                name=b['name'],
                defaults={'logo': b['logo'], 'website': b['website']}
            )
            brand_objs[b['name']] = brand
            if created:
                self.stdout.write(f'  Created brand: {brand.name}')

        cat_objs = {}
        for c in CATEGORIES:
            slug = slugify(c['name'])
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': c['name'], 'description': c['description']}
            )
            cat_objs[c['name']] = cat
            if created:
                self.stdout.write(f'  Created category: {cat.name}')

        created_count = 0
        for i, (name, brand_name, cat_name, base_price, desc) in enumerate(ACCESSORY_PRODUCTS):
            sku = f'ACC-{brand_name[:3].upper()}-{i+1:04d}'
            brand = brand_objs.get(brand_name)
            category = cat_objs.get(cat_name)
            sale = round(base_price * 0.9, 2) if random.random() > 0.6 else None

            specs = {
                'compatibility': random.choice(['Universal', 'iPhone 15', 'iPhone 14', 'Samsung Galaxy S23', 'All devices']),
                'material': random.choice(['Silicone', 'Polycarbonate', 'TPU', 'Aluminum', 'Leather']),
                'color': random.choice(['Black', 'Clear', 'White', 'Navy', 'Red']),
                'warranty': '1 Year',
            }

            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'brand': brand,
                    'category': category,
                    'description': desc,
                    'price': Decimal(str(base_price)),
                    'sale_price': Decimal(str(sale)) if sale else None,
                    'stock': random.randint(10, 300),
                    'specifications': specs,
                }
            )

            if created:
                created_count += 1
                ProductImage.objects.get_or_create(
                    product=product,
                    image=f'https://placehold.co/800x600?text={brand_name}+Accessory',
                    defaults={'is_primary': True, 'alt_text': f'{name} - Main Image'}
                )
                Inventory.objects.get_or_create(
                    product=product,
                    defaults={'quantity': product.stock, 'reserved_qty': 0, 'low_stock_threshold': 20}
                )
                Rating.objects.get_or_create(
                    product=product,
                    defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 500)}
                )

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(9.99, 149.99), 2)
            sku = f'ACC-EXTRA-{i+1:04d}'
            sale = round(price * 0.85, 2) if random.random() > 0.5 else None
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': f'{brand.name} Accessory {i+100}',
                    'brand': brand, 'category': cat,
                    'description': f'Quality accessory from {brand.name}',
                    'price': Decimal(str(price)),
                    'sale_price': Decimal(str(sale)) if sale else None,
                    'stock': random.randint(0, 200),
                    'specifications': {'material': 'Various', 'color': 'Black'},
                }
            )
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Accessory+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)})

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new accessory products. Total: {Product.objects.count()} products.'))
