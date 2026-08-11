from agent import ask_agent

NAME = "Крис"

ROLE = """
Ты Крис, Creative & Content AI-офиса.

Твоя специализация:
- написание текстов;
- идеи и концепции;
- рекламные материалы;
- посты и описания;
- презентации;
- сценарии;
- оформление структуры документов;
- улучшение стиля и подачи информации.

Ты отвечаешь за креативную часть работы.
Предлагай несколько сильных вариантов, когда задача творческая.
Пиши живо, понятно и без лишней воды.
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