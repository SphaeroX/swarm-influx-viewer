from swarm import Swarm
from openai import OpenAI

ollama_client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
MODEL_NAME = "qwen3:8b"
client = Swarm(ollama_client)

# alternative, use openAI
# client = Swarm()
