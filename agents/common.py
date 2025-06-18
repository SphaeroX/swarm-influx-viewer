import os
from swarm import Swarm
from openai import OpenAI

try:
    from config import (
        MODEL_PROVIDER,
        OPENAI_API_KEY,
        OPENAI_MODEL_NAME,
        OLLAMA_BASE_URL,
        OLLAMA_MODEL_NAME,
    )
except ImportError:  # pragma: no cover - fallback for runtime usage
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "qwen3:8b")

ollama_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

provider = (MODEL_PROVIDER or "").lower()
if provider == "openai" or (not provider and OPENAI_API_KEY):
    client = Swarm(openai_client)
    MODEL_NAME = OPENAI_MODEL_NAME
else:
    client = Swarm(ollama_client)
    MODEL_NAME = OLLAMA_MODEL_NAME
