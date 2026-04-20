from django.contrib import admin
from .models import Payment, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'user_id', 'method', 'status', 'amount', 'currency', 'created_at')
    list_filter = ('status', 'method', 'currency')
    search_fields = ('order_id', 'user_id', 'gateway_ref')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TransactionInline]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment', 'type', 'amount', 'status', 'created_at')
    list_filter = ('type', 'status')
    readonly_fields = ('created_at',)
