"""Example configuration for swarm-influx-viewer.

Copy this file to ``config.py`` and adjust the values. When ``config.py`` is not
present, the application falls back to the corresponding environment variables.
"""

# InfluxDB configuration
INFLUX_URL = "https://example.com"
INFLUX_TOKEN = "example-token"
INFLUX_ORG = "example-org"
INFLUX_BUCKET = "example-bucket"
MEASUREMENT = "full"

# Model configuration
LLM_PROVIDER = ""  # "openai" or "ollama"

# OpenAI settings
OPENAI_API_KEY = ""
OPENAI_MODEL_NAME_1 = "gpt-4o"
OPENAI_MODEL_NAME_2 = OPENAI_MODEL_NAME_1
OPENAI_MODEL_NAME_3 = OPENAI_MODEL_NAME_1

# Ollama settings
OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_MODEL_NAME_1 = "qwen3:8b"
OLLAMA_MODEL_NAME_2 = OLLAMA_MODEL_NAME_1
OLLAMA_MODEL_NAME_3 = OLLAMA_MODEL_NAME_1
