from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.cache import cache
from .models import Brand, Category, Product, Inventory, Review, Rating
from .serializers import (
    BrandSerializer, CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ProductWriteSerializer, ReviewSerializer,
    InventorySerializer
)
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly, IsStaffUser


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name', 'slug']

    @action(detail=False, methods=['get'], url_path='all')
    def all_categories(self, request):
        cache_key = 'all_categories'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        cats = Category.objects.all()
        data = CategorySerializer(cats, many=True).data
        cache.set(cache_key, data, 3600)
        return Response(data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category').prefetch_related('images', 'rating')
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'sku', 'description', 'brand__name']
    ordering_fields = ['price', 'name', 'created_at', 'stock']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ProductWriteSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.META.get('HTTP_X_USER_ROLE', '')
        if role in ('admin', 'staff') and self.request.query_params.get('show_inactive'):
            qs = Product.objects.all().select_related('brand', 'category').prefetch_related('images', 'rating')
        return qs

    def retrieve(self, request, *args, **kwargs):
        cache_key = f'product_{kwargs.get("pk")}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 300)
        return response

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f'product_{instance.pk}')

    def perform_destroy(self, instance):
        cache.delete(f'product_{instance.pk}')
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsStaffUser])
    def reserve(self, request, pk=None):
        product = self.get_object()
        quantity = request.data.get('quantity', 1)
        inventory, _ = Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
        if inventory.available_qty < quantity:
            return Response(
                {'error': f'Insufficient stock. Available: {inventory.available_qty}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        inventory.reserved_qty += quantity
        inventory.save()
        return Response({'message': f'{quantity} units reserved.', 'available': inventory.available_qty})

    @action(detail=True, methods=['get'])
    def inventory(self, request, pk=None):
        product = self.get_object()
        inv, _ = Inventory.objects.get_or_create(product=product, defaults={'quantity': product.stock})
        return Response(InventorySerializer(inv).data)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.filter(is_approved=True)
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['product', 'rating', 'is_verified']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def create(self, request, *args, **kwargs):
        user_id = request.META.get('HTTP_X_USER_ID')
        if not user_id:
            return Response({'error': 'Authentication required to post a review.'}, status=status.HTTP_401_UNAUTHORIZED)
        data = request.data.copy()
        data['user_id'] = user_id
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
