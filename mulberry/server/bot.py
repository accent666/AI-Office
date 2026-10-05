"""MULBERRY (@MulberryPokerBot): отвечает на /start кнопкой игры, /start login_<код> — вход в Android-приложение. Long polling, только stdlib."""
import hashlib, hmac, json, re, time, urllib.request, urllib.parse
from pathlib import Path

TOKEN = Path(__file__).with_name(".env").read_text().split("=", 1)[1].strip()
API = f"https://api.telegram.org/bot{TOKEN}/"
URL = "https://2-56-120-214.sslip.io/monaco/"
LOCAL_API = "http://127.0.0.1:8098/"  # api.py на этом же сервере
BIND_KEY = hmac.new(TOKEN.encode(), b"mulberry-login-bind", hashlib.sha256).hexdigest()  # api.py считает так же
HELLO = ("<b>MULBERRY</b>\n"
         "Техасский холдем и блэкджек. Соперники с характером, столы от новичка до хайроллера.\n\n"
         "Фишки игровые: не продаются и не выводятся.")


def call(method, **p):
    data = urllib.parse.urlencode({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in p.items()}).encode()
    with urllib.request.urlopen(API + method, data, timeout=40) as r:
        return json.load(r)


def login_bind(code, user):
    """Вход в Android-приложение: привязать одноразовый код к Telegram id. True — получилось."""
    body = json.dumps({"key": BIND_KEY, "code": code, "user": user}).encode()
    req = urllib.request.Request(LOCAL_API + "login_bind", body, {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    off = 0
    while True:
        try:
            r = call("getUpdates", offset=off, timeout=30, allowed_updates=["message", "callback_query"])
            for u in r.get("result", []):
                off = u["update_id"] + 1
                cq = u.get("callback_query")
                if cq and str(cq.get("data", "")).startswith("login:"):  # нажали «Войти»
                    fr = cq.get("from") or {}
                    ok = login_bind(cq["data"][6:], {k: fr[k] for k in ("id", "first_name", "last_name", "username") if fr.get(k)})
                    call("answerCallbackQuery", callback_query_id=cq["id"])
                    msg = cq.get("message") or {}
                    if msg:
                        call("editMessageText", chat_id=msg["chat"]["id"], message_id=msg["message_id"], parse_mode="HTML",
                             text="✅ <b>Вход выполнен</b>, вернитесь в игру." if ok else "Код входа устарел. Нажмите «Войти через Telegram» в игре ещё раз.")
                    continue
                m = u.get("message") or {}
                t = m.get("text", "")
                room = re.fullmatch(r"/start r(\d{4})", t.strip())
                login = re.fullmatch(r"/start login_([0-9a-f]{16})", t.strip())
                if login:  # вход в приложение: https://t.me/MulberryPokerBot?start=login_<код> — сначала спрашиваем подтверждение
                    call("sendMessage", chat_id=m["chat"]["id"], parse_mode="HTML",
                         text="Войти в приложение <b>MULBERRY</b> с этим Telegram-аккаунтом?\nЕсли ссылку прислал кто-то другой — не нажимайте.",
                         reply_markup={"inline_keyboard": [[{"text": "Войти", "callback_data": "login:" + login[1]}]]})
                elif room:  # приглашение друга: https://t.me/MulberryPokerBot?start=r1234
                    call("sendMessage", chat_id=m["chat"]["id"], parse_mode="HTML",
                         text=f"Тебя зовут в блэкджек 1 на 1, комната <b>{room[1]}</b>.",
                         reply_markup={"inline_keyboard": [[{"text": "Войти в комнату", "web_app": {"url": URL + "?room=" + room[1]}}]]})
                elif t:
                    call("sendMessage", chat_id=m["chat"]["id"], text=HELLO, parse_mode="HTML",
                         reply_markup={"inline_keyboard": [[{"text": "Играть", "web_app": {"url": URL}}]]})
        except Exception as e:
            print("poll error:", e, flush=True)
            time.sleep(5)


if __name__ == "__main__":
    main()
