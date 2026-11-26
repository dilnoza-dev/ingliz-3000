"""Ilova belgisini (ikonkasini) chizadi: icons/icon-192.png, icon-512.png, maskable-512.png.
Ishlatish:  python3 manba/ikonka.py   (Pillow kerak)"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'icons')
LAPIS = (23, 53, 122)
GOLD = (241, 182, 84)
TEAL = (85, 208, 196)
WHITE = (255, 255, 255)
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def star(d, cx, cy, r, color, width):
    # 8-point star: two overlapping squares, like the app's tile band
    for rot in (0, 45):
        pts = []
        for k in range(4):
            a = math.radians(rot + 45 + 90 * k)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.line(pts + [pts[0]], fill=color, width=width)


def draw(size, maskable):
    s = 4  # supersample
    W = size * s
    img = Image.new('RGB', (W, W), LAPIS)
    d = ImageDraw.Draw(img)
    # faint tile pattern
    step = W // 5
    for y in range(-step // 2, W + step, step):
        for x in range(-step // 2, W + step, step):
            star(d, x, y, step * 0.28, (40, 75, 150), max(2, W // 200))
    # content area (maskable icons keep everything inside the central 80%)
    pad = W * (0.2 if maskable else 0.1)
    inner = W - 2 * pad
    f1 = ImageFont.truetype(BOLD, int(inner * 0.36))
    f2 = ImageFont.truetype(BOLD, int(inner * 0.17))
    t1, t2 = '3000', 'SOʻZ'
    b1 = d.textbbox((0, 0), t1, font=f1)
    b2 = d.textbbox((0, 0), t2, font=f2)
    gap = inner * 0.05
    total = (b1[3] - b1[1]) + gap + (b2[3] - b2[1])
    y = (W - total) / 2
    d.text(((W - (b1[2] - b1[0])) / 2 - b1[0], y - b1[1]), t1, font=f1, fill=WHITE)
    y2 = y + (b1[3] - b1[1]) + gap
    d.text(((W - (b2[2] - b2[0])) / 2 - b2[0], y2 - b2[1]), t2, font=f2, fill=GOLD)
    # underline bar in the app's progress gradient colors
    bar_y = y2 + (b2[3] - b2[1]) + gap * 0.9
    bw = inner * 0.5
    x0 = (W - bw) / 2
    d.rounded_rectangle([x0, bar_y, x0 + bw / 2, bar_y + W * 0.025], radius=W * 0.0125, fill=TEAL)
    d.rounded_rectangle([x0 + bw / 2, bar_y, x0 + bw, bar_y + W * 0.025], radius=W * 0.0125, fill=GOLD)
    img = img.resize((size, size), Image.LANCZOS)
    if not maskable:
        # rounded corners for the plain icon
        m = Image.new('L', (size * s, size * s), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, size * s - 1, size * s - 1], radius=size * s * 0.22, fill=255)
        m = m.resize((size, size), Image.LANCZOS)
        rgba = img.convert('RGBA')
        rgba.putalpha(m)
        img = rgba
    return img


os.makedirs(OUT, exist_ok=True)
draw(192, False).save(os.path.join(OUT, 'icon-192.png'))
draw(512, False).save(os.path.join(OUT, 'icon-512.png'))
draw(512, True).save(os.path.join(OUT, 'maskable-512.png'))
draw(180, True).save(os.path.join(OUT, 'apple-touch-icon.png'))
print('icons tayyor')
