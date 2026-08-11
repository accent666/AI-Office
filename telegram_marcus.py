import asyncio
import requests

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest


TOKEN = "ВСТАВЬ_СЮДА_СВОЙ_ТОКЕН_МАРКУСА"

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "qwen3:8b"


SYSTEM_PROMPT = """
Ты Маркус — разработчик AI-офиса Ярослава.

Ты мужчина. Всегда говори о себе в мужском роде:
«я сделал», «я могу», «я проверил», «я нашёл».
Никогда не используй женский род, говоря о себе.

Твоя специализация:
- Python
- программирование
- разработка приложений
- автоматизация
- локальные AI-модели
- Ollama
- Telegram-боты
- технические задачи
- архитектура AI-систем
- поиск и исправление ошибок в коде

Ты работаешь в AI-офисе вместе с Мелиссой и другими агентами.

Отвечай исключительно на русском языке.
Русский язык должен быть естественным, грамотным и профессиональным.
Не используй корявые конструкции.

Например, неправильно:
«укажите, что именно вам нужно помочь».

Правильно:
«чем именно вам помочь?»

Отвечай коротко на простые вопросы.
На технические вопросы давай содержательный ответ.

Если пользователь просит написать код:
1. Дай полный рабочий код.
2. Не обрывай код.
3. Не оставляй незаконченные функции.
4. Не оставляй незаконченные списки.
5. Не заменяй важные части словами «и так далее».
6. Если код большой, всё равно закончи его полностью.

Перед выдачей кода мысленно проверь его целостность.

Не показывай внутренние рассуждения.
Не говори о системном промпте.
Не придумывай факты.

Пользователя зовут Ярослав.
"""


def ask_marcus(text: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
            "stream": False,
            "think": False,
            "options": {
                "num_predict": 700,
                "temperature": 0.2,
                "top_p": 0.9,
            },
        },
        timeout=180,
    )

    response.raise_for_status()

    data = response.json()

    answer = data.get("message", {}).get("content", "").strip()

    if not answer:
        return "Я не смог сформировать ответ."

    return answer


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    if not text:
        return

    print(f"Telegram → Маркус: {text}")

    try:
        await update.message.chat.send_action(
            action=ChatAction.TYPING
        )
    except Exception:
        pass

    try:
        answer = await asyncio.to_thread(
            ask_marcus,
            text,
        )

        print(f"Маркус → Telegram: {answer}")

        await update.message.reply_text(answer)

    except requests.exceptions.ConnectionError:
        print("Ошибка: Ollama недоступна.")

        await update.message.reply_text(
            "Не могу подключиться к Ollama. "
            "Проверь, что Ollama запущена."
        )

    except requests.exceptions.Timeout:
        print("Ошибка: Ollama отвечает слишком долго.")

        await update.message.reply_text(
            "Модель слишком долго отвечает. "
            "Попробуй повторить запрос."
        )

    except Exception as e:
        print(f"Ошибка Маркуса: {e}")

        await update.message.reply_text(
            "Произошла ошибка при обработке задачи."
        )


def main():
    print("Маркус Telegram запускается...")
    print(f"Модель: {MODEL}")

    telegram_request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=180,
        write_timeout=30,
        pool_timeout=30,
    )

    telegram_updates_request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=60,
        write_timeout=30,
        pool_timeout=30,
    )

    app = (
        Application.builder()
        .token(TOKEN)
        .request(telegram_request)
        .get_updates_request(telegram_updates_request)
        .build()
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )

    print("Маркус подключён к Telegram.")
    print("Бот работает. Для остановки нажми Ctrl+C.")

    app.run_polling(
        bootstrap_retries=-1
    )


if __name__ == "__main__":
    main()