"""Вставляет каталог sk3/cat.json в index.html (SK, GRP, PACKS) и api.py (ITEMS, PACKS)."""
import json, re
from pathlib import Path
ROOT = Path(__file__).parent
D = json.load(open(ROOT / "sk3" / "cat.json"))
cat, grp, packs = D["cat"], D["grp"], D["packs"]


def js(o):
    return "{" + ", ".join(f'{k}:{json.dumps(v, ensure_ascii=False)}' for k, v in o.items()) + "}"


s = (ROOT / "index.html").read_text()
a = s.index("var SK = {"); b = s.index("\n};\n", a) + 4
face = re.search(r'  face: \{t:"Колоды", items:\[[^\n]*\]\},\n', s[a:b]).group(0)
sk = ('var SK = {\n  back: {t:"Карты", items:[\n' + ",\n".join("    " + js(x) for x in cat["back"]) + "]},\n" + face +
      '  felt: {t:"Столы", items:[\n' + ",\n".join("    " + js(x) for x in cat["felt"]) + "]},\n" +
      '  chip: {t:"Фишки", items:[\n' + ",\n".join("    " + js(x) for x in cat["chip"]) + "]}\n};\n")
s = s[:a] + sk + s[b:]
s = re.sub(r"var GRP = \{\"?back\"?: .*?\};\n", lambda m: "var GRP = " + json.dumps(grp, ensure_ascii=False) + ";\n", s, count=1, flags=re.S)
s = re.sub(r"var PACKS = \[ // должны совпадать с PACKS в api.py\n.*?\];\n",
           lambda m: "var PACKS = [ // должны совпадать с PACKS в api.py\n" + ",\n".join("  " + json.dumps(p, ensure_ascii=False) for p in packs) + "];\n", s, count=1, flags=re.S)
s = s.replace('webp?v=25', 'webp?v=40').replace('".webp?v=23)"', '".webp?v=40)"')
(ROOT / "index.html").write_text(s)

t = (ROOT / "api.py").read_text()
first = {"back": "raspberry", "felt": "emerald", "chip": "classic"}
L = []
for k in ["back", "face", "felt", "chip"]:
    if k == "face":
        L.append('    "face": {"classic": 0},'); continue
    its = sorted(cat[k], key=lambda x: x["id"] != first[k])
    L.append(f'    "{k}": {{' + ", ".join(f'"{x["id"]}": {x["p"]}' for x in its) + "},")
t = re.sub(r"ITEMS = \{.*?\n\}\n", lambda m: "ITEMS = {  # каталог скинов и цены в игровых фишках: должен совпадать с SK в index.html\n" + "\n".join(L) + "\n}\n", t, count=1, flags=re.S)
t = re.sub(r"PACKS = \{.*?\}\)\}\n", lambda m: "PACKS = {" + ",\n         ".join(f'"{p["id"]}": ({p["p"]}, {json.dumps(p["it"])})' for p in packs) + "}\n", t, count=1, flags=re.S)
(ROOT / "api.py").write_text(t)
print("ok", len(cat["back"]), len(cat["felt"]), len(cat["chip"]), len(packs))
