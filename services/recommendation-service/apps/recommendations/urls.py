from django.urls import path
from .views import RecommendationsView, CrossServiceRecommendationsView

urlpatterns = [
    path('', RecommendationsView.as_view()),
    path('cross/', CrossServiceRecommendationsView.as_view()),
]
