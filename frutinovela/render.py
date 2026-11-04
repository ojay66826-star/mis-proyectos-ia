"""Frutinovela de amor: corto de 10 segundos (vertical 1080x1920, 30 fps).

Todo se genera por código: personajes dibujados, cámara, subtítulos y sonido.
Uso:  python3 render.py   -> crea frutinovela_amor.mp4 en esta carpeta
Voces: espeak-ng + MBROLA (apt install espeak-ng mbrola mbrola-es3 mbrola-mx1 mbrola-mx2)
"""
import math, os, random, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 10.0
NF = int(FPS * DUR)
SR = 44100
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
rnd = random.Random(7)

def font(sz, f=FONT):
    return ImageFont.truetype(f, sz)

# ----------------------------------------------------------------- fondos
def gradient(c1, c2):
    t = np.linspace(0, 1, H)[:, None, None]
    a = np.array(c1)[None, None, :] * (1 - t) + np.array(c2)[None, None, :] * t
    return Image.fromarray(np.repeat(a, W, axis=1).astype(np.uint8))

def radial_lines(img, color, n=28, phase=0.0):
    d = ImageDraw.Draw(img)
    cx, cy, R = W / 2, H * 0.45, 3000
    for i in range(n):
        a0 = (i / n) * 2 * math.pi + phase
        a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=color)
    return img

_vig = None
def vignette(img):
    global _vig
    if _vig is None:
        y, x = np.mgrid[0:H, 0:W]
        r = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.7)) ** 2)
        _vig = np.clip(1.15 - r * 0.75, 0.25, 1)[..., None]
    return Image.fromarray((np.asarray(img).astype(np.float32) * _vig).astype(np.uint8))

# ------------------------------------------------------------- personajes
def face(d, cx, cy, s, e):
    """Cara expresiva. e: dict con eyes, brows, mouth, tears, blush, sweat, glasses."""
    ex, ey, er = 0.32 * s, -0.08 * s, 0.17 * s
    for side in (-1, 1):
        x = cx + side * ex
        y = cy + ey
        kind = e.get("eyes", "normal")
        if kind == "closed":
            d.arc([x - er, y - er * 0.6, x + er, y + er * 0.9], 200, 340, fill="black", width=int(s * 0.05))
        elif kind == "heart":
            hs = er * 1.1
            d.ellipse([x - hs, y - hs * 0.8, x, y + hs * 0.2], fill=(230, 20, 70))
            d.ellipse([x, y - hs * 0.8, x + hs, y + hs * 0.2], fill=(230, 20, 70))
            d.polygon([(x - hs, y - hs * 0.2), (x + hs, y - hs * 0.2), (x, y + hs * 1.1)], fill=(230, 20, 70))
        else:
            big = 1.25 if kind == "wide" else 1.0
            r = er * big
            d.ellipse([x - r, y - r * 1.15, x + r, y + r * 1.15], fill="white", outline="black", width=int(s * 0.025))
            pr = r * (0.35 if kind == "wide" else 0.55)
            lx = e.get("look", 0) * r * 0.35
            d.ellipse([x + lx - pr, y - pr, x + lx + pr, y + pr], fill="black")
            d.ellipse([x + lx - pr * 0.2 - pr * 0.35, y - pr * 0.7, x + lx - pr * 0.2 + pr * 0.15, y - pr * 0.2], fill="white")
        b = e.get("brows")
        if b:
            by = y - er * 1.7
            if b == "sad":      # extremo interior arriba
                p = [(x - er, by - er * 0.35 * side), (x + er, by + er * 0.35 * side)]
            elif b == "angry":  # extremo interior abajo
                p = [(x - er, by + er * 0.35 * side), (x + er, by - er * 0.35 * side)]
            else:  # up
                p = [(x - er, by - er * 0.3), (x + er, by - er * 0.3)]
            d.line(p, fill="black", width=int(s * 0.06))
        if e.get("tears"):
            t = e.get("t", 0)
            for k in range(3):
                ph = (t * 2.2 + k / 3) % 1
                ty = y + er + ph * s * 0.9
                d.ellipse([x - s * 0.04, ty - s * 0.05, x + s * 0.04, ty + s * 0.05], fill=(90, 190, 255))
            d.rectangle([x - s * 0.03, y + er, x + s * 0.03, y + er + s * 0.55], fill=(120, 205, 255))
    if e.get("glasses"):
        gy = cy + ey
        for side in (-1, 1):
            x = cx + side * ex
            d.rounded_rectangle([x - er * 1.4, gy - er * 0.9, x + er * 1.4, gy + er * 0.9], radius=er * 0.4, fill=(15, 15, 25))
            d.line([(x - er * 0.8, gy - er * 0.4), (x - er * 0.2, gy - er * 0.4)], fill=(120, 120, 160), width=int(s * 0.02))
        d.line([(cx - ex + er * 1.4, gy), (cx + ex - er * 1.4, gy)], fill=(15, 15, 25), width=int(s * 0.04))
    if e.get("blush"):
        for side in (-1, 1):
            x = cx + side * ex * 1.25
            d.ellipse([x - s * 0.1, cy + s * 0.1, x + s * 0.1, cy + s * 0.18], fill=(255, 120, 150))
    m = e.get("mouth", "smile")
    my = cy + 0.22 * s
    mw = 0.17 * s
    if m == "smile":
        d.arc([cx - mw, my - mw * 0.7, cx + mw, my + mw * 0.6], 10, 170, fill="black", width=int(s * 0.05))
    elif m == "frown":
        d.arc([cx - mw, my, cx + mw, my + mw * 1.1], 195, 345, fill="black", width=int(s * 0.05))
    elif m == "o":
        d.ellipse([cx - mw * 0.55, my - mw * 0.35, cx + mw * 0.55, my + mw * 0.95], fill=(70, 0, 20), outline="black", width=int(s * 0.03))
    elif m == "open":  # grito
        d.chord([cx - mw * 1.2, my - mw * 0.8, cx + mw * 1.2, my + mw * 1.4], 0, 180, fill=(70, 0, 20), outline="black", width=int(s * 0.03))
        d.chord([cx - mw * 0.6, my + mw * 0.4, cx + mw * 0.6, my + mw * 1.3], 180, 360, fill=(240, 90, 110))
    elif m == "kiss":
        d.ellipse([cx - mw * 0.3, my - mw * 0.2, cx + mw * 0.3, my + mw * 0.4], fill=(220, 30, 80), outline="black", width=int(s * 0.03))
    elif m == "smug":
        d.arc([cx - mw, my - mw * 0.6, cx + mw * 0.6, my + mw * 0.5], 20, 120, fill="black", width=int(s * 0.05))
    if e.get("sweat"):
        x, y = cx + s * 0.55, cy - s * 0.35
        d.ellipse([x - s * 0.06, y, x + s * 0.06, y + s * 0.16], fill=(120, 205, 255))
        d.polygon([(x - s * 0.055, y + s * 0.06), (x + s * 0.055, y + s * 0.06), (x, y - s * 0.08)], fill=(120, 205, 255))

def fresa(d, cx, cy, s, e):
    """Valentina Fresa."""
    pts = []
    for i in range(60):
        a = i / 60 * 2 * math.pi
        rx = s * (0.95 - 0.35 * max(0, math.sin(a)))      # se estrecha abajo
        ry = s * (1.05 if math.sin(a) > 0 else 0.8)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    d.polygon(pts, fill=(225, 25, 55), outline=(110, 0, 20), width=int(s * 0.04))
    r2 = random.Random(3)
    for _ in range(26):
        a = r2.uniform(0, 2 * math.pi); rr = r2.uniform(0.2, 0.75)
        x, y = cx + math.cos(a) * s * rr * 0.85, cy + math.sin(a) * s * rr * 0.85 + s * 0.15
        if abs(x - cx) < s * 0.55 and -0.35 * s < y - cy < 0.3 * s:
            continue
        d.ellipse([x - s * 0.03, y - s * 0.045, x + s * 0.03, y + s * 0.045], fill=(255, 225, 90))
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.55
        tip = (cx + math.cos(a) * s * 0.75, cy - s * 0.8 + math.sin(a) * s * 0.35)
        d.polygon([(cx - s * 0.12, cy - s * 0.78), (cx + s * 0.12, cy - s * 0.78), tip], fill=(40, 160, 60))
    d.rectangle([cx - s * 0.04, cy - s * 1.1, cx + s * 0.04, cy - s * 0.8], fill=(30, 120, 40))
    # moño telenovela
    d.ellipse([cx + s * 0.35, cy - s * 0.95, cx + s * 0.6, cy - s * 0.7], fill=(255, 90, 180))
    d.ellipse([cx + s * 0.6, cy - s * 0.95, cx + s * 0.85, cy - s * 0.7], fill=(255, 90, 180))
    d.ellipse([cx + s * 0.55, cy - s * 0.87, cx + s * 0.65, cy - s * 0.78], fill=(200, 30, 120))
    face(d, cx, cy - s * 0.05, s, e)

def platano(d, cx, cy, s, e):
    """Ricardo Plátano."""
    top, bot = [], []
    for i in range(41):
        t = i / 40
        a = math.pi * (0.15 + 0.7 * t)
        x = cx + math.cos(a) * s * 1.1 * -1
        y = cy - math.sin(a) * s * 0.35 + (t - 0.5) * 0 + s * 0.0
        y = cy + (t - 0.5) * s * 2.3
        x = cx - math.sin(math.pi * t) * s * 0.35 + s * 0.1
        wdt = s * 0.62 * math.sin(math.pi * (0.08 + 0.84 * t)) ** 0.6
        top.append((x - wdt, y)); bot.append((x + wdt, y))
    poly = top + bot[::-1]
    d.polygon(poly, fill=(255, 220, 50), outline=(150, 110, 0), width=int(s * 0.04))
    d.rectangle([top[0][0] + s * 0.25, cy - s * 1.3, top[0][0] + s * 0.45, cy - s * 1.1], fill=(110, 80, 20))
    d.ellipse([bot[-1][0] - s * 0.5, cy + s * 1.08, bot[-1][0] - s * 0.3, cy + s * 1.2], fill=(90, 60, 10))
    # bigote de galán
    face(d, cx - s * 0.05, cy - s * 0.25, s * 0.9, e)
    my = cy - s * 0.25 + 0.13 * s
    if e.get("stache", True):
        d.chord([cx - s * 0.33, my - s * 0.08, cx - s * 0.02, my + s * 0.12], 180, 360, fill=(70, 40, 10))
        d.chord([cx - s * 0.08, my - s * 0.08, cx + s * 0.23, my + s * 0.12], 180, 360, fill=(70, 40, 10))

def pina(d, cx, cy, s, e):
    """Doña Piña."""
    for k in range(7):
        a = -math.pi / 2 + (k - 3) * 0.32
        L = s * (1.1 - abs(k - 3) * 0.12)
        tip = (cx + math.cos(a) * L, cy - s * 0.95 + math.sin(a) * L)
        d.polygon([(cx - s * 0.18, cy - s * 0.9), (cx + s * 0.18, cy - s * 0.9), tip], fill=(30, 140, 60), outline=(10, 80, 30))
    box = [cx - s * 0.8, cy - s * 1.0, cx + s * 0.8, cy + s * 1.05]
    img = d._image
    body = Image.new("RGB", img.size, (235, 160, 30))
    bd = ImageDraw.Draw(body)
    for k in range(-4, 5):  # textura de rombos, recortada a la silueta
        off = k * s * 0.3
        bd.line([(cx + off - s * 0.6, cy - s * 0.8), (cx + off + s * 0.6, cy + s * 0.9)], fill=(190, 110, 10), width=int(s * 0.025))
        bd.line([(cx + off + s * 0.6, cy - s * 0.8), (cx + off - s * 0.6, cy + s * 0.9)], fill=(190, 110, 10), width=int(s * 0.025))
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).ellipse(box, fill=255)
    img.paste(body, (0, 0), mask)
    d.ellipse(box, outline=(130, 70, 0), width=int(s * 0.04))
    d.ellipse([cx - s * 0.5, cy - s * 0.5, cx + s * 0.5, cy + s * 0.65], fill=(240, 175, 50))
    # perlas de villana
    for k in range(9):
        a = math.pi * (0.15 + 0.7 * k / 8)
        x, y = cx + math.cos(a) * s * 0.55, cy + s * 0.35 + math.sin(a) * s * 0.35
        d.ellipse([x - s * 0.06, y - s * 0.06, x + s * 0.06, y + s * 0.06], fill=(250, 250, 255), outline=(170, 170, 190))
    face(d, cx, cy - s * 0.05, s * 0.85, e)

def heart(d, x, y, r, col=(255, 40, 90)):
    d.ellipse([x - r, y - r * 0.8, x, y + r * 0.2], fill=col)
    d.ellipse([x, y - r * 0.8, x + r, y + r * 0.2], fill=col)
    d.polygon([(x - r * 0.97, y - r * 0.15), (x + r * 0.97, y - r * 0.15), (x, y + r * 1.1)], fill=col)

# ----------------------------------------------------------------- texto
def caption(img, text, t_in, t, y=1480, size=92, col=(255, 255, 255), stroke=(0, 0, 0), who=None):
    """Subtítulo que entra con un 'pop'."""
    p = min(1, max(0, (t - t_in) / 0.12))
    if p <= 0:
        return img
    sc = 0.6 + 0.4 * p + 0.12 * math.sin(p * math.pi)
    f = font(int(size * sc))
    d = ImageDraw.Draw(img)
    lines = text.split("\n")
    yy = y
    if who:
        fw = font(int(46 * sc))
        tw = d.textlength(who, font=fw)
        d.rounded_rectangle([W / 2 - tw / 2 - 24, yy - 78, W / 2 + tw / 2 + 24, yy - 12], radius=20, fill=(255, 40, 120))
        d.text((W / 2 - tw / 2, yy - 72), who, font=fw, fill="white")
    widest = max(d.textlength(ln, font=f) for ln in lines)
    if widest > W - 80:  # encoge si no cabe
        sc *= (W - 80) / widest
        f = font(int(size * sc))
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text((W / 2 - tw / 2, yy), ln, font=f, fill=col, stroke_width=int(9 * sc), stroke_fill=stroke)
        yy += int(size * sc * 1.12)
    return img

# ---------------------------------------------------------------- cámara
def camera(img, zoom=1.0, cx=0.5, cy=0.45, shake=0.0, t=0.0, rot=0.0):
    if shake:
        cx += math.sin(t * 91) * shake * 0.02
        cy += math.cos(t * 77) * shake * 0.015
    if rot:
        img = img.rotate(rot, resample=Image.BICUBIC, center=(W * cx, H * cy))
    if zoom != 1.0:
        w, h = W / zoom, H / zoom
        x0 = min(max(W * cx - w / 2, 0), W - w)
        y0 = min(max(H * cy - h / 2, 0), H - h)
        img = img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
    return img

def ease(x):
    x = min(1, max(0, x))
    return 1 - (1 - x) ** 3

# ---------------------------------------------------------------- escenas
PINK = ((120, 0, 60), (255, 70, 140))
GOLD = ((60, 10, 0), (230, 120, 20))
PURP = ((25, 0, 50), (140, 30, 160))

def frame(i):
    t = i / FPS
    if t < 1.5:            # 1. Fresa descubre la traición
        img = gradient(*PURP)
        for k in range(40):  # lluvia dramática
            x = (k * 137 + 50) % W; y = ((k * 211) + t * 2600) % H
            ImageDraw.Draw(img).line([(x, y), (x - 20, y + 70)], fill=(170, 150, 255), width=4)
        d = ImageDraw.Draw(img)
        fresa(d, W / 2, 880, 400, dict(eyes="wide", brows="sad", mouth="open", tears=True, t=t))
        img = camera(vignette(img), zoom=1.0 + 0.35 * ease(t / 0.4) + 0.04 * t, shake=1.2 if t > 0.35 else 0, t=t)
        return caption(img, "¡¿ME ENGAÑASTE\nCON LA PIÑA?!", 0.1, t, who="VALENTINA FRESA")
    if t < 2.9:            # 2. Plátano niega todo
        lt = t - 1.5
        img = gradient(*GOLD)
        d = ImageDraw.Draw(img)
        platano(d, W / 2 + math.sin(lt * 30) * 12, 900, 430, dict(eyes="wide", brows="up", mouth="o", sweat=True, look=math.sin(lt * 8)))
        img = camera(vignette(img), zoom=1.15 + 0.15 * lt, t=lt)
        return caption(img, "¡NO ES LO QUE\nPARECE, FRESITA!", 1.55, t, who="RICARDO PLÁTANO")
    if t < 4.6:            # 3. Entra la Piña: revelación
        lt = t - 2.9
        img = gradient((20, 0, 0), (180, 0, 30))
        if lt > 0.45:
            radial_lines(img, (230, 30, 60), phase=lt * 0.6)
        d = ImageDraw.Draw(img)
        x = W / 2 + (1 - ease(lt / 0.3)) * 900
        pina(d, x, 900, 420, dict(eyes="normal", brows="angry", mouth="smug" if lt < 0.45 else "open", glasses=lt < 0.45))
        z = 1.0 if lt < 0.45 else 1.0 + 0.45 * ease((lt - 0.45) / 0.15)
        img = camera(vignette(img), zoom=z, shake=1.5 if lt > 0.45 else 0, t=lt)
        if lt < 0.45:
            return caption(img, "¡ALTO AHÍ!", 2.95, t, who="DOÑA PIÑA")
        return caption(img, "¡FRESA...\nSOY TU MADRE!", 3.35, t, size=110, col=(255, 230, 60), who="DOÑA PIÑA")
    if t < 5.8:            # 4. Triple zoom de reacción (DUN DUN DUN)
        lt = t - 4.6
        k = min(2, int(lt / 0.4))
        bgs = [PINK, GOLD, PURP]
        img = gradient(*bgs[k]); radial_lines(img, (255, 255, 255, 40) if False else tuple(min(255, c + 40) for c in bgs[k][1]), phase=k)
        d = ImageDraw.Draw(img)
        if k == 0:
            fresa(d, W / 2, 900, 420, dict(eyes="wide", brows="up", mouth="o"))
        elif k == 1:
            platano(d, W / 2, 900, 430, dict(eyes="wide", brows="up", mouth="o", sweat=True))
        else:
            fresa(d, W / 2, 900, 420, dict(eyes="wide", brows="angry", mouth="open"))
        sub = (lt - k * 0.4) / 0.4
        img = camera(vignette(img), zoom=1.0 + 0.25 * k + 0.5 * ease(sub / 0.25), cy=0.42, t=lt, shake=0.6)
        words = ["¿¡MAMÁ?!", "¿¡SUEGRA?!", "¡¿Y MI PAPÁ?!"]
        return caption(img, words[k], 4.6 + k * 0.4, t, size=120)
    if t < 7.1:            # 5. Plátano se arrodilla
        lt = t - 5.8
        img = gradient(*PINK)
        d = ImageDraw.Draw(img)
        for k in range(14):
            heart(d, (k * 173) % W, (H - ((k * 241 + lt * 500) % H)), 30 + (k % 3) * 12, (255, 150, 190))
        platano(d, W / 2 - 40, 1000 + (1 - ease(lt / 0.3)) * 200, 400, dict(eyes="normal", brows="sad", mouth="smile", blush=True))
        # anillo
        rx, ry = W / 2 + 330, 1050 - math.sin(min(lt, .4) / .4 * math.pi / 2) * 80
        d.ellipse([rx - 70, ry - 40, rx + 70, ry + 100], outline=(255, 215, 60), width=18)
        d.polygon([(rx - 40, ry - 40), (rx + 40, ry - 40), (rx, ry - 110)], fill=(190, 240, 255), outline=(255, 255, 255))
        sp = abs(math.sin(lt * 12))
        d.line([(rx + 60, ry - 140 - sp * 30), (rx + 60, ry - 80 + sp * 30)], fill="white", width=8)
        d.line([(rx + 30 - sp * 30, ry - 110), (rx + 90 + sp * 30, ry - 110)], fill="white", width=8)
        img = camera(vignette(img), zoom=1.05 + 0.1 * lt, t=lt)
        return caption(img, "Me da igual...\n¿TE CASAS CONMIGO?", 5.85, t, who="RICARDO PLÁTANO")
    if t < 8.7:            # 6. ¡Sí! Beso y explosión de corazones
        lt = t - 7.1
        img = gradient((255, 90, 150), (255, 200, 120))
        radial_lines(img, (255, 150, 190), n=24, phase=lt)
        d = ImageDraw.Draw(img)
        close = ease(lt / 0.5) * 120
        fresa(d, W / 2 - 300 + close, 950, 300, dict(eyes="closed" if lt > 0.45 else "heart", brows=None, mouth="kiss", blush=True))
        platano(d, W / 2 + 290 - close, 930, 300, dict(eyes="closed" if lt > 0.45 else "heart", brows=None, mouth="kiss", blush=True))
        if lt > 0.45:  # explosión
            p = lt - 0.45
            for k in range(30):
                a = k / 30 * 2 * math.pi + k
                r = p * (900 + (k % 5) * 160)
                heart(d, W / 2 + math.cos(a) * r, 800 + math.sin(a) * r, 34 + (k % 4) * 14, [(255, 30, 80), (255, 255, 255), (200, 0, 60)][k % 3])
            heart(d, W / 2, 620, 90 * min(1, p * 4) + 10 * math.sin(p * 20), (230, 0, 60))
        img = camera(vignette(img), zoom=1.0 + 0.2 * ease(lt / 0.5), cy=0.48, shake=0.4 if lt > 0.45 else 0, t=lt)
        return caption(img, "¡SÍ, MI PLATANITO!", 7.2, t, who="VALENTINA FRESA")
    # 7. Cierre: título + cliffhanger
    lt = t - 8.7
    img = gradient((10, 0, 10), (90, 0, 40))
    d = ImageDraw.Draw(img)
    for k in range(18):
        heart(d, (k * 211) % W, (k * 331) % H, 20 + (k % 3) * 10, (120, 0, 50))
    # sombra amenazante de la licuadora
    if lt > 0.55:
        a = min(1, (lt - 0.55) / 0.2)
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        al = int(200 * a)
        sd.polygon([(260, 1150), (820, 1150), (740, 1650), (340, 1650)], fill=(0, 0, 0, al))
        sd.rectangle([300, 1650, 780, 1800], fill=(0, 0, 0, al))
        sd.rectangle([240, 1100, 840, 1160], fill=(0, 0, 0, al))
        img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
        d = ImageDraw.Draw(img)
    s = 0.7 + 0.3 * ease(lt / 0.25)
    f1, f2 = font(int(118 * s), SERIF), font(int(72 * s), SERIF)
    for txt, f, y, col in [("FRUTINOVELA", f1, 560, (255, 215, 80)), ("Amor de Licuadora", f2, 760, (255, 160, 200))]:
        tw = d.textlength(txt, font=f)
        d.text((W / 2 - tw / 2, y), txt, font=f, fill=col, stroke_width=8, stroke_fill=(80, 0, 30))
    heart(d, W / 2, 960, 60 + 8 * math.sin(lt * 14), (230, 0, 60))
    img = camera(img, zoom=1.0 + 0.03 * lt, t=lt, shake=0.5 if lt > 0.55 else 0)
    if lt > 0.7:
        img = caption(img, "BRRRRRRRR...", 9.4, t, y=1250, size=80, col=(200, 220, 255))
    return caption(img, "CONTINUARÁ...", 8.8, t, y=1060, size=86)

# ----------------------------------------------------------------- voces
# Fonemas que espeak-ng genera pero las voces MBROLA no tienen -> equivalentes
PHO_FIX = {"e/": ["e"], "o/": ["o"], "h": ["r"], "oI": ["o", "i"], "jj": ["j"], "L": ["l"]}
#            voz espeak, base MBROLA, velocidad, tono, factor de frecuencia
REPARTO = {"fresa":    ("mb-es3", "es3", 190, 80, 1.18),   # dama joven, aguda
           "platano":  ("mb-mx2", "mx2", 185, 45, 1.0),    # galán mexicano
           "pina":     ("mb-es3", "es3", 160, 25, 0.78),   # villana, grave
           "narrador": ("mb-mx1", "mx1", 150, 15, 0.8)}

def _pho(ev, text, speed, pitch):
    out = subprocess.run(["espeak-ng", "-v", ev, "-q", "--pho", "-s", str(speed), "-p", str(pitch), text],
                         capture_output=True, text=True, check=True).stdout
    res = []
    for ln in out.splitlines():
        parts = ln.split()
        if not parts:
            continue
        new = PHO_FIX.get(parts[0])
        if new is None:
            res.append(ln); continue
        dur = int(parts[1]) // len(new)
        for k, ph in enumerate(new):
            res.append(" ".join([ph, str(dur)] + (parts[2:] if k == 0 else [])))
    return "\n".join(res) + "\n"

def voz(quien, text, max_dur):
    """Sintetiza una línea y la ajusta para que dure como máximo max_dur segundos."""
    ev, db, speed, pitch, fr = REPARTO[quien]
    tmp = os.path.join(HERE, "_voz")
    with open(tmp + ".pho", "w") as f:
        f.write(_pho(ev, text, speed, pitch))
    tr = 1.0
    for _ in range(2):  # 2ª pasada: comprime el tiempo si no cabe
        subprocess.run(["mbrola", "-e", "-f", str(fr), "-t", str(tr), f"/usr/share/mbrola/{db}/{db}",
                        tmp + ".pho", tmp + ".wav"], check=True, capture_output=True)
        with wave.open(tmp + ".wav") as w:
            sr = w.getframerate()
            y = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        nz = np.nonzero(np.abs(y) > 0.01)[0]
        y = y[nz[0]:nz[-1] + 1] if len(nz) else y      # recorta silencios
        if len(y) / sr <= max_dur:
            break
        tr *= max_dur / (len(y) / sr) * 0.97
    os.remove(tmp + ".pho"); os.remove(tmp + ".wav")
    y = np.interp(np.arange(int(len(y) * SR / sr)) / SR, np.arange(len(y)) / sr, y)
    y *= np.minimum(1, np.arange(len(y)) / (0.01 * SR)) * np.minimum(1, (len(y) - np.arange(len(y))) / (0.02 * SR))
    return y / (np.max(np.abs(y)) + 1e-9)

#          inicio, duración máx, personaje, texto
GUION = [(0.08, 1.40, "fresa",    "¡¿Me engañaste con la piña?!"),
         (1.52, 1.35, "platano",  "¡No es lo que parece, fresita!"),
         (2.93, 0.42, "pina",     "¡Alto ahí!"),
         (3.36, 1.20, "pina",     "¡Fresa! ¡Soy tu madre!"),
         (4.62, 0.36, "fresa",    "¿Mamá?"),
         (5.02, 0.36, "platano",  "¿Suegra?"),
         (5.42, 0.38, "fresa",    "¿Y mi papá?"),
         (5.85, 1.22, "platano",  "Me da igual. ¿Te casas conmigo?"),
         (7.13, 1.00, "fresa",    "¡Sí, mi platanito!"),
         (8.78, 0.65, "narrador", "Continuará.")]

# ----------------------------------------------------------------- audio
def build_audio(path):
    n = int(SR * DUR); out = np.zeros(n)
    tt = np.arange(n) / SR
    def add(sig, at, gain=1.0):
        s = int(at * SR); e = min(n, s + len(sig)); out[s:e] += sig[:e - s] * gain
    def tone(freqs, dur, attack=0.005, decay=3.0, kind="saw"):
        x = np.arange(int(SR * dur)) / SR; y = np.zeros_like(x)
        for f in freqs:
            for h in range(1, 7 if kind == "saw" else 2):
                y += np.sin(2 * np.pi * f * h * x) / h
        env = np.minimum(1, x / attack) * np.exp(-x * decay)
        return y * env / len(freqs)
    def noise(dur, decay=6.0, sweep=True):
        x = np.arange(int(SR * dur)) / SR
        nz = np.random.default_rng(1).standard_normal(len(x))
        k = 30 if sweep else 4
        nz = np.convolve(nz, np.ones(k) / k, mode="same")
        env = np.sin(np.pi * np.minimum(1, x / dur)) if sweep else np.exp(-x * decay)
        return nz * env
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    # cuerdas en trémolo de fondo (drama constante)
    pad_chords = [(0, [50, 53, 57]), (1.5, [48, 52, 55]), (2.9, [49, 52, 56]), (4.6, [47, 50, 53]),
                  (5.8, [53, 57, 60]), (7.1, [55, 59, 62]), (8.7, [50, 53, 56])]
    for j, (st, ch) in enumerate(pad_chords):
        en = pad_chords[j + 1][0] if j + 1 < len(pad_chords) else DUR
        seg = tone([hz(m) for m in ch], en - st, attack=0.05, decay=0.2)
        x = np.arange(len(seg)) / SR
        add(seg * (0.6 + 0.4 * np.sin(2 * np.pi * 12 * x)), st, 0.18)
    # golpes dramáticos
    add(tone([hz(38), hz(45), hz(50)], 1.4, decay=2.2), 0.0, 0.9)
    add(noise(0.35), 1.42, 0.5)                    # whoosh
    add(noise(0.35), 2.85, 0.5)
    add(tone([hz(70), hz(74)], 0.2, decay=15, kind="sine"), 2.95, 0.4)
    add(tone([hz(33), hz(40), hz(45)], 1.6, decay=1.8), 3.35, 1.1)   # ¡SOY TU MADRE!
    add(noise(0.6, decay=5, sweep=False), 3.35, 0.4)
    for k, m in enumerate([36, 39, 42]):                             # DUN DUN DUN
        add(tone([hz(m), hz(m + 7), hz(m + 12)], 0.38, decay=4), 4.6 + k * 0.4, 1.0)
    # romántico: campanitas en arpegio
    arp = [65, 69, 72, 77, 72, 69, 65, 69, 72, 76, 79, 84]
    for k, m in enumerate(arp):
        add(tone([hz(m)], 0.6, decay=5, kind="sine"), 5.85 + k * 0.11, 0.25)
    add(tone([hz(84)], 0.4, decay=8, kind="sine"), 7.55, 0.4)        # "mua"
    for k in range(12):                                              # pops de corazones
        add(tone([hz(80 + k % 5 * 2)], 0.08, decay=40, kind="sine"), 7.58 + k * 0.08, 0.3)
    add(tone([hz(53), hz(57), hz(60), hz(65)], 1.6, attack=0.02, decay=1.2), 7.1, 0.5)
    # cierre: acorde + licuadora
    add(tone([hz(38), hz(45), hz(50), hz(53)], 1.3, decay=1.5), 8.7, 0.9)
    bl = np.arange(int(SR * 0.75)) / SR
    blender = (np.sign(np.sin(2 * np.pi * (110 + 60 * bl) * bl)) * 0.5 + noise(0.75, sweep=False) * 0.8) * np.minimum(1, bl / 0.15)
    add(blender, 9.4, 0.35)
    # voces encima, con la música bajando cuando alguien habla
    music = out / (np.max(np.abs(out)) + 1e-9)
    vox = np.zeros(n)
    for st, md, quien, txt in GUION:
        y = voz(quien, txt, md)
        if quien == "pina" and "madre" in txt:   # eco de revelación
            y = np.concatenate([y, np.zeros(int(SR * 0.6))])
            for k, g in ((0.15, 0.45), (0.3, 0.25), (0.45, 0.12)):
                d_ = int(SR * k); y[d_:] += y[:-d_] * g
        s0 = int(st * SR); e0 = min(n, s0 + len(y)); vox[s0:e0] += y[:e0 - s0]
    act = np.convolve((np.abs(vox) > 0.02).astype(float), np.ones(int(SR * 0.08)) / int(SR * 0.08), mode="same")
    out = music * (1 - 0.6 * np.clip(act * 3, 0, 1)) * 0.75 + vox * 0.95
    out[-int(SR * 0.08):] *= np.linspace(1, 0, int(SR * 0.08))
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.9
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

def main():
    wav = os.path.join(HERE, "_audio.wav")
    mp4 = os.path.join(HERE, "frutinovela_amor.mp4")
    build_audio(wav)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", mp4],
                          stdin=subprocess.PIPE)
    for i in range(NF):
        ff.stdin.write(frame(i).convert("RGB").tobytes())
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    print("listo:", mp4)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:  # previsualizar fotogramas: python3 render.py 0.5 3.5 ...
        for s in sys.argv[1:]:
            frame(int(float(s) * FPS)).save(os.path.join(HERE, f"_preview_{s}.png"))
    else:
        main()
