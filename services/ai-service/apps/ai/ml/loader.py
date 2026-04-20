import json
import pickle
from pathlib import Path

import torch

from .torch_models import RNNNextAction, LSTMNextAction, BiLSTMNextAction


DEFAULT_CLASSES = ["view", "click", "add_to_cart", "purchase", "search", "wishlist", "remove_cart", "checkout"]
DEFAULT_CLASSES_FOR_LABEL_ENCODER = sorted(DEFAULT_CLASSES)


class ModelArtifacts:
    def __init__(self, model_type="heuristic", classes=None, window_size=5, model=None):
        self.model_type = model_type
        self.classes = classes or DEFAULT_CLASSES_FOR_LABEL_ENCODER
        self.window_size = window_size
        self.model = model


def load_artifacts(models_dir: str) -> ModelArtifacts:
    models_path = Path(models_dir)
    config_path = models_path / "config.json"
    encoder_path = models_path / "label_encoder.pkl"
    model_path = models_path / "best_model.pt"
    if not config_path.exists():
        return ModelArtifacts()

    config = json.loads(config_path.read_text(encoding="utf-8"))
    classes = config.get("classes")
    if encoder_path.exists():
        try:
            with encoder_path.open("rb") as f:
                encoder = pickle.load(f)
                classes = list(getattr(encoder, "classes_", []) or classes or [])
        except Exception:
            # label_encoder.pkl requires sklearn to unpickle; fallback to config/default classes
            pass

    model_type = config.get("model_type", "heuristic")
    num_classes = int(config.get("num_classes", len(classes or DEFAULT_CLASSES_FOR_LABEL_ENCODER)))
    hidden_dim = int(config.get("hidden_dim", 64))

    model = None
    if model_path.exists() and model_type in {"rnn", "lstm", "bilstm"}:
        model_cls = {
            "rnn": RNNNextAction,
            "lstm": LSTMNextAction,
            "bilstm": BiLSTMNextAction,
        }[model_type]
        model = model_cls(num_classes=num_classes, hidden_dim=hidden_dim)
        state = torch.load(model_path, map_location="cpu")
        model.load_state_dict(state)
        model.eval()

    return ModelArtifacts(
        model_type=model_type,
        classes=classes,
        window_size=config.get("window_size", 5),
        model=model,
    )
