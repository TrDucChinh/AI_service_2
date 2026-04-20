from django.conf import settings

try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None


class Neo4jClient:
    def __init__(self):
        self._driver = None
        if GraphDatabase is not None:
            try:
                self._driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                )
            except Exception:
                self._driver = None

    @property
    def enabled(self):
        return self._driver is not None

    def execute(self, query, params=None):
        if not self._driver:
            return []
        with self._driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
