"""MULBERRY API: аккаунты через Telegram initData (Mini App) или токен сессии (Android-приложение, вход через бота), баланс и скины на сервере. Только stdlib.
nginx: /monaco/api/ -> 127.0.0.1:8098. Данные: users.json рядом (одна запись на Telegram id)."""
import base64, hashlib, hmac, json, os, secrets, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qsl

ROOT = Path(__file__).parent
TOKEN = (ROOT / ".env").read_text().split("=", 1)[1].strip()
DB = ROOT / "users.json"
START_BAL, BONUS, MAX_BAL = 5000, 1000, 50_000_000
ITEMS = {  # каталог скинов и цены в игровых фишках: должен совпадать с SK в index.html
    "back": {"raspberry": 0, "classic": 10000, "blue": 10000, "gold": 10000, "sticker": 15000, "mbblack": 15000, "mbnavy": 15000, "mbemerald": 15000, "mbplum": 15000, "mbcream": 15000, "noir": 15000, "snow": 15000, "ltnavy": 15000, "ltwine": 15000, "ltgreen": 15000, "ltgrey": 15000, "casino": 25000, "csgreen": 25000, "csblue": 25000, "csblack": 25000, "cspurple": 25000, "mono": 25000, "argyle": 25000, "wine": 25000, "agreen": 25000, "agrey": 25000, "atan": 25000, "night": 30000, "nspurple": 30000, "nsteal": 30000, "nsblack": 30000, "nsburg": 30000, "berryfield": 50000, "berrypink": 50000, "berrymint": 50000, "berrysky": 50000, "berrycream": 50000, "berrylemon": 50000, "berrylilac": 50000, "berrypeach": 50000, "berrygreen": 50000, "berryblack": 50000, "berrynoir": 50000, "bblush": 40000, "bmint": 40000, "bsky": 40000, "blav": 40000, "bcherry": 40000, "botanica": 40000, "blemon": 40000, "baqua": 40000, "bnight": 40000, "bnoir": 40000, "vruby": 60000, "velvet": 60000, "vnoir": 60000, "vemerald": 60000, "vnavy": 60000, "vplum": 60000, "vcognac": 60000, "vrose": 60000, "vteal": 60000, "vsapph": 60000, "volive": 60000, "vgraph": 60000, "royal": 120000, "rgreen": 120000, "rburg": 120000, "rblack": 120000, "rpurple": 120000, "gatsby": 150000, "gemerald": 150000, "gnavy": 150000, "gburg": 150000, "gsilver": 150000, "mosaic": 60000, "mzblue": 60000, "mzred": 60000, "mzgreen": 60000, "mzblack": 60000, "aurora": 75000, "apink": 75000, "ablue": 75000, "dcoonyx": 90000, "dcoemerald": 90000, "dconavy": 90000, "dcoburg": 90000, "glcdollar": 50000, "glcazure": 50000, "glcmauve": 50000, "glcsepia": 50000, "mrbcarrara": 80000, "mrbnero": 80000, "mrbverde": 80000, "mrbrosa": 80000, "mngcocoa": 60000, "mngblack": 60000, "mngwine": 60000, "mngnavy": 60000, "crwblue": 110000, "crwblack": 110000, "crwpurple": 110000, "crwred": 110000, "cbnred": 40000, "cbnblue": 40000, "cbngold": 40000, "cbngreen": 40000, "mbred": 15000, "mbteal": 15000, "mbsand": 15000, "mbgraph": 15000, "mbsky": 15000, "ltplum": 15000, "ltteal": 15000, "ltcocoa": 15000, "ltcream": 15000, "csteal": 25000, "csorange": 25000, "csgold": 25000, "cspink": 25000, "anavy": 25000, "aplum": 25000, "ateal": 25000, "ared": 25000, "nsgreen": 30000, "nsrose": 30000, "nsindigo": 30000, "vcopper": 60000, "vforest": 60000, "vmidnight": 60000, "vberry": 60000, "rteal": 120000, "rcopper": 120000, "rgrey": 120000, "gpurple": 150000, "gteal": 150000, "grose": 150000, "mzpurple": 60000, "mzgold": 60000, "mzpink": 60000, "aviolet": 75000, "alime": 75000, "asunset": 75000, "vlys": 18000, "vwillow": 60000, "vwautumn": 70000, "vwnight": 85000, "vwgold": 120000, "vdamverde": 95000, "vvelours": 310000, "vjardin": 450000, "voeillet": 740000, "vcygne": 1100000, "vcerf": 640000, "vrusse": 2700000},
    "face": {"classic": 0},
    "felt": {"emerald": 0, "green": 0, "red": 15000, "grey": 15000, "purple": 15000, "choco": 15000, "olive": 15000, "pink": 15000, "berry": 15000, "midnight": 15000, "teal": 15000, "blue": 15000, "orange": 15000, "sand": 15000, "plum": 15000, "black": 15000, "forest": 15000, "wine": 15000, "slate": 15000, "mint": 15000, "indigo": 15000, "copper": 15000, "sage": 15000, "sky": 15000, "mauve": 15000, "sepia": 15000, "stone": 15000, "fgold": 15000, "vfruby": 60000, "vfemerald": 60000, "vfnoir": 60000, "vfnavy": 60000, "vfplum": 60000, "vfcopper": 60000, "rfnavy": 100000, "rfgreen": 100000, "rfburg": 100000, "rfblack": 100000, "rfpurple": 100000, "gfblack": 120000, "gfemerald": 120000, "gfnavy": 120000, "gfburg": 120000, "mfteal": 50000, "mfnavy": 50000, "mfsand": 50000, "mfred": 50000, "mfblack": 50000, "mfgreen": 50000, "vgred": 50000, "vggreen": 50000, "vgblue": 50000, "vgblack": 50000, "vgpurple": 50000, "dfonyx": 90000, "dfemerald": 90000, "dfnavy": 90000, "dfburg": 90000, "cfblue": 110000, "cfblack": 110000, "cfpurple": 110000, "cfred": 110000, "nfpink": 60000, "nfcyan": 60000, "nflime": 60000, "nfsunset": 60000, "nfvegas": 60000, "nfmint": 60000, "sfdusk": 40000, "sfocean": 40000, "sfrose": 40000, "sfaurora": 40000, "sfember": 40000, "sflagoon": 40000, "pfclassicblue": 15000, "pfwillowsage": 15000, "pfwillowautumn": 15000, "pfwillownight": 15000, "pfwillowgold": 15000, "pfdamaskverde": 15000, "pfveloursrouge": 15000, "pfjardinbleu": 15000, "pfoeilletbordeaux": 15000, "pfcerfjaune": 15000, "pfcygneviolet": 15000, "pfrusseantique": 15000},
    "chip": {"classic": 0, "cred": 10000, "ocean": 10000, "cgreen": 10000, "csage": 10000, "csky": 10000, "cmauve": 10000, "csepia": 10000, "cstone": 10000, "cgoldc": 10000, "cblack": 10000, "mono": 20000, "ice": 20000, "lred": 20000, "lgreen": 20000, "candy": 30000, "pastel": 30000, "retro": 30000, "neon": 30000, "vegas": 30000, "berry": 35000, "bcnoir": 35000, "bcmint": 35000, "bcsky": 35000, "sunset": 30000, "cscred": 30000, "cscgreen": 30000, "cscblue": 30000, "cscblack": 30000, "vcruby": 60000, "vcwine": 60000, "vcnoir": 60000, "vcemerald": 60000, "vcnavy": 60000, "vcplum": 60000, "royal": 90000, "rcnavy": 90000, "rcgreen": 90000, "rcburg": 90000, "rcblack": 90000, "gold": 120000, "noir": 120000, "gcemerald": 120000, "gcnavy": 120000, "gcburg": 120000, "corange": 10000, "cpurple": 10000, "cteal": 10000, "cpink": 10000, "lblue": 20000, "lpurple": 20000, "lgold": 20000, "lpink": 20000, "cscpurple": 30000, "cscteal": 30000, "cscorange": 30000, "cscpink": 30000, "bclilac": 35000, "bcpeach": 35000, "bclemon": 35000, "vccopper": 60000, "vcforest": 60000, "vcmidnight": 60000, "vcberry": 60000, "rcteal": 90000, "rccopper": 90000, "rcgrey": 90000, "gcpurple": 120000, "gcteal": 120000, "gcrose": 120000, "dconyx": 80000, "dcemerald": 80000, "dcnavy": 80000, "dcburg": 80000, "ccblue": 100000, "ccblack": 100000, "ccpurple": 100000, "ccred": 100000, "pcclassicblue": 10000, "pcwillowsage": 10000, "pcwillowautumn": 10000, "pcwillownight": 10000, "pcwillowgold": 10000, "pcdamaskverde": 10000, "pcveloursrouge": 10000, "pcjardinbleu": 10000, "pcoeilletbordeaux": 10000, "pccerfjaune": 10000, "pccygneviolet": 10000, "pcrusseantique": 10000},
}
# паки: рубашка + стол + фишки в одном стиле дешевле, чем по отдельности; должны совпадать с PACKS в index.html
PACKS = {"classicred": (24500, {"back": "classic", "felt": "red", "chip": "cred"}),
         "classicblue": (24500, {"back": "blue", "felt": "pfclassicblue", "chip": "pcclassicblue"}),
         "willowsage": (59500, {"back": "vwillow", "felt": "pfwillowsage", "chip": "pcwillowsage"}),
         "willowautumn": (66500, {"back": "vwautumn", "felt": "pfwillowautumn", "chip": "pcwillowautumn"}),
         "willownight": (77000, {"back": "vwnight", "felt": "pfwillownight", "chip": "pcwillownight"}),
         "willowgold": (101500, {"back": "vwgold", "felt": "pfwillowgold", "chip": "pcwillowgold"}),
         "damaskverde": (84000, {"back": "vdamverde", "felt": "pfdamaskverde", "chip": "pcdamaskverde"}),
         "veloursrouge": (234500, {"back": "vvelours", "felt": "pfveloursrouge", "chip": "pcveloursrouge"}),
         "jardinbleu": (332500, {"back": "vjardin", "felt": "pfjardinbleu", "chip": "pcjardinbleu"}),
         "oeilletbordeaux": (535500, {"back": "voeillet", "felt": "pfoeilletbordeaux", "chip": "pcoeilletbordeaux"}),
         "cygneviolet": (787500, {"back": "vcygne", "felt": "pfcygneviolet", "chip": "pccygneviolet"}),
         "cerfjaune": (465500, {"back": "vcerf", "felt": "pfcerfjaune", "chip": "pccerfjaune"}),
         "russeantique": (1907500, {"back": "vrusse", "felt": "pfrusseantique", "chip": "pcrusseantique"})}


def pack_price(pk, r):  # уже купленное из пака вычитается пропорционально
    price, its = PACKS[pk]
    full = sum(ITEMS[k][i] for k, i in its.items())
    left = sum(ITEMS[k][i] for k, i in its.items() if i not in r["own"][k])
    return round(price * left / full / 100) * 100 if full else 0


lock = threading.Lock()
users = json.loads(DB.read_text()) if DB.exists() else {}
ADMINS = {"8283052665"}  # владелец: админка в профиле
PROMO = ROOT / "promos.json"  # промокоды: {КОД: {rw, skin:[k,id]|None, max, until, on, used:[uid], created}}
promos = json.loads(PROMO.read_text()) if PROMO.exists() else {}
PRICES = ROOT / "prices.json"  # правки цен из админки поверх каталога: {k: {id: цена}, "pack": {id: цена}}
prices = json.loads(PRICES.read_text()) if PRICES.exists() else {}


def save_json(path, obj):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False))
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def apply_prices():
    for k, d in prices.items():
        if k == "hide":
            continue
        for i, p in d.items():
            if k == "pack" and i in PACKS:
                PACKS[i] = (p, PACKS[i][1])
            elif k in ITEMS and i in ITEMS[k]:
                ITEMS[k][i] = p


def persist():
    tmp = DB.with_suffix(".tmp")
    tmp.write_text(json.dumps(users, ensure_ascii=False))
    os.chmod(tmp, 0o600)
    os.replace(tmp, DB)


def check(init_data):
    """Проверка подписи Telegram WebApp initData. Возвращает user dict или None."""
    try:
        d = dict(parse_qsl(init_data, strict_parsing=True))
        h = d.pop("hash")
        dcs = "\n".join(f"{k}={v}" for k, v in sorted(d.items()))
        secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest(), h):
            return None
        if time.time() - int(d.get("auth_date", 0)) > 7 * 86400:
            return None
        return json.loads(d["user"])
    except Exception:
        return None


# ---------- вход из Android-приложения через бота (там нет Telegram initData) ----------
# приложение: login_start -> код -> t.me/MulberryPokerBot?start=login_<код> -> бот шлёт login_bind -> приложение login_poll -> токен сессии
SESSION_FILE = ROOT / ".session"  # секрет подписи токенов сессии, создаётся сам при первом запуске (chmod 600)
if not SESSION_FILE.exists():
    SESSION_FILE.write_text(secrets.token_hex(32))
    os.chmod(SESSION_FILE, 0o600)
SESSION_KEY = SESSION_FILE.read_text().strip().encode()
BIND_KEY = hmac.new(TOKEN.encode(), b"mulberry-login-bind", hashlib.sha256).hexdigest()  # bot.py считает так же
LOGIN_TTL, SESSION_TTL = 300, 365 * 86400  # код живёт 5 минут; токен — год
logins = {}  # код -> {"t": время создания, "u": user от бота или None}
APP_ORIGINS = {"https://localhost", "http://localhost", "capacitor://localhost"}  # WebView Capacitor на Android/iOS
VERSION_FILE = ROOT / "version.json"  # {"apk": номер сборки (versionCode) последнего APK, "url": "ссылка на канал"}


def b64(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def session_make(u):
    body = b64(json.dumps({"u": u, "iat": int(time.time())}, ensure_ascii=False, separators=(",", ":")).encode())
    return body + "." + b64(hmac.new(SESSION_KEY, body.encode(), hashlib.sha256).digest())


def session_check(tok):
    """Токен сессии приложения. Возвращает user dict (как в initData) или None."""
    try:
        body, sig = str(tok).split(".", 1)
        if not hmac.compare_digest(b64(hmac.new(SESSION_KEY, body.encode(), hashlib.sha256).digest()), sig):
            return None
        d = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if time.time() - d["iat"] > SESSION_TTL or not d["u"].get("id"):
            return None
        return d["u"]
    except Exception:
        return None


def login_gc():
    now = time.time()
    for c in [c for c, x in logins.items() if now - x["t"] > LOGIN_TTL]:
        del logins[c]


def login_act(act, q):
    """Действия входа без авторизации. Возвращает (code, obj) или None, если act не про вход."""
    if act == "version":
        try:
            return 200, json.loads(VERSION_FILE.read_text())
        except Exception:
            return 200, {}
    if act not in ("login_start", "login_bind", "login_poll"):
        return None
    with lock:
        login_gc()
        if act == "login_start":
            if len(logins) > 2000:
                return 429, {"error": "busy"}
            c = secrets.token_hex(8)
            logins[c] = {"t": time.time(), "u": None}
            return 200, {"code": c, "ttl": LOGIN_TTL}
        c = str(q.get("code", ""))
        x = logins.get(c)
        if act == "login_bind":  # только от bot.py: ключ выводится из токена бота
            if not hmac.compare_digest(str(q.get("key", "")), BIND_KEY):
                return 403, {"error": "key"}
            u = q.get("user") or {}
            if not x or x["u"] or not isinstance(u.get("id"), int):
                return 410, {"error": "code"}
            x["u"] = {k: u[k] for k in ("id", "first_name", "last_name", "username") if u.get(k)}
            return 200, {"ok": True}
        if not x:
            return 410, {"error": "code"}
        if not x["u"]:
            return 200, {"wait": True}
        del logins[c]  # одноразовый
        return 200, {"token": session_make(x["u"]), "user": x["u"]}


def today():
    return time.strftime("%Y-%m-%d", time.gmtime(time.time() + 3 * 3600))  # сутки по МСК


# бонус дня растёт, если заходить подряд: 1-й день 1 000 … 7-й и дальше 10 000; пропуск — серия с начала
BONUS_SER = [1000, 1500, 2000, 3000, 4000, 6000, 10000]
# задания дня: 3 из списка (выбор по дате), прогресс = рост счётчика статистики за сегодня
QUESTS = [("bj10", "Сыграй 10 раздач в блэкджек", "bj", 10, 1500), ("bjw5", "Выиграй 5 раздач в блэкджек", "bjw", 5, 2000),
          ("pk10", "Сыграй 10 раздач в покер", "hands", 10, 1500), ("pkw3", "Выиграй 3 раздачи в покере", "wins", 3, 2500),
          ("dk2", "Сыграй 2 партии в дурака", "dk", 2, 2000), ("dkw1", "Не останься дураком 2 раза", "dkw", 2, 2500),
          ("bc10", "Сыграй 10 раздач в баккару", "bc", 10, 1500)]


def yday():
    return time.strftime("%Y-%m-%d", time.gmtime(time.time() + 3 * 3600 - 86400))


def streak(r):  # серия, которая будет после сегодняшнего бонуса (если ещё не забран) или текущая
    if r["bonus"] == today():
        return r.get("streak", 1)
    # бонус, взятый до появления серий, хранился без streak — считаем его первым днём
    return r.get("streak", 1 if r["bonus"] else 0) + 1 if r["bonus"] == yday() else 1


def quests(r):
    d = today()
    if (r.get("qd") or {}).get("day") != d:
        r["qd"] = {"day": d, "base": dict(r["st"]), "done": []}
    k = sum(map(ord, d))
    pick = [QUESTS[(k + i * 3) % len(QUESTS)] for i in range(3)]
    q = r["qd"]
    return [{"id": i, "t": t, "p": min(g, r["st"].get(c, 0) - q["base"].get(c, 0)), "g": g, "rw": rw, "done": i in q["done"]} for i, t, c, g, rw in pick]


def rec(u):
    uid = str(u["id"])
    r = users.get(uid)
    if not r:
        r = users[uid] = {"bal": START_BAL, "own": {k: [next(iter(ITEMS[k]))] for k in ITEMS},
                          "eq": {k: next(iter(ITEMS[k])) for k in ITEMS}, "bonus": "",
                          "st": {"hands": 0, "wins": 0, "bj": 0, "bjw": 0}, "created": int(time.time())}
    r["name"] = (u.get("first_name") or "") + (" " + u["last_name"] if u.get("last_name") else "")
    r["username"] = u.get("username", "")
    for k in ("dk", "dkw", "bc"):
        r["st"].setdefault(k, 0)
    for k in ITEMS:  # новые категории у старых записей
        first = next(iter(ITEMS[k]))  # бесплатный скин категории есть у всех
        if first not in r["own"].setdefault(k, []):
            r["own"][k].append(first)
        if r["eq"].get(k) not in ITEMS[k] or r["eq"][k] not in r["own"][k]:
            r["eq"][k] = first
    return r


def view(uid, r):
    return {"id": int(uid), "name": r["name"], "username": r["username"], "bal": r["bal"], "own": r["own"], "eq": r["eq"],
            "bonus": r["bonus"] != today(), "st": r["st"], "created": r["created"], "adm": uid in ADMINS, "prices": prices,
            "streak": streak(r), "next": BONUS_SER[min(streak(r), 7) - 1], "quests": quests(r)}


# ---------- комнаты: блэкджек-дуэль вдвоём по коду ----------
# Всё считает сервер: колода, карты, ходы, выплата. Клиент раз в секунду спрашивает room_get.
# Фишки двигаются только в конце раздачи (проигравший -ставка, победитель +ставка), поэтому
# перезапуск сервера посреди раздачи ничего не отнимает. Комнаты живут в памяти.
import random
rooms = {}
DIRTY = [False]  # баланс поменялся в комнате: сохранить users.json
TURN_S, ROOM_TTL = 25, 1800
RK, SU = "23456789TJQKA", "shdc"


def bjt(h):
    t = a = 0
    for c in h:
        if c[0] == "A":
            a += 1
            t += 11
        else:
            t += 10 if c[0] in "TJQK" else int(c[0])
    while t > 21 and a:
        t -= 10
        a -= 1
    return t


def rdeal(rm):
    if len(rm["shoe"]) < 30:
        rm["shoe"] = [r + s for r in RK for s in SU] * 4
        random.shuffle(rm["shoe"])
    return rm["shoe"].pop()


def rstart(rm):
    for p in rm["p"]:
        p.update(h=[], st="play", ready=False)
    f = rm["first"]
    for k in range(4):
        rm["p"][(f + k) % 2]["h"].append(rdeal(rm))
    rm.update(phase="play", turn=f, res=None, n=rm["n"] + 1)
    radvance(rm)


def radvance(rm):
    """Автостоп на 21, перебор, передача хода, конец раздачи."""
    while rm["phase"] == "play":
        p = rm["p"][rm["turn"]]
        t = bjt(p["h"])
        if p["st"] == "play" and t < 21:
            rm["dl"] = time.time() + TURN_S
            return
        if p["st"] == "play":
            p["st"] = "bust" if t > 21 else "stand"
        if rm["turn"] == rm["first"] and p["st"] != "bust":
            rm["turn"] = 1 - rm["first"]
            continue
        rend(rm)


def rend(rm, left=None):
    a, b = rm["p"]
    ta, tb = bjt(a["h"]), bjt(b["h"])
    if left is not None:
        w = 1 - left
    elif ta > 21 and tb > 21 or (ta <= 21 and tb <= 21 and ta == tb):
        w = -1
    elif ta > 21:
        w = 1
    elif tb > 21:
        w = 0
    else:
        w = 0 if ta > tb else 1
    if w >= 0:
        win, lose = users[rm["p"][w]["id"]], users[rm["p"][1 - w]["id"]]
        amt = min(rm["bet"], lose["bal"])
        lose["bal"] -= amt
        win["bal"] = min(MAX_BAL, win["bal"] + amt)
        rm["p"][w]["score"] += 1
    rm.update(phase="end", turn=-1, res={"w": w, "t": [ta, tb], "left": left})
    DIRTY[0] = True
    rm["first"] = 1 - rm["first"]


def rview(rm, uid):
    me = 0 if rm["p"][0]["id"] == uid else 1
    show = rm["phase"] == "end"
    ps = []
    for i, p in enumerate(rm["p"]):
        h = p["h"] if (i == me or show) else p["h"][:1] + ["X"] * (len(p["h"]) - 1)
        ps.append({"name": p["name"], "h": h, "st": p["st"], "score": p["score"], "ready": p["ready"],
                   "t": bjt(p["h"]) if (i == me or show) else None})
    if len(ps) == 1:
        ps.append(None)
    return {"code": rm["code"], "bet": rm["bet"], "phase": rm["phase"], "me": me, "p": ps, "turn": rm["turn"], "n": rm["n"],
            "res": rm["res"], "left": max(0, int(rm.get("dl", 0) - time.time())) if rm["phase"] == "play" else None}


def rtick():
    now = time.time()
    for code, rm in list(rooms.items()):
        if now - rm["seen"] > ROOM_TTL:
            del rooms[code]
        elif rm["phase"] == "play" and now > rm["dl"]:  # время хода вышло: «хватит»
            rm["p"][rm["turn"]]["st"] = "stand"
            radvance(rm)


def room_act(act, q, uid, r):
    rtick()
    if act == "room_new":
        bet = q.get("bet")
        if not isinstance(bet, int) or not 10 <= bet <= MAX_BAL:
            return 400, {"error": "bet"}
        if r["bal"] < bet:
            return 402, {"error": "money"}
        code = next(c for c in (f"{random.randint(1000, 9999)}" for _ in range(100)) if c not in rooms)
        rooms[code] = {"code": code, "bet": bet, "phase": "wait", "first": 0, "turn": -1, "n": 0, "res": None, "seen": time.time(),
                       "shoe": [], "p": [{"id": uid, "name": r["name"] or "Игрок", "h": [], "st": "", "score": 0, "ready": False}]}
        return 200, {"room": rview(rooms[code], uid)}
    rm = rooms.get(str(q.get("code", "")))
    if not rm:
        return 404, {"error": "room"}
    ids = [p["id"] for p in rm["p"]]
    if act == "room_join":
        if uid not in ids:
            if len(ids) == 2:
                return 409, {"error": "full"}
            if r["bal"] < rm["bet"]:
                return 402, {"error": "money", "bet": rm["bet"]}
            rm["p"].append({"id": uid, "name": r["name"] or "Игрок", "h": [], "st": "", "score": 0, "ready": False})
            rm["phase"] = "ready"
    elif uid not in ids:
        return 403, {"error": "not in room"}
    rm["seen"] = time.time()
    me = ids.index(uid) if uid in ids else len(rm["p"]) - 1
    p = rm["p"][me]
    if act == "room_leave":
        if rm["phase"] == "play":
            rend(rm, left=me)
        if len(rm["p"]) == 2:
            rm["p"].pop(me)
            rm.update(phase="wait", turn=-1)
            rm["p"][0].update(h=[], st="", ready=False)
            rm["gone"] = p["name"]
        else:
            del rooms[rm["code"]]
        return 200, {"ok": True}
    if act == "room_ready" and rm["phase"] in ("ready", "end") and len(rm["p"]) == 2:
        if r["bal"] < rm["bet"]:
            return 402, {"error": "money"}
        p["ready"] = True
        if all(x["ready"] for x in rm["p"]):
            if any(users[x["id"]]["bal"] < rm["bet"] for x in rm["p"]):
                for x in rm["p"]:
                    x["ready"] = False
                return 402, {"error": "friend money", "room": rview(rm, uid)}
            rstart(rm)
    elif act in ("room_hit", "room_stand") and rm["phase"] == "play" and rm["turn"] == me:
        if act == "room_hit":
            p["h"].append(rdeal(rm))
        else:
            p["st"] = "stand"
        radvance(rm)
    v = rview(rm, uid)
    v["gone"] = rm.pop("gone", None) if rm["phase"] == "wait" else None
    return 200, {"room": v}


# ---------- публичные онлайн-столы блэкджека: до 5 живых игроков против дилера ----------
# Всё ведёт сервер: ставки списываются при ставке, выплата при расчёте. Раунд: приём ставок (10 с после
# первой ставки или сразу, когда поставили все) → раздача → ходы по очереди (20 с, иначе «хватит») →
# дилер добирает до 17 → расчёт → 5 с показ итога → снова ставки. Пустой стол просто ждёт.
# Столы создают игроки (pt_new): публичный виден в pt_list, приватный — только по коду. Пустой стол удаляется.
PT_LV = [(10, 500), (50, 2000), (100, 5000), (500, 20000), (1000, 50000), (5000, 200000)]  # должны совпадать с BJT в index.html (min/max)
PT_SEATS, PT_BET_S, PT_TURN_S, PT_END_S, PT_IDLE = 5, 10, 20, 5, 180
PT_INS_S = 10  # секунд на решение о страховке
ptables = {}
SEQ = [0]


def new_code():
    used = set(rooms) | {t["code"] for t in ptables.values()} | {t["code"] for t in dtables.values()} | {t["code"] for t in ktables.values()} | {t["code"] for t in ctables.values()}
    return next(c for c in (f"{random.randint(1000, 9999)}" for _ in range(200)) if c not in used)


def gc_tables(tabs):
    now = time.time()
    for k, t in list(tabs.items()):
        if not t["seats"] and now - t["made"] > 20:
            del tabs[k]


def pt_new(q, r):
    lvl = q.get("lvl")
    if not isinstance(lvl, int) or not 0 <= lvl < len(PT_LV):
        return None
    SEQ[0] += 1
    k = "b%d" % SEQ[0]
    ptables[k] = {"id": k, "min": PT_LV[lvl][0], "max": PT_LV[lvl][1], "lvl": lvl, "pub": bool(q.get("pub")), "code": new_code(),
                  "name": r["name"] or "Игрок", "made": time.time(), "seats": [], "phase": "bet", "dl": 0, "turn": -1, "d": [], "shoe": [], "n": 0}
    return ptables[k]


def pt_card(t):
    if len(t["shoe"]) < 60:
        t["shoe"] = [r + s for r in RK for s in SU] * 6
        random.shuffle(t["shoe"])
    return t["shoe"].pop()


def pt_betting(t):
    return [s for s in t["seats"] if s["bet"] > 0]


def pt_deal(t):
    t["d"] = []
    for s in t["seats"]:
        s["h"], s["st"], s["res"], s["dbl"], s["h2"], s["b2"], s["ai"], s["ins"] = [], "", "", False, None, 0, 0, 0
    for _ in range(2):
        for s in pt_betting(t):
            s["h"].append(pt_card(t))
        t["d"].append(pt_card(t))
    for s in pt_betting(t):
        s["st"] = "bj" if bjt(s["h"]) == 21 else "play"
    t["phase"], t["n"] = "play", t["n"] + 1
    if t["d"][0][0] == "A":  # у дилера туз — сначала страховка (как в игре с ботами)
        for s in pt_betting(t):
            s["ins"] = None
        t["phase"], t["dl"], t["turn"] = "ins", time.time() + PT_INS_S, -1
        return
    pt_after_ins(t)


def pt_after_ins(t):
    t["phase"] = "play"
    for s in pt_betting(t):
        if s.get("ins") is None:
            s["ins"] = 0
    if bjt(t["d"]) == 21:  # у дилера блэкджек — сразу расчёт
        return pt_settle(t)
    t["turn"] = -1
    pt_next(t)


def pt_next(t):
    """Передать ход следующему живому игроку, иначе — дилер и расчёт."""
    seats = t["seats"]
    for i in range(t["turn"] + 1, len(seats)):
        if seats[i]["bet"] > 0 and seats[i]["st"] == "play":
            t["turn"], t["dl"] = i, time.time() + PT_TURN_S
            return
    t["turn"] = -1
    if any(s["st"] in ("stand", "play") for s in pt_betting(t)):  # есть живая рука (после сплита st=stand, если жива хоть одна)
        while bjt(t["d"]) < 17:
            t["d"].append(pt_card(t))
    pt_settle(t)


def pt_settle(t):
    d = bjt(t["d"])
    dbj = d == 21 and len(t["d"]) == 2
    for s in pt_betting(t):
        split, win, staked, rs = s.get("h2") is not None, 0, 0, []
        for h, bet in [(s["h"], s["bet"])] + ([(s["h2"], s["b2"])] if split else []):
            p, pbj = bjt(h), bjt(h) == 21 and len(h) == 2 and not split
            if p > 21:
                w, res = 0, "перебор"
            elif pbj and not dbj:
                w, res = bet * 5 // 2, "блэкджек"
            elif dbj and not pbj:
                w, res = 0, "проигрыш"
            elif d > 21 or p > d:
                w, res = bet * 2, "выигрыш"
            elif p == d:
                w, res = bet, "ничья"
            else:
                w, res = 0, "проигрыш"
            win, staked = win + w, staked + bet
            rs.append(res)
        if s.get("ins"):  # страховка: половина ставки, при блэкджеке дилера платит 2:1
            win, staked = win + (s["ins"] * 3 if dbj else 0), staked + s["ins"]
        u = users.get(s["uid"])
        if u:
            u["bal"] = min(MAX_BAL, u["bal"] + win)
            u["st"]["bj"] = u["st"].get("bj", 0) + 1
            u["st"]["bjw"] = u["st"].get("bjw", 0) + (1 if win > staked else 0)
        s["res"], s["net"] = (rs[0] if len(rs) == 1 else "сплит"), win - staked
    t["phase"], t["turn"], t["dl"] = "end", -1, time.time() + PT_END_S
    DIRTY[0] = True


def pt_tick(t):
    now = time.time()
    if t["phase"] != "play":  # ушедших убираем только между раздачами; несыгранную ставку возвращаем
        for s in [s for s in t["seats"] if now - s["seen"] >= PT_IDLE]:
            if t["phase"] == "bet" and s["bet"] and s["uid"] in users:
                users[s["uid"]]["bal"] += s["bet"]
                DIRTY[0] = True
            t["seats"].remove(s)
    if t["phase"] == "bet":
        bs = pt_betting(t)
        if bs and (len(bs) == len(t["seats"]) and all(s.get("ready") for s in t["seats"]) or now > t["dl"]):
            pt_deal(t)
    elif t["phase"] == "ins" and (now > t["dl"] or all(s.get("ins") is not None for s in pt_betting(t))):
        pt_after_ins(t)
    elif t["phase"] == "play" and t["turn"] >= 0 and now > t["dl"]:
        t["seats"][t["turn"]]["st"] = "stand"  # время хода вышло
        pt_next(t)
    elif t["phase"] == "end" and now > t["dl"]:
        for s in t["seats"]:
            s.update(bet=0, h=[], st="", res="", ready=False, net=0)
        t.update(phase="bet", d=[], dl=0, turn=-1)


def pt_view(t, uid):
    hide = t["phase"] in ("play", "ins")
    me = next((i for i, s in enumerate(t["seats"]) if s["uid"] == uid), -1)
    return {"id": t["id"], "min": t["min"], "max": t["max"], "lvl": t["lvl"], "pub": t["pub"], "code": t["code"], "name": t["name"], "phase": t["phase"], "n": t["n"], "turn": t["turn"], "me": me,
            "left": max(0, int(t["dl"] - time.time())) if t["dl"] else None,
            "d": (t["d"][:1] + ["X"] if hide and len(t["d"]) == 2 else t["d"]), "dt": None if hide else (bjt(t["d"]) if t["d"] else None),
            "seats": [{"name": s["name"], "bet": s["bet"] + s.get("b2", 0), "h": s["h"], "t": bjt(s["h"]) if s["h"] else None, "st": s["st"],
                       "h2": s.get("h2"), "t2": bjt(s["h2"]) if s.get("h2") else None, "ai": s.get("ai", 0),
                       "res": s["res"], "net": s.get("net", 0), "ready": s.get("ready", False), "ins": s.get("ins")} for s in t["seats"]]}


def pt_act(act, q, uid, r):
    for t in ptables.values():
        pt_tick(t)
    gc_tables(ptables)
    if act == "pt_list":
        return 200, {"tables": [{"id": k, "lvl": t["lvl"], "n": len(t["seats"]), "name": t["name"], "min": t["min"], "max": t["max"]}
                                for k, t in ptables.items() if t["pub"] and t["seats"]]}
    if act == "pt_new":
        if r["bal"] < PT_LV[q.get("lvl") if isinstance(q.get("lvl"), int) and 0 <= q.get("lvl") < len(PT_LV) else 0][0]:
            return 402, {"error": "money"}
        t = pt_new(q, r)
        if not t:
            return 400, {"error": "lvl"}
        act = "pt_join"
    else:
        t = ptables.get(str(q.get("t", ""))) or next((x for x in ptables.values() if q.get("code") and x["code"] == str(q.get("code"))), None)
    if not t:
        return 404, {"error": "table"}
    seat = next((s for s in t["seats"] if s["uid"] == uid), None)
    if act == "pt_join":
        if not seat:
            if len(t["seats"]) >= PT_SEATS:
                return 409, {"error": "full"}
            seat = {"uid": uid, "name": r["name"] or "Игрок", "bet": 0, "h": [], "st": "", "res": "", "seen": time.time()}
            t["seats"].append(seat)
    elif not seat:
        return 403, {"error": "not seated"}
    seat["seen"] = time.time()
    if act == "pt_leave":
        if t["phase"] == "play" and seat["bet"] > 0 and seat["st"] == "play":
            seat["st"] = "stand"  # ставка остаётся на столе и доигрывается «хватит»
            if t["turn"] == t["seats"].index(seat):
                pt_next(t)
        if not (t["phase"] == "play" and seat["bet"] > 0):
            t["seats"].remove(seat)
        else:
            seat["seen"] = 0
        return 200, {"ok": True}
    if act == "pt_bet" and t["phase"] == "bet":
        amt = q.get("amt")
        if not isinstance(amt, int) or amt < 0:
            return 400, {"error": "bet"}
        new = seat["bet"] + amt
        if amt and (new < t["min"] or new > t["max"]):
            return 400, {"error": "limit", "min": t["min"], "max": t["max"]}
        if r["bal"] < amt:
            return 402, {"error": "money"}
        r["bal"] -= amt
        seat["bet"] = new
        if not t["dl"] and seat["bet"]:
            t["dl"] = time.time() + PT_BET_S
        DIRTY[0] = True
    elif act == "pt_clear" and t["phase"] == "bet":
        r["bal"] += seat["bet"]
        seat["bet"], seat["ready"] = 0, False
        DIRTY[0] = True
    elif act == "pt_ready" and t["phase"] == "bet" and seat["bet"]:
        seat["ready"] = True
    elif act == "pt_ins" and t["phase"] == "ins" and seat["bet"] > 0 and seat.get("ins") is None:
        cost = seat["bet"] // 2 if q.get("y") else 0
        if cost and r["bal"] < cost:
            return 402, {"error": "money"}
        r["bal"] -= cost
        seat["ins"] = cost
        DIRTY[0] = True
        if all(s.get("ins") is not None for s in pt_betting(t)):
            pt_after_ins(t)
    elif act in ("pt_hit", "pt_stand", "pt_dbl", "pt_split") and t["phase"] == "play" and t["turn"] >= 0 and t["seats"][t["turn"]] is seat:
        # после сплита две руки: h (ставка bet) и h2 (b2), ai — какая сейчас играет
        two = seat.get("h2") is not None
        h = seat["h2"] if two and seat.get("ai") else seat["h"]
        done = False
        if act == "pt_split":
            cv = lambda c: 10 if c[0] in "TJQK" else 11 if c[0] == "A" else int(c[0])
            if two or len(h) != 2 or cv(h[0]) != cv(h[1]) or r["bal"] < seat["bet"]:
                return 409, {"error": "split"}
            r["bal"] -= seat["bet"]
            seat["h2"], seat["b2"], seat["ai"] = [seat["h"].pop()], seat["bet"], 0
            seat["h"].append(pt_card(t))
            seat["h2"].append(pt_card(t))
            DIRTY[0] = True
            if seat["h"][0][0] == "A":  # тузы после сплита — по одной карте, обе руки готовы
                seat["ai"], done = 1, True
            elif bjt(seat["h"]) == 21:
                seat["ai"] = 1
                done = bjt(seat["h2"]) == 21
        elif act == "pt_dbl":
            bet = seat["b2"] if two and seat.get("ai") else seat["bet"]
            if len(h) != 2 or r["bal"] < bet:
                return 402, {"error": "money"}
            r["bal"] -= bet
            if two and seat.get("ai"):
                seat["b2"] *= 2
            else:
                seat["bet"] *= 2
            h.append(pt_card(t))
            done = True
            DIRTY[0] = True
        elif act == "pt_hit":
            h.append(pt_card(t))
            done = bjt(h) >= 21
        else:
            done = True
        two = seat.get("h2") is not None
        if done:
            if two and not seat.get("ai"):
                seat["ai"] = 1
                if bjt(seat["h2"]) == 21:
                    done = True
                else:
                    done = False
            if done:
                hs = [seat["h"]] + ([seat["h2"]] if two else [])
                seat["st"] = "bust" if all(bjt(x) > 21 for x in hs) else "stand"
        if seat["st"] != "play":
            pt_next(t)
        else:
            t["dl"] = time.time() + PT_TURN_S
    pt_tick(t)
    return 200, {"pt": pt_view(t, uid)}


# ---------- публичные онлайн-столы Дурака: 2–6 живых игроков, всё ведёт сервер ----------
# Столы: p1..p5 — подкидной, t1..t5 — переводной, ставки как DKT в index.html. Партия стартует,
# когда за столом ≥2 и все нажали «Готов». Таймеры: первый ход и защита 25 с (иначе: ход младшей картой /
# «беру»), после отбоя 6 с на подкидывание (иначе «бито»). Ставка списывается при старте, дурак теряет,
# остальные делят. Ушедший посреди партии — автоматически берёт/ходит младшей, пока не станет дураком или не выйдет.
DK_STAKES = [50, 250, 1000, 5000, 20000, 100000]
DR_ = "6789TJQKA"
DK_SEATS, DK_TURN_S, DK_THROW_S, DK_END_S, DK_IDLE = 6, 25, 15, 8, 300
dtables = {}  # создают игроки (dko_new), как столы блэкджека


def dk_r(c):
    return DR_.index(c[0])


def dk_beats(t, d, a):
    return (d[1] == a[1] and dk_r(d) > dk_r(a)) or (d[1] == t["trump"] and a[1] != t["trump"])


def dk_live(t):
    return [i for i, s in enumerate(t["seats"]) if not s.get("out")]


def dk_next(t, i):
    n = len(t["seats"])
    for k in range(1, n + 1):
        j = (i + k) % n
        if not t["seats"][j].get("out"):
            return j
    return i


def dk_ranks(t):
    r = set()
    for x in t["table"]:
        r.add(x["a"][0])
        if x.get("d"):
            r.add(x["d"][0])
    return r


def dk_start(t):
    deck = [r + s for r in DR_ for s in SU]
    random.shuffle(deck)
    t.update(deck=deck, trump=deck[0][1], tcard=deck[0], table=[], bito=0, took=False, phase="play", n=t["n"] + 1, res=None, order=[])
    for s in t["seats"]:
        u = users.get(s["uid"])
        if u:
            u["bal"] = max(0, u["bal"] - t["stake"])
        s.update(hand=[deck.pop() for _ in range(6)], out=False, passed=False, ready=False, tag="")
    best, t["att"] = 99, 0
    for i, s in enumerate(t["seats"]):
        for c in s["hand"]:
            if c[1] == t["trump"] and dk_r(c) < best:
                best, t["att"] = dk_r(c), i
    dk_bout(t)
    DIRTY[0] = True


def dk_bout(t):
    t["table"], t["took"] = [], False
    for s in t["seats"]:
        s["passed"], s["tag"] = False, ""
    if t["seats"][t["att"]].get("out") or not t["seats"][t["att"]]["hand"]:
        t["att"] = dk_next(t, t["att"])
    t["def"] = dk_next(t, t["att"])
    t["limit"] = min(6, len(t["seats"][t["def"]]["hand"]))
    t["dl"] = time.time() + DK_TURN_S


def dk_unbeaten(t):
    return [k for k, x in enumerate(t["table"]) if not x.get("d")]


def dk_can_transfer(t):
    tb = t["table"]
    if t["mode"] != "t" or not tb or any(x.get("d") or x["a"][0] != tb[0]["a"][0] for x in tb):
        return False
    nx = dk_next(t, t["def"])
    return nx != t["def"] and len(t["seats"][nx]["hand"]) >= len(tb) + 1  # вдвоём тоже можно — обратно атакующему


def dk_touch(t):
    """Что-то изменилось на столе: снять «пас» у атакующих и перезапустить таймер."""
    for s in t["seats"]:
        s["passed"] = False
    t["dl"] = time.time() + (DK_TURN_S if dk_unbeaten(t) and not t["took"] else DK_THROW_S)


def dk_end_bout(t):
    d = t["seats"][t["def"]]
    if t["took"]:
        for x in t["table"]:
            d["hand"].append(x["a"])
            if x.get("d"):
                d["hand"].append(x["d"])
        nxt = dk_next(t, t["def"])
    else:
        t["bito"] += sum(1 + (1 if x.get("d") else 0) for x in t["table"])
        nxt = t["def"]
    # добор: атакующий, остальные по кругу, защитник последним
    order, i = [t["att"]], t["att"]
    for _ in range(len(t["seats"])):
        i = dk_next(t, i)
        if i != t["def"] and i not in order:
            order.append(i)
    order.append(t["def"])
    for j in order:
        s = t["seats"][j]
        while len(s["hand"]) < 6 and t["deck"]:
            s["hand"].append(t["deck"].pop())
    t["table"] = []
    if not t["deck"]:
        for s in t["seats"]:
            if not s.get("out") and not s["hand"]:
                s["out"] = True
                t["order"].append(s["uid"])
    live = [s for s in t["seats"] if not s.get("out") and s["hand"]]
    if len(live) < 2:
        return dk_finish(t, live[0] if live else None)
    t["att"] = nxt
    dk_bout(t)


def dk_finish(t, dur):
    n = len(t["seats"])
    share = t["stake"] // max(1, n - 1)
    for s in t["seats"]:
        u = users.get(s["uid"])
        if not u:
            continue
        u["st"]["dk"] = u["st"].get("dk", 0) + 1
        u["st"]["dkw"] = u["st"].get("dkw", 0) + (0 if s is dur else 1)
        if dur is None:
            u["bal"] += t["stake"]
            s["net"] = 0
        elif s is dur:
            s["net"] = -t["stake"]
        else:
            u["bal"] = min(MAX_BAL, u["bal"] + t["stake"] + share)
            s["net"] = share
    t.update(phase="end", res={"dur": dur["name"] if dur else None}, dl=time.time() + DK_END_S)
    DIRTY[0] = True


def dk_auto(t):
    """Истёк таймер: за молчащего игрока делаем самое простое."""
    if t["phase"] != "play":
        return
    if not t["table"]:  # первый ход — младшей некозырной
        h = sorted(t["seats"][t["att"]]["hand"], key=lambda c: (c[1] == t["trump"], dk_r(c)))
        return dk_do(t, t["att"], "attack", h[0])
    if dk_unbeaten(t) and not t["took"]:
        return dk_do(t, t["def"], "take")
    dk_end_bout(t)


def dk_do(t, i, act, card=None, idx=None):
    """Одно действие игрока i. Возвращает текст ошибки или None."""
    s = t["seats"][i]
    if act == "attack":
        if t["table"] or i != t["att"] or card not in s["hand"]:
            return "move"
        s["hand"].remove(card)
        t["table"].append({"a": card})
        dk_touch(t)
    elif act == "throw":
        if not t["table"] or i == t["def"] or s.get("out") or card not in s["hand"] or card[0] not in dk_ranks(t) or len(t["table"]) >= t["limit"]:
            return "move"
        s["hand"].remove(card)
        t["table"].append({"a": card})
        dk_touch(t)
    elif act == "defend":
        un = dk_unbeaten(t)
        if i != t["def"] or t["took"] or card not in s["hand"] or idx not in un or not dk_beats(t, card, t["table"][idx]["a"]):
            return "move"
        s["hand"].remove(card)
        t["table"][idx]["d"] = card
        dk_touch(t)
    elif act == "transfer":
        if i != t["def"] or card not in s["hand"] or not dk_can_transfer(t) or card[0] != t["table"][0]["a"][0]:
            return "move"
        s["hand"].remove(card)
        t["table"].append({"a": card})
        s["tag"] = "перевёл"
        t["att"], t["def"] = i, dk_next(t, i)
        t["limit"] = min(6, len(t["seats"][t["def"]]["hand"]))
        dk_touch(t)
    elif act == "take":
        if i != t["def"] or t["took"] or not dk_unbeaten(t):
            return "move"
        t["took"], s["tag"] = True, "беру"
        dk_touch(t)
    elif act == "pass":
        if i == t["def"]:
            return "move"
        s["passed"] = True
    else:
        return "act"
    # конец боя: всё отбито (или защитник берёт) и все атакующие сказали «пас» или им нечем подкинуть
    if t["phase"] == "play" and (t["took"] or not dk_unbeaten(t)) and t["table"]:
        r = dk_ranks(t)
        waiting = [j for j in dk_live(t) if j != t["def"] and not t["seats"][j]["passed"]
                   and len(t["table"]) < t["limit"] and any(c[0] in r for c in t["seats"][j]["hand"])]
        if not waiting:
            dk_end_bout(t)
    return None


def dk_tick(t):
    now = time.time()
    if t["phase"] != "play":
        for s in [s for s in t["seats"] if now - s["seen"] >= DK_IDLE]:
            t["seats"].remove(s)
    if t["phase"] == "wait":
        if len(t["seats"]) >= 2 and all(s.get("ready") for s in t["seats"]):
            dk_start(t)
    elif t["phase"] == "play" and now > t["dl"]:
        dk_auto(t)
    elif t["phase"] == "end" and now > t["dl"]:
        for s in t["seats"]:
            s.update(hand=[], out=False, ready=False, tag="", net=0)
        t.update(phase="wait", table=[], res=None)
        t["seats"] = [s for s in t["seats"] if now - s["seen"] < 60]


def dk_view(t, uid):
    me = next((i for i, s in enumerate(t["seats"]) if s["uid"] == uid), -1)
    v = {"id": t["id"], "mode": t["mode"], "stake": t["stake"], "lvl": t["lvl"], "pub": t["pub"], "code": t["code"], "name": t["name"], "phase": t["phase"], "n": t["n"], "me": me,
         "seats": [{"name": s["name"], "cards": len(s.get("hand", [])), "out": s.get("out", False), "ready": s.get("ready", False),
                    "tag": s.get("tag", ""), "passed": s.get("passed", False), "net": s.get("net", 0)} for s in t["seats"]]}
    if t["phase"] in ("play", "end") and t.get("deck") is not None:
        v.update(trump=t["trump"], tcard=t["tcard"], deck=len(t["deck"]), bito=t["bito"], table=t["table"], att=t.get("att", -1),
                 dfn=t.get("def", -1), limit=t.get("limit", 6), took=t.get("took", False),
                 left=max(0, int(t.get("dl", 0) - time.time())), res=t.get("res"), transfer=dk_can_transfer(t) if t["phase"] == "play" else False)
        if me >= 0:
            v["hand"] = t["seats"][me].get("hand", [])
    return v


def dko_act(act, q, uid, r):
    for t in dtables.values():
        dk_tick(t)
    gc_tables(dtables)
    if act == "dko_list":
        return 200, {"tables": [{"id": k, "mode": t["mode"], "lvl": t["lvl"], "n": len(t["seats"]), "name": t["name"], "stake": t["stake"], "play": t["phase"] != "wait"}
                                for k, t in dtables.items() if t["pub"] and t["seats"]]}
    if act == "dko_new":
        lvl, m = q.get("lvl"), q.get("m")
        if not isinstance(lvl, int) or not 0 <= lvl < len(DK_STAKES) or m not in ("p", "t"):
            return 400, {"error": "lvl"}
        if r["bal"] < DK_STAKES[lvl]:
            return 402, {"error": "money"}
        SEQ[0] += 1
        k = "d%d" % SEQ[0]
        dtables[k] = {"id": k, "mode": m, "stake": DK_STAKES[lvl], "lvl": lvl, "pub": bool(q.get("pub")), "code": new_code(), "name": r["name"] or "Игрок",
                      "made": time.time(), "seats": [], "phase": "wait", "n": 0}
        t, act = dtables[k], "dko_join"
    else:
        t = dtables.get(str(q.get("t", ""))) or next((x for x in dtables.values() if q.get("code") and x["code"] == str(q.get("code"))), None)
    if not t:
        return 404, {"error": "table"}
    i = next((k for k, s in enumerate(t["seats"]) if s["uid"] == uid), -1)
    if act == "dko_join":
        if i < 0:
            if len(t["seats"]) >= DK_SEATS or t["phase"] != "wait":
                return 409, {"error": "full" if len(t["seats"]) >= DK_SEATS else "playing"}
            t["seats"].append({"uid": uid, "name": r["name"] or "Игрок", "hand": [], "seen": time.time()})
            i = len(t["seats"]) - 1
    elif i < 0:
        return 403, {"error": "not seated"}
    s = t["seats"][i]
    s["seen"] = time.time()
    if act == "dko_leave":
        if t["phase"] == "play" and not s.get("out"):
            s["seen"] = 0  # за ушедшего доиграет таймер
        else:
            t["seats"].remove(s)
        return 200, {"ok": True}
    if act == "dko_ready" and t["phase"] == "wait":
        if r["bal"] < t["stake"]:
            return 402, {"error": "money"}
        s["ready"] = not s.get("ready")
    elif act == "dko_move" and t["phase"] == "play":
        err = dk_do(t, i, str(q.get("a", "")), q.get("c"), q.get("i"))
        if err:
            return 409, {"error": err, "dko": dk_view(t, uid)}
    dk_tick(t)
    return 200, {"dko": dk_view(t, uid)}



# ---------- онлайн-покер: Холдем и Омаха, 2–6 живых игроков, всё ведёт сервер ----------
# Фишки игрока = его баланс: ставка списывается сразу, банк выплачивается на вскрытии (рестарт сервера = потерян только текущий банк).
# Раздача стартует сама, если за столом ≥2 игроков с балансом ≥ BB. Ход 20 с, иначе чек/пас. Ушедший — пас, место освобождается после раздачи.
PK_LV = [(10, 20), (25, 50), (50, 100), (100, 200), (250, 500), (500, 1000), (1000, 2000), (2500, 5000), (5000, 10000)]  # = TABLES в index.html
PK_SEATS, PK_TURN_S, PK_END_S, PK_IDLE = 6, 20, 6, 120
ktables = {}
PRK = "23456789TJQKA"
PK_CAT = ["Старшая карта", "Пара", "Две пары", "Сет", "Стрит", "Флеш", "Фулл-хаус", "Каре", "Стрит-флеш"]


def pk_ev5(cs):
    rs = sorted((PRK.index(c[0]) for c in cs), reverse=True)
    fl = len({c[1] for c in cs}) == 1
    u = sorted(set(rs), reverse=True)
    st = None
    if len(u) == 5 and u[0] - u[4] == 4:
        st = u[0]
    elif u == [12, 3, 2, 1, 0]:
        st = 3
    cnt = sorted(((rs.count(r), r) for r in set(rs)), reverse=True)
    g = [r for _, r in cnt]
    if st is not None and fl:
        return (8, st)
    if cnt[0][0] == 4:
        return (7, *g)
    if cnt[0][0] == 3 and cnt[1][0] == 2:
        return (6, *g)
    if fl:
        return (5, *rs)
    if st is not None:
        return (4, st)
    if cnt[0][0] == 3:
        return (3, *g)
    if cnt[0][0] == 2 and cnt[1][0] == 2:
        return (2, *g)
    if cnt[0][0] == 2:
        return (1, *g)
    return (0, *rs)


def pk_best(hole, board, omaha):
    from itertools import combinations
    if omaha:
        return max(pk_ev5(list(h) + list(b)) for h in combinations(hole, 2) for b in combinations(board, 3))
    return max(pk_ev5(list(c)) for c in combinations(list(hole) + list(board), 5))


def pk_new(q, r):
    lvl = q.get("lvl")
    if not isinstance(lvl, int) or not 0 <= lvl < len(PK_LV):
        return None
    SEQ[0] += 1
    k = "k%d" % SEQ[0]
    ktables[k] = {"id": k, "lvl": lvl, "sb": PK_LV[lvl][0], "bb": PK_LV[lvl][1], "v": "o" if q.get("v") == "o" else "h", "pub": bool(q.get("pub")),
                  "code": new_code(), "name": r["name"] or "Игрок", "made": time.time(), "seats": [], "phase": "wait", "dl": time.time() + 3,
                  "n": 0, "board": [], "dealer": -1, "cur": -1, "bet": 0, "minr": 0, "log": "", "res": None}
    return ktables[k]


def pk_bal(s):  # фишки игрока за столом: взятые с собой (stk), но не больше баланса
    u = users.get(s["uid"])
    return min(u["bal"], s.get("stk", u["bal"])) if u else 0


def pk_take(t, s, amt):  # поставить amt (не больше баланса), вернуть сколько реально
    u = users.get(s["uid"])
    amt = max(0, min(amt, pk_bal(s)))
    if u:
        u["bal"] -= amt
    s["bet"] += amt
    s["tot"] += amt
    if "stk" in s:
        s["stk"] -= amt
    if pk_bal(s) == 0:
        s["allin"] = True
    DIRTY[0] = True
    return amt


def pk_live(t):
    return [s for s in t["seats"] if s.get("in") and not s["fold"]]


def pk_can(s):
    return s.get("in") and not s["fold"] and not s["allin"]


def pk_order(t, start):  # индексы игроков, начиная с start по кругу
    n = len(t["seats"])
    return [(start + k) % n for k in range(n)]


def pk_start(t):
    bb = t["bb"]
    for s in t["seats"]:  # кончились фишки за столом — докупаем столько же, сколько брал с собой (из баланса)
        if s.get("stk", bb) < bb:
            s["stk"] = s.get("bx", 100) * bb
    ready = [s for s in t["seats"] if pk_bal(s) >= bb and time.time() - s["seen"] < PK_IDLE]
    if len(ready) < 2:
        return False
    deck = [r + su for r in PRK for su in "shdc"]
    random.shuffle(deck)
    for s in t["seats"]:
        s.update(cards=[], bet=0, tot=0, fold=False, allin=False, acted=False, act="", show=False, win=0, hn="")
        s["in"] = s in ready
    n = len(t["seats"])
    d = t["dealer"]
    for k in range(1, n + 1):
        if t["seats"][(d + k) % n]["in"]:
            d = (d + k) % n
            break
    ins = [i for i in pk_order(t, d + 1) if t["seats"][i]["in"]]
    sb_i = d if len(ins) == 2 else ins[0]
    bb_i = ins[0] if len(ins) == 2 else ins[1]
    t.update(phase="play", deck=deck, board=[], dealer=d, n=t["n"] + 1, res=None, street=0, log="")
    for _ in range(4 if t["v"] == "o" else 2):
        for i in ins:
            t["seats"][i]["cards"].append(deck.pop())
    pk_take(t, t["seats"][sb_i], t["sb"])
    t["seats"][sb_i]["act"] = "SB"
    pk_take(t, t["seats"][bb_i], bb)
    t["seats"][bb_i]["act"] = "BB"
    t["bet"], t["minr"] = bb, bb
    t["cur"] = -1
    pk_next(t, bb_i)
    return True


def pk_next(t, frm):
    """Следующий, кто должен ходить после frm; если круг ставок закрыт — следующая улица или вскрытие."""
    live = pk_live(t)
    if len(live) == 1:
        return pk_finish(t)
    n = len(t["seats"])
    for k in range(1, n + 1):
        i = (frm + k) % n
        s = t["seats"][i]
        if pk_can(s) and (not s["acted"] or s["bet"] < t["bet"]):
            t["cur"], t["dl"] = i, time.time() + PK_TURN_S
            return
    # круг закрыт
    if len([s for s in live if not s["allin"]]) <= 1 and all(s["bet"] >= t["bet"] or s["allin"] for s in live):
        while len(t["board"]) < 5:  # все в ва-банке — докладываем борд
            t["board"].append(t["deck"].pop())
        return pk_finish(t)
    if len(t["board"]) == 5:
        return pk_finish(t)
    t["board"] += [t["deck"].pop() for _ in range(3 if not t["board"] else 1)]
    for s in t["seats"]:
        s["bet"], s["acted"] = 0, False
        if s.get("in") and not s["fold"] and s["act"] not in ("Ва-банк",):
            s["act"] = ""
    t["bet"], t["minr"] = 0, t["bb"]
    pk_next(t, t["dealer"])


def pk_finish(t):
    live = pk_live(t)
    t["cur"] = -1
    show = len(live) > 1
    sc = {id(s): pk_best(s["cards"], t["board"], t["v"] == "o") for s in live} if show else {}
    # банки: по уровням вложений
    levels = sorted({s["tot"] for s in t["seats"] if s.get("in") and s["tot"] > 0})
    prev, wins = 0, []
    for lv in levels:
        part = sum(min(s["tot"], lv) - min(s["tot"], prev) for s in t["seats"] if s.get("in"))
        elig = [s for s in live if s["tot"] >= lv]
        prev = lv
        if not part or not elig:
            continue
        if len(elig) == 1 and sum(1 for s in t["seats"] if s.get("in") and s["tot"] >= lv) == 1:
            s = elig[0]  # 02.10: неуравненную часть ставки просто возвращаем — это не выигрыш
            if "stk" in s:
                s["stk"] += part
            u = users.get(s["uid"])
            if u:
                u["bal"] = min(MAX_BAL, u["bal"] + part)
            continue
        if show:
            best = max(sc[id(s)] for s in elig)
            w = [s for s in elig if sc[id(s)] == best]
        else:
            w = elig
        share = part // len(w)
        for j, s in enumerate(w):
            got = share + (part - share * len(w) if j == 0 else 0)
            s["win"] += got
            if "stk" in s:
                s["stk"] += got
            u = users.get(s["uid"])
            if u:
                u["bal"] = min(MAX_BAL, u["bal"] + got)
    for s in live:
        s["show"] = show
        if show:
            s["hn"] = PK_CAT[sc[id(s)][0]]
    for s in t["seats"]:
        if s.get("in"):
            u = users.get(s["uid"])
            if u:
                u["st"]["hands"] = u["st"].get("hands", 0) + 1
                u["st"]["wins"] = u["st"].get("wins", 0) + (1 if s["win"] > 0 else 0)
    top = max(live, key=lambda s: s["win"])
    t["res"] = {"w": [s["name"] for s in live if s["win"] > 0], "hn": top.get("hn", "")}
    t.update(phase="end", dl=time.time() + PK_END_S)
    DIRTY[0] = True


def pk_tick(t):
    now = time.time()
    if t["phase"] == "play" and t["cur"] >= 0 and now > t["dl"]:
        s = t["seats"][t["cur"]]
        pk_do(t, s, "check" if s["bet"] >= t["bet"] else "fold", 0)
    elif t["phase"] in ("end", "wait") and now > t["dl"]:
        t["seats"] = [s for s in t["seats"] if now - s["seen"] < PK_IDLE and not s.get("gone")]
        t.update(phase="wait", board=[], cur=-1, res=None, dl=now + 2)
        for s in t["seats"]:
            s.update(cards=[], bet=0, tot=0, fold=False, allin=False, act="", show=False, win=0, hn="", **{"in": False})
        if not pk_start(t):
            t["dl"] = now + 2


def pk_do(t, s, a, to):
    i = t["seats"].index(s)
    if t["phase"] != "play" or t["cur"] != i:
        return "turn"
    tc = t["bet"] - s["bet"]
    if a == "fold":
        s["fold"], s["act"] = True, "Пас"
    elif a == "check":
        if tc > 0:
            return "check"
        s["act"] = "Чек"
    elif a == "call":
        pk_take(t, s, tc)
        s["act"] = "Ва-банк" if s["allin"] else ("Колл" if tc else "Чек")
    elif a == "raise":
        if not isinstance(to, int):
            return "amount"
        hi = s["bet"] + pk_bal(s)
        if t["v"] == "o":
            pot = sum(x["tot"] for x in t["seats"])
            hi = min(hi, t["bet"] + pot + tc)
        lo = min(hi, t["bet"] + t["minr"])
        to = max(lo, min(hi, to))
        if to <= t["bet"]:
            return "amount"
        if to - t["bet"] >= t["minr"]:
            t["minr"] = to - t["bet"]
            for x in t["seats"]:
                x["acted"] = False
        t["bet"] = to
        pk_take(t, s, to - s["bet"])
        s["act"] = "Ва-банк" if s["allin"] else "Рейз"
    else:
        return "act"
    s["acted"] = True
    pk_next(t, i)
    return ""


def pk_view(t, uid):
    me = next((i for i, s in enumerate(t["seats"]) if s["uid"] == uid), -1)
    v = {"id": t["id"], "lvl": t["lvl"], "sb": t["sb"], "bb": t["bb"], "v": t["v"], "pub": t["pub"], "code": t["code"], "name": t["name"],
         "phase": t["phase"], "n": t["n"], "me": me, "dealer": t["dealer"], "cur": t["cur"], "bet": t["bet"], "minr": t["minr"],
         "pot": sum(s.get("tot", 0) for s in t["seats"]), "board": t["board"], "res": t["res"],
         "left": max(0, int(t["dl"] - time.time())) if t["phase"] == "play" else None,
         "seats": [{"name": s["name"], "chips": pk_bal(s), "bet": s.get("bet", 0), "fold": s.get("fold", False), "allin": s.get("allin", False), "in": s.get("in", False),
                    "act": s.get("act", ""), "nc": len(s.get("cards", [])), "win": s.get("win", 0), "hn": s.get("hn", ""),
                    "cards": s.get("cards", []) if (s["uid"] == uid or s.get("show")) else []} for s in t["seats"]]}
    return v


def pko_act(act, q, uid, r):
    for t in ktables.values():
        pk_tick(t)
    gc_tables(ktables)
    if act == "pko_list":
        return 200, {"tables": [{"id": k, "lvl": t["lvl"], "v": t["v"], "n": len(t["seats"]), "name": t["name"], "sb": t["sb"], "bb": t["bb"]}
                                for k, t in ktables.items() if t["pub"] and t["seats"]]}
    if act == "pko_new":
        lvl = q.get("lvl")
        if not isinstance(lvl, int) or not 0 <= lvl < len(PK_LV):
            return 400, {"error": "lvl"}
        if r["bal"] < PK_LV[lvl][1] * 10:
            return 402, {"error": "money"}
        t, act = pk_new(q, r), "pko_join"
    else:
        t = ktables.get(str(q.get("t", ""))) or next((x for x in ktables.values() if q.get("code") and x["code"] == str(q.get("code"))), None)
    if not t:
        return 404, {"error": "table"}
    s = next((x for x in t["seats"] if x["uid"] == uid), None)
    if act == "pko_join":
        if not s:
            if len(t["seats"]) >= PK_SEATS:
                return 409, {"error": "full"}
            if r["bal"] < t["bb"] * 10:
                return 402, {"error": "money"}
            bx = q.get("bx") if isinstance(q.get("bx"), int) else 100  # сколько больших блайндов взять с собой
            bx = max(10, min(100000, bx))
            s = {"uid": uid, "name": r["name"] or "Игрок", "seen": time.time(), "cards": [], "bet": 0, "tot": 0, "fold": False, "allin": False, "act": "", "in": False,
                 "bx": bx, "stk": min(r["bal"], bx * t["bb"])}
            t["seats"].append(s)
            if t["phase"] == "wait":
                t["dl"] = min(t["dl"], time.time() + 2)
    elif not s:
        return 403, {"error": "not seated"}
    s["seen"] = time.time()
    if act == "pko_leave":
        if t["phase"] == "play" and s.get("in") and not s["fold"]:
            if t["cur"] == t["seats"].index(s):
                pk_do(t, s, "fold", 0)
            else:
                s["fold"], s["act"] = True, "Пас"
                if len(pk_live(t)) == 1:
                    pk_finish(t)
            s["gone"] = True
        else:
            t["seats"].remove(s)
        return 200, {"ok": True}
    if act == "pko_move":
        err = pk_do(t, s, str(q.get("a", "")), q.get("to"))
        if err:
            return 409, {"error": err, "pko": pk_view(t, uid)}
    pk_tick(t)
    return 200, {"pko": pk_view(t, uid)}



# ---------- онлайн-баккара: до 7 игроков, все ставят против банка; сервер раздаёт и платит ----------
# Ставки 15 с после первой (или сразу, когда все нажали «Готов»), ставка списывается сразу. Ничья: ставки на игрока/банкира возвращаются.
BC_LV = [(10, 1000), (50, 5000), (100, 10000), (500, 50000), (1000, 100000), (5000, 500000)]  # = BCT в index.html
BC_SEATS, BC_BET_S, BC_END_S, BC_IDLE = 7, 15, 7, 180
ctables = {}


def bc_v(c):
    return 1 if c[0] == "A" else 0 if c[0] in "TJQK" else int(c[0])


def bc_t(h):
    return sum(bc_v(c) for c in h) % 10


def bc_deal(t):
    if len(t["shoe"]) < 20:
        t["shoe"] = [r + su for r in RK for su in SU] * 8
        random.shuffle(t["shoe"])
    P, B = [], []
    for _ in range(2):
        P.append(t["shoe"].pop())
        B.append(t["shoe"].pop())
    pt, bt, p3 = bc_t(P), bc_t(B), None
    if pt < 8 and bt < 8:
        if pt <= 5:
            P.append(t["shoe"].pop())
            p3 = bc_v(P[2])
        bt = bc_t(B)
        if p3 is None:
            draw = bt <= 5
        else:
            draw = bt <= 2 or (bt == 3 and p3 != 8) or (bt == 4 and 2 <= p3 <= 7) or (bt == 5 and 4 <= p3 <= 7) or (bt == 6 and p3 in (6, 7))
        if draw:
            B.append(t["shoe"].pop())
    pt, bt = bc_t(P), bc_t(B)
    r = "p" if pt > bt else "b" if bt > pt else "t"
    for s in t["seats"]:
        b = s["bets"]
        ret = (b["p"] * 2 if r == "p" else 0) + (b["b"] + b["b"] * 95 // 100 if r == "b" else 0) + (b["t"] * 9 + b["p"] + b["b"] if r == "t" else 0)
        s["net"] = ret - (b["p"] + b["t"] + b["b"])
        u = users.get(s["uid"])
        if u and (b["p"] or b["t"] or b["b"]):
            u["bal"] = min(MAX_BAL, u["bal"] + ret)
            u["st"]["bc"] = u["st"].get("bc", 0) + 1
    t["hist"] = (t["hist"] + [r])[-14:]
    t.update(phase="end", P=P, B=B, r=r, n=t["n"] + 1, dl=time.time() + BC_END_S)
    DIRTY[0] = True


def bc_tick(t):
    now = time.time()
    if t["phase"] == "bet":
        for s in [s for s in t["seats"] if now - s["seen"] >= BC_IDLE]:
            u = users.get(s["uid"])
            if u:
                u["bal"] += sum(s["bets"].values())
            t["seats"].remove(s)
            DIRTY[0] = True
        bs = [s for s in t["seats"] if sum(s["bets"].values())]
        if bs and (all(s.get("ready") for s in bs) and len(bs) == len(t["seats"]) or (t["dl"] and now > t["dl"])):
            bc_deal(t)
    elif t["phase"] == "end" and now > t["dl"]:
        for s in t["seats"]:
            s.update(bets={"p": 0, "t": 0, "b": 0}, ready=False, net=0)
        t.update(phase="bet", dl=0, P=[], B=[], r="")


def bc_view(t, uid):
    me = next((i for i, s in enumerate(t["seats"]) if s["uid"] == uid), -1)
    return {"id": t["id"], "lvl": t["lvl"], "min": t["min"], "max": t["max"], "pub": t["pub"], "code": t["code"], "name": t["name"], "phase": t["phase"], "n": t["n"],
            "me": me, "P": t.get("P", []), "B": t.get("B", []), "r": t.get("r", ""), "hist": t["hist"], "left": max(0, int(t["dl"] - time.time())) if t["dl"] else None,
            "seats": [{"name": s["name"], "bets": s["bets"], "ready": s.get("ready", False), "net": s.get("net", 0)} for s in t["seats"]]}


def bco_act(act, q, uid, r):
    for t in ctables.values():
        bc_tick(t)
    gc_tables(ctables)
    if act == "bco_list":
        return 200, {"tables": [{"id": k, "lvl": t["lvl"], "n": len(t["seats"]), "name": t["name"], "min": t["min"], "max": t["max"]} for k, t in ctables.items() if t["pub"] and t["seats"]]}
    if act == "bco_new":
        lvl = q.get("lvl")
        if not isinstance(lvl, int) or not 0 <= lvl < len(BC_LV):
            return 400, {"error": "lvl"}
        SEQ[0] += 1
        k = "c%d" % SEQ[0]
        ctables[k] = {"id": k, "lvl": lvl, "min": BC_LV[lvl][0], "max": BC_LV[lvl][1], "pub": bool(q.get("pub")), "code": new_code(), "name": r["name"] or "Игрок",
                      "made": time.time(), "seats": [], "phase": "bet", "dl": 0, "n": 0, "shoe": [], "hist": []}
        t, act = ctables[k], "bco_join"
    else:
        t = ctables.get(str(q.get("t", ""))) or next((x for x in ctables.values() if q.get("code") and x["code"] == str(q.get("code"))), None)
    if not t:
        return 404, {"error": "table"}
    s = next((x for x in t["seats"] if x["uid"] == uid), None)
    if act == "bco_join":
        if not s:
            if len(t["seats"]) >= BC_SEATS:
                return 409, {"error": "full"}
            s = {"uid": uid, "name": r["name"] or "Игрок", "seen": time.time(), "bets": {"p": 0, "t": 0, "b": 0}, "ready": False, "net": 0}
            t["seats"].append(s)
    elif not s:
        return 403, {"error": "not seated"}
    s["seen"] = time.time()
    if act == "bco_leave":
        if t["phase"] == "bet":
            r["bal"] += sum(s["bets"].values())
            DIRTY[0] = True
        t["seats"].remove(s)
        return 200, {"ok": True}
    if act == "bco_bet" and t["phase"] == "bet" and not s.get("ready"):
        z, amt = q.get("z"), q.get("amt")
        if z not in ("p", "t", "b") or not isinstance(amt, int) or amt <= 0:
            return 400, {"error": "bet"}
        if s["bets"][z] + amt > t["max"]:
            return 400, {"error": "limit"}
        if r["bal"] < amt:
            return 402, {"error": "money"}
        r["bal"] -= amt
        s["bets"][z] += amt
        if not t["dl"]:
            t["dl"] = time.time() + BC_BET_S
        DIRTY[0] = True
    elif act == "bco_clear" and t["phase"] == "bet" and not s.get("ready"):
        r["bal"] += sum(s["bets"].values())
        s["bets"] = {"p": 0, "t": 0, "b": 0}
        DIRTY[0] = True
    elif act == "bco_ready" and t["phase"] == "bet" and sum(s["bets"].values()):
        if any(0 < v < t["min"] for v in s["bets"].values()):
            return 400, {"error": "min"}
        s["ready"] = True
    bc_tick(t)
    return 200, {"bco": bc_view(t, uid)}


def all_tables():
    return [ptables, dtables, ktables, ctables]


def adm_user_row(k, x):
    return {"id": k, "name": x.get("name"), "username": x.get("username"), "bal": x["bal"], "ban": bool(x.get("ban")), "seen": x.get("seen", 0),
            "created": x.get("created", 0), "own": x["own"], "st": x["st"]}


def adm_act(act, q):
    """Админка владельца: сводка, игроки (фишки, скины, бан), промокоды, цены."""
    now = time.time()
    if act == "adm_stats":
        at = set()
        for tabs in all_tables():
            for tb in tabs.values():
                at.update(str(s["uid"]) for s in tb["seats"])
        at.update(str(x["id"]) for rm in rooms.values() for x in rm["p"])
        real = {k: x for k, x in users.items() if not k.startswith("99900000")}
        return 200, {"users": len(real), "online": sum(1 for x in real.values() if now - x.get("seen", 0) < 300),
                     "day": sum(1 for x in real.values() if now - x.get("seen", 0) < 86400), "tables": len(at),
                     "new": sum(1 for x in real.values() if now - x.get("created", 0) < 86400), "chips": sum(x["bal"] for x in real.values()),
                     "banned": sum(1 for x in real.values() if x.get("ban")), "promos": sum(1 for x in promos.values() if x["on"])}
    if act == "adm_users":
        s = str(q.get("q", "")).strip().lower().lstrip("@")
        rows = [adm_user_row(k, x) for k, x in users.items() if not s or s in k or s in (x.get("name") or "").lower() or s in (x.get("username") or "").lower()]
        rows.sort(key=lambda x: -x["seen"])
        return 200, {"users": rows[:40]}
    uid = str(q.get("id", ""))
    if act in ("adm_grant", "adm_skin", "adm_ban", "adm_user"):
        x = users.get(uid)
        if not x:
            return 404, {"error": "user"}
        if act == "adm_grant":
            amt = q.get("amt")
            if not isinstance(amt, int):
                return 400, {"error": "amt"}
            x["bal"] = max(0, min(MAX_BAL, x["bal"] + amt))
        elif act == "adm_skin":
            k, i = q.get("k"), q.get("item")
            if k not in ITEMS or i not in ITEMS[k]:
                return 400, {"error": "item"}
            if i not in x["own"][k]:
                x["own"][k].append(i)
        elif act == "adm_ban":
            if uid in ADMINS:
                return 400, {"error": "self"}
            x["ban"] = bool(q.get("ban"))
        if act != "adm_user":
            persist()
        return 200, {"user": adm_user_row(uid, x)}
    if act == "adm_promos":
        return 200, {"promos": [dict(v, code=k, n=len(v["used"]), used=None) for k, v in sorted(promos.items(), key=lambda kv: -kv[1]["created"])]}
    if act == "adm_promo_new":
        c = str(q.get("code", "")).strip().upper()
        rw, mx, days, skin = q.get("rw"), q.get("max"), q.get("days"), q.get("skin")
        if not (2 <= len(c) <= 24) or not c.replace("_", "").replace("-", "").isalnum():
            return 400, {"error": "code"}
        if c in promos:
            return 409, {"error": "exists"}
        if not isinstance(rw, int) or not 0 <= rw <= 10_000_000 or not isinstance(mx, int) or not 1 <= mx <= 1_000_000:
            return 400, {"error": "num"}
        if skin and (not isinstance(skin, list) or len(skin) != 2 or skin[0] not in ITEMS or skin[1] not in ITEMS[skin[0]]):
            return 400, {"error": "item"}
        if not rw and not skin:
            return 400, {"error": "empty"}
        until = time.strftime("%Y-%m-%d", time.gmtime(now + 3 * 3600 + 86400 * int(days))) if isinstance(days, int) and days > 0 else ""
        promos[c] = {"rw": rw, "skin": skin or None, "max": mx, "until": until, "on": True, "used": [], "created": int(now)}
        save_json(PROMO, promos)
        return 200, {"ok": True}
    if act in ("adm_promo_toggle", "adm_promo_del"):
        c = str(q.get("code", "")).upper()
        if c not in promos:
            return 404, {"error": "code"}
        if act == "adm_promo_del":
            del promos[c]
        else:
            promos[c]["on"] = not promos[c]["on"]
        save_json(PROMO, promos)
        return 200, {"ok": True}
    if act == "adm_hide":  # убрать из Маркета / вернуть: у купивших остаётся
        k, i = q.get("k"), q.get("id")
        src = PACKS if k == "pack" else ITEMS.get(k)
        if src is None or i not in src:
            return 400, {"error": "item"}
        h = prices.setdefault("hide", {}).setdefault(k, [])
        if q.get("hide") and i not in h:
            h.append(i)
        elif not q.get("hide") and i in h:
            h.remove(i)
        save_json(PRICES, prices)
        return 200, {"prices": prices}
    if act == "adm_price":  # k: back/felt/chip/pack, ids: [..] (вся линейка), p: цена
        k, ids, p = q.get("k"), q.get("ids"), q.get("p")
        if not isinstance(p, int) or not 0 <= p <= 50_000_000 or not isinstance(ids, list) or not ids:
            return 400, {"error": "num"}
        src = PACKS if k == "pack" else ITEMS.get(k)
        if src is None or any(i not in src for i in ids):
            return 400, {"error": "item"}
        for i in ids:
            if k != "pack" and ITEMS[k][i] == 0 and i == next(iter(ITEMS[k])):
                continue  # базовый бесплатный скин не продаём
            prices.setdefault(k, {})[i] = p
        apply_prices()
        save_json(PRICES, prices)
        return 200, {"prices": prices}
    return 404, {"error": "unknown"}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def reply(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.cors()
        self.end_headers()
        self.wfile.write(b)

    def cors(self):  # приложение (Capacitor) ходит с origin https://localhost
        o = self.headers.get("Origin", "")
        if o in APP_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", o)
            self.send_header("Vary", "Origin")

    def do_OPTIONS(self):
        self.send_response(204)
        self.cors()
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            if n > 20000:
                return self.reply(413, {"error": "big"})
            q = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self.reply(400, {"error": "bad json"})
        if self.path.rstrip("/").endswith("/admin"):  # начисление фишек с сервера: grant.sh, ключ в .admin
            key = (ROOT / ".admin").read_text().strip() if (ROOT / ".admin").exists() else ""
            uid, amt = str(q.get("uid", "")), q.get("amt")
            if not key or q.get("key") != key or not isinstance(amt, int):
                return self.reply(403, {"error": "key"})
            with lock:
                u = users.get(uid) or next((x for k2, x in users.items() if (x.get("username") or "").lower() == uid.lower().lstrip("@") and (uid := k2)), None)
                if not u:
                    return self.reply(404, {"error": "user"})
                old = u["bal"]
                u["bal"] = max(0, min(MAX_BAL, old + amt))
                persist()
                return self.reply(200, {"uid": uid, "name": u.get("name"), "was": old, "bal": u["bal"]})
        act = self.path.rstrip("/").rsplit("/", 1)[-1]
        la = login_act(act, q)
        if la:
            return self.reply(*la)
        u = check(q.get("initData", "")) or (session_check(q["token"]) if q.get("token") else None)  # Telegram или токен приложения
        if not u:
            return self.reply(401, {"error": "auth"})
        with lock:
            r, uid = rec(u), str(u["id"])
            r["seen"] = int(time.time())
            if r.get("ban"):
                return self.reply(403, {"error": "ban"})
            if act.startswith("adm_"):
                if uid not in ADMINS:
                    return self.reply(403, {"error": "admin"})
                code, res = adm_act(act, q)
                return self.reply(code, res)
            if act == "promo":
                c = str(q.get("code", "")).strip().upper()
                pr = promos.get(c)
                if not pr or not pr["on"] or (pr["until"] and pr["until"] < today()) or len(pr["used"]) >= pr["max"]:
                    return self.reply(404, {"error": "promo", "state": view(uid, r)})
                if uid in pr["used"]:
                    return self.reply(409, {"error": "used", "state": view(uid, r)})
                pr["used"].append(uid)
                r["bal"] = min(MAX_BAL, r["bal"] + pr["rw"])
                if pr.get("skin"):
                    k, i = pr["skin"]
                    if k in ITEMS and i in ITEMS[k] and i not in r["own"][k]:
                        r["own"][k].append(i)
                save_json(PROMO, promos)
                persist()
                return self.reply(200, {"rw": pr["rw"], "skin": pr.get("skin"), "state": view(uid, r)})
            if act == "sync":  # клиент сообщает изменение баланса (d) и счётчики после раздачи
                d = q.get("d")
                if isinstance(d, (int, float)) and abs(d) <= MAX_BAL:
                    r["bal"] = max(0, min(MAX_BAL, r["bal"] + int(d)))
                st = q.get("st") or {}
                for k in r["st"]:
                    if isinstance(st.get(k), int) and st[k] >= r["st"][k]:
                        r["st"][k] = st[k]
            elif act == "bonus":
                if r["bonus"] == today():
                    return self.reply(409, {"error": "already", "state": view(uid, r)})
                r["streak"] = streak(r)
                r["bonus"] = today()
                r["bal"] += BONUS_SER[min(r["streak"], 7) - 1]
            elif act == "quest":
                qs = {x["id"]: x for x in quests(r)}
                x = qs.get(q.get("id"))
                if not x or x["done"] or x["p"] < x["g"]:
                    return self.reply(409, {"error": "quest", "state": view(uid, r)})
                r["qd"]["done"].append(x["id"])
                r["bal"] += x["rw"]
            elif act == "refill":  # фишки игровые: при нуле бесплатно даём 2 000
                if r["bal"] < 200:
                    r["bal"] = 2000
            elif act in ("buy", "equip"):
                k, i = q.get("k"), q.get("id")
                if k not in ITEMS or i not in ITEMS[k]:
                    return self.reply(400, {"error": "item"})
                if act == "buy" and i not in r["own"][k]:
                    if i in prices.get("hide", {}).get(k, []):
                        return self.reply(410, {"error": "hidden", "state": view(uid, r)})
                    if r["bal"] < ITEMS[k][i]:
                        return self.reply(402, {"error": "money", "state": view(uid, r)})
                    r["bal"] -= ITEMS[k][i]
                    r["own"][k].append(i)
                if i not in r["own"][k] and ITEMS[k][i] > 0:
                    return self.reply(403, {"error": "not owned"})
                r["eq"][k] = i
            elif act == "sell":  # продать купленный скин обратно: половина текущей цены, базовые не продаются
                k, i = q.get("k"), q.get("id")
                if k not in ITEMS or i not in ITEMS[k] or i not in r["own"][k] or ITEMS[k][i] <= 0:
                    return self.reply(400, {"error": "item", "state": view(uid, r)})
                r["own"][k].remove(i)
                r["bal"] = min(MAX_BAL, r["bal"] + ITEMS[k][i] // 2)
                if r["eq"].get(k) == i:
                    r["eq"][k] = next(iter(ITEMS[k]))
            elif act == "pack":
                pk = q.get("id")
                if pk not in PACKS or pk in prices.get("hide", {}).get("pack", []):
                    return self.reply(400, {"error": "item"})
                cost = pack_price(pk, r)
                if cost <= 0:
                    return self.reply(409, {"error": "owned", "state": view(uid, r)})
                if r["bal"] < cost:
                    return self.reply(402, {"error": "money", "state": view(uid, r)})
                r["bal"] -= cost
                for k, i in PACKS[pk][1].items():
                    if i not in r["own"][k]:
                        r["own"][k].append(i)
                    r["eq"][k] = i
            elif act == "live":  # для главной: сколько публичных столов и игроков онлайн по играм
                cnt = lambda tabs: [len([t for t in tabs.values() if t["pub"] and t["seats"]]), sum(len(t["seats"]) for t in tabs.values())]
                return self.reply(200, {"live": {"pk": cnt(ktables), "bj": cnt(ptables), "dk": cnt(dtables), "bc": cnt(ctables)}, "state": view(uid, r)})
            elif act == "code":  # куда ведёт код: стол блэкджека, стол дурака или старая комната 1 на 1
                c = str(q.get("code", ""))
                hit = next((("pt", t["id"]) for t in ptables.values() if t["code"] == c), None) or next((("dko", t["id"]) for t in dtables.values() if t["code"] == c), None) \
                    or next((("pko", t["id"]) for t in ktables.values() if t["code"] == c), None) or next((("bco", t["id"]) for t in ctables.values() if t["code"] == c), None)
                return self.reply(200, {"kind": hit[0], "id": hit[1]} if hit else {"kind": "room" if c in rooms else ""})
            elif act.startswith("bco_"):
                code, res = bco_act(act, q, uid, r)
                if DIRTY[0]:
                    DIRTY[0] = False
                    persist()
                if code == 200:
                    res["state"] = view(uid, r)
                return self.reply(code, res)
            elif act.startswith("pko_"):
                code, res = pko_act(act, q, uid, r)
                if DIRTY[0]:
                    DIRTY[0] = False
                    persist()
                if code == 200:
                    res["state"] = view(uid, r)
                return self.reply(code, res)
            elif act.startswith("dko_"):
                code, res = dko_act(act, q, uid, r)
                if DIRTY[0]:
                    DIRTY[0] = False
                    persist()
                if code == 200:
                    res["state"] = view(uid, r)
                return self.reply(code, res)
            elif act.startswith("pt_"):
                code, res = pt_act(act, q, uid, r)
                if DIRTY[0]:
                    DIRTY[0] = False
                    persist()
                if code == 200:
                    res["state"] = view(uid, r)
                return self.reply(code, res)
            elif act.startswith("room_"):
                code, res = room_act(act, q, uid, r)
                if DIRTY[0]:
                    DIRTY[0] = False
                    persist()
                if code == 200:
                    res["state"] = view(uid, r)
                return self.reply(code, res)
            elif act != "auth":
                return self.reply(404, {"error": "unknown"})
            persist()
            return self.reply(200, {"state": view(uid, r)})


if __name__ == "__main__":
    apply_prices()
    ThreadingHTTPServer(("127.0.0.1", 8098), H).serve_forever()
