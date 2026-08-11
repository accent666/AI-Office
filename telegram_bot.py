import asyncio

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

from core.brain import ask_agent


TOKEN = "8897726059:AAGH9k6-pi0dA4OHkxWLiKAKBUnACa5k2N8"


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return


    text = update.message.text.strip()


    print(f"Telegram → Мелисса: {text}")


    try:
        await update.message.chat.send_action(
            action=ChatAction.TYPING
        )
    except Exception:
        pass


    try:

        answer = await asyncio.to_thread(
            ask_agent,
            "melissa",
            text
        )


        print(f"Мелисса → Telegram: {answer}")


        await update.message.reply_text(
            answer
        )


    except Exception as e:

        print(
            "Ошибка Мелиссы:",
            e
        )


        await update.message.reply_text(
            "У меня возникла ошибка при обработке запроса."
        )



def main():

    print("Мелисса запускается...")
    

    request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=60,
        write_timeout=30,
        pool_timeout=30,
    )


    updates_request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=60,
        write_timeout=30,
        pool_timeout=30,
    )


    app = (
        Application.builder()
        .token(TOKEN)
        .request(request)
        .get_updates_request(updates_request)
        .build()
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )


    print("Мелисса подключена.")
    print("Бот работает.")


    app.run_polling(
        bootstrap_retries=-1
    )



if __name__ == "__main__":
    main()