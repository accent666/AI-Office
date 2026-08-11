import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:8b"


def ask_agent(name, role, task):
    prompt = f"""
Ты — {name}, сотрудник AI-офиса.

Твоя роль:
{role}

Твоя задача:
{task}

Работай самостоятельно в рамках своей роли.
Отвечай кратко, конкретно и по делу.
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
            "stream": False
        },
        timeout=300
    )

    response.raise_for_status()

    return response.json()["message"]["content"]