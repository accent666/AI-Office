# Склейка скриншотов: для каждого экрана — 4 размера в одну картинку.
# usage: python3 -I sheet.py <shots_dir> <out_dir> [screen_prefix ...]
import sys, os, glob
from PIL import Image, ImageDraw

src, out = sys.argv[1], sys.argv[2]
only = sys.argv[3:]
os.makedirs(out, exist_ok=True)
SIZES = ["390x844", "360x740", "844x390", "740x360"]
names = sorted({os.path.basename(f).split("_", 1)[1][:-4] for f in glob.glob(os.path.join(src, "*.png"))})
for n in names:
    if only and not any(n.startswith(p) for p in only):
        continue
    ims = []
    for s in SIZES:
        f = os.path.join(src, f"{s}_{n}.png")
        if os.path.exists(f):
            im = Image.open(f).convert("RGB")
            im = im.resize((im.width // 2, im.height // 2))
            ims.append((s, im))
    if not ims:
        continue
    # портреты в ряд, ландшафты в ряд под ними
    port = [x for x in ims if x[1].height > x[1].width]
    land = [x for x in ims if x[1].height <= x[1].width]
    pw = sum(i.width for _, i in port) + 20 * len(port)
    lw = sum(i.width for _, i in land) + 20 * len(land)
    W = max(pw, lw) + 20
    H = max([i.height for _, i in port] or [0]) + max([i.height for _, i in land] or [0]) + 80
    c = Image.new("RGB", (W, H), (60, 60, 70))
    d = ImageDraw.Draw(c)
    x, y = 10, 20
    for s, i in port:
        d.text((x, 4), s, fill=(255, 255, 0)); c.paste(i, (x, y)); x += i.width + 20
    y = 20 + max([i.height for _, i in port] or [0]) + 30
    x = 10
    for s, i in land:
        d.text((x, y - 16), s, fill=(255, 255, 0)); c.paste(i, (x, y)); x += i.width + 20
    c.save(os.path.join(out, n + ".png"))
print("ok")
