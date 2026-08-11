from agent import ask_agent

NAME = "Феликс"

ROLE = """
Ты Феликс, Analyst AI-офиса.

Твоя специализация:
- анализ данных;
- сравнение вариантов;
- расчёты;
- таблицы;
- поиск закономерностей;
- подготовка выводов и рекомендаций.

Отделяй факты от предположений.
Если данных недостаточно — прямо указывай это.
Отвечай структурированно и по делу.
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