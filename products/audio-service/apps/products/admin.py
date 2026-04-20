from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Inventory, Review, Rating


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('created_at',)


class InventoryInline(admin.StackedInline):
    model = Inventory
    extra = 0
    readonly_fields = ('last_updated',)


class RatingInline(admin.StackedInline):
    model = Rating
    extra = 0
    readonly_fields = ('average_rating', 'total_reviews', 'updated_at')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'website', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent', 'slug', 'created_at')
    search_fields = ('name', 'slug')
    list_filter = ('parent',)
    readonly_fields = ('created_at',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'sku', 'price', 'sale_price', 'stock', 'is_active', 'created_at')
    list_filter = ('is_active', 'brand', 'category')
    search_fields = ('name', 'sku', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, InventoryInline, RatingInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user_id', 'rating', 'is_verified', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified', 'is_approved')
    search_fields = ('product__name', 'user_id', 'title')
    readonly_fields = ('created_at',)
