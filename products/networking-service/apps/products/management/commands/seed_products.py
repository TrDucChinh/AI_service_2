from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'TP-Link', 'logo': 'https://placehold.co/200x100?text=TP-Link', 'website': 'https://tp-link.com'},
    {'name': 'ASUS', 'logo': 'https://placehold.co/200x100?text=ASUS', 'website': 'https://asus.com'},
    {'name': 'Netgear', 'logo': 'https://placehold.co/200x100?text=Netgear', 'website': 'https://netgear.com'},
    {'name': 'Ubiquiti', 'logo': 'https://placehold.co/200x100?text=Ubiquiti', 'website': 'https://ui.com'},
    {'name': 'Cisco', 'logo': 'https://placehold.co/200x100?text=Cisco', 'website': 'https://cisco.com'},
]

CATEGORIES = [
    {'name': 'Routers', 'description': 'WiFi and wired routers'},
    {'name': 'Switches', 'description': 'Network switches'},
    {'name': 'Access Points', 'description': 'Wireless access points'},
    {'name': 'Network Adapters', 'description': 'USB and PCIe network adapters'},
    {'name': 'Modems', 'description': 'Cable and DSL modems'},
]

PRODUCTS = [
    ('TP-Link Archer AXE75', 'TP-Link', 'Routers', 129.99, 'WiFi 6E, Tri-band, 6600Mbps'),
    ('TP-Link Deco XE75 Pro', 'TP-Link', 'Routers', 299.99, 'WiFi 6E Mesh, 3-pack, 5400Mbps'),
    ('ASUS RT-AXE7800', 'ASUS', 'Routers', 349.99, 'WiFi 6E, Tri-band, AiMesh'),
    ('ASUS ZenWiFi Pro ET12', 'ASUS', 'Access Points', 499.99, 'WiFi 6E Mesh, 2-pack, 11000Mbps'),
    ('Netgear Nighthawk AX12', 'Netgear', 'Routers', 399.99, 'WiFi 6, 12-stream, 10.8Gbps'),
    ('Netgear Orbi RBK863S', 'Netgear', 'Routers', 699.99, 'WiFi 6 Mesh, 3-pack, 6Gbps'),
    ('Ubiquiti UniFi Dream Machine', 'Ubiquiti', 'Routers', 379.99, 'UniFi OS, 4-port, 1Gbps'),
    ('Ubiquiti UniFi AP U6 Pro', 'Ubiquiti', 'Access Points', 199.99, 'WiFi 6, 2.4/5GHz, 4.8Gbps'),
    ('Cisco SG350-10', 'Cisco', 'Switches', 299.99, '10-port Gigabit managed switch'),
    ('TP-Link TL-SG108E', 'TP-Link', 'Switches', 39.99, '8-port Gigabit easy smart switch'),
    ('Netgear GS308E', 'Netgear', 'Switches', 44.99, '8-port Gigabit Plus switch'),
    ('TP-Link Archer T3U Plus', 'TP-Link', 'Network Adapters', 29.99, 'USB WiFi 6 adapter, AC1300'),
]


class Command(BaseCommand):
    help = 'Seed networking products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding networking products...')
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
            sku = f'NET-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(10, 100),
                'specifications': {'wifi_standard': random.choice(['WiFi 5', 'WiFi 6', 'WiFi 6E']), 'ports': random.randint(4, 16), 'speed': random.choice(['1Gbps', '2.5Gbps', '10Gbps'])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Network', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 10})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 200)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(19.99, 499.99), 2)
            sku = f'NET-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Networking {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 80),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Network+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} networking products. Total: {Product.objects.count()}'))
