"""Каталог v40 (01.10): линейки скинов — один рисунок, много цветов. SVG → sk3/, растр в c/ (raster.js), каталог → sk3/cat.json.
Запуск: python3 skins3.py; затем node raster.js sk3 c 300 418 back- ; node raster.js sk3 c 400 440 felt- ; python3 cat3_apply.py"""
import json, math, os, re, sys, io, contextlib
from pathlib import Path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
import gen_skins as G
with contextlib.redirect_stdout(io.StringIO()):
    import new_backs as NB  # при импорте пишет nb/*.svg — безвредно

OUT = ROOT / "sk3"
OUT.mkdir(exist_ok=True)
CAT = {"back": [], "felt": [], "chip": []}
GRP = {"back": {}, "felt": {}, "chip": {}}


def add(k, g, gname, id_, color, price, svg=None, sw=None, **kw):
    GRP[k][g] = gname
    it = {"id": id_, "n": f"{gname} {color}", "p": price, "g": g}
    if sw:
        it["sw"] = sw
    it.update(kw)
    CAT[k].append(it)
    if svg:
        (OUT / f"{k if k == 'felt' else 'back'}-{id_}.svg").write_text(svg)


def light(h):
    h = h.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return r * .299 + g * .587 + b * .114 > 150


def mix(h, k):  # k<0 темнее, k>0 светлее
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    c = [round(x * (1 + k)) if k < 0 else round(x + (255 - x) * k) for x in c]
    return "#" + "".join(f"{max(0, min(255, x)):02x}" for x in c)


# ---------------- КАРТЫ ----------------
add("back", "classic", "Classic", "classic", "Red", 3000, sw="#c62f2f")
add("back", "classic", "Classic", "blue", "Blue", 3000, sw="#2f5cc6")
add("back", "classic", "Classic", "gold", "Gold", 3000, sw="#e2ce94")

for id_, col, bg, p in [("raspberry", "Raspberry", "#8e1340", 0), ("sticker", "Pink", "#e02a62", 5000), ("mbblack", "Black", "#141416", 5000),
                        ("mbnavy", "Navy", "#1b2d5c", 5000), ("mbemerald", "Emerald", "#0d5a3c", 5000), ("mbplum", "Plum", "#4b1f5c", 5000), ("mbcream", "Cream", "#f4ead3", 5000)]:
    lt = light(bg)
    add("back", "mulberry", "Mulberry", id_, col, p, G.back(bg, "dots", "#8e1340" if lt else "#fff", .25 if lt else .18, "berry", line="#8e1340" if lt else "#fff"), bg)

for id_, col, bg in [("noir", "Noir", "#141416"), ("snow", "Snow", "#f4f4f6"), ("ltnavy", "Navy", "#1b2d5c"), ("ltwine", "Wine", "#6a1426"), ("ltgreen", "Green", "#0d5a3c"), ("ltgrey", "Steel", "#4a4f57")]:
    lt = light(bg)
    add("back", "lattice", "Lattice", id_, col, 5000, G.back(bg, "lattice", "#111" if lt else "#fff", .18 if lt else .22, "spade", line="#111" if lt else "#fff"), bg)

for id_, col, bg in [("casino", "Red", "#7a0d12"), ("csgreen", "Green", "#0d5a3c"), ("csblue", "Blue", "#1b2d5c"), ("csblack", "Black", "#141416"), ("cspurple", "Purple", "#4b2a7a"), ("mono", "White", "#fafafa")]:
    lt = light(bg)
    add("back", "casino", "Casino", id_, col, 8000, G.back(bg, "suits", "#000" if lt else "#fff", .14 if lt else .16, "spade", line="#111" if lt else "#fff"), bg)

for id_, col, bg, fg in [("argyle", "Blue", "#2d3a55", "#9fb3d9"), ("wine", "Wine", "#40101d", "#e8b4c0"), ("agreen", "Green", "#1d4d2f", "#a8dcb9"), ("agrey", "Grey", "#3a3a3e", "#c9c9cf"), ("atan", "Tan", "#7a5a32", "#f0d9b0")]:
    add("back", "argyle", "Argyle", id_, col, 8000, G.back(bg, "argyle", fg, .35, "none", line="#fff"), bg)

for id_, col, bg in [("night", "Navy", "#0d1330"), ("nspurple", "Purple", "#2a1145"), ("nsteal", "Teal", "#0b3a3f"), ("nsblack", "Black", "#0b0b0d"), ("nsburg", "Burgundy", "#3a0b1a")]:
    add("back", "night", "Night Sky", id_, col, 10000, G.back(bg, "stars", "#fff", .7, "star", line="#fff"), bg)

for id_, col, bg in [("berryfield", "Blossom", "#fbeef3"), ("berrypink", "Pink", "#f9d3e0"), ("berrymint", "Mint", "#d8f3e6"), ("berrysky", "Sky", "#d9e9fb"), ("berrycream", "Cream", "#f4ead3"),
                     ("berrylemon", "Lemon", "#fbf3c4"), ("berrylilac", "Lilac", "#ece0f7"), ("berrypeach", "Peach", "#fde2d2"), ("berrygreen", "Garden", "#1f5a2a"), ("berryblack", "Night", "#1a1a2e"), ("berrynoir", "Noir", "#111111")]:
    add("back", "berry", "Berry", id_, col, 20000, G.back(bg, "berries", "#000", 1, "none", line="#111" if light(bg) else "#fff"), bg)

NB.B.clear()
for id_, col, bg, c, mono, kw in [("bblush", "Blush", "#fbe3ea", "#c2185b", "#8e1340", {}), ("bmint", "Mint", "#e1f4ea", "#2e7d5b", "#1f5a43", {}), ("bsky", "Sky", "#e3edf9", "#3b4f9c", "#22306b", {}),
                                  ("blav", "Lavender", "#eee6f6", "#6b4a8e", "#4a2b66", {}), ("bcherry", "Peach", "#fde9dc", "#c0623a", "#9b3a1e", {}), ("botanica", "Cream", "#f6efdc", "#b48a3c", "#8e1340", {}),
                                  ("blemon", "Lemon", "#fbf6d6", "#b8962a", "#8a6a1f", {}), ("baqua", "Aqua", "#ddf3f1", "#1f8a85", "#14605c", {}),
                                  ("bnight", "Forest", "#10291c", "#e2c46e", "#e2c46e", {"stem": "#c9a54a", "leafc": "#2f6b45", "vein": "#e2c46e"}), ("bnoir", "Noir", "#141416", "#d81b60", "#f06292", {"stem": "#888"})]:
    NB.botan(id_, bg, c, c, "rasp", mono=mono, **kw)
    add("back", "botanica", "Botanica", id_, col, 15000, NB.B[id_], bg)

NB.B.clear()
for id_, col, c1, c2, dark, th, fr in [("vruby", "Ruby", "#c8102e", "#6e0618", "#3d020c", "#f7d774", "#e9d5c0"), ("velvet", "Wine", "#8d1630", "#5a0b1d", "#2a0510", "#f0c9a0", "#e9d5c0"),
                                       ("vnoir", "Noir", "#2c2c30", "#0c0c0e", "#000000", "#d4af37", "#d4af37"), ("vemerald", "Emerald", "#1d7a52", "#0b3d28", "#04261a", "#e9c46a", "#e9d5c0"),
                                       ("vnavy", "Navy", "#26407e", "#101d45", "#08122e", "#d8dde8", "#e9d5c0"), ("vplum", "Plum", "#6b2a73", "#331238", "#1e0822", "#f3b8c8", "#e9d5c0"),
                                       ("vcognac", "Cognac", "#8a4b22", "#4a230c", "#2a1305", "#f4dfc2", "#f4dfc2"), ("vrose", "Rose", "#c2507a", "#7a2346", "#45122a", "#fde2ea", "#fde2ea"),
                                       ("vteal", "Teal", "#1f8a8a", "#0d4a4a", "#062a2a", "#e9c46a", "#e9d5c0"), ("vsapph", "Sapphire", "#2a5bd7", "#12307a", "#0a1c4a", "#e9c46a", "#e9d5c0"),
                                       ("volive", "Olive", "#6b7a2a", "#3a4512", "#1f2608", "#f0e2b0", "#f0e2b0"), ("vgraph", "Graphite", "#55585f", "#26282c", "#111214", "#d8dde8", "#d8dde8")]:
    NB.velvet(id_, c1, c2, dark, th, "shield", True, fr)
    add("back", "velvet", "Velvet", id_, col, 20000, NB.B[id_], c1)

with contextlib.redirect_stdout(io.StringIO()):
    import importlib; importlib.reload(NB)  # заново: исходные royal/gatsby/mosaic/aurora
R0 = NB.B["royal"]
for id_, col, a, b in [("royal", "Navy", "#1d2c6b", "#0a1033"), ("rgreen", "Emerald", "#1d6b45", "#08301c"), ("rburg", "Burgundy", "#6b1d2c", "#330a12"), ("rblack", "Black", "#2c2c30", "#0c0c0e"), ("rpurple", "Purple", "#4a1d6b", "#1e0a33")]:
    add("back", "royal", "Royal", id_, col, 50000, R0.replace("#1d2c6b", a).replace("#0a1033", b), a)
G0 = NB.B["gatsby"]
for id_, col, bg, gold in [("gatsby", "Black", "#0c0c0e", "#d4af37"), ("gemerald", "Emerald", "#0a2e1e", "#d4af37"), ("gnavy", "Navy", "#0b1433", "#d4af37"), ("gburg", "Burgundy", "#2e0812", "#d4af37"), ("gsilver", "Silver", "#0c0c0e", "#c9ccd3")]:
    add("back", "gatsby", "Gatsby", id_, col, 60000, G0.replace("#0c0c0e", bg).replace("#d4af37", gold), bg if bg != "#0c0c0e" else gold)
M0 = NB.B["mosaic"]
for id_, col, a, b in [("mosaic", "Teal", "#0e5c63", "#1b8a8f"), ("mzblue", "Blue", "#1b3f8a", "#2f62c9"), ("mzred", "Red", "#8a1b2a", "#c42f45"), ("mzgreen", "Green", "#1d5e33", "#2f8a4f"), ("mzblack", "Black", "#1a1a1e", "#3a3a42")]:
    add("back", "mosaic", "Mosaic", id_, col, 25000, M0.replace("#0e5c63", a).replace("#1b8a8f", b), a)
A0 = NB.B["aurora"]
for id_, col, c1, c2 in [("aurora", "Green", "#2af5b5", "#8b5cf6"), ("apink", "Pink", "#ff5fa2", "#ffb347"), ("ablue", "Blue", "#4fc3ff", "#2a5bd7")]:
    add("back", "aurora", "Aurora", id_, col, 30000, A0.replace("#2af5b5", c1).replace("#8b5cf6", c2), c1)


# ---------------- 02.10: НОВЫЕ ЛИНЕЙКИ РУБАШЕК (6 × 4) И РАСЦВЕТКИ К СТАРЫМ ----------------
import new_lines as NL
for id_, (g, gname, col, svg, sw) in NL.build().items():
    add("back", g, gname, id_, col, 1, svg, sw)
for id_, col, bg in [("mbred", "Red", "#9b1b2a"), ("mbteal", "Teal", "#0f5c63"), ("mbsand", "Sand", "#c9a46a"), ("mbgraph", "Graphite", "#3a3d44"), ("mbsky", "Sky", "#dbe8f7")]:
    lt = light(bg); add("back", "mulberry", "Mulberry", id_, col, 1, G.back(bg, "dots", "#8e1340" if lt else "#fff", .25 if lt else .18, "berry", line="#8e1340" if lt else "#fff"), bg)
for id_, col, bg in [("ltplum", "Plum", "#4b1f5c"), ("ltteal", "Teal", "#0f5c63"), ("ltcocoa", "Cocoa", "#4a2e1f"), ("ltcream", "Cream", "#f4ead3")]:
    lt = light(bg); add("back", "lattice", "Lattice", id_, col, 1, G.back(bg, "lattice", "#111" if lt else "#fff", .18 if lt else .22, "spade", line="#111" if lt else "#fff"), bg)
for id_, col, bg in [("csteal", "Teal", "#0f5c63"), ("csorange", "Orange", "#b4471a"), ("csgold", "Gold", "#8a6a1f"), ("cspink", "Pink", "#b0376a")]:
    lt = light(bg); add("back", "casino", "Casino", id_, col, 1, G.back(bg, "suits", "#000" if lt else "#fff", .14 if lt else .16, "spade", line="#111" if lt else "#fff"), bg)
for id_, col, bg, fg in [("anavy", "Navy", "#1a2440", "#d7c38a"), ("aplum", "Plum", "#3b1a45", "#e0b6e8"), ("ateal", "Teal", "#123f42", "#9fe0dc"), ("ared", "Red", "#5a1016", "#f2b8a8")]:
    add("back", "argyle", "Argyle", id_, col, 1, G.back(bg, "argyle", fg, .35, "none", line="#fff"), bg)
for id_, col, bg in [("nsgreen", "Forest", "#0b2a1c"), ("nsrose", "Rose", "#3a0f2a"), ("nsindigo", "Indigo", "#1a1a5a")]:
    add("back", "night", "Night Sky", id_, col, 1, G.back(bg, "stars", "#fff", .7, "star", line="#fff"), bg)
NB.B.clear()
for id_, col, c1, c2, dark, th, fr in [("vcopper", "Copper", "#b0602e", "#5e2c10", "#331604", "#f6dcc0", "#f6dcc0"), ("vforest", "Forest", "#2f6b3a", "#14351b", "#08200e", "#e9c46a", "#e9d5c0"),
                                       ("vmidnight", "Midnight", "#2a2f5e", "#11142e", "#070919", "#c9ccd3", "#c9ccd3"), ("vberry", "Berry", "#a3174f", "#550826", "#2e0314", "#fbd3e0", "#fbd3e0")]:
    NB.velvet(id_, c1, c2, dark, th, "shield", True, fr); add("back", "velvet", "Velvet", id_, col, 1, NB.B[id_], c1)
with contextlib.redirect_stdout(io.StringIO()):
    importlib.reload(NB)
for id_, col, a, b in [("rteal", "Teal", "#0f5c63", "#05272b"), ("rcopper", "Copper", "#7a3a16", "#331505"), ("rgrey", "Steel", "#3d434c", "#14171b")]:
    add("back", "royal", "Royal", id_, col, 1, NB.B["royal"].replace("#1d2c6b", a).replace("#0a1033", b), a)
for id_, col, bg, gold in [("gpurple", "Purple", "#1c0b2e", "#d4af37"), ("gteal", "Teal", "#062628", "#d4af37"), ("grose", "Rose", "#0c0c0e", "#e8a3b5")]:
    add("back", "gatsby", "Gatsby", id_, col, 1, NB.B["gatsby"].replace("#0c0c0e", bg).replace("#d4af37", gold), bg if bg != "#0c0c0e" else gold)
for id_, col, a, b in [("mzpurple", "Purple", "#4a1d6b", "#7a3aa8"), ("mzgold", "Gold", "#7a5a12", "#b8902e"), ("mzpink", "Pink", "#8a1b5a", "#c42f85")]:
    add("back", "mosaic", "Mosaic", id_, col, 1, NB.B["mosaic"].replace("#0e5c63", a).replace("#1b8a8f", b), a)
for id_, col, c1, c2 in [("aviolet", "Violet", "#b16cff", "#ff5fa2"), ("alime", "Lime", "#c6ff3d", "#2af5b5"), ("asunset", "Sunset", "#ffb347", "#ff4f6d")]:
    add("back", "aurora", "Aurora", id_, col, 1, NB.B["aurora"].replace("#2af5b5", c1).replace("#8b5cf6", c2), c1)

# ---------------- СТОЛЫ: однотонное сукно, у каждой линейки свой центр и разметка (без узоров по всему полю) ----------------
FV = "var(--table) url(c/felt-{}.webp?v=50) center/cover no-repeat"
LIGHT = ('<radialGradient id="lt" cx="50%" cy="46%" r="62%"><stop offset="0" stop-color="#fff" stop-opacity=".12"/>'
         '<stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>')


def cloth(fill, deco, defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="880" viewBox="0 0 400 440" preserveAspectRatio="xMidYMid slice"><defs>{G.noise("n", 1.4, 3, .3)}{LIGHT}{defs}</defs>'
            f'<rect width="400" height="440" fill="{fill}"/><rect width="400" height="440" filter="url(#n)"/><rect width="400" height="440" fill="url(#lt)"/>{deco}</svg>')


def ring(line, op=.3, w=1.6, rx=164, ry=182, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<ellipse cx="200" cy="220" rx="{rx}" ry="{ry}" fill="none" stroke="{line}" stroke-opacity="{op}" stroke-width="{w}"{d}/>'


def word(text, line, y=372, op=.5, size=14, sp=6):
    return f'<text x="200" y="{y}" text-anchor="middle" font-family="Georgia,serif" font-size="{size}" letter-spacing="{sp}" fill="{line}" fill-opacity="{op}">{text}</text>'


def velvet_cloth(c):  # бархат: мягкий отлив ворса (рельеф шума с освещением), без рисунка
    f = ('<filter id="vv" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".004 .012" numOctaves="2" seed="11" result="t"/>'
         '<feDiffuseLighting in="t" surfaceScale="3" lighting-color="#fff" result="l"><feDistantLight azimuth="235" elevation="55"/></feDiffuseLighting>'
         '<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  .16 0 0 0 -.08"/></filter>')
    return cloth(c, '<rect width="400" height="440" filter="url(#vv)"/>', f)


# Classic — чистое сукно без логотипа: тонкая линия и надпись
add("felt", "classic", "Classic", "emerald", "Theme", 0, sw="var(--table)", v="var(--table)")
for id_, col, c, p in [("green", "Green", "#1f6b47", 0), ("red", "Red", "#8a1c2b", 5000), ("grey", "Grey", "#4a4d52", 5000), ("purple", "Purple", "#4b2a7a", 5000),
                       ("choco", "Chocolate", "#4a2c1d", 5000), ("olive", "Olive", "#4d5a1f", 5000), ("pink", "Pink", "#b0376a", 5000), ("berry", "Raspberry", "#7d1240", 5000), ("midnight", "Midnight", "#16223f", 5000),
                       ("teal", "Teal", "#0f5c5a", 5000), ("blue", "Blue", "#1f4f8f", 5000), ("orange", "Orange", "#a8481c", 5000), ("sand", "Sand", "#9a7a4a", 5000), ("plum", "Plum", "#5a1f5e", 5000), ("black", "Black", "#1a1a1d", 5000),
                       ("forest", "Forest", "#14432a", 5000), ("wine", "Wine", "#5a1020", 5000), ("slate", "Slate", "#3a4a5a", 5000), ("mint", "Mint", "#2e8a6e", 5000), ("indigo", "Indigo", "#2a2a6e", 5000), ("copper", "Copper", "#7a3e1e", 5000)]:
    add("felt", "classic", "Classic", id_, col, p, cloth(c, ""), c, v=FV.format(id_), dc=["classic", "#ffffff", "#ffffff"])
# v70: однотонные столы средних тонов под светлые рубашки (Guilloche, Marble Carrara, Carbon Gold)
for id_, col, c in [("sage", "Sage", "#4f6b4c"), ("sky", "Sky", "#36557a"), ("mauve", "Mauve", "#664363"), ("sepia", "Sepia", "#6e5136"), ("stone", "Stone", "#5f5b55"), ("fgold", "Gold", "#7a5c16")]:
    add("felt", "classic", "Classic", id_, col, 5000, cloth(c, ""), c, v=FV.format(id_), dc=["classic", "#ffffff", "#ffffff"])

# Velvet — строчка по краю; в центре вензель: тонкое двойное кольцо, строчка, M и ромбики по бокам
def velvet_t(c, line):
    orn = "".join(f'<path d="M{x} 220 l5 -5 5 5 -5 5z" fill="{line}" fill-opacity=".7"/><path d="M{x + (10 if x > 200 else 0) + (6 if x > 200 else -26)} 220 h20" stroke="{line}" stroke-opacity=".5" stroke-width="1"/>' for x in (134, 256))
    return cloth(c, ring(line, .55, 1.6, 166, 184, "6 5") + ring(line, .25, 1, 157, 175) +
                 f'<circle cx="200" cy="220" r="44" fill="none" stroke="{line}" stroke-opacity=".6" stroke-width="1.4"/>'
                 f'<circle cx="200" cy="220" r="38" fill="none" stroke="{line}" stroke-opacity=".45" stroke-width="1" stroke-dasharray="3 3"/>'
                 f'<circle cx="200" cy="220" r="32" fill="none" stroke="{line}" stroke-opacity=".3" stroke-width="1"/>' + orn +
                 f'<text x="200" y="226" text-anchor="middle" font-family="DejaVu Serif,Georgia,serif" font-size="32" fill="{line}" fill-opacity=".75">M</text>' + word("VELVET CLUB", line, 372, .5, 12, 5))


# Royal — двойная золотая линия, герб: маленькая корона над щитом, M ровно по центру щита
def royal_t(c, line):
    shield = (f'<path d="M170 192 L 230 192 L 230 222 C 230 244, 216 256, 200 264 C 184 256, 170 244, 170 222Z" fill="none" stroke="{line}" stroke-opacity=".75" stroke-width="2"/>'
              f'<path d="M176 198 L 224 198 L 224 222 C 224 240, 213 250, 200 257 C 187 250, 176 240, 176 222Z" fill="none" stroke="{line}" stroke-opacity=".4" stroke-width="1"/>'
              f'<text x="200" y="236" text-anchor="middle" font-family="DejaVu Serif,Georgia,serif" font-size="26" fill="{line}" fill-opacity=".8">M</text>')
    return cloth(c, ring(line, .7, 2.2, 166, 184) + ring(line, .45, 1, 159, 177) + f'<g transform="translate(0,6)"><g transform="translate(200,176) scale(.62)" opacity=".8">{NB.crown_svg(line)}</g>{shield}</g>' + word("ROYAL", line, 372, .6, 13, 8))


# Gatsby — золотое кольцо с ромбами, двойной ромб и ровные лучи ар-деко (8 направлений, одинаковая длина)
def gatsby_t(c, line):
    rays = ""
    for a in range(0, 360, 45):
        for d in (-6, 0, 6):
            ca, sa = math.cos(math.radians(a + d)), math.sin(math.radians(a + d))
            r1, r2 = (58, 86) if d == 0 else (60, 76)
            rays += f'<path d="M{200 + r1 * ca:.1f} {220 + r1 * sa:.1f} L {200 + r2 * ca:.1f} {220 + r2 * sa:.1f}" stroke="{line}" stroke-opacity="{.6 if d == 0 else .35}" stroke-width="{1.4 if d == 0 else 1}"/>'
    med = (f'<path d="M200 166 L 248 220 L 200 262 L 152 220Z" fill="{c}" stroke="{line}" stroke-opacity=".85" stroke-width="2"/>'
           f'<path d="M200 178 L 236 220 L 200 250 L 164 220Z" fill="none" stroke="{line}" stroke-opacity=".5"/>')
    dia = "".join(f'<path d="M{x} {y - 7} l7 7 -7 7 -7 -7z" fill="{line}" opacity=".85"/>' for x, y in [(200, 38), (200, 402), (36, 220), (364, 220)])
    return cloth(c, ring(line, .7, 2) + ring(line, .3, 1, 157, 175) + dia + rays + med + f'<text x="200" y="223" text-anchor="middle" font-family="DejaVu Serif,Georgia,serif" font-size="24" fill="{line}" fill-opacity=".9">M</text>' + word("GATSBY", line, 372, .6, 13, 8))


# Neon — тёмное сукно, две неоновые трубки по краю (тонкая яркая линия + мягкое свечение), малинка-контур в центре
def neon_t(c, glow, glow2):
    f = ('<filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>'
         '<filter id="gs" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter>')
    def tube(svg, col):  # свечение + яркая сердцевина
        return (f'<g filter="url(#gl)" opacity=".55">{svg.format(c=col, w=5)}</g><g filter="url(#gs)" opacity=".9">{svg.format(c=col, w=3)}</g>'
                f'{svg.format(c=col, w=1.6)}{svg.format(c="#ffffff", w=.6)}')
    ell = lambda rx, ry: '<ellipse cx="200" cy="220" rx="' + str(rx) + '" ry="' + str(ry) + '" fill="none" stroke="{c}" stroke-width="{w}"/>'
    pts = [(0, -10), (-8, -5), (8, -5), (-10, 4), (0, 1), (10, 4), (-6, 12), (6, 12), (0, 20)]
    berry = "".join(f'<circle cx="{200 + x * 2.2:.1f}" cy="{206 + y * 2.2:.1f}" r="12" fill="none" stroke="{{c}}" stroke-width="{{w}}"/>' for x, y in pts)
    leaf = '<path d="M200 178c-13-17-31-17-35-9 11 2 20 6 24 13-13-2-24 2-26 11 13-4 24-4 33 0 2-11 4-15 4-15s2 4 4 15c9-4 20-4 33 0-2-9-13-13-26-11 4-7 13-11 24-13-4-8-22-8-35 9z" fill="none" stroke="{c}" stroke-width="{w}" stroke-linejoin="round"/>'
    return cloth(c, tube(ell(166, 184), glow) + tube(ell(156, 174), glow2) + '<g transform="translate(0,14)">' + tube(berry, glow) + tube(leaf, glow2) + '</g>' +
                 f'<text x="200" y="350" text-anchor="middle" font-family="DejaVu Sans,Arial,sans-serif" font-weight="700" font-size="15" letter-spacing="7" fill="{glow2}" fill-opacity=".85">MULBERRY</text>', f)


# Vegas — табло-знак: ромбовидный щит с лампочками, звезда, «LAS VEGAS», по краю гирлянда огней
def vegas_t(c, line):
    bulbs = "".join(f'<circle cx="{200 + 166 * math.cos(math.radians(a)):.1f}" cy="{220 + 184 * math.sin(math.radians(a)):.1f}" r="2.6" fill="{line}" fill-opacity=".85"/>' for a in range(0, 360, 8))
    sign = ('M200 136 L 280 214 L 200 292 L 120 214Z')
    sb = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.8" fill="#fff" fill-opacity=".9"/>' for x, y in
                 [(200 + (62 - 6) * t * (1 if i < 2 else -1) * (1 if i % 3 == 0 else 1), 0) for t in [] for i in []])
    edge = []
    corners = [(200, 143), (273, 214), (200, 285), (127, 214)]
    for i in range(4):
        (x1, y1), (x2, y2) = corners[i], corners[(i + 1) % 4]
        for k in range(9):
            t = k / 9
            edge.append((x1 + (x2 - x1) * t, y1 + (y2 - y1) * t))
    sb = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.9" fill="#fff8d8"/>' for x, y in edge)
    star = '<polygon points="' + " ".join(f"{200 + (15 if k % 2 == 0 else 6.5) * math.cos(math.radians(-90 + 36 * k)):.1f},{116 + (15 if k % 2 == 0 else 6.5) * math.sin(math.radians(-90 + 36 * k)):.1f}" for k in range(10)) + '" fill="' + line + '"/>'
    return cloth(c, bulbs + ring(line, .55, 1.4, 156, 174) +
                 f'<g transform="translate(0,6)"><path d="{sign}" fill="{line}" fill-opacity=".14" stroke="{line}" stroke-width="2.4"/>' + sb + star +
                 f'<text x="200" y="204" text-anchor="middle" font-family="DejaVu Serif,Georgia,serif" font-size="12" letter-spacing="4" fill="{line}">LAS</text>'
                 f'<text x="200" y="230" text-anchor="middle" font-family="DejaVu Serif,Georgia,serif" font-weight="700" font-size="21" letter-spacing="1" fill="{line}">VEGAS</text></g>'
                 + word("MULBERRY", line, 372, .55, 13, 6))


# Monaco — роза ветров в центре, тонкая серебряная разметка
def monaco_t(c, line):
    star = "".join(f'<path d="M200 220 L {200 + 9 * math.cos(math.radians(a + 90)):.1f} {220 + 9 * math.sin(math.radians(a + 90)):.1f} L {200 + (56 if i % 2 == 0 else 34) * math.cos(math.radians(a)):.1f} {220 + (56 if i % 2 == 0 else 34) * math.sin(math.radians(a)):.1f}Z" fill="{line}" fill-opacity="{.6 if i % 2 == 0 else .35}"/>' for i, a in enumerate(range(0, 360, 45)))
    return cloth(c, ring(line, .45, 1.4) + ring(line, .2, 1, 156, 174) + f'<circle cx="200" cy="220" r="62" fill="none" stroke="{line}" stroke-opacity=".35"/>' + star + word("MONACO", line, 372, .55, 13, 8))

# Sunset — сукно с плавным переходом цвета, тонкая белая линия
def sunset_t(c1, c2):
    g = f'<linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'
    return cloth("url(#sg)", ring("#fff", .35, 1.6) + word("MULBERRY", "#fff", 372, .45), g)


for fam, gname, price, fn, rows in [
        ("velvet", "Velvet", 15000, velvet_t, [("vfruby", "Ruby", "#7a1028", "#f0d2a8"), ("vfemerald", "Emerald", "#0f4f34", "#f0d2a8"), ("vfnoir", "Noir", "#1a1a1d", "#e2c46e"),
                                               ("vfnavy", "Navy", "#16285a", "#f0d2a8"), ("vfplum", "Plum", "#4a1a52", "#f3b8c8"), ("vfcopper", "Copper", "#6e3416", "#f6dcc0")]),
        ("royal", "Royal", 25000, royal_t, [("rfnavy", "Navy", "#16285a", "#e2c46e"), ("rfgreen", "Emerald", "#0f5134", "#e2c46e"), ("rfburg", "Burgundy", "#561021", "#e2c46e"), ("rfblack", "Black", "#18181b", "#e2c46e"), ("rfpurple", "Purple", "#3a1858", "#e2c46e")]),
        ("gatsby", "Gatsby", 25000, gatsby_t, [("gfblack", "Black", "#141416", "#d4af37"), ("gfemerald", "Emerald", "#0c3826", "#d4af37"), ("gfnavy", "Navy", "#0b1433", "#d4af37"), ("gfburg", "Burgundy", "#2e0812", "#d4af37")]),
        ("monaco", "Monaco", 20000, monaco_t, [("mfteal", "Teal", "#0d4f55", "#e8eef2"), ("mfnavy", "Navy", "#13244a", "#e8eef2"), ("mfsand", "Sand", "#8a6a45", "#fff6e6"), ("mfred", "Red", "#7a1424", "#f4e6e8"), ("mfblack", "Black", "#18181b", "#e8eef2"), ("mfgreen", "Green", "#155a3a", "#e8eef2")]),
        ("vegas", "Vegas", 20000, vegas_t, [("vgred", "Red", "#8f1424", "#f5d77a"), ("vggreen", "Green", "#145a36", "#f5d77a"), ("vgblue", "Blue", "#16306e", "#f5d77a"), ("vgblack", "Black", "#18181b", "#f5d77a"), ("vgpurple", "Purple", "#3e1660", "#f5d77a")]),
        ("deco", "Deco", 20000, None, [("dfonyx", "Onyx", "#151515", "#d4b25a"), ("dfemerald", "Emerald", "#0d4532", "#d4b25a"), ("dfnavy", "Navy", "#13214a", "#d4b25a"), ("dfburg", "Burgundy", "#4a0d1c", "#d4b25a")]),
        ("crown", "Crown", 20000, None, [("cfblue", "Blue", "#1d2c6b", "#e2c46e"), ("cfblack", "Black", "#18181b", "#d4af37"), ("cfpurple", "Purple", "#3d1a5c", "#e2c46e"), ("cfred", "Red", "#6e0d14", "#e9c46a")])]:
    for id_, col, c, line in rows:  # 04.10: сукно — только ткань; разметку и эмблему рисует игра по форме стола (dc)
        add("felt", fam, gname, id_, col, price, velvet_cloth(c) if fam == "velvet" else cloth(c, ""), c, v=FV.format(id_), dc=[fam, line, line])
for id_, col, c, g1, g2 in [("nfpink", "Miami", "#0d0b14", "#ff4fa3", "#35e0ff"), ("nfcyan", "Ice", "#0a1016", "#35e0ff", "#e8fbff"), ("nflime", "Tokyo", "#0f0a16", "#b46bff", "#9dff5a"), ("nfsunset", "Sunset", "#140a0c", "#ff7a3d", "#ffd23d"), ("nfvegas", "Vegas", "#0b0d14", "#ff2d55", "#2dd4ff"), ("nfmint", "Mint", "#08120f", "#2affb0", "#e8fff6")]:
    add("felt", "neon", "Neon", id_, col, 20000, cloth(c, ""), f"linear-gradient(135deg,{g1},{g2})", v=FV.format(id_), dc=["neon", g1, g2])
for id_, col, c1, c2 in [("sfdusk", "Dusk", "#c2410c", "#4a1d6b"), ("sfocean", "Ocean", "#0e7490", "#312e81"), ("sfrose", "Rose", "#be185d", "#7c2d12"), ("sfaurora", "Aurora", "#0f766e", "#6d28d9"), ("sfember", "Ember", "#b91c1c", "#f59e0b"), ("sflagoon", "Lagoon", "#0369a1", "#059669")]:
    add("felt", "sunset", "Sunset", id_, col, 20000, cloth("url(#sg)", "", f'<linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient>'), f"linear-gradient(135deg,{c1},{c2})", v=FV.format(id_), dc=["sunset", "#ffffff", "#ffffff"])

# ---------------- ФИШКИ: внутри линейки одинаковые край и вставка, разные палитры ----------------
def pal(base, acc):  # 5000, 1000, 500, 100, 25, 5, 1 — оттенки одного цвета + акцент
    return [mix(base, -.45), acc, base, "#161618", mix(base, .35), "#f4f1ea", mix(base, -.2)]

add("chip", "classic", "Classic", "classic", "Casino", 0, edge="#ffffff", ins="rect")
add("chip", "classic", "Classic", "cred", "Red", 5000, edge="#ffffff", ins="rect", tint=pal("#c62828", "#f0c419"), num="#c62828")
add("chip", "classic", "Classic", "ocean", "Blue", 5000, edge="#ffffff", ins="rect", tint=["#1b3a8a", "#1fa3c7", "#0f6b8a", "#0b1d33", "#3fb8a8", "#e6f6fb", "#6fc7e8"], num="#0f4c6e")
add("chip", "classic", "Classic", "cgreen", "Green", 5000, edge="#ffffff", ins="rect", tint=pal("#1f7a45", "#f0c419"), num="#1f7a45")
# v70: фишки в тон новым столам
for id_, col, c in [("csage", "Sage", "#56784f"), ("csky", "Sky", "#3c6496"), ("cmauve", "Mauve", "#7a4a74"), ("csepia", "Sepia", "#86603a"), ("cstone", "Stone", "#6e6a63"), ("cgoldc", "Gold", "#a07818")]:
    add("chip", "classic", "Classic", id_, col, 5000, edge="#ffffff", ins="rect", tint=pal(c, "#f4f1ea"), num=c)
add("chip", "classic", "Classic", "cblack", "Black", 5000, edge="#ffffff", ins="rect", tint=pal("#3a3a40", "#f0c419"), num="#111")

add("chip", "line", "Line", "mono", "Mono", 8000, edge="#ffffff", ins="fine", tint=["#2a2a2e", "#d9d9db", "#55555a", "#111113", "#8a8a8e", "#fafafa", "#b5b5b8"], num="#111")
add("chip", "line", "Line", "ice", "Ice", 8000, edge="#e6f6ff", ins="fine", tint=["#3b5bd6", "#8fd3ff", "#5e9ad0", "#1d2a44", "#9fe3d9", "#ffffff", "#c7d2fe"], num="#1d4ed8")
add("chip", "line", "Line", "lred", "Red", 8000, edge="#ffffff", ins="fine", tint=pal("#b3263a", "#ffd166"), num="#b3263a")
add("chip", "line", "Line", "lgreen", "Green", 8000, edge="#ffffff", ins="fine", tint=pal("#2a8a5a", "#ffd166"), num="#1f6b45")

add("chip", "pop", "Pop", "candy", "Candy", 15000, edge="#ffffff", ins="double", tint=["#8b5cf6", "#fde047", "#f43f5e", "#0f172a", "#22c55e", "#f8fafc", "#ec4899"])
add("chip", "pop", "Pop", "pastel", "Pastel", 15000, edge="#ffffff", ins="double", tint=["#a08be0", "#f5d98a", "#f29c9c", "#6f7a8a", "#9fd8a4", "#f7f4ee", "#f4a7c8"])
add("chip", "pop", "Pop", "retro", "Retro", 15000, edge="#ffffff", ins="double", tint=["#264653", "#e9c46a", "#e76f51", "#1d1d1d", "#2a9d8f", "#f4f1de", "#f4a261"], num="#264653")
add("chip", "pop", "Pop", "neon", "Neon", 15000, edge="#ffffff", ins="double", tint=["#7c3aed", "#facc15", "#ff2d75", "#0b0b12", "#00e5a0", "#f5f5ff", "#22d3ee"], num="#7c3aed")
add("chip", "pop", "Pop", "vegas", "Vegas", 15000, edge="#ffffff", ins="double", tint=["#1e3a8a", "#facc15", "#dc2626", "#000000", "#16a34a", "#ffffff", "#db2777"], num="#b91c1c")

add("chip", "berry", "Berry", "berry", "Pink", 15000, edge="#ffffff", ins="dot", tint=["#5b1e6e", "#e02a62", "#9c0f45", "#2a0f1d", "#f07aa6", "#fbe6ee", "#c2185b"], num="#9c0f45")
add("chip", "berry", "Berry", "bcnoir", "Noir", 15000, edge="#f07aa6", ins="dot", tint=["#2a0f1d", "#e02a62", "#3a1626", "#0d0d0f", "#5b1e3e", "#fbe6ee", "#7a1a40"], num="#c2185b")
add("chip", "berry", "Berry", "bcmint", "Mint", 15000, edge="#ffffff", ins="dot", tint=pal("#2e9e6e", "#e02a62"), num="#1f6b4a")
add("chip", "berry", "Berry", "bcsky", "Sky", 15000, edge="#ffffff", ins="dot", tint=pal("#3b7bd6", "#e02a62"), num="#22306b")

add("chip", "casino", "Casino", "sunset", "Sunset", 10000, edge="#ffffff", ins="diamond", tint=["#7a1f5c", "#f59e0b", "#ea580c", "#3b0d0d", "#facc15", "#fff7ed", "#fb7185"], num="#c2410c")
add("chip", "casino", "Casino", "cscred", "Red", 10000, edge="#ffffff", ins="diamond", tint=pal("#a3172a", "#f0c419"), num="#a3172a")
add("chip", "casino", "Casino", "cscgreen", "Green", 10000, edge="#ffffff", ins="diamond", tint=pal("#1d7a4a", "#f0c419"), num="#1d6b40")
add("chip", "casino", "Casino", "cscblue", "Blue", 10000, edge="#ffffff", ins="diamond", tint=pal("#1f4fa8", "#f0c419"), num="#1f4fa8")
add("chip", "casino", "Casino", "cscblack", "Black", 10000, edge="#ffffff", ins="diamond", tint=pal("#3a3a40", "#e02a62"), num="#111")

for id_, col, base, inl in [("vcruby", "Ruby", "#b0102a", "#fbeee0"), ("vcwine", "Wine", "#7a1430", "#fbeee0"), ("vcnoir", "Noir", "#2c2c30", "#f4e6c4"), ("vcemerald", "Emerald", "#156b48", "#fbeee0"),
                            ("vcnavy", "Navy", "#1f3570", "#f2f2f2"), ("vcplum", "Plum", "#5e2266", "#fbeee0")]:
    add("chip", "velvet", "Velvet", id_, col, 20000, edge="#f4dfc2", ins="fine", tint=pal(base, "#e9c46a"), inlay=inl, num=mix(base, -.2))

add("chip", "royal", "Royal", "royal", "Purple", 30000, edge="#d4af37", ins="wide", tint=["#2a1240", "#d4af37", "#4b1f73", "#101014", "#86699f", "#f5efe0", "#3a1858"], inlay="#101014", num="#d4af37")
for id_, col, base in [("rcnavy", "Navy", "#1d2c6b"), ("rcgreen", "Emerald", "#1d6b45"), ("rcburg", "Burgundy", "#6b1d2c"), ("rcblack", "Black", "#2c2c30")]:
    add("chip", "royal", "Royal", id_, col, 30000, edge="#d4af37", ins="wide", tint=pal(base, "#d4af37"), inlay="#101014", num="#d4af37")

add("chip", "gatsby", "Gatsby", "gold", "Gold", 40000, edge="#e8c77f", ins="wide", tint=["#3d2a08", "#d4af37", "#8a6418", "#1f1a12", "#b8995a", "#efe3c0", "#5c430f"], inlay="#fff8e6", num="#8a6a1a")
add("chip", "gatsby", "Gatsby", "noir", "Black", 40000, edge="#d6b16a", ins="wide", tint=["#2a2a2e", "#1f1f22", "#26262a", "#141416", "#222226", "#2c2c30", "#3a3a3e"], inlay="#111113", num="#d6b16a")
for id_, col, base in [("gcemerald", "Emerald", "#0f4a32"), ("gcnavy", "Navy", "#13204a"), ("gcburg", "Burgundy", "#4a0f1c")]:
    add("chip", "gatsby", "Gatsby", id_, col, 40000, edge="#d6b16a", ins="wide", tint=pal(base, "#d6b16a"), inlay="#111113", num="#d6b16a")


# ---------------- 02.10: новые палитры фишек и линейки Deco / Crown ----------------
for id_, col, base, acc in [("corange", "Orange", "#c2561a", "#f0c419"), ("cpurple", "Purple", "#5b2a8a", "#f0c419"), ("cteal", "Teal", "#0f7a72", "#f0c419"), ("cpink", "Pink", "#c2306e", "#f0c419")]:
    add("chip", "classic", "Classic", id_, col, 1, edge="#ffffff", ins="rect", tint=pal(base, acc), num=base)
for id_, col, base, acc in [("lblue", "Blue", "#2a5bd7", "#ffd166"), ("lpurple", "Purple", "#6d3ab8", "#ffd166"), ("lgold", "Gold", "#a07a1a", "#ffffff"), ("lpink", "Pink", "#c2306e", "#ffd166")]:
    add("chip", "line", "Line", id_, col, 1, edge="#ffffff", ins="fine", tint=pal(base, acc), num=mix(base, -.2))
for id_, col, base, acc in [("cscpurple", "Purple", "#5b2a8a", "#f0c419"), ("cscteal", "Teal", "#0f6b66", "#f0c419"), ("cscorange", "Orange", "#b4471a", "#f0c419"), ("cscpink", "Pink", "#b0306a", "#f0c419")]:
    add("chip", "casino", "Casino", id_, col, 1, edge="#ffffff", ins="diamond", tint=pal(base, acc), num=base)
for id_, col, base in [("bclilac", "Lilac", "#8a5bd6"), ("bcpeach", "Peach", "#e07a4a"), ("bclemon", "Lemon", "#c9a41a")]:
    add("chip", "berry", "Berry", id_, col, 1, edge="#ffffff", ins="dot", tint=pal(base, "#e02a62"), num=mix(base, -.3))
for id_, col, base, inl in [("vccopper", "Copper", "#a0521f", "#fbeee0"), ("vcforest", "Forest", "#2a6b38", "#fbeee0"), ("vcmidnight", "Midnight", "#262b5a", "#f2f2f2"), ("vcberry", "Berry", "#a3174f", "#fbeee0")]:
    add("chip", "velvet", "Velvet", id_, col, 1, edge="#f4dfc2", ins="fine", tint=pal(base, "#e9c46a"), inlay=inl, num=mix(base, -.2))
for id_, col, base in [("rcteal", "Teal", "#0f5c63"), ("rccopper", "Copper", "#7a3a16"), ("rcgrey", "Steel", "#3d434c")]:
    add("chip", "royal", "Royal", id_, col, 1, edge="#d4af37", ins="wide", tint=pal(base, "#d4af37"), inlay="#101014", num="#d4af37")
for id_, col, base in [("gcpurple", "Purple", "#2e1248"), ("gcteal", "Teal", "#0a3a3c"), ("gcrose", "Rose", "#4a1a2a")]:
    add("chip", "gatsby", "Gatsby", id_, col, 1, edge="#d6b16a", ins="wide", tint=pal(base, "#d6b16a"), inlay="#111113", num="#d6b16a")
for id_, col, base in [("dconyx", "Onyx", "#2a2a2e"), ("dcemerald", "Emerald", "#0f5a3e"), ("dcnavy", "Navy", "#1a2a5a"), ("dcburg", "Burgundy", "#5a1426")]:
    add("chip", "deco", "Deco", id_, col, 1, edge="#d4b25a", ins="diamond", tint=pal(base, "#d4b25a"), inlay="#15130f", num="#d4b25a")
for id_, col, base in [("ccblue", "Blue", "#1d2c6b"), ("ccblack", "Black", "#2a2a2e"), ("ccpurple", "Purple", "#3d1a5c"), ("ccred", "Red", "#8a1018")]:
    add("chip", "crown", "Crown", id_, col, 1, edge="#e2c46e", ins="double", tint=pal(base, "#e2c46e"), inlay="#fbf6e6", num=base)

# ---------------- ЦЕНЫ по линейкам (01.10 вечер: владелец — «всё дёшево») ----------------
PRICE = {"back": {"classic": 10000, "mulberry": 15000, "lattice": 15000, "casino": 25000, "argyle": 25000, "night": 30000, "botanica": 40000, "berry": 50000,
                  "mosaic": 60000, "velvet": 60000, "aurora": 75000, "royal": 120000, "gatsby": 150000,
                  "carbon": 40000, "guilloche": 50000, "monogram": 60000, "marble": 80000, "deco": 90000, "crown": 110000},
         "felt": {"classic": 15000, "sunset": 40000, "monaco": 50000, "vegas": 50000, "neon": 60000, "velvet": 60000, "royal": 100000, "gatsby": 120000, "deco": 90000, "crown": 110000},
         "chip": {"classic": 10000, "line": 20000, "pop": 30000, "casino": 30000, "berry": 35000, "velvet": 60000, "royal": 90000, "gatsby": 120000, "deco": 80000, "crown": 100000}}
for k, d in PRICE.items():
    for it in CAT[k]:
        if it["p"]:
            it["p"] = d[it["g"]]

# ---------------- 04.10: НОВЫЕ РУБАШКИ — старинные рисунки public domain (cards2/vint*, готовые c/back-<id>.webp), каждая — своя линейка и цена ----------------
VINT = [("vlys", "fleur", "Fleur", "Violet", 18000, "#4b1f78"), ("vwillow", "willow", "Willow", "Sage", 60000, "#9aa58a"), ("vwautumn", "willowa", "Willow", "Autumn", 70000, "#b8641e"), ("vwnight", "willown", "Willow", "Night", 85000, "#16271f"), ("vwgold", "willowg", "Willow", "Gold", 120000, "#e2c46e"),
        ("vdamverde", "damask", "Damask", "Verde", 95000, "#7d9a3a"), ("vvelours", "velours", "Velours", "Rouge", 310000, "#a3192f"),
        ("vjardin", "jardin", "Jardin", "Bleu", 450000, "#14213d"), ("voeillet", "oeillet", "Oeillet", "Bordeaux", 740000, "#5a1020"),
        ("vcygne", "cygne", "Cygne", "Violet", 1100000, "#2a1240"), ("vcerf", "cerf", "Cerf", "Jaune", 640000, "#a87412"), ("vrusse", "russe", "Russe", "Antique", 2700000, "#c08a5a")]
for id_, g, gname, col, price, sw in VINT:
    add("back", g, gname, id_, col, price, sw=sw)

# 05.10 15:50: у каждого пака свой стол и свои фишки с именем пака, в цветах рубашки (владелец: «каждый индивидуальный»)
# pack id, линейка, имя линейки, цвет, сукно, фишка (основа), фишка (акцент), премиум
PKOWN = [("classicblue", "classic", "Classic", "Blue", "#1f3f78", "#2449a0", "#f0c419", 0),
         ("willowsage", "willow", "Willow", "Sage", "#5f7356", "#6f8a62", "#efe6cc", 0), ("willowautumn", "willowa", "Willow", "Autumn", "#7a4a22", "#b8641e", "#f3e6c8", 0),
         ("willownight", "willown", "Willow", "Night", "#16271f", "#2f5a43", "#e9dcb5", 0), ("willowgold", "willowg", "Willow", "Gold", "#1d1915", "#c9a24a", "#1a1612", 0),
         ("damaskverde", "damask", "Damask", "Verde", "#4f6a24", "#7d9a3a", "#f0e6c0", 0), ("veloursrouge", "velours", "Velours", "Rouge", "#7a1428", "#a3192f", "#f0d2a8", 1),
         ("jardinbleu", "jardin", "Jardin", "Bleu", "#14213d", "#2a3f73", "#f3ead7", 1), ("oeilletbordeaux", "oeillet", "Oeillet", "Bordeaux", "#5a1020", "#8a1a32", "#f6efe2", 1),
         ("cerfjaune", "cerf", "Cerf", "Jaune", "#7e5a12", "#a87412", "#fff2d2", 1), ("cygneviolet", "cygne", "Cygne", "Violet", "#2a1240", "#4b2370", "#e9dcc0", 1),
         ("russeantique", "russe", "Russe", "Antique", "#5e3a20", "#9c4a22", "#e8c98a", 1)]
PKOWN_IT = {}
for pid, g, gname, col, felt, cb, ca, prem in PKOWN:
    fid, cid = "pf" + pid, "pc" + pid
    add("felt", g, gname, fid, col, 15000, cloth(felt, ""), felt, v=FV.format(fid), dc=["classic", "#ffffff", "#ffffff"])
    add("chip", g, gname, cid, col, 10000, edge=ca if prem else "#ffffff", ins="wide" if prem else "rect", tint=pal(cb, ca), inlay="#101014" if prem else None, num=ca if prem else cb)
    PKOWN_IT[pid] = (fid, cid)
# 05.10 16:05: фишки Russe Antique — «ковровые»: ржаво-рыжая основа, золотые ромбы по краю, кремовая вставка как поле ковра
for it in CAT["chip"]:
    if it["id"] == "pcrusseantique":
        it.update(edge="#e8c98a", ins="diamond", inlay="#f3e6c8", num="#7a2e14", tint=["#5a2410", "#e8c98a", "#9c4a22", "#2a1a10", "#c98a52", "#f3e6c8", "#7a3418"])
for it in CAT["chip"]:
    if it.get("inlay", 0) is None: del it["inlay"]

# ---------------- 02.10: чистка расцветок — похожие и слабые скрыты из магазина (у купивших остаются в инвентаре) ----------------
HIDE = {"back": "mbsand mbsky mbgraph ltcocoa ltcream csorange csgold atan agrey ared nsrose berrylemon berrypeach berrylilac blemon bcherry volive vgraph vforest vmidnight rgrey rcopper grose mzgold alime",
        "felt": "grey olive choco sand orange slate copper mint nfmint sfember",
        "chip": "corange lgold cscorange bclemon bcpeach"}
# 05.10 15:40: цены паков — стол и фишки во всех паках классические (15к/10к), цену пака задаёт рубашка; Classic Blue = Classic Red
# 05.10 15:10: Fleur Violet (рубашка vlys и пак) — «первую можно удалить»
HIDE["back"] += " vlys"
# 05.10: чистка по листам владельца (зачёркнутые рубашки и столы); фишки — только под оставшиеся столы и паки
HIDE["back"] += " mosaic mzblue mzred mzgreen mzblack aurora apink ablue glcdollar glcazure glcmauve glcsepia crwblue crwblack crwpurple crwred cbnred cbnblue cbngold cbngreen mzpurple mzpink aviolet asunset"
HIDE["felt"] += " midnight teal blue wine fgold vfruby vfemerald vfnoir vfnavy vfplum vfcopper rfnavy rfgreen rfburg rfblack rfpurple gfblack gfemerald gfnavy gfburg dfonyx dfemerald dfnavy dfburg cfblue cfblack cfpurple cfred nfpink nfcyan nflime nfsunset nfvegas"
KEEPCHIPS = {"pc" + x[0] for x in PKOWN} | set("candy cblack cgreen classic cmauve cpink cpurple cred csage cscblack cscblue cscgreen cscpurple cscred csepia csky cstone cteal lblue lgreen lred mono neon ocean pastel rcburg rccopper rcnavy retro royal vcforest vcruby vegas".split())
# 04.10 18:00: оранжевые («узоры говно, все говно») тоже убраны из магазина
HIDE["back"] += " noir snow ltnavy ltwine ltgreen ltgrey casino csgreen csblue csblack cspurple mono vruby velvet vnoir vemerald vnavy vplum vcognac vrose vteal vsapph gatsby gemerald gnavy gburg gsilver dcoonyx dcoemerald dconavy dcoburg mrbcarrara mrbnero mrbverde mrbrosa mngcocoa mngblack mngwine mngnavy ltplum ltteal csteal cspink vcopper vberry gpurple gteal"
# 04.10: владелец вычеркнул красным — убрать из магазина (у купивших остаются)
HIDE["back"] += " sticker mbblack mbnavy mbemerald mbplum mbcream argyle wine agreen night nspurple nsteal nsblack nsburg berryfield berrypink berrymint berrysky berrycream berrygreen berryblack berrynoir royal rgreen rburg rblack rpurple mbred mbteal anavy aplum ateal nsgreen nsindigo rteal"
for k, ids in HIDE.items():
    for it in CAT[k]:
        if it["id"] in ids.split():
            it["hide"] = 1
for it in CAT["chip"]:
    if it["id"] not in KEEPCHIPS:
        it["hide"] = 1

# ---------------- ПАКИ: карты, стол и фишки одной линейки и одного цвета ----------------
PK = [("classicred", "Classic Red", "classic", "red", "cred"),
      ("velvetruby", "Velvet Ruby", "vruby", "vfruby", "vcruby"), ("velvetemerald", "Velvet Emerald", "vemerald", "vfemerald", "vcemerald"), ("velvetnoir", "Velvet Noir", "vnoir", "vfnoir", "vcnoir"),
      ("royalnavy", "Royal Navy", "royal", "rfnavy", "rcnavy"), ("royalemerald", "Royal Emerald", "rgreen", "rfgreen", "rcgreen"), ("royalburgundy", "Royal Burgundy", "rburg", "rfburg", "rcburg"),
      ("gatsbyblack", "Gatsby Black", "gatsby", "gfblack", "noir"), ("gatsbyemerald", "Gatsby Emerald", "gemerald", "gfemerald", "gcemerald"),
      ("decoonyx", "Deco Onyx", "dcoonyx", "dfonyx", "dconyx"), ("decoemerald", "Deco Emerald", "dcoemerald", "dfemerald", "dcemerald"), ("deconavy", "Deco Navy", "dconavy", "dfnavy", "dcnavy"), ("decoburgundy", "Deco Burgundy", "dcoburg", "dfburg", "dcburg"),
      ("crownblue", "Crown Blue", "crwblue", "cfblue", "ccblue"), ("crownblack", "Crown Black", "crwblack", "cfblack", "ccblack"), ("crownpurple", "Crown Purple", "crwpurple", "cfpurple", "ccpurple"), ("crownred", "Crown Red", "crwred", "cfred", "ccred"),
      ("velvetcopper", "Velvet Copper", "vcopper", "vfcopper", "vccopper"), ("royalpurple", "Royal Purple", "rpurple", "rfpurple", "royal"), ("royalblack", "Royal Black", "rblack", "rfblack", "rcblack"),
      ("gatsbynavy", "Gatsby Navy", "gnavy", "gfnavy", "gcnavy"), ("gatsbyburgundy", "Gatsby Burgundy", "gburg", "gfburg", "gcburg"),
      ("velvetnavy", "Velvet Navy", "vnavy", "vfnavy", "vcnavy"), ("velvetplum", "Velvet Plum", "vplum", "vfplum", "vcplum")]
# v68: паки новых рубашек — стол и фишки другой линейки, но в тон (имя пака = имя рубашки)
PKMIX = [("marbleverde", "Marble Verde", "mrbverde", "forest", "vcforest"), ("marblenero", "Marble Nero", "mrbnero", "black", "cblack"), ("marblerosa", "Marble Rosa", "mrbrosa", "pink", "cpink"),
         ("monogramwine", "Monogram Wine", "mngwine", "wine", "vcwine"), ("monogramnavy", "Monogram Navy", "mngnavy", "midnight", "vcmidnight"), ("monogramcocoa", "Monogram Cocoa", "mngcocoa", "vfcopper", "rccopper"),
         ("monogramblack", "Monogram Black", "mngblack", "black", "cscblack"), ("carbonred", "Carbon Red", "cbnred", "red", "lred"), ("carbonblue", "Carbon Blue", "cbnblue", "blue", "lblue"), ("carbongreen", "Carbon Green", "cbngreen", "green", "lgreen"),
         ("guillochedollar", "Guilloche Dollar", "glcdollar", "sage", "csage"), ("guillocheazure", "Guilloche Azure", "glcazure", "sky", "csky"), ("guillochemauve", "Guilloche Mauve", "glcmauve", "mauve", "cmauve"),
         ("guillochesepia", "Guilloche Sepia", "glcsepia", "sepia", "csepia"), ("marblecarrara", "Marble Carrara", "mrbcarrara", "stone", "cstone"), ("carbongold", "Carbon Gold", "cbngold", "fgold", "cgoldc")]
PKMIX += [("classicblue", "Classic Blue", "blue", "sky", "ocean")]
PKMIX += [("fleurviolet", "Fleur Violet", "vlys", "purple", "cpurple"), ("willowsage", "Willow Sage", "vwillow", "sage", "csage"), ("willowautumn", "Willow Autumn", "vwautumn", "sepia", "csepia"), ("willownight", "Willow Night", "vwnight", "forest", "cgreen"), ("willowgold", "Willow Gold", "vwgold", "black", "cblack"),
         ("damaskverde", "Damask Verde", "vdamverde", "forest", "cgreen"), ("veloursrouge", "Velours Rouge", "vvelours", "red", "cred"),
         ("jardinbleu", "Jardin Bleu", "vjardin", "indigo", "ocean"), ("oeilletbordeaux", "Oeillet Bordeaux", "voeillet", "berry", "cred"),
         ("cygneviolet", "Cygne Violet", "vcygne", "plum", "cpurple"), ("cerfjaune", "Cerf Jaune", "vcerf", "sepia", "csepia"), ("russeantique", "Russe Antique", "vrusse", "sepia", "csepia")]  # 04.10: новые старинные
ix = {k: {x["id"]: x for x in CAT[k]} for k in CAT}
packs = []
PKMIX = [(i, n, b, *PKOWN_IT[i]) if i in PKOWN_IT else (i, n, b, f, c) for i, n, b, f, c in PKMIX]  # 05.10: свои стол и фишки
for id_, n, b, f, c in PK + PKMIX:
    full = ix["back"][b]["p"] + ix["felt"][f]["p"] + ix["chip"][c]["p"]
    for k, i in (("back", b), ("felt", f), ("chip", c)):
        assert ix[k][i]["n"] == n or (id_, n, b, f, c) in PKMIX, (n, k, ix[k][i]["n"])
    if any(ix[k][i].get("hide") for k, i in (("back", b), ("felt", f), ("chip", c))):
        continue  # 04.10: в паке скрытая вещь — пак убираем из магазина
    packs.append({"id": id_, "n": n, "p": int(round(full * .7 / 500) * 500), "it": {"back": b, "felt": f, "chip": c}})

json.dump({"cat": CAT, "grp": GRP, "packs": packs}, open(OUT / "cat.json", "w"), ensure_ascii=False, indent=0)
print({k: len(v) for k, v in CAT.items()}, "packs", len(packs), "svg", len(list(OUT.glob("*.svg"))))
