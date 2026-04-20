from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'HP', 'logo': 'https://placehold.co/200x100?text=HP', 'website': 'https://hp.com'},
    {'name': 'Canon', 'logo': 'https://placehold.co/200x100?text=Canon', 'website': 'https://canon.com'},
    {'name': 'Epson', 'logo': 'https://placehold.co/200x100?text=Epson', 'website': 'https://epson.com'},
    {'name': 'Brother', 'logo': 'https://placehold.co/200x100?text=Brother', 'website': 'https://brother.com'},
]

CATEGORIES = [
    {'name': 'Inkjet Printers', 'description': 'Color inkjet printers'},
    {'name': 'Laser Printers', 'description': 'Monochrome and color laser printers'},
    {'name': 'All-in-One Printers', 'description': 'Print, scan, and copy'},
    {'name': 'Photo Printers', 'description': 'High-quality photo printing'},
    {'name': 'Label Printers', 'description': 'Label and barcode printers'},
]

PRODUCTS = [
    ('HP OfficeJet Pro 9015e', 'HP', 'All-in-One Printers', 229.99, 'Wireless, auto 2-sided, 22ppm'),
    ('HP LaserJet Pro M404dn', 'HP', 'Laser Printers', 279.99, 'Monochrome, 40ppm, duplex'),
    ('HP ENVY Photo 7855', 'HP', 'Photo Printers', 179.99, 'Wireless, 6-color, 4800x1200dpi'),
    ('Canon PIXMA TR8620a', 'Canon', 'All-in-One Printers', 149.99, 'Wireless, 15ipm color, ADF'),
    ('Canon imageCLASS MF743Cdw', 'Canon', 'Laser Printers', 499.99, 'Color laser, AIO, 40ppm'),
    ('Canon PIXMA TS9521C', 'Canon', 'Photo Printers', 149.99, 'Wireless, 5-ink, crafting friendly'),
    ('Epson EcoTank ET-4850', 'Epson', 'All-in-One Printers', 349.99, 'Supertank, wireless, cartridge-free'),
    ('Epson WorkForce WF-7820', 'Epson', 'Inkjet Printers', 249.99, 'Wide-format, wireless, 13x19'),
    ('Brother HL-L8260CDW', 'Brother', 'Laser Printers', 349.99, 'Color laser, 33ppm, duplex'),
    ('Brother MFC-J995DW', 'Brother', 'All-in-One Printers', 199.99, 'INKvestment Tank, wireless, ADF'),
    ('HP Color LaserJet Pro M479fdw', 'HP', 'Laser Printers', 549.99, 'Color laser AIO, 28ppm, fax'),
    ('Epson SureColor P700', 'Epson', 'Photo Printers', 799.99, '13-inch, 10-color, UltraChrome Pro'),
]


class Command(BaseCommand):
    help = 'Seed printer products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding printer products...')
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
            sku = f'PRNT-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(5, 50),
                'specifications': {'type': random.choice(['Inkjet', 'Laser', 'Thermal']), 'connectivity': random.choice(['USB', 'Wireless', 'Ethernet']), 'speed_ppm': random.randint(10, 40), 'duplex': random.choice([True, False])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Printer', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 5})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 150)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(79.99, 799.99), 2)
            sku = f'PRNT-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Printer {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 40),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Printer+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} printer products. Total: {Product.objects.count()}'))
