from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='user-profile'),
    path('addresses/', views.AddressListCreateView.as_view(), name='user-addresses'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='user-address-detail'),
    path('wishlist/', views.WishlistView.as_view(), name='user-wishlist'),
    path('wishlist/<int:pk>/', views.WishlistDeleteView.as_view(), name='user-wishlist-delete'),
]
