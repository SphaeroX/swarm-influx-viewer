from swarm import Agent
from .common import MODEL_NAME
from .database_manager import influxDB_agent
from .data_specialist_agent import data_specialist_agent
from .clarifying_agent import clarifying_agent


def transfer_back_to_triage():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return triage_agent


def transfer_to_database_manager():
    """Transfer the conversation to the InfluxDB management agent."""
    return influxDB_agent


def transfer_to_data_specialist():
    """Transfer the conversation to the Data Specialist agent."""
    return data_specialist_agent


def transfer_to_clarifying_agent():
    """Transfer the conversation to the Clarifying agent."""
    return clarifying_agent


triage_agent = Agent(
    name="Triage Agent",
    instructions="Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.",
    model=MODEL_NAME,
)

triage_agent.functions = [
    transfer_to_database_manager,
    transfer_to_data_specialist,
    transfer_to_clarifying_agent,
]

# add transfer functions to other agents
influxDB_agent.functions.append(transfer_back_to_triage)
influxDB_agent.functions.append(transfer_to_data_specialist)
data_specialist_agent.functions.append(transfer_back_to_triage)
clarifying_agent.functions.append(transfer_back_to_triage)
