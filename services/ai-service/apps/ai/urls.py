from django.urls import path
from .views import HealthView, AIStatusView, BehaviorEventIngestView, UserBehaviorTimelineView, PredictNextActionView, ChatbotQueryView

urlpatterns = [
    path("health/", HealthView.as_view()),
    path("status/", AIStatusView.as_view()),
    path("behavior/event/", BehaviorEventIngestView.as_view()),
    path("behavior/timeline/", UserBehaviorTimelineView.as_view()),
    path("predict-next-action/", PredictNextActionView.as_view()),
    path("chat/", ChatbotQueryView.as_view()),
]
