import django_filters
from .models import Product, Brand, Category


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.all())
    brand_name = django_filters.CharFilter(field_name='brand__name', lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    on_sale = django_filters.BooleanFilter(method='filter_on_sale')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ['brand', 'brand_name', 'category', 'category_name', 'min_price', 'max_price', 'in_stock', 'on_sale', 'is_active', 'name']

    def filter_in_stock(self, queryset, name, value):
        return queryset.filter(stock__gt=0) if value else queryset.filter(stock=0)

    def filter_on_sale(self, queryset, name, value):
        return queryset.filter(sale_price__isnull=False) if value else queryset.filter(sale_price__isnull=True)
