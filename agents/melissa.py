import sys
from pathlib import Path

# Позволяем импортировать файлы из корня проекта
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from agent import ask_agent
from memory_manager import (
    get_long_term_memory,
    add_conversation,
    remember_user,
)


NAME = "Мелисса"


def get_memory():
    memory = get_long_term_memory()

    user = memory.get("user", {})
    office = memory.get("office", {})

    return {
        "name": user.get("name", "не указано"),
        "office": office,
    }


def choose_agent(task):
    """Быстрый выбор агента без дополнительного вызова Qwen."""

    text = task.lower().replace("ё", "е")

    # Программист
    if any(word in text for word in [
        "python",
        "код",
        "скрипт",
        "программ",
        "github",
        "терминал",
        "ошибк",
        ".py",
        "разработ",
    ]):
        return "Маркус"

    # Аналитик
    if any(word in text for word in [
        "сравни",
        "анализ",
        "аналитик",
        "таблиц",
        "рассчитай",
        "расчет",
        "данные",
        "статистик",
    ]):
        return "Феликс"

    # Researcher
    if any(word in text for word in [
        "исследуй",
        "исследован",
        "найди информацию",
        "изучи",
        "узнай",
        "источники",
        "модели",
        "технологии",
    ]):
        return "Лукас"

    # Creative / Content
    if any(word in text for word in [
        "придумай",
        "слоган",
        "пост",
        "статья",
        "сценарий",
        "контент",
        "идею",
        "реклам",
    ]):
        return "Крис"

    return "Мелисса"


def save_fact(task):
    """
    Обрабатывает команды:
    Запомни, что ...
    Запомни: ...
    """

    text = task.strip()

    if not text.lower().startswith("запомни"):
        return None

    fact = text[len("запомни"):].strip()

    # Убираем возможное "что"
    if fact.lower().startswith("что "):
        fact = fact[4:].strip()

    if not fact:
        return "Что именно мне запомнить?"

    # Сохраняем последний факт в постоянную память
    remember_user("last_fact", fact)

    return f"Запомнила: {fact}"


def answer_as_melissa(task, memory):
    role = """
Ты Мелисса, главный ассистент AI-офиса.

Общайся естественно и дружелюбно.
Отвечай на русском языке.
Отвечай кратко и понятно.
Не показывай рассуждения.
Не используй канцелярит.
Не повторяй вопрос пользователя.

Если пользователь спрашивает, чем ты занимаешься,
объясни, что ты главный ассистент и координируешь работу AI-офиса.
"""

    context = f"""
Имя пользователя: {memory['name']}

Твоя задача:
{task}
"""

    return ask_agent(NAME, role, context)


def main():
    print("Мелисса запущена.")
    print("Постоянная память загружена.\n")

    memory = get_memory()

    while True:
        task = input("Ты: ").strip()

        if task.lower() in ("выход", "exit", "quit"):
            break

        if not task:
            continue

        add_conversation("user", task)

        # ----------------------------------------
        # 1. Запоминание — вообще без Qwen
        # ----------------------------------------

        saved = save_fact(task)

        if saved is not None:
            answer = saved
            selected = "Мелисса"

        else:
            # ----------------------------------------
            # 2. Быстрые простые ответы
            # ----------------------------------------

            text = task.lower().strip().replace("ё", "е")

            if text in ("привет", "здравствуй", "здравствуйте"):
                answer = "Привет, Ярослав! Я на связи."
                selected = "Мелисса"

            elif text in ("как дела", "как ты", "как поживаешь"):
                answer = "Всё хорошо. Готова работать."
                selected = "Мелисса"

            elif text in ("кто ты", "ты кто", "как тебя зовут"):
                answer = "Я Мелисса, главный ассистент AI-офиса."
                selected = "Мелисса"

            elif "как меня зовут" in text:
                answer = f"Тебя зовут {memory['name']}."
                selected = "Мелисса"

            elif "чем занимаешься" in text:
                answer = (
                    "Я главный ассистент AI-офиса: "
                    "помогаю тебе и координирую работу остальных агентов."
                )
                selected = "Мелисса"

            else:
                # ----------------------------------------
                # 3. Сложные задачи
                # ----------------------------------------

                selected = choose_agent(task)

                if selected == "Мелисса":
                    answer = answer_as_melissa(task, memory)

                else:
                    # Пока передаём сложные задачи Мелиссе.
                    # Следующим этапом подключим полноценные роли
                    # Маркуса, Феликса, Лукаса и Криса.
                    answer = answer_as_melissa(task, memory)

        add_conversation("assistant", answer)

        print(f"\nМелисса → {selected}")
        print(f"Результат: {answer}\n")


if __name__ == "__main__":
    main()