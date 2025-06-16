"""Script to Analyse Data from the Triage Agent."""
from agents import client, triage_agent

if __name__ == "__main__":
    response = client.run(
        agent=triage_agent,
        messages=[
            {
                "role": "user",
                "content": "Zeige mir die letzten 1 stunde co2 und scd41_sensoren werte von der luftqualitaet",
            }
        ],
        debug=True,
    )
    print(response.messages[-1]["content"])
