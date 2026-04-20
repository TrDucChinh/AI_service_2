from django.conf import settings

from .loader import load_artifacts
from .predictor import NextActionPredictor


class InferenceService:
    def __init__(self):
        artifacts = load_artifacts(settings.ML_MODELS_DIR)
        self.model_type = artifacts.model_type
        self.predictor = NextActionPredictor(
            classes=artifacts.classes,
            window_size=settings.MODEL_WINDOW_SIZE or artifacts.window_size,
            model=artifacts.model,
        )
        self.using_trained_model = artifacts.model is not None

    def predict_next_action(self, events):
        result = self.predictor.predict(events)
        result["model_type"] = self.model_type
        result["using_trained_model"] = self.using_trained_model
        return result
