import csv
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from .kg.graph_builder import GraphBuilderService
from .ml.inference import InferenceService
from .rag.chatbot import GraphRAGChatbot

VALID_ACTIONS = {"view", "click", "add_to_cart", "purchase", "search", "wishlist", "remove_cart", "checkout"}


def _dataset_path() -> Path:
    path = Path(settings.BEHAVIOR_DATASET_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("user_id,product_id,action,timestamp\n", encoding="utf-8")
    return path


def _read_user_events(user_id: str, limit: int = 100):
    events = []
    with _dataset_path().open("r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if str(row.get("user_id")) == str(user_id):
                events.append(row)
    events.sort(key=lambda e: e.get("timestamp", ""))
    return events[-limit:]


def _derive_session_id(user_id: str, timestamp: str):
    # Hourly session bucketing is enough for analytics and keeps IDs stable.
    hour = str(timestamp)[:13].replace(":", "").replace("T", "-")
    return f"{user_id}-{hour}"


inference_service = InferenceService()
graph_service = GraphBuilderService()
chatbot = GraphRAGChatbot(graph_service)


class HealthView(APIView):
    def get(self, request):
        return JsonResponse({"status": "ok", "service": "ai-service"})


class AIStatusView(APIView):
    def get(self, request):
        return JsonResponse(
            {
                "status": "ok",
                "service": "ai-service",
                "neo4j_enabled": graph_service.client.enabled,
                "inference": {
                    "model_type": inference_service.model_type,
                    "using_trained_model": inference_service.using_trained_model,
                },
                "chatbot": chatbot.health(),
            }
        )


class BehaviorEventIngestView(APIView):
    def post(self, request):
        payload = request.data or {}
        action = str(payload.get("action", "")).strip()
        if action not in VALID_ACTIONS:
            return JsonResponse({"error": "Invalid action"}, status=400)

        event = {
            "user_id": str(payload.get("user_id", "")).strip(),
            "product_id": str(payload.get("product_id", "")).strip(),
            "action": action,
            "timestamp": payload.get("timestamp") or datetime.utcnow().isoformat(timespec="seconds") + "Z",
        }
        if not event["user_id"] or not event["product_id"]:
            return JsonResponse({"error": "user_id and product_id are required"}, status=400)
        event["session_id"] = str(payload.get("session_id") or _derive_session_id(event["user_id"], event["timestamp"]))

        with _dataset_path().open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "product_id", "action", "timestamp"])
            writer.writerow(event)

        return JsonResponse({"status": "ok", "event": event, "graph": graph_service.ingest_event(event)})


class UserBehaviorTimelineView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user_id") or request.META.get("HTTP_X_USER_ID")
        if not user_id:
            return JsonResponse({"error": "user_id is required"}, status=400)
        limit = int(request.query_params.get("limit", 30))
        events = _read_user_events(user_id, limit=limit)
        return JsonResponse({"user_id": user_id, "count": len(events), "events": events})


class PredictNextActionView(APIView):
    def post(self, request):
        payload = request.data or {}
        user_id = payload.get("user_id") or request.META.get("HTTP_X_USER_ID")
        events = payload.get("events")
        if events is None:
            events = _read_user_events(user_id, limit=settings.MODEL_WINDOW_SIZE) if user_id else []
        if not isinstance(events, list):
            return JsonResponse({"error": "events must be a list"}, status=400)
        prediction = inference_service.predict_next_action(events)
        return JsonResponse({"user_id": user_id, **prediction})


class ChatbotQueryView(APIView):
    def post(self, request):
        question = str((request.data or {}).get("question", "")).strip()
        if not question:
            return JsonResponse({"error": "question is required"}, status=400)
        return JsonResponse({"question": question, **chatbot.answer(question)})
