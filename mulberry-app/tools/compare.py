# «до/после»: python3 -I compare.py <before_dir> <after_dir> <out_dir>
import sys, os
from PIL import Image, ImageDraw, ImageFont
B, A, O = sys.argv[1:4]
try:
    F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
except Exception:
    F = ImageFont.load_default()
pairs = [("01_home", "главная"), ("07_poker_my_turn", "покер"), ("11_bj_table_play", "блэкджек"), ("13_bc_table", "баккара"), ("24_profile", "профиль")]
for key, title in pairs:
    for orient, sizes in (("portrait", ["390x844"]), ("landscape", ["844x390"])):
        s = sizes[0]
        b = Image.open(os.path.join(B, f"{s}_{key}.png")).convert("RGB")
        a = Image.open(os.path.join(A, f"{s}_{key}.png")).convert("RGB")
        k = 0.5
        b = b.resize((int(b.width * k), int(b.height * k))); a = a.resize((int(a.width * k), int(a.height * k)))
        pad, head = 24, 64
        if orient == "portrait":
            W, H = b.width * 2 + pad * 3, b.height + head + pad
            pos = [(pad, head), (pad * 2 + b.width, head)]
        else:
            W, H = b.width + pad * 2, b.height * 2 + head * 2 + pad
            pos = [(pad, head), (pad, head * 2 + b.height)]
        c = Image.new("RGB", (W, H), (38, 38, 44)); d = ImageDraw.Draw(c)
        for (x, y), im, lab in zip(pos, (b, a), ("ДО", "ПОСЛЕ")):
            d.text((x, y - 46), f"{lab} · {title} · {s}", fill=(255, 255, 255), font=F)
            c.paste(im, (x, y))
        c.save(os.path.join(O, f"{key.split('_')[0]}_{title}_{orient}.png"), optimize=True)
print("ok")
