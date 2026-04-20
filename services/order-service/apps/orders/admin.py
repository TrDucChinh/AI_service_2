from django.contrib import admin
from .models import Order, OrderItem, OrderStatusLog


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ('changed_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'status', 'total_amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('user_id',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline, OrderStatusLogInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product_id', 'product_service', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('product_service',)


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'old_status', 'new_status', 'changed_by', 'changed_at')
    list_filter = ('new_status',)
    readonly_fields = ('changed_at',)
