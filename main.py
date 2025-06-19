"""Interactive script to analyse data using the triage agent."""

from agents import client, triage_agent, ask_user


def main() -> None:
    """Run the triage agent in a loop and keep asking for new requests."""
    user_message = ask_user("What would you like to do?")
    while user_message.strip():
        response = client.run(
            agent=triage_agent,
            messages=[{"role": "user", "content": user_message}],
            debug=True,
        )
        print(response.messages[-1]["content"])
        user_message = ask_user("Anything else I can help with? (Leave blank to exit)")


if __name__ == "__main__":
    main()
