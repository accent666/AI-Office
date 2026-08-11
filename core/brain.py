import requests

from core.memory import (
    build_memory_context,
    add_event,
    add_agent_note,
)

from core.agents.profiles import AGENTS


OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:8b"


def ask_agent(agent, user_text):

    if agent not in AGENTS:
        return "Такого агента нет."

    config = AGENTS[agent]

    memory = build_memory_context()


    prompt = f"""
{config['role']}

Ты работаешь внутри AI-офиса Ярослава.

У всех агентов общая память.
Используй её, если это помогает.

Память офиса:

{memory}


Сообщение пользователя:

{user_text}


Правила ответа:

- отвечай на грамотном русском языке;
- отвечай полностью;
- не обрывай мысли;
- не показывай внутренние рассуждения;
- не выдумывай факты.
"""


    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            "stream": False,
            "think": False,
            "options": {
                "num_predict": 700,
                "temperature": 0.25
            }
        },
        timeout=180
    )


    response.raise_for_status()


    answer = response.json()["message"]["content"].strip()


    add_event(
        config["name"],
        "response",
        f"Ответил пользователю: {user_text[:100]}"
    )


    add_agent_note(
        agent,
        answer[:500]
    )


    return answer