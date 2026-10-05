# Изменения сервера для Android-приложения (v84)

Всё обратно совместимо: Telegram Mini App работает как раньше (initData проверяется тем же кодом).

## api.py
- **Вход по токену сессии.** Каждый запрос принимает `initData` (Telegram) **или** `token` (приложение). Токен: `base64(json{u, iat}).HMAC-SHA256`, живёт год.
  Секрет подписи создаётся сам при первом запуске в файле `.session` рядом с api.py (chmod 600). Удалишь файл — все приложения разлогинятся.
- **Новые действия без авторизации:**
  - `login_start` → `{code, ttl}`: одноразовый код (16 hex), живёт 5 минут.
  - `login_poll {code}` → `{wait: true}`, пока бот не подтвердил; потом один раз `{token, user}`, после этого код удаляется (`410`).
  - `login_bind {key, code, user}` — вызывает только bot.py (локально). `key` = HMAC от токена бота, считается одинаково в api.py и bot.py, отдельно настраивать не надо.
  - `version` → содержимое `version.json`: `{"apk": номер последней сборки APK, "url": ссылка на канал}`. Нет файла → `{}` (плашка обновления не показывается).
- **CORS** только для origin приложения: `https://localhost`, `http://localhost`, `capacitor://localhost`. Плюс `do_OPTIONS` (preflight). Другим сайтам заголовки не отдаются.

## bot.py
- `/start login_<код>` → сообщение «Войти в приложение MULBERRY с этим Telegram-аккаунтом?» с кнопкой **Войти**.
  Нажатие (callback `login:<код>`) → `login_bind` в api.py → сообщение меняется на «✅ Вход выполнен, вернитесь в игру» или «Код входа устарел».
  Подтверждение кнопкой защищает от кражи аккаунта присланной ссылкой.
- `getUpdates` теперь получает `message` и `callback_query`.

## Новые файлы на сервере
- `version.json` (пример — `version.example.json`) создать вручную.
- `.session` создастся сам.

## Как выкатить
Проще всего: распаковать архив на сервере и выполнить `bash deploy.sh` (бэкап, замена, перезапуск, проверка). Откат: `bash deploy.sh rollback`.

Вручную:
```bash
cd /root/work/monaco
cp api.py api.v84-pre.py && cp bot.py bot.v84-pre.py          # бэкап
# положить новые api.py и bot.py сюда
python3 -m py_compile api.py bot.py && echo OK
echo '{"apk": 1, "url": "https://t.me/ВАШ_КАНАЛ"}' > version.json
systemctl restart monaco-api monaco-bot
# клиент для Telegram (вёрстка landscape + вход в браузере), обратно совместим:
cp index.html /var/www/monaco/index.html
```

## Проверка после выката
```bash
B=https://2-56-120-214.sslip.io/monaco/api
curl -s -X POST $B/version -d '{}'                 # {"apk": 1, "url": "..."}
curl -s -X POST $B/login_start -d '{}'             # {"code": "…16 символов…", "ttl": 300}
curl -s -X POST $B/login_poll -d '{"code":"<код>"}' # {"wait": true}
curl -si -X OPTIONS -H 'Origin: https://localhost' $B/auth | grep -i access-control   # Allow-Origin: https://localhost
curl -s -X POST $B/auth -d '{"token":"bad"}'       # {"error": "auth"}
```
Затем в Telegram открыть `https://t.me/MulberryPokerBot?start=login_<код>` → «Войти» → повторить `login_poll`, вернётся `token`.
И проверить, что игра в Telegram открывается и баланс на месте.
