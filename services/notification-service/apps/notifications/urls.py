from django.urls import path
from . import views

urlpatterns = [
    path('order-confirmation/', views.order_confirmation),
    path('payment-success/', views.payment_success),
    path('order-shipped/', views.order_shipped),
    path('low-stock/', views.low_stock_alert),
]
