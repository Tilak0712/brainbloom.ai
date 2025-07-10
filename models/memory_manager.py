from firebase_config import db
from datetime import datetime

def save_memory(username, memory_name, chat_messages, metadata=None):
    """
    Save memory for user under a given name.
    chat_messages: list of dict with role, content, timestamp
    metadata: optional dict for personality, goals etc
    """
    data = {
        "chat_messages": chat_messages,
        "metadata": metadata or {},
        "saved_at": datetime.now().isoformat()
    }
    db.reference(f"memories/{username}/{memory_name}").set(data)
    return True

def list_memories(username):
    """
    List saved memory names for the user.
    """
    memories = db.reference(f"memories/{username}").get() or {}
    return sorted(memories.keys(), reverse=True)

def load_memory(username, memory_name):
    """
    Load a memory's data: chat_messages and metadata
    """
    data = db.reference(f"memories/{username}/{memory_name}").get()
    if data:
        return data.get("chat_messages", []), data.get("metadata", {})
    return [], {}
