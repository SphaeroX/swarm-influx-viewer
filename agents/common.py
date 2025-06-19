import os
from swarm import Swarm
from openai import OpenAI

try:
    from config import (
        LLM_PROVIDER,
        OPENAI_API_KEY,
        OPENAI_MODEL_NAME_1,
        OPENAI_MODEL_NAME_2,
        OPENAI_MODEL_NAME_3,
        OLLAMA_BASE_URL,
        OLLAMA_MODEL_NAME_1,
        OLLAMA_MODEL_NAME_2,
        OLLAMA_MODEL_NAME_3,
    )
except ImportError:  # pragma: no cover - fallback for runtime usage
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME_1 = os.getenv("OPENAI_MODEL_NAME_1", "gpt-4o")
    OPENAI_MODEL_NAME_2 = os.getenv("OPENAI_MODEL_NAME_2", OPENAI_MODEL_NAME_1)
    OPENAI_MODEL_NAME_3 = os.getenv("OPENAI_MODEL_NAME_3", OPENAI_MODEL_NAME_1)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL_NAME_1 = os.getenv("OLLAMA_MODEL_NAME_1", "qwen3:8b")
    OLLAMA_MODEL_NAME_2 = os.getenv("OLLAMA_MODEL_NAME_2", OLLAMA_MODEL_NAME_1)
    OLLAMA_MODEL_NAME_3 = os.getenv("OLLAMA_MODEL_NAME_3", OLLAMA_MODEL_NAME_1)

ollama_client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

provider = (LLM_PROVIDER or "").lower()
if provider == "openai":
    client = Swarm(openai_client)
    MODEL_NAME_1 = OPENAI_MODEL_NAME_1
    MODEL_NAME_2 = OPENAI_MODEL_NAME_2
    MODEL_NAME_3 = OPENAI_MODEL_NAME_3
else:
    client = Swarm(ollama_client)
    MODEL_NAME_1 = OLLAMA_MODEL_NAME_1
    MODEL_NAME_2 = OLLAMA_MODEL_NAME_2
    MODEL_NAME_3 = OLLAMA_MODEL_NAME_3
