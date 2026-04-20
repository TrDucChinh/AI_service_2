from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, AddItemSerializer, UpdateItemSerializer


def get_user_id(request):
    """Extract user ID from request headers or JWT."""
    user_id = request.META.get('HTTP_X_USER_ID')
    if user_id:
        return int(user_id)
    if hasattr(request.user, 'id') and request.user.id:
        return request.user.id
    return None


class CartAuthentication(JWTAuthentication):
    def authenticate(self, request):
        user_id = request.META.get('HTTP_X_USER_ID')
        user_role = request.META.get('HTTP_X_USER_ROLE')
        if user_id and user_role:
            return (CartGatewayUser(user_id, user_role), None)
        return super().authenticate(request)


class CartGatewayUser:
    def __init__(self, user_id, role):
        self.id = int(user_id)
        self.pk = self.id
        self.role_name = role
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return f"GatewayUser(id={self.id})"


class CartView(APIView):
    authentication_classes = [CartAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = get_user_id(request)
        if not user_id:
            return Response({'error': 'User ID not found.'}, status=status.HTTP_401_UNAUTHORIZED)
        cart, _ = Cart.objects.get_or_create(user_id=user_id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemView(APIView):
    authentication_classes = [CartAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = get_user_id(request)
        if not user_id:
            return Response({'error': 'User ID not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = AddItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        cart, _ = Cart.objects.get_or_create(user_id=user_id)

        # Check if item already exists
        existing = CartItem.objects.filter(
            cart=cart,
            product_id=data['product_id'],
            product_service=data['product_service']
        ).first()

        if existing:
            existing.quantity += data['quantity']
            existing.price = data['price']
            if data.get('product_name'):
                existing.product_name = data['product_name']
            if data.get('product_image'):
                existing.product_image = data['product_image']
            existing.save()
            return Response(CartItemSerializer(existing).data, status=status.HTTP_200_OK)

        item = CartItem.objects.create(
            cart=cart,
            product_id=data['product_id'],
            product_service=data['product_service'],
            product_name=data.get('product_name', ''),
            product_sku=data.get('product_sku', ''),
            product_image=data.get('product_image', ''),
            quantity=data['quantity'],
            price=data['price'],
        )
        return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    authentication_classes = [CartAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, item_id):
        user_id = get_user_id(request)
        if not user_id:
            return Response({'error': 'User ID not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        cart = get_object_or_404(Cart, user_id=user_id)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)

        serializer = UpdateItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        item.quantity = serializer.validated_data['quantity']
        item.save()
        return Response(CartItemSerializer(item).data)

    def delete(self, request, item_id):
        user_id = get_user_id(request)
        if not user_id:
            return Response({'error': 'User ID not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        cart = get_object_or_404(Cart, user_id=user_id)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    authentication_classes = [CartAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user_id = get_user_id(request)
        if not user_id:
            return Response({'error': 'User ID not found.'}, status=status.HTTP_401_UNAUTHORIZED)

        cart = get_object_or_404(Cart, user_id=user_id)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared successfully.'}, status=status.HTTP_200_OK)
