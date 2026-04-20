from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.InitiatePaymentView.as_view(), name='payment-initiate'),
    path('<int:payment_id>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('<int:payment_id>/confirm/', views.ConfirmPaymentView.as_view(), name='payment-confirm'),
    path('<int:payment_id>/refund/', views.RefundPaymentView.as_view(), name='payment-refund'),
]
