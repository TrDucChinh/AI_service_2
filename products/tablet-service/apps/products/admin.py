from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Inventory, Review, Rating


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class InventoryInline(admin.StackedInline):
    model = Inventory
    extra = 0


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'website', 'created_at')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'sku', 'price', 'stock', 'is_active')
    list_filter = ('is_active', 'brand', 'category')
    search_fields = ('name', 'sku')
    inlines = [ProductImageInline, InventoryInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user_id', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
