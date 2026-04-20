from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Profile, Address, Wishlist
from .serializers import ProfileSerializer, AddressSerializer, WishlistSerializer


def get_user_id(request):
    """Extract user ID from request (set by gateway or JWT)."""
    if hasattr(request.user, 'id') and request.user.id:
        return request.user.id
    user_id = request.META.get('HTTP_X_USER_ID')
    return int(user_id) if user_id else None


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = get_user_id(request)
        profile, _ = Profile.objects.get_or_create(user_id=user_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        user_id = get_user_id(request)
        profile, _ = Profile.objects.get_or_create(user_id=user_id)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = get_user_id(request)
        addresses = Address.objects.filter(user_id=user_id).order_by('-is_default', '-created_at')
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        user_id = get_user_id(request)
        data = request.data.copy()
        data['user_id'] = user_id
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user_id = get_user_id(request)
        address = get_object_or_404(Address, pk=pk, user_id=user_id)
        return Response(AddressSerializer(address).data)

    def put(self, request, pk):
        user_id = get_user_id(request)
        address = get_object_or_404(Address, pk=pk, user_id=user_id)
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_id = get_user_id(request)
        address = get_object_or_404(Address, pk=pk, user_id=user_id)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = get_user_id(request)
        wishlist = Wishlist.objects.filter(user_id=user_id).order_by('-added_at')
        serializer = WishlistSerializer(wishlist, many=True)
        return Response({'count': wishlist.count(), 'items': serializer.data})

    def post(self, request):
        user_id = get_user_id(request)
        data = request.data.copy()
        # Check if already in wishlist
        product_id = data.get('product_id')
        product_service = data.get('product_service')
        if Wishlist.objects.filter(user_id=user_id, product_id=product_id, product_service=product_service).exists():
            return Response({'error': 'Product already in wishlist.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = WishlistSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user_id=user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WishlistDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        user_id = get_user_id(request)
        item = get_object_or_404(Wishlist, pk=pk, user_id=user_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
