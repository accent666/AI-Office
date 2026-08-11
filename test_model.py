from ollama import chat

response = chat(
    model="qwen3:8b",
    messages=[
        {
            "role": "user",
            "content": "Привет! Кратко скажи, кто ты."
        }
    ]
)

print(response.message.content)