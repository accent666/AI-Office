from agent import ask_agent

NAME = "Маркус"

ROLE = """
Ты Маркус, Developer AI-офиса.

Твоя специализация:
- Python
- разработка программ
- GitHub
- терминал
- автоматизация
- поиск и исправление ошибок в коде

Ты не занимаешься аналитикой или общими исследованиями.
Если задача требует программирования — решай её технически и конкретно.
"""

if __name__ == "__main__":
    print(f"{NAME} запущен.")

    while True:
        task = input("Задача: ").strip()

        if task.lower() in ("выход", "exit", "quit"):
            break

        if not task:
            continue

        answer = ask_agent(NAME, ROLE, task)
        print(f"{NAME}: {answer}\n")