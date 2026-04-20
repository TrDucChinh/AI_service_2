from django.core.management.base import BaseCommand
from apps.authentication.models import Role, Permission, RolePermission


ROLES = [
    {'name': 'admin', 'description': 'Full system access'},
    {'name': 'staff', 'description': 'Inventory and order management'},
    {'name': 'customer', 'description': 'Standard shopping access'},
]

PERMISSIONS = [
    ('View Products', 'products.view'),
    ('Create Products', 'products.create'),
    ('Update Products', 'products.update'),
    ('Delete Products', 'products.delete'),
    ('View Orders', 'orders.view'),
    ('Update Orders', 'orders.update'),
    ('Cancel Orders', 'orders.cancel'),
    ('View Users', 'users.view'),
    ('Manage Users', 'users.manage'),
    ('Manage Roles', 'roles.manage'),
    ('View Analytics', 'analytics.view'),
]

ROLE_PERMISSIONS = {
    'admin': [p[1] for p in PERMISSIONS],
    'staff': [
        'products.view', 'products.create', 'products.update',
        'orders.view', 'orders.update', 'orders.cancel',
        'users.view', 'analytics.view',
    ],
    'customer': [
        'products.view', 'orders.view', 'orders.cancel',
    ],
}


class Command(BaseCommand):
    help = 'Seed default roles and permissions'

    def handle(self, *args, **options):
        perms = {}
        for name, codename in PERMISSIONS:
            perm, _ = Permission.objects.get_or_create(codename=codename, defaults={'name': name})
            perms[codename] = perm
            self.stdout.write(f'  Permission: {codename}')

        for role_data in ROLES:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']},
            )
            action = 'Created' if created else 'Exists'
            self.stdout.write(f'  Role [{action}]: {role.name}')

            for codename in ROLE_PERMISSIONS.get(role.name, []):
                perm = perms.get(codename)
                if perm:
                    RolePermission.objects.get_or_create(role=role, permission=perm)

        self.stdout.write(self.style.SUCCESS('Default roles and permissions seeded successfully.'))
