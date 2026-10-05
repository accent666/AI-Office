#!/bin/bash
# Обновление сервера MULBERRY до v84: вход в Android-приложение через бота + CORS + проверка обновлений.
# Запуск на сервере (root), из папки, куда распакован server-v84.zip:   bash deploy.sh
# Откат:   bash deploy.sh rollback
set -e
cd "$(dirname "$0")"
DST=/root/work/monaco      # где лежат api.py и bot.py (см. monaco-api.service)
WEB=/var/www/monaco        # где лежит index.html игры (см. nginx-snippet.conf)

if [ "$1" = "rollback" ]; then
  for f in api.py bot.py; do [ -f "$DST/$f.before-v84" ] && cp "$DST/$f.before-v84" "$DST/$f"; done
  [ -f "$WEB/index.html.before-v84" ] && cp "$WEB/index.html.before-v84" "$WEB/index.html"
  systemctl restart monaco-api monaco-bot
  echo "Откатил на версию до v84."; exit 0
fi

python3 -m py_compile api.py bot.py
[ -f "$DST/api.py.before-v84" ] || cp "$DST/api.py" "$DST/api.py.before-v84"
[ -f "$DST/bot.py.before-v84" ] || cp "$DST/bot.py" "$DST/bot.py.before-v84"
[ -f "$WEB/index.html.before-v84" ] || cp "$WEB/index.html" "$WEB/index.html.before-v84"
cp api.py bot.py "$DST/"
cp index.html "$WEB/index.html"
[ -f "$DST/version.json" ] || cp version.example.json "$DST/version.json"
systemctl restart monaco-api monaco-bot
sleep 2
echo "Проверка:"
curl -s -X POST http://127.0.0.1:8098/login_start -d '{}' ; echo
curl -s -X POST http://127.0.0.1:8098/version -d '{}' ; echo
systemctl is-active monaco-api monaco-bot
echo "Готово. Не забудь вписать ссылку на свой канал в $DST/version.json (поле url)."
