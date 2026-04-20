from django.urls import path, re_path
from apps.gateway import views

urlpatterns = [
    path('health/', views.HealthView.as_view(), name='health'),
    re_path(r'^api/auth/(?P<path>.*)$', views.AuthProxyView.as_view(), name='auth-proxy'),
    re_path(r'^api/users/(?P<path>.*)$', views.UserProxyView.as_view(), name='user-proxy'),
    re_path(r'^api/cart/(?P<path>.*)$', views.CartProxyView.as_view(), name='cart-proxy'),
    re_path(r'^api/orders/(?P<path>.*)$', views.OrderProxyView.as_view(), name='order-proxy'),
    re_path(r'^api/payments/(?P<path>.*)$', views.PaymentProxyView.as_view(), name='payment-proxy'),
    re_path(r'^api/search/(?P<path>.*)$', views.SearchProxyView.as_view(), name='search-proxy'),
    re_path(r'^api/products/(?P<service>[^/]+)/(?P<path>.*)$', views.ProductProxyView.as_view(), name='product-proxy'),
    re_path(r'^api/recommendations/(?P<path>.*)$', views.RecommendationProxyView.as_view(), name='recommendation-proxy'),
    re_path(r'^api/inventory/(?P<path>.*)$', views.InventoryProxyView.as_view(), name='inventory-proxy'),
    re_path(r'^api/ai/(?P<path>.*)$', views.AIProxyView.as_view(), name='ai-proxy'),
]
