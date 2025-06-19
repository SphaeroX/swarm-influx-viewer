import json
import os

MEMORY_FILE = "memory.json"
MAX_HISTORY = 10


def load_memory() -> dict:
    """Return stored history and notes from disk."""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    return {"history": data, "notes": []}
                if isinstance(data, dict):
                    data.setdefault("history", [])
                    data.setdefault("notes", [])
                    return data
            except json.JSONDecodeError:
                pass
    return {"history": [], "notes": []}


def save_memory(memory: dict) -> None:
    trimmed = {
        "history": memory.get("history", [])[-MAX_HISTORY:],
        "notes": memory.get("notes", []),
    }
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(trimmed, f)


def append_history(memory: dict, role: str, content: str) -> dict:
    memory.setdefault("history", [])
    memory["history"].append({"role": role, "content": content})
    memory["history"] = memory["history"][-MAX_HISTORY:]
    return memory


def append_note(memory: dict, content: str) -> dict:
    memory.setdefault("notes", [])
    memory["notes"].append({"role": "system", "content": content})
    return memory


def remember_note(content: str) -> str:
    memory = load_memory()
    memory = append_note(memory, content)
    save_memory(memory)
    return "note saved"
