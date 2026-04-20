from django.urls import path
from .views import InventoryAggregateView, LowStockView

urlpatterns = [
    path('', InventoryAggregateView.as_view()),
    path('low-stock/', LowStockView.as_view()),
]
