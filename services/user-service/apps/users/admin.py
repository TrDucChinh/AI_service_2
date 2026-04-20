from django.contrib import admin
from .models import Profile, Address, Wishlist


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'first_name', 'last_name', 'phone', 'created_at')
    search_fields = ('user_id', 'first_name', 'last_name', 'phone')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'label', 'street', 'city', 'country', 'is_default')
    list_filter = ('is_default', 'country')
    search_fields = ('user_id', 'street', 'city')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'product_id', 'product_service', 'added_at')
    list_filter = ('product_service',)
