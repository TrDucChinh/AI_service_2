from rest_framework import serializers
from .models import Brand, Category, Product, ProductImage, Inventory, Review, Rating


class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo', 'description', 'website', 'product_count', 'created_at')
        read_only_fields = ('id', 'created_at', 'product_count')

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'description', 'image', 'slug', 'children', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_children(self, obj):
        children = obj.children.all()
        return CategorySerializer(children, many=True).data if children.exists() else []


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'is_primary', 'alt_text', 'created_at')
        read_only_fields = ('id', 'created_at')


class InventorySerializer(serializers.ModelSerializer):
    available_qty = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Inventory
        fields = ('id', 'quantity', 'reserved_qty', 'available_qty', 'low_stock_threshold', 'is_low_stock', 'last_updated')
        read_only_fields = ('id', 'last_updated', 'available_qty', 'is_low_stock')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('average_rating', 'total_reviews', 'updated_at')
        read_only_fields = ('average_rating', 'total_reviews', 'updated_at')


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            'id', 'product', 'user_id', 'user_name', 'rating',
            'title', 'body', 'is_verified', 'is_approved', 'created_at'
        )
        read_only_fields = ('id', 'is_verified', 'is_approved', 'created_at')


class ProductListSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    current_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    primary_image = serializers.CharField(read_only=True)
    rating = RatingSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'brand', 'brand_name', 'category', 'category_name',
            'sku', 'price', 'sale_price', 'current_price', 'is_on_sale',
            'stock', 'is_active', 'primary_image', 'rating', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ProductDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    inventory = InventorySerializer(read_only=True)
    rating = RatingSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True, source='reviews.all')
    current_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'brand', 'category', 'sku', 'description',
            'price', 'sale_price', 'current_price', 'is_on_sale',
            'stock', 'is_active', 'specifications', 'images',
            'inventory', 'rating', 'reviews', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'name', 'brand', 'category', 'sku', 'description',
            'price', 'sale_price', 'stock', 'is_active', 'specifications'
        )
        read_only_fields = ('id',)
