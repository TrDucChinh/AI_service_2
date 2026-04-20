"""
Seed command for audio products.
Creates 50 sample products with brands, categories, images, and inventory.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random


BRANDS = [
    {'name': 'Sony', 'logo': 'https://placehold.co/200x100?text=Sony', 'website': 'https://sony.com'},
    {'name': 'Bose', 'logo': 'https://placehold.co/200x100?text=Bose', 'website': 'https://bose.com'},
    {'name': 'Sennheiser', 'logo': 'https://placehold.co/200x100?text=Sennheiser', 'website': 'https://sennheiser.com'},
    {'name': 'Apple', 'logo': 'https://placehold.co/200x100?text=Apple', 'website': 'https://apple.com'},
    {'name': 'JBL', 'logo': 'https://placehold.co/200x100?text=JBL', 'website': 'https://jbl.com'},
    {'name': 'Audio-Technica', 'logo': 'https://placehold.co/200x100?text=AudioTechnica', 'website': 'https://audio-technica.com'},
    {'name': 'Jabra', 'logo': 'https://placehold.co/200x100?text=Jabra', 'website': 'https://jabra.com'},
    {'name': 'Anker', 'logo': 'https://placehold.co/200x100?text=Anker', 'website': 'https://anker.com'},
]

CATEGORIES = [
    {'name': 'Headphones', 'description': 'Over-ear and on-ear headphones'},
    {'name': 'Earbuds', 'description': 'True wireless and wired earbuds'},
    {'name': 'Speakers', 'description': 'Portable and home speakers'},
    {'name': 'Soundbars', 'description': 'Home theater soundbars'},
    {'name': 'Microphones', 'description': 'Studio and gaming microphones'},
]

AUDIO_PRODUCTS = [
    ('Sony WH-1000XM5', 'Sony', 'Headphones', 349.99, 'Industry-leading noise canceling headphones with 30hr battery'),
    ('Sony WF-1000XM4', 'Sony', 'Earbuds', 279.99, 'True wireless earbuds with noise canceling'),
    ('Sony SRS-XB43', 'Sony', 'Speakers', 149.99, 'Extra bass portable bluetooth speaker'),
    ('Sony HT-A7000', 'Sony', 'Soundbars', 1299.99, '7.1.2ch Dolby Atmos soundbar'),
    ('Bose QuietComfort 45', 'Bose', 'Headphones', 329.99, 'Wireless noise cancelling headphones'),
    ('Bose QuietComfort Earbuds II', 'Bose', 'Earbuds', 299.99, 'True wireless noise cancelling earbuds'),
    ('Bose SoundLink Flex', 'Bose', 'Speakers', 149.99, 'Waterproof portable bluetooth speaker'),
    ('Bose Smart Soundbar 900', 'Bose', 'Soundbars', 899.99, 'Dolby Atmos soundbar with voice control'),
    ('Sennheiser HD 660S2', 'Sennheiser', 'Headphones', 499.99, 'Open-back audiophile headphones'),
    ('Sennheiser Momentum True Wireless 3', 'Sennheiser', 'Earbuds', 249.99, 'Premium TWS earbuds'),
    ('Apple AirPods Pro 2nd Gen', 'Apple', 'Earbuds', 249.99, 'Active noise cancellation and transparency mode'),
    ('Apple AirPods Max', 'Apple', 'Headphones', 549.99, 'High-fidelity headphones with ANC'),
    ('Apple HomePod', 'Apple', 'Speakers', 299.99, 'Intelligent home speaker with Spatial Audio'),
    ('JBL Charge 5', 'JBL', 'Speakers', 179.99, 'Portable waterproof speaker with powerbank'),
    ('JBL Flip 6', 'JBL', 'Speakers', 129.99, 'Compact portable bluetooth speaker'),
    ('JBL Tune 760NC', 'JBL', 'Headphones', 99.99, 'Wireless over-ear noise cancelling headphones'),
    ('JBL Live Pro+ TWS', 'JBL', 'Earbuds', 149.99, 'True wireless earbuds with noise cancelling'),
    ('JBL Bar 9.1', 'JBL', 'Soundbars', 699.99, '9.1ch Dolby Atmos soundbar system'),
    ('Audio-Technica ATH-M50xBT2', 'Audio-Technica', 'Headphones', 199.99, 'Professional wireless headphones'),
    ('Audio-Technica AT2020', 'Audio-Technica', 'Microphones', 99.99, 'Cardioid condenser studio microphone'),
    ('Jabra Evolve2 85', 'Jabra', 'Headphones', 449.99, 'Professional wireless ANC headset'),
    ('Jabra Elite 7 Pro', 'Jabra', 'Earbuds', 199.99, 'MultiSensor Voice true wireless earbuds'),
    ('Anker Soundcore Liberty 4', 'Anker', 'Earbuds', 99.99, 'True wireless earbuds with LDAC'),
    ('Anker Soundcore Motion+', 'Anker', 'Speakers', 79.99, 'Portable speaker with Hi-Res Audio'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample audio products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding audio products...')

        # Create brands
        brand_objs = {}
        for b in BRANDS:
            brand, created = Brand.objects.get_or_create(
                name=b['name'],
                defaults={'logo': b['logo'], 'website': b['website']}
            )
            brand_objs[b['name']] = brand
            if created:
                self.stdout.write(f'  Created brand: {brand.name}')

        # Create categories
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

        # Create products
        created_count = 0
        for i, (name, brand_name, cat_name, base_price, desc) in enumerate(AUDIO_PRODUCTS):
            sku = f'AUDIO-{brand_name[:3].upper()}-{i+1:04d}'
            brand = brand_objs.get(brand_name)
            category = cat_objs.get(cat_name)
            sale = round(base_price * 0.9, 2) if random.random() > 0.6 else None

            specs = {
                'connectivity': random.choice(['Bluetooth 5.0', 'Bluetooth 5.2', 'Wired 3.5mm', 'USB-C', 'Wireless']),
                'battery_life': f'{random.randint(6, 40)}hrs',
                'driver_size': random.choice(['6mm', '8mm', '10mm', '40mm', '50mm']),
                'frequency_response': random.choice(['20Hz-20kHz', '10Hz-22kHz', '4Hz-40kHz']),
                'impedance': random.choice(['16 Ohm', '32 Ohm', '64 Ohm', '150 Ohm', '250 Ohm']),
                'noise_cancelling': random.choice([True, False]),
                'waterproof': random.choice(['IPX4', 'IPX5', 'IP67', 'Not rated']),
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
                    'stock': random.randint(5, 150),
                    'specifications': specs,
                }
            )

            if created:
                created_count += 1
                ProductImage.objects.get_or_create(
                    product=product,
                    image=f'https://placehold.co/800x600?text={brand_name}+Audio',
                    defaults={'is_primary': True, 'alt_text': f'{name} - Main Image'}
                )
                ProductImage.objects.get_or_create(
                    product=product,
                    image=f'https://placehold.co/800x600?text={brand_name}+Side',
                    defaults={'is_primary': False, 'alt_text': f'{name} - Side View'}
                )
                Inventory.objects.get_or_create(
                    product=product,
                    defaults={
                        'quantity': product.stock,
                        'reserved_qty': 0,
                        'low_stock_threshold': 10,
                    }
                )
                Rating.objects.get_or_create(
                    product=product,
                    defaults={
                        'average_rating': round(random.uniform(3.5, 5.0), 2),
                        'total_reviews': random.randint(0, 500),
                    }
                )

        # Generate extra products to reach 50
        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(29.99, 999.99), 2)
            sku = f'AUDIO-EXTRA-{i+1:04d}'
            sale = round(price * 0.85, 2) if random.random() > 0.5 else None

            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': f'{brand.name} Audio Product {i+100}',
                    'brand': brand,
                    'category': cat,
                    'description': f'Premium audio product from {brand.name}',
                    'price': Decimal(str(price)),
                    'sale_price': Decimal(str(sale)) if sale else None,
                    'stock': random.randint(0, 100),
                    'specifications': {
                        'connectivity': random.choice(['Bluetooth 5.0', 'Wired', 'USB-C']),
                        'battery_life': f'{random.randint(6, 30)}hrs',
                        'noise_cancelling': random.choice([True, False]),
                    },
                }
            )
            if created:
                created_count += 1
                ProductImage.objects.create(
                    product=product,
                    image=f'https://placehold.co/800x600?text=Audio+{i+100}',
                    is_primary=True,
                )
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(
                    product=product,
                    defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 200)}
                )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {created_count} new audio products. '
            f'Total: {Product.objects.count()} products.'
        ))
