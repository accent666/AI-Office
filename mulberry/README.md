# MULBERRY — исходники игры (снимок прода, Release 1.1, v83, 05.10.2026)

Карточный клуб на игровые фишки: Техасский холдем и Омаха, Блэкджек, Дурак, Баккара, Трёхкарточный покер, Карибский покер, Пай-гоу, Стад. Боты-соперники, онлайн-столы с друзьями, магазин скинов (рубашки, столы, фишки, паки), ежедневный бонус, квесты, промокоды, админка.
Сейчас работает как Telegram Mini App: бот @MulberryPokerBot → https://2-56-120-214.sslip.io/monaco/

## Структура
- `client/index.html` — ВСЯ игра в одном файле (~430 КБ: HTML + CSS + JS, без фреймворков и сборки). Версия — `var VERSION`.
  - `client/c/` — картинки: рубашки `back-*.webp`, столы `felt-*.webp` (800x880), колоды `classic/` и др. (300x418), обложки игр `g/*.webp`, логотип.
  - `client/s/` — звуки (Kenney Casino Audio, CC0), `client/f/` — шрифты (Inter, Russo One) и `telegram-web-app.js`.
- `server/api.py` — бэкенд на чистом Python stdlib (порт 8098, nginx проксирует `/monaco/api/`). Аккаунты по Telegram `initData` (HMAC с токеном бота), баланс, покупки скинов, бонусы, промокоды, онлайн-комнаты (блэкджек, покер, дурак) — вся логика онлайна на сервере. Данные: `users.json`, `promos.json`, `prices.json` рядом с api.py.
  - Клиент ходит так: `fetch("api/" + act, {method:"POST", body: JSON(initData, ...)})` — относительный путь.
- `server/bot.py` — бот: на /start шлёт кнопку «Играть», `/start rNNNN` — приглашение в комнату друга.
- `server/*.service` — systemd, `nginx-snippet.conf` — как раздаётся, `.env.example` — формат токена (сам токен не включён).
- `tools/` — генерация каталога скинов: `skins3.py` → SVG → `raster.js` (puppeteer) → webp; `cat3_apply.py` вставляет каталог в index.html (SK/GRP/PACKS) и api.py (ITEMS/PACKS). Каталог в клиенте и на сервере ДОЛЖЕН совпадать. `licenses/` — источники картинок рубашек (только Public Domain / CC0).
- `tests/` — puppeteer: `smoke.js` (обход экранов, ошибки JS), `bjsim2.js` (симуляция блэкджека).
- `CHANGELOG.md` — история всех версий и решений владельца (что пробовали и что он отверг) — прочитать перед правками.

## Android-приложение (v84)
- `app/` — Capacitor-обёртка над `client/` (пакет `club.mulberry.game`, только альбомная ориентация, полный экран). Сборка APK — GitHub Actions (`.github/workflows/mulberry-apk.yml` в корне репозитория).
- Вход вне Telegram — через бота (код → `/start login_<код>` → токен сессии). Подробно: `APP.md`, изменения сервера: `server/CHANGES.md`.
- Горизонтальная вёрстка: блок `LANDSCAPE` в конце `<style>` в `client/index.html` (`@media (orientation:landscape) and (max-height:560px)`), портрет не тронут.

## Что важно знать
- Вёрстка: ПОРТРЕТ телефона, эталон 390x700 (`@media (max-height:...)`) + горизонтальная для телефона 844x390 / 740x360 (блок LANDSCAPE).
- Telegram API в клиенте: `TG.initData`, `initDataUnsafe` (имя/аватар), `BackButton`, `HapticFeedback`, `openTelegramLink` (приглашения), цвета шапки. Вне Telegram этих вещей нет.
- Фишки только игровые: не покупаются за деньги, не выводятся (решение владельца). Донат — только скины (план: Telegram Stars).
- Вкус владельца: минимализм, тёмная тема «клуб» (фон #0d090b, акцент #e3305f), столы однотонные (узоры = «колхоз»), никаких чужих логотипов, качество важнее количества.
