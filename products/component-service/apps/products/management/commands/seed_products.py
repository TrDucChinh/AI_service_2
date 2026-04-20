from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random

BRANDS = [
    {'name': 'Intel', 'logo': 'https://placehold.co/200x100?text=Intel', 'website': 'https://intel.com'},
    {'name': 'AMD', 'logo': 'https://placehold.co/200x100?text=AMD', 'website': 'https://amd.com'},
    {'name': 'NVIDIA', 'logo': 'https://placehold.co/200x100?text=NVIDIA', 'website': 'https://nvidia.com'},
    {'name': 'Corsair', 'logo': 'https://placehold.co/200x100?text=Corsair', 'website': 'https://corsair.com'},
    {'name': 'ASUS', 'logo': 'https://placehold.co/200x100?text=ASUS', 'website': 'https://asus.com'},
    {'name': 'EVGA', 'logo': 'https://placehold.co/200x100?text=EVGA', 'website': 'https://evga.com'},
]

CATEGORIES = [
    {'name': 'CPUs', 'description': 'Processors and CPUs'},
    {'name': 'GPUs', 'description': 'Graphics cards and GPUs'},
    {'name': 'RAM', 'description': 'Memory modules'},
    {'name': 'Motherboards', 'description': 'Motherboards and mainboards'},
    {'name': 'PSUs', 'description': 'Power supply units'},
    {'name': 'CPU Coolers', 'description': 'Air and liquid CPU coolers'},
]

PRODUCTS = [
    ('Intel Core i9-14900K', 'Intel', 'CPUs', 589.99, '24 cores, 6GHz boost, LGA1700'),
    ('Intel Core i7-14700K', 'Intel', 'CPUs', 409.99, '20 cores, 5.6GHz boost, LGA1700'),
    ('AMD Ryzen 9 7950X', 'AMD', 'CPUs', 699.99, '16 cores, 5.7GHz boost, AM5'),
    ('AMD Ryzen 7 7700X', 'AMD', 'CPUs', 299.99, '8 cores, 5.4GHz boost, AM5'),
    ('NVIDIA RTX 4090', 'NVIDIA', 'GPUs', 1599.99, '24GB GDDR6X, 16384 CUDA cores'),
    ('NVIDIA RTX 4070 Ti', 'NVIDIA', 'GPUs', 799.99, '12GB GDDR6X, 7680 CUDA cores'),
    ('AMD RX 7900 XTX', 'AMD', 'GPUs', 999.99, '24GB GDDR6, 6144 stream processors'),
    ('Corsair Vengeance 32GB DDR5', 'Corsair', 'RAM', 99.99, 'DDR5-5200, 2x16GB, CL40'),
    ('Corsair Vengeance 32GB DDR4', 'Corsair', 'RAM', 64.99, 'DDR4-3200, 2x16GB, CL16'),
    ('ASUS ROG Strix Z790-E', 'ASUS', 'Motherboards', 499.99, 'LGA1700, DDR5, PCIe 5.0'),
    ('Corsair RM1000x 1000W', 'Corsair', 'PSUs', 199.99, '80+ Gold, fully modular'),
    ('Corsair H150i Elite 360mm', 'Corsair', 'CPU Coolers', 179.99, '360mm AIO, RGB, iCUE'),
]


class Command(BaseCommand):
    help = 'Seed PC component products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding component products...')
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
            sku = f'COMP-{brand_name[:3].upper()}-{i+1:04d}'
            sale = round(price * 0.9, 2) if random.random() > 0.6 else None
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name, 'brand': brand_objs.get(brand_name), 'category': cat_objs.get(cat_name),
                'description': desc, 'price': Decimal(str(price)),
                'sale_price': Decimal(str(sale)) if sale else None,
                'stock': random.randint(5, 80),
                'specifications': {'socket': random.choice(['LGA1700', 'AM5', 'AM4', 'N/A']), 'tdp': f'{random.randint(65, 350)}W', 'generation': random.choice(['Gen 4', 'Gen 5', 'DDR5', 'DDR4'])},
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text={brand_name}+Component', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock, 'low_stock_threshold': 5})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(4.0, 5.0), 2), 'total_reviews': random.randint(0, 300)})

        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(49.99, 999.99), 2)
            sku = f'COMP-EXTRA-{i+1:04d}'
            product, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': f'{brand.name} Component {i+100}', 'brand': brand, 'category': cat,
                'price': Decimal(str(price)), 'stock': random.randint(0, 50),
            })
            if created:
                created_count += 1
                ProductImage.objects.create(product=product, image=f'https://placehold.co/800x600?text=Component+{i+100}', is_primary=True)
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(product=product, defaults={'average_rating': round(random.uniform(3.5, 5.0), 2), 'total_reviews': random.randint(0, 200)})

        self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} component products. Total: {Product.objects.count()}'))
