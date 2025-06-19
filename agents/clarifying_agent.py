from swarm import Agent
from .common import MODEL_NAME_1


def ask_user(question: str) -> str:
    """Prompt the user for additional information."""
    return input(f"{question}\n> ")


clarifying_agent = Agent(
    name="Clarifying Agent",
    instructions=(
        "You help gather missing details and check if the user has further requests. "
        "Whenever more information is needed or a conversation ends, call the ask_user function to interact with the user."
    ),
    functions=[ask_user],
    model=MODEL_NAME_1,
)
