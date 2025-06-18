import os

# Default InfluxDB Configuration values
DEFAULT_INFLUX_URL = "https://example.com"
DEFAULT_INFLUX_TOKEN = "example-token"
DEFAULT_INFLUX_ORG = "example-org"
DEFAULT_INFLUX_BUCKET = "example-bucket"

# InfluxDB Configuration with environment variables and fallback to default values
INFLUX_URL = os.getenv("INFLUX_URL", DEFAULT_INFLUX_URL)
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", DEFAULT_INFLUX_TOKEN)
INFLUX_ORG = os.getenv("INFLUX_ORG", DEFAULT_INFLUX_ORG)
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", DEFAULT_INFLUX_BUCKET)

# Measurement configuration
DEFAULT_MEASUREMENT = "full"
MEASUREMENT = os.getenv("MEASUREMENT", DEFAULT_MEASUREMENT)

# Model configuration
DEFAULT_OPENAI_MODEL_NAME = "gpt-4o"
DEFAULT_OLLAMA_MODEL_NAME = "qwen3:8b"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", DEFAULT_OPENAI_MODEL_NAME)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", DEFAULT_OLLAMA_MODEL_NAME)
