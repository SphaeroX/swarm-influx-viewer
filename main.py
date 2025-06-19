"""Interactive script to analyse data using the triage agent."""

from agents import client, triage_agent, ask_user
from memory import load_memory, save_memory, append_history


def main() -> None:
    """Run the triage agent in a loop, keeping a small conversation history."""
    memory = load_memory()
    user_message = ask_user("What would you like to do?")
    while user_message.strip():
        memory = append_history(memory, "user", user_message)
        messages = memory.get("notes", []) + memory.get("history", [])
        response = client.run(
            agent=triage_agent,
            messages=messages,
            debug=True,
        )
        assistant_reply = response.messages[-1]["content"]
        print(assistant_reply)
        memory = append_history(memory, "assistant", assistant_reply)
        save_memory(memory)
        user_message = ask_user(
            "Anything else I can help with? (Leave blank to exit)"
        )


if __name__ == "__main__":
    main()
