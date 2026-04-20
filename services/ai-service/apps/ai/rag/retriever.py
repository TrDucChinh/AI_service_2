import re


class GraphRetriever:
    def __init__(self, graph_builder):
        self.graph_builder = graph_builder

    def detect_intent(self, question: str) -> str:
        q = question.lower()
        if "click" in q and "product" in q:
            return "top_clicked_products"
        if "laptop" in q and ("buy" in q or "mua" in q):
            return "frequent_laptop_buyers"
        if ("user" in q or "nguoi dung" in q) and ("view" in q or "xem" in q):
            return "user_viewed"
        return "general"

    def _extract_user_id(self, question: str):
        match = re.search(r"user\s*([0-9]+)", question.lower())
        if match:
            return match.group(1)
        match = re.search(r"nguoi dung\s*([0-9]+)", question.lower())
        if match:
            return match.group(1)
        return None

    def retrieve(self, question: str):
        intent = self.detect_intent(question)
        if intent == "top_clicked_products":
            return intent, self.graph_builder.top_clicked_products(limit=10)
        if intent == "frequent_laptop_buyers":
            return intent, self.graph_builder.frequent_laptop_buyers(limit=10)
        if intent == "user_viewed":
            user_id = self._extract_user_id(question)
            if user_id is None:
                return intent, []
            return intent, self.graph_builder.user_viewed_products(user_id=user_id, limit=10)
        return intent, []
