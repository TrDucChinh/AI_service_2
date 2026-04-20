from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusLog


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            'id', 'product_id', 'product_service', 'product_name',
            'product_sku', 'product_image', 'quantity', 'unit_price', 'subtotal'
        )
        read_only_fields = ('id', 'subtotal')


class OrderStatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusLog
        fields = ('id', 'old_status', 'new_status', 'changed_by', 'changed_at', 'note')
        read_only_fields = ('id', 'changed_at')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'user_id', 'status', 'status_display', 'total_amount',
            'shipping_address', 'billing_address', 'notes',
            'items', 'status_logs', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user_id', 'created_at', 'updated_at', 'status_display')


class CreateOrderSerializer(serializers.Serializer):
    items = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    shipping_address = serializers.DictField(required=True)
    billing_address = serializers.DictField(required=False, default=dict)
    notes = serializers.CharField(required=False, default='')

    def validate_items(self, items):
        for item in items:
            required = ['product_id', 'product_service', 'product_name', 'quantity', 'unit_price']
            for field in required:
                if field not in item:
                    raise serializers.ValidationError(f"Item missing required field: {field}")
            if int(item.get('quantity', 0)) < 1:
                raise serializers.ValidationError("Item quantity must be at least 1.")
            if float(item.get('unit_price', 0)) <= 0:
                raise serializers.ValidationError("Item unit_price must be positive.")
        return items
