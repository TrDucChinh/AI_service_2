import json
import urllib.request

from django.conf import settings


class LLMClient:
    def __init__(self):
        self.api_key = getattr(settings, "RAG_LLM_API_KEY", "")
        self.api_url = getattr(settings, "RAG_LLM_API_URL", "https://api.openai.com/v1/chat/completions")
        self.model = getattr(settings, "RAG_LLM_MODEL", "gpt-4o-mini")

    @property
    def enabled(self):
        return bool(self.api_key)

    def complete(self, prompt: str):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]
