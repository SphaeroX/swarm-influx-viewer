from swarm import Agent
from .common import MODEL_NAME


def ask_user(question: str) -> str:
    """Prompt the user for additional information."""
    return input(f"{question}\n> ")


clarifying_agent = Agent(
    name="Clarifying Agent",
    instructions=(
        "You help gather missing details. "
        "Whenever you need more information, call the ask_user function to pose a question to the user. "
        "After responding, always ask if the user needs anything else or if everything is clear."
    ),
    functions=[ask_user],
    model=MODEL_NAME,
)
