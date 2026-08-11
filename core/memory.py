import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE_DIR / "memory"

OFFICE_MEMORY_FILE = MEMORY_DIR / "office_memory.json"
EVENTS_FILE = MEMORY_DIR / "office_events.json"

MEMORY_DIR.mkdir(exist_ok=True)


def _load(path, default):
    if not path.exists():
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return default


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_office_memory():
    return _load(
        OFFICE_MEMORY_FILE,
        {
            "facts": [],
            "decisions": [],
            "tasks": [],
            "agent_notes": {}
        }
    )


def save_office_memory(memory):
    _save(OFFICE_MEMORY_FILE, memory)


def add_event(agent, event_type, text):
    events = _load(EVENTS_FILE, [])

    events.append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "agent": agent,
        "type": event_type,
        "text": text
    })

    # Чтобы память не разрасталась бесконечно.
    events = events[-500:]

    _save(EVENTS_FILE, events)


def get_recent_events(limit=30):
    events = _load(EVENTS_FILE, [])
    return events[-limit:]


def remember_fact(text):
    memory = get_office_memory()

    if text not in memory["facts"]:
        memory["facts"].append(text)

    save_office_memory(memory)


def add_task(text, agent=None):
    memory = get_office_memory()

    memory["tasks"].append({
        "text": text,
        "agent": agent,
        "status": "active",
        "created": datetime.now().isoformat(timespec="seconds")
    })

    save_office_memory(memory)


def add_agent_note(agent, text):
    memory = get_office_memory()

    if agent not in memory["agent_notes"]:
        memory["agent_notes"][agent] = []

    memory["agent_notes"][agent].append({
        "time": datetime.now().isoformat(timespec="seconds"),
        "text": text
    })

    memory["agent_notes"][agent] = memory["agent_notes"][agent][-100:]

    save_office_memory(memory)


def build_memory_context(limit=20):
    memory = get_office_memory()
    events = get_recent_events(limit)

    parts = []

    if memory["facts"]:
        parts.append(
            "ВАЖНЫЕ ФАКТЫ:\n" +
            "\n".join(f"- {x}" for x in memory["facts"][-30:])
        )

    if memory["tasks"]:
        active = [
            x for x in memory["tasks"]
            if x.get("status") == "active"
        ]

        if active:
            parts.append(
                "АКТИВНЫЕ ЗАДАЧИ:\n" +
                "\n".join(
                    f"- {x['text']} "
                    f"(ответственный: {x.get('agent') or 'не назначен'})"
                    for x in active[-20:]
                )
            )

    if events:
        parts.append(
            "ПОСЛЕДНИЕ СОБЫТИЯ ОФИСА:\n" +
            "\n".join(
                f"- [{x['agent']}] {x['text']}"
                for x in events
            )
        )

    return "\n\n".join(parts)