import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="django-insecure-ai-service-key")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.ai",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "ai_service.urls"
WSGI_APPLICATION = "ai_service.wsgi.application"

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "ai_service.sqlite3"),
    }
}

CORS_ALLOW_ALL_ORIGINS = True
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

BEHAVIOR_DATASET_PATH = config("BEHAVIOR_DATASET_PATH", default=str(BASE_DIR / "data" / "data_user500.csv"))
ML_MODELS_DIR = config("ML_MODELS_DIR", default=str(Path(__file__).resolve().parents[3] / "ml_models"))
MODEL_WINDOW_SIZE = config("MODEL_WINDOW_SIZE", default=5, cast=int)

NEO4J_URI = config("NEO4J_URI", default="bolt://neo4j:7687")
NEO4J_USER = config("NEO4J_USER", default="neo4j")
NEO4J_PASSWORD = config("NEO4J_PASSWORD", default="password")

RAG_LLM_API_KEY = config("RAG_LLM_API_KEY", default="")
RAG_LLM_API_URL = config("RAG_LLM_API_URL", default="https://api.openai.com/v1/chat/completions")
RAG_LLM_MODEL = config("RAG_LLM_MODEL", default="gpt-4o-mini")
