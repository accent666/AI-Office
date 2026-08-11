import json
from pathlib import Path

MEMORY_DIR = Path(__file__).parent / "memory"

LONG_TERM_FILE = MEMORY_DIR / "long_term.json"
CONVERSATIONS_FILE = MEMORY_DIR / "conversations.json"
TASKS_FILE = MEMORY_DIR / "tasks.json"


def load_json(path, default):
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_long_term_memory():
    return load_json(LONG_TERM_FILE, {})


def save_long_term_memory(data):
    save_json(LONG_TERM_FILE, data)


def add_conversation(role, content):
    conversations = load_json(CONVERSATIONS_FILE, [])

    conversations.append({
        "role": role,
        "content": content
    })

    # Храним последние 100 сообщений,
    # чтобы файл не рос бесконечно.
    conversations = conversations[-100:]

    save_json(CONVERSATIONS_FILE, conversations)


def get_conversations():
    return load_json(CONVERSATIONS_FILE, [])


def get_tasks():
    return load_json(
        TASKS_FILE,
        {
            "active": [],
            "completed": []
        }
    )


def save_tasks(tasks):
    save_json(TASKS_FILE, tasks)

def remember_user(key, value):
    memory = get_long_term_memory()

    if "user" not in memory:
        memory["user"] = {}

    memory["user"][key] = value

    save_long_term_memory(memory)


if __name__ == "__main__":
    print("Менеджер памяти работает.")

    memory = get_long_term_memory()

    print("Пользователь:", memory.get("user", {}).get("name", "не указан"))

    print("Агенты:")
    for role, name in memory.get("office", {}).items():
        print(f"  {role}: {name}")