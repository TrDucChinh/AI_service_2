from .neo4j_client import Neo4jClient
from .queries import upsert_event_query, TOP_CLICKED_PRODUCTS, FREQUENT_LAPTOP_BUYERS, USER_VIEWED_PRODUCTS


class GraphBuilderService:
    def __init__(self):
        self.client = Neo4jClient()

    def ingest_event(self, event):
        if not self.client.enabled:
            return {"status": "skipped", "reason": "neo4j_unavailable"}
        self.client.execute(upsert_event_query(event["action"]), event)
        return {"status": "ok"}

    def top_clicked_products(self, limit=10):
        if not self.client.enabled:
            return []
        return self.client.execute(TOP_CLICKED_PRODUCTS, {"limit": limit})

    def frequent_laptop_buyers(self, limit=10):
        if not self.client.enabled:
            return []
        return self.client.execute(FREQUENT_LAPTOP_BUYERS, {"limit": limit})

    def user_viewed_products(self, user_id, limit=10):
        if not self.client.enabled:
            return []
        return self.client.execute(USER_VIEWED_PRODUCTS, {"user_id": str(user_id), "limit": limit})
