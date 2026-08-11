import requests
import time

url = "http://127.0.0.1:11434/api/chat"

data = {
    "model": "qwen3:8b",
    "messages": [
        {
            "role": "system",
            "content": "Ты Маркус, разработчик AI-офиса. Отвечай на хорошем русском языке. Если пишешь код — всегда заканчивай его полностью."
        },
        {
            "role": "user",
            "content": "Напиши полный Python-скрипт, который выводит «Привет, Ярослав!»."
        }
    ],
    "stream": False,
    "think": False,
    "options": {
        "num_predict": 300,
        "temperature": 0.2
    }
}

print("Запрос к Qwen 3 8B...")
start = time.time()

response = requests.post(
    url,
    json=data,
    timeout=120
)

elapsed = time.time() - start

response.raise_for_status()

result = response.json()

print()
print(f"Время ответа: {elapsed:.1f} сек")
print()
print(result["message"]["content"])