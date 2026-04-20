from django.urls import path
from apps.search import views

urlpatterns = [
    path('health/', views.HealthView.as_view(), name='health'),
    path('search/', views.SearchView.as_view(), name='search'),
]
