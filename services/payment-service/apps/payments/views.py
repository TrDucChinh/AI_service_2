import uuid
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Payment, Transaction
from .serializers import (
    PaymentSerializer, InitiatePaymentSerializer,
    ConfirmPaymentSerializer, RefundSerializer
)


class PaymentAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user_id = request.META.get('HTTP_X_USER_ID')
        user_role = request.META.get('HTTP_X_USER_ROLE')
        if user_id and user_role:
            return (PaymentGatewayUser(user_id, user_role), None)
        return super().authenticate(request)


class PaymentGatewayUser:
    def __init__(self, user_id, role):
        self.id = int(user_id)
        self.pk = self.id
        self.role_name = role
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return f"GatewayUser(id={self.id})"


def get_user_id(request):
    user_id = request.META.get('HTTP_X_USER_ID')
    if user_id:
        return int(user_id)
    if hasattr(request.user, 'id') and request.user.id:
        return request.user.id
    return None


def mock_payment_processor(method, amount, card_data=None):
    """
    Mock payment processor.
    - CREDIT_CARD: always succeeds
    - COD: always succeeds (pay on delivery)
    - BANK_TRANSFER: returns pending until confirmed
    """
    if method == 'CREDIT_CARD':
        return {
            'success': True,
            'gateway_ref': f'CC-{uuid.uuid4().hex[:12].upper()}',
            'status': 'COMPLETED',
            'message': 'Payment processed successfully.',
        }
    elif method == 'COD':
        return {
            'success': True,
            'gateway_ref': f'COD-{uuid.uuid4().hex[:12].upper()}',
            'status': 'PENDING',
            'message': 'Cash on delivery order created.',
        }
    elif method == 'BANK_TRANSFER':
        return {
            'success': True,
            'gateway_ref': f'BT-{uuid.uuid4().hex[:12].upper()}',
            'status': 'PENDING',
            'message': 'Bank transfer initiated. Awaiting confirmation.',
        }
    return {'success': False, 'message': 'Unknown payment method.'}


class InitiatePaymentView(APIView):
    authentication_classes = [PaymentAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = get_user_id(request)
        if not user_id:
            return Response({'error': 'User ID not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        order_id = data['order_id']

        # Check if payment already exists for this order
        if Payment.objects.filter(order_id=order_id).exists():
            return Response(
                {'error': 'Payment already exists for this order.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process payment via mock processor
        card_data = {
            'number': data.get('card_number', ''),
            'holder': data.get('card_holder', ''),
            'expiry': data.get('card_expiry', ''),
        }
        result = mock_payment_processor(data['method'], data['amount'], card_data)

        payment = Payment.objects.create(
            order_id=order_id,
            user_id=user_id,
            method=data['method'],
            status=result['status'],
            amount=data['amount'],
            currency=data.get('currency', 'USD'),
            gateway_ref=result.get('gateway_ref', ''),
            gateway_response=result,
        )

        Transaction.objects.create(
            payment=payment,
            type='CHARGE',
            amount=data['amount'],
            status='SUCCESS' if result['success'] else 'FAILED',
            gateway_transaction_id=result.get('gateway_ref', ''),
            metadata=result,
        )

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentDetailView(APIView):
    authentication_classes = [PaymentAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        user_id = get_user_id(request)
        user_role = getattr(request.user, 'role_name', 'customer')

        if user_role in ('admin', 'staff'):
            payment = get_object_or_404(Payment, id=payment_id)
        else:
            payment = get_object_or_404(Payment, id=payment_id, user_id=user_id)

        return Response(PaymentSerializer(payment).data)


class ConfirmPaymentView(APIView):
    authentication_classes = [PaymentAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        user_id = get_user_id(request)
        user_role = getattr(request.user, 'role_name', 'customer')

        if user_role in ('admin', 'staff'):
            payment = get_object_or_404(Payment, id=payment_id)
        else:
            payment = get_object_or_404(Payment, id=payment_id, user_id=user_id)

        if payment.status != 'PENDING':
            return Response(
                {'error': f'Payment cannot be confirmed from status {payment.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = 'COMPLETED'
        payment.save()

        Transaction.objects.create(
            payment=payment,
            type='CHARGE',
            amount=payment.amount,
            status='SUCCESS',
            gateway_transaction_id=f'CONFIRM-{payment.gateway_ref}',
            metadata={'confirmed_by': user_id},
        )

        return Response(PaymentSerializer(payment).data)


class RefundPaymentView(APIView):
    authentication_classes = [PaymentAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, payment_id):
        user_id = get_user_id(request)
        user_role = getattr(request.user, 'role_name', 'customer')

        if user_role in ('admin', 'staff'):
            payment = get_object_or_404(Payment, id=payment_id)
        else:
            payment = get_object_or_404(Payment, id=payment_id, user_id=user_id)

        if payment.status != 'COMPLETED':
            return Response(
                {'error': 'Only completed payments can be refunded.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RefundSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        refund_amount = serializer.validated_data.get('amount', payment.amount)
        reason = serializer.validated_data.get('reason', 'Customer requested refund')

        if refund_amount > payment.amount:
            return Response(
                {'error': 'Refund amount cannot exceed original payment amount.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment.status = 'REFUNDED'
        payment.save()

        Transaction.objects.create(
            payment=payment,
            type='REFUND' if refund_amount == payment.amount else 'PARTIAL_REFUND',
            amount=refund_amount,
            status='SUCCESS',
            gateway_transaction_id=f'REFUND-{uuid.uuid4().hex[:10].upper()}',
            metadata={'reason': reason, 'initiated_by': user_id},
        )

        return Response({
            'message': 'Refund processed successfully.',
            'refund_amount': str(refund_amount),
            'payment': PaymentSerializer(payment).data,
        })
