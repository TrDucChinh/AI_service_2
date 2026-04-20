from .llm_client import LLMClient
from .prompting import build_context_answer, build_prompt
from .retriever import GraphRetriever


class GraphRAGChatbot:
    def __init__(self, graph_builder):
        self.retriever = GraphRetriever(graph_builder)
        self.llm_client = LLMClient()

    def answer(self, question: str):
        intent, records = self.retriever.retrieve(question)
        fallback = build_context_answer(intent, records)

        if not self.llm_client.enabled:
            return fallback

        prompt = build_prompt(question, intent, records)
        try:
            llm_answer = self.llm_client.complete(prompt)
            return {
                "intent": intent,
                "answer": llm_answer,
                "context": records,
                "generator": "llm",
            }
        except Exception:
            return fallback

    def health(self):
        return {
            "llm_enabled": self.llm_client.enabled,
            "llm_mode": "remote" if self.llm_client.enabled else "fallback",
        }
