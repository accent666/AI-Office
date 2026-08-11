import json
import os
import requests

MODEL = "qwen3:8b"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def save_memory(messages):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

memory = load_memory()

system_message = {
    "role": "system",
    "content": (
        "Ты локальный ассистент. Отвечай по-русски, кратко и понятно. "
        "Используй предыдущие сообщения из памяти для продолжения разговора."
    )
}

messages = [system_message] + memory

print("Локальный чат с постоянной памятью запущен.")
print("Напиши 'выход' для завершения.\n")

while True:
    try:
        user_text = input("Ты: ").strip()

        if user_text.lower() == "выход":
            print("Чат завершён.")
            break

        if not user_text:
            continue

        messages.append({
            "role": "user",
            "content": user_text
        })

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=300
        )

        response.raise_for_status()

        data = response.json()
        answer = data["message"]["content"]

        print("Qwen:", answer)

        messages.append({
            "role": "assistant",
            "content": answer
        })

        memory = messages[1:]
        save_memory(memory)

        print()

    except requests.exceptions.ConnectionError:
        print("Ошибка: Ollama не запущен.")
        print("Запусти Ollama и попробуй снова.\n")

    except requests.exceptions.Timeout:
        print("Ошибка: Ollama слишком долго отвечает.\n")

    except Exception as e:
        print(f"Ошибка: {e}\n")