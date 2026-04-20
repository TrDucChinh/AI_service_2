from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth-register'),
    path('login/', views.LoginView.as_view(), name='auth-login'),
    path('logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('refresh/', views.RefreshView.as_view(), name='auth-refresh'),
    path('verify/', views.TokenVerifyView.as_view(), name='auth-verify'),
    path('me/', views.MeView.as_view(), name='auth-me'),
    path('password/change/', views.PasswordChangeView.as_view(), name='auth-password-change'),
    path('users/', views.UserListView.as_view(), name='auth-users'),
    path('users/<int:pk>/assign-role/', views.AssignRoleView.as_view(), name='auth-assign-role'),
    path('roles/', views.RoleListView.as_view(), name='auth-roles'),
]
