"""Script to Analyse Data from the Triage Agent."""
from agents import client, triage_agent

if __name__ == "__main__":
    response = client.run(
        agent=triage_agent,
        messages=[
            {
                "role": "user",
                "content": "Zeige mir die letzten 1 stunde scd41_co2 und scd41_temperature aus der Measurement 'full'",
            }
        ],
        debug=True,
    )
    print(response.messages[-1]["content"])
