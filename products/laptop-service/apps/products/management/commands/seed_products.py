"""
Seed command for laptop products.
Creates 50 sample products with brands, categories, images, and inventory.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.products.models import Brand, Category, Product, ProductImage, Inventory, Rating
from decimal import Decimal
import random


BRANDS = [
    {'name': 'Dell', 'logo': 'https://placehold.co/200x100?text=Dell', 'website': 'https://dell.com'},
    {'name': 'HP', 'logo': 'https://placehold.co/200x100?text=HP', 'website': 'https://hp.com'},
    {'name': 'Lenovo', 'logo': 'https://placehold.co/200x100?text=Lenovo', 'website': 'https://lenovo.com'},
    {'name': 'Apple', 'logo': 'https://placehold.co/200x100?text=Apple', 'website': 'https://apple.com'},
    {'name': 'ASUS', 'logo': 'https://placehold.co/200x100?text=ASUS', 'website': 'https://asus.com'},
    {'name': 'Acer', 'logo': 'https://placehold.co/200x100?text=Acer', 'website': 'https://acer.com'},
    {'name': 'MSI', 'logo': 'https://placehold.co/200x100?text=MSI', 'website': 'https://msi.com'},
    {'name': 'Razer', 'logo': 'https://placehold.co/200x100?text=Razer', 'website': 'https://razer.com'},
]

CATEGORIES = [
    {'name': 'Gaming Laptops', 'description': 'High-performance gaming laptops'},
    {'name': 'Business Laptops', 'description': 'Professional business laptops'},
    {'name': 'Ultrabooks', 'description': 'Thin and light ultrabooks'},
    {'name': 'Budget Laptops', 'description': 'Affordable laptops for everyday use'},
    {'name': 'Workstation Laptops', 'description': 'Professional workstation laptops'},
]

LAPTOP_PRODUCTS = [
    ('Dell XPS 15', 'Dell', 'Ultrabooks', 1299.99, '15" OLED, Intel Core i7, 16GB RAM, 512GB SSD'),
    ('Dell Alienware m15', 'Dell', 'Gaming Laptops', 1799.99, 'RTX 3080, Intel Core i9, 32GB RAM'),
    ('HP Spectre x360 14', 'HP', 'Ultrabooks', 1399.99, 'OLED touchscreen, Core i7-1255U, 16GB'),
    ('HP Omen 16', 'HP', 'Gaming Laptops', 1199.99, 'RTX 3060, Ryzen 7 5800H, 16GB RAM'),
    ('Lenovo ThinkPad X1 Carbon', 'Lenovo', 'Business Laptops', 1499.99, 'Intel Core i7, 16GB, 512GB SSD'),
    ('Lenovo Legion 5i', 'Lenovo', 'Gaming Laptops', 999.99, 'RTX 3060, Core i5-12500H, 16GB RAM'),
    ('Apple MacBook Pro 14', 'Apple', 'Ultrabooks', 1999.99, 'M2 Pro chip, 16GB, 512GB SSD'),
    ('Apple MacBook Air M2', 'Apple', 'Ultrabooks', 1299.99, 'M2 chip, 8GB RAM, 256GB SSD'),
    ('ASUS ROG Strix G15', 'ASUS', 'Gaming Laptops', 1299.99, 'RTX 3070, Ryzen 9 5900HX, 32GB'),
    ('ASUS ZenBook 14', 'ASUS', 'Ultrabooks', 849.99, 'OLED, Intel Core i5, 8GB, 512GB SSD'),
    ('Acer Predator Helios 300', 'Acer', 'Gaming Laptops', 1099.99, 'RTX 3060, Core i7, 16GB, 512GB SSD'),
    ('Acer Swift 3', 'Acer', 'Budget Laptops', 549.99, 'AMD Ryzen 5, 8GB, 256GB SSD'),
    ('MSI GE76 Raider', 'MSI', 'Gaming Laptops', 1999.99, 'RTX 3080 Ti, Core i9, 32GB, 1TB SSD'),
    ('MSI Modern 14', 'MSI', 'Business Laptops', 749.99, 'Intel Core i5, 8GB, 512GB SSD'),
    ('Razer Blade 15', 'Razer', 'Gaming Laptops', 1699.99, 'RTX 3070 Ti, Core i7, 16GB, 512GB SSD'),
    ('Dell Vostro 15', 'Dell', 'Budget Laptops', 649.99, 'Intel Core i5, 8GB, 256GB SSD'),
    ('HP EliteBook 840', 'HP', 'Business Laptops', 1149.99, 'Core i7-1165G7, 16GB, 512GB SSD'),
    ('Lenovo IdeaPad 5', 'Lenovo', 'Budget Laptops', 549.99, 'AMD Ryzen 5, 8GB, 256GB SSD'),
    ('ASUS TUF Gaming A15', 'ASUS', 'Gaming Laptops', 899.99, 'RTX 3050, Ryzen 7, 16GB RAM'),
    ('Acer Aspire 5', 'Acer', 'Budget Laptops', 449.99, 'Intel Core i3, 4GB, 256GB SSD'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample laptop products'

    def handle(self, *args, **options):
        self.stdout.write('Seeding laptop products...')

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
        for i, (name, brand_name, cat_name, base_price, desc) in enumerate(LAPTOP_PRODUCTS):
            sku = f'LAPTOP-{brand_name[:3].upper()}-{i+1:04d}'
            brand = brand_objs.get(brand_name)
            category = cat_objs.get(cat_name)
            sale = round(base_price * 0.9, 2) if random.random() > 0.6 else None

            specs = {
                'processor': random.choice(['Intel Core i5', 'Intel Core i7', 'Intel Core i9', 'AMD Ryzen 5', 'AMD Ryzen 7', 'Apple M2']),
                'ram': random.choice(['8GB', '16GB', '32GB', '64GB']),
                'storage': random.choice(['256GB SSD', '512GB SSD', '1TB SSD', '2TB SSD']),
                'display': random.choice(['13.3"', '14"', '15.6"', '16"', '17.3"']),
                'os': random.choice(['Windows 11', 'macOS', 'FreeDOS']),
                'battery': f'{random.randint(50, 99)}Wh',
                'weight': f'{round(random.uniform(1.2, 3.5), 1)}kg',
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
                    'stock': random.randint(5, 100),
                    'specifications': specs,
                }
            )

            if created:
                created_count += 1
                # Add images
                ProductImage.objects.get_or_create(
                    product=product,
                    image=f'https://placehold.co/800x600?text={brand_name}+Laptop',
                    defaults={'is_primary': True, 'alt_text': f'{name} - Main Image'}
                )
                ProductImage.objects.get_or_create(
                    product=product,
                    image=f'https://placehold.co/800x600?text={brand_name}+Side',
                    defaults={'is_primary': False, 'alt_text': f'{name} - Side View'}
                )

                # Create inventory
                Inventory.objects.get_or_create(
                    product=product,
                    defaults={
                        'quantity': product.stock,
                        'reserved_qty': 0,
                        'low_stock_threshold': 10,
                    }
                )

                # Create rating
                Rating.objects.get_or_create(
                    product=product,
                    defaults={
                        'average_rating': round(random.uniform(3.5, 5.0), 2),
                        'total_reviews': random.randint(0, 200),
                    }
                )

        # Generate extra products to reach 50
        extra_needed = max(0, 50 - Product.objects.count())
        for i in range(extra_needed):
            brand = random.choice(list(brand_objs.values()))
            cat = random.choice(list(cat_objs.values()))
            price = round(random.uniform(399.99, 2499.99), 2)
            sku = f'LAPTOP-EXTRA-{i+1:04d}'
            sale = round(price * 0.85, 2) if random.random() > 0.5 else None

            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': f'{brand.name} Laptop Model {i+100}',
                    'brand': brand,
                    'category': cat,
                    'description': f'High-quality laptop from {brand.name}',
                    'price': Decimal(str(price)),
                    'sale_price': Decimal(str(sale)) if sale else None,
                    'stock': random.randint(0, 50),
                    'specifications': {
                        'ram': random.choice(['8GB', '16GB', '32GB']),
                        'storage': random.choice(['256GB SSD', '512GB SSD', '1TB SSD']),
                        'display': random.choice(['14"', '15.6"', '16"']),
                    },
                }
            )
            if created:
                created_count += 1
                ProductImage.objects.create(
                    product=product,
                    image=f'https://placehold.co/800x600?text=Laptop+{i+100}',
                    is_primary=True,
                )
                Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
                Rating.objects.get_or_create(
                    product=product,
                    defaults={'average_rating': round(random.uniform(3.0, 5.0), 2), 'total_reviews': random.randint(0, 100)}
                )

        self.stdout.write(self.style.SUCCESS(
            f'Successfully seeded {created_count} new laptop products. '
            f'Total: {Product.objects.count()} products.'
        ))
