from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = (
            'id', 'cart', 'product_id', 'product_service', 'product_name',
            'product_sku', 'product_image', 'quantity', 'price',
            'subtotal', 'added_at', 'updated_at'
        )
        read_only_fields = ('id', 'cart', 'added_at', 'updated_at', 'subtotal')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ('id', 'user_id', 'items', 'total', 'item_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user_id', 'created_at', 'updated_at')


class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    product_service = serializers.CharField(max_length=50, required=True)
    product_name = serializers.CharField(max_length=255, required=False, default='')
    product_sku = serializers.CharField(max_length=100, required=False, default='')
    product_image = serializers.URLField(required=False, default='')
    quantity = serializers.IntegerField(min_value=1, default=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)


class UpdateItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=True)
