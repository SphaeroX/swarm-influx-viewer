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
