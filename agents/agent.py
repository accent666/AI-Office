import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:1.7b"


def ask_agent(name, role, task):
    prompt = f"""
Ты {name}, сотрудник AI-офиса.

Твоя роль:
{role}

Пользователь:
{task}

Отвечай естественно, по-русски и кратко.
Не показывай рассуждения.
Не используй Thinking.
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
                "num_predict": 80,
                "temperature": 0.3
            }
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    return data["message"]["content"].strip()