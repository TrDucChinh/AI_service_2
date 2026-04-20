from rest_framework import serializers
from .models import Payment, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'type', 'amount', 'status', 'gateway_transaction_id', 'metadata', 'created_at')
        read_only_fields = ('id', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'order_id', 'user_id', 'method', 'method_display',
            'status', 'status_display', 'amount', 'currency',
            'gateway_ref', 'transactions', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'user_id', 'status', 'gateway_ref', 'created_at', 'updated_at')


class InitiatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    method = serializers.ChoiceField(choices=['CREDIT_CARD', 'COD', 'BANK_TRANSFER'])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=3, default='USD')
    card_number = serializers.CharField(max_length=20, required=False, write_only=True)
    card_holder = serializers.CharField(max_length=100, required=False, write_only=True)
    card_expiry = serializers.CharField(max_length=10, required=False, write_only=True)
    card_cvv = serializers.CharField(max_length=4, required=False, write_only=True)


class ConfirmPaymentSerializer(serializers.Serializer):
    confirmation_code = serializers.CharField(required=False)


class RefundSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False)
    reason = serializers.CharField(required=False, default='Customer requested refund')
