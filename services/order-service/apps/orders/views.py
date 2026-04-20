from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Order, OrderItem, OrderStatusLog
from .serializers import OrderSerializer, CreateOrderSerializer


class OrderAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user_id = request.META.get('HTTP_X_USER_ID')
        user_role = request.META.get('HTTP_X_USER_ROLE')
        if user_id and user_role:
            return (OrderGatewayUser(user_id, user_role), None)
        return super().authenticate(request)


class OrderGatewayUser:
    def __init__(self, user_id, role):
        self.id = int(user_id)
        self.pk = self.id
        self.role_name = role
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return f"GatewayUser(id={self.id}, role={self.role_name})"


def get_user_id(request):
    user_id = request.META.get('HTTP_X_USER_ID')
    if user_id:
        return int(user_id)
    if hasattr(request.user, 'id') and request.user.id:
        return request.user.id
    return None


class OrderListCreateView(APIView):
    authentication_classes = [OrderAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = get_user_id(request)
        user_role = getattr(request.user, 'role_name', 'customer')

        # Admin/staff can see all orders, customers only their own
        if user_role in ('admin', 'staff'):
            orders = Order.objects.all()
            # Filter by user if provided
            filter_user_id = request.query_params.get('user_id')
            if filter_user_id:
                orders = orders.filter(user_id=filter_user_id)
        else:
            orders = Order.objects.filter(user_id=user_id)

        # Filter by status
        filter_status = request.query_params.get('status')
        if filter_status:
            orders = orders.filter(status=filter_status.upper())

        serializer = OrderSerializer(orders, many=True)
        return Response({
            'count': orders.count(),
            'results': serializer.data
        })

    def post(self, request):
        user_id = get_user_id(request)
        if not user_id:
            return Response({'error': 'User ID not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        items_data = data['items']

        # Calculate total
        total_amount = sum(
            Decimal(str(item['unit_price'])) * int(item['quantity'])
            for item in items_data
        )

        # Create order
        order = Order.objects.create(
            user_id=user_id,
            status='PENDING',
            total_amount=total_amount,
            shipping_address=data['shipping_address'],
            billing_address=data.get('billing_address', {}),
            notes=data.get('notes', ''),
        )

        # Create order items
        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                product_service=item['product_service'],
                product_name=item['product_name'],
                product_sku=item.get('product_sku', ''),
                product_image=item.get('product_image', ''),
                quantity=int(item['quantity']),
                unit_price=Decimal(str(item['unit_price'])),
                subtotal=Decimal(str(item['unit_price'])) * int(item['quantity']),
            )

        # Log status
        OrderStatusLog.objects.create(
            order=order,
            old_status='',
            new_status='PENDING',
            changed_by=user_id,
            note='Order created.',
        )

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    authentication_classes = [OrderAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        user_id = get_user_id(request)
        user_role = getattr(request.user, 'role_name', 'customer')

        if user_role in ('admin', 'staff'):
            order = get_object_or_404(Order, id=order_id)
        else:
            order = get_object_or_404(Order, id=order_id, user_id=user_id)

        return Response(OrderSerializer(order).data)


class OrderCancelView(APIView):
    authentication_classes = [OrderAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user_id = get_user_id(request)
        user_role = getattr(request.user, 'role_name', 'customer')

        if user_role in ('admin', 'staff'):
            order = get_object_or_404(Order, id=order_id)
        else:
            order = get_object_or_404(Order, id=order_id, user_id=user_id)

        if not order.can_cancel():
            return Response(
                {'error': f'Cannot cancel order in status {order.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = order.status
        order.status = 'CANCELLED'
        order.save()

        OrderStatusLog.objects.create(
            order=order,
            old_status=old_status,
            new_status='CANCELLED',
            changed_by=user_id,
            note=request.data.get('reason', 'Order cancelled by user.'),
        )

        return Response({'message': 'Order cancelled.', 'order': OrderSerializer(order).data})


class OrderStatusUpdateView(APIView):
    """Admin/staff endpoint to update order status."""
    authentication_classes = [OrderAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user_id = get_user_id(request)
        user_role = getattr(request.user, 'role_name', 'customer')

        if user_role not in ('admin', 'staff'):
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, id=order_id)
        new_status = request.data.get('status', '').upper()

        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Invalid status. Choices: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = order.status
        order.status = new_status
        order.save()

        OrderStatusLog.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=user_id,
            note=request.data.get('note', ''),
        )

        return Response(OrderSerializer(order).data)
