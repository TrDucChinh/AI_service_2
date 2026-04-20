from collections import Counter

import torch

FUNNEL_TRANSITIONS = {
    "view": "click",
    "click": "add_to_cart",
    "add_to_cart": "checkout",
    "checkout": "purchase",
    "wishlist": "add_to_cart",
    "remove_cart": "view",
    "search": "view",
}


class NextActionPredictor:
    def __init__(self, classes, window_size=5, model=None):
        self.classes = classes
        self.window_size = window_size
        self.model = model

    def _predict_with_model(self, actions):
        action_to_idx = {name: idx for idx, name in enumerate(self.classes)}
        encoded = [action_to_idx[a] for a in actions if a in action_to_idx]
        if not encoded:
            return None

        if len(encoded) < self.window_size:
            encoded = ([encoded[0]] * (self.window_size - len(encoded))) + encoded
        else:
            encoded = encoded[-self.window_size :]

        x = torch.tensor([encoded], dtype=torch.long)
        with torch.no_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1)[0]
            pred_idx = int(torch.argmax(probs).item())
            confidence = float(probs[pred_idx].item())
        if pred_idx >= len(self.classes):
            return None
        return {
            "predicted_action": self.classes[pred_idx],
            "confidence": round(confidence, 4),
            "method": "pytorch_model",
        }

    def predict(self, events):
        actions = [e.get("action") if isinstance(e, dict) else str(e) for e in events]
        actions = [a for a in actions if a]
        if not actions:
            return {"predicted_action": "view", "confidence": 0.35, "method": "fallback"}

        if self.model is not None:
            model_result = self._predict_with_model(actions)
            if model_result is not None:
                return model_result

        last_action = actions[-1]
        if last_action in FUNNEL_TRANSITIONS:
            return {"predicted_action": FUNNEL_TRANSITIONS[last_action], "confidence": 0.82, "method": "heuristic_funnel"}

        common = Counter(actions[-self.window_size:]).most_common(1)[0][0]
        return {"predicted_action": common, "confidence": 0.55, "method": "frequency"}
