import json
import os

MEMORY_FILE = "memory.json"

def save_memory(messages):
    """Saves the conversation history to a JSON file."""
    try:
        # We only save user and assistant messages, not the system prompt
        history = [m for m in messages if m["role"] != "system"]
        with open(MEMORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"[*] Memory save error: {e}")

def load_memory():
    """Loads the conversation history from a JSON file."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"[*] Memory load error: {e}")
    return []
