"""Ilova belgisini (ikonkasini) chizadi: icons/icon-192.png, icon-512.png, maskable-512.png, apple-touch-icon.png.
Uslub: qorongʻi zamonaviy — toʻq fon, firuza→binafsha rangli progress halqasi, Unbounded shrifti.
Ishlatish:  python3 manba/ikonka.py   (Pillow kerak; Unbounded shrifti birinchi marta Google Fonts'dan yuklanadi)"""
import math
import os
import re
import urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'icons')
FONT_DIR = os.path.join(ROOT, '.venv', 'fonts')
BG = (9, 13, 24)
TRACK = (30, 38, 58)
CYAN = (34, 211, 238)
VIOLET = (139, 92, 246)
WHITE = (246, 248, 255)


def font_file(weight):
    """Unbounded (SIL Open Font License) — Google Fonts'dan TTF yuklab olinadi va keshlanadi."""
    os.makedirs(FONT_DIR, exist_ok=True)
    path = os.path.join(FONT_DIR, 'Unbounded-%d.ttf' % weight)
    if not os.path.exists(path):
        req = urllib.request.Request('https://fonts.googleapis.com/css2?family=Unbounded:wght@%d' % weight,
                                     headers={'User-Agent': 'Mozilla/4.0'})
        css = urllib.request.urlopen(req).read().decode()
        url = re.search(r'url\((https://[^)]+\.ttf)\)', css).group(1)
        urllib.request.urlretrieve(url, path)
    return path


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def glow(size, cx, cy, r, color, alpha):
    layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    return layer.filter(ImageFilter.GaussianBlur(r * 0.55))


def draw(size, maskable):
    s = 4  # supersample
    W = size * s
    img = Image.new('RGBA', (W, W), BG + (255,))
    # soft colour glows in opposite corners
    img = Image.alpha_composite(img, glow(W, W * 0.18, W * 0.12, W * 0.42, VIOLET, 70))
    img = Image.alpha_composite(img, glow(W, W * 0.86, W * 0.9, W * 0.42, CYAN, 55))
    d = ImageDraw.Draw(img)

    scale = 0.86 if maskable else 1.0      # maskable: keep everything inside the 80% safe circle
    cx = cy = W / 2
    R = W * 0.355 * scale                  # ring radius
    th = W * 0.05 * scale                  # ring thickness
    box = [cx - R, cy - R, cx + R, cy + R]
    d.arc(box, 0, 360, fill=TRACK, width=round(th))
    # progress arc: a gauge open at the bottom (270°), colour runs cyan → violet
    start, sweep, steps = 135, 270, 240
    for k in range(steps):
        a0 = start + sweep * k / steps
        a1 = start + sweep * (k + 1) / steps + 0.6
        d.arc(box, a0, a1, fill=mix(CYAN, VIOLET, k / (steps - 1)), width=round(th))
    # rounded caps + a glowing dot at the end of the arc
    for ang, col in ((start, CYAN), (start + sweep, VIOLET)):
        x = cx + (R - th / 2) * math.cos(math.radians(ang))
        y = cy + (R - th / 2) * math.sin(math.radians(ang))
        d.ellipse([x - th / 2, y - th / 2, x + th / 2, y + th / 2], fill=col)
    ex = cx + (R - th / 2) * math.cos(math.radians(start + sweep))
    ey = cy + (R - th / 2) * math.sin(math.radians(start + sweep))
    img = Image.alpha_composite(img, glow(W, ex, ey, th * 1.3, VIOLET, 150))
    d = ImageDraw.Draw(img)
    d.ellipse([ex - th * 0.32, ey - th * 0.32, ex + th * 0.32, ey + th * 0.32], fill=WHITE)

    # text
    # size '3000' so it sits well inside the ring
    size1 = round(W * 0.2 * scale)
    while size1 > 10 and d.textlength('3000', font=ImageFont.truetype(font_file(800), size1)) > R * 1.22:
        size1 -= 2
    f1 = ImageFont.truetype(font_file(800), size1)
    f2 = ImageFont.truetype(font_file(500), round(size1 * 0.42))
    t1, t2 = '3000', 'SOʻZ'
    b1 = d.textbbox((0, 0), t1, font=f1)
    h1 = b1[3] - b1[1]
    spacing = size1 * 0.13
    widths = [d.textlength(ch, font=f2) for ch in t2]
    w2 = sum(widths) + spacing * (len(t2) - 1)
    b2 = d.textbbox((0, 0), t2, font=f2)
    h2 = b2[3] - b2[1]
    gap = size1 * 0.3
    top = cy - (h1 + gap + h2) / 2
    d.text((cx - (b1[2] - b1[0]) / 2 - b1[0], top - b1[1]), t1, font=f1, fill=WHITE)
    x = cx - w2 / 2
    y2 = top + h1 + gap - b2[1]
    for ch, w in zip(t2, widths):
        d.text((x, y2), ch, font=f2, fill=CYAN)
        x += w + spacing

    img = img.resize((size, size), Image.LANCZOS)
    if not maskable:
        m = Image.new('L', (W, W), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, W - 1, W - 1], radius=W * 0.22, fill=255)
        img.putalpha(m.resize((size, size), Image.LANCZOS))
    else:
        img = img.convert('RGB')
    return img


os.makedirs(OUT, exist_ok=True)
draw(192, False).save(os.path.join(OUT, 'icon-192.png'))
draw(512, False).save(os.path.join(OUT, 'icon-512.png'))
draw(512, True).save(os.path.join(OUT, 'maskable-512.png'))
draw(180, True).save(os.path.join(OUT, 'apple-touch-icon.png'))
print('icons tayyor')
