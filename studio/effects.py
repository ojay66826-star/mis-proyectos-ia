"""Efectos visuales con partículas deterministas.

Cada partícula se calcula analíticamente a partir de su semilla y su edad, así
que cualquier frame se puede renderizar de forma independiente (render
paralelo, saltos en la línea de tiempo y bucles perfectos).
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from .core import clamp, mix, rng

EFFECTS = {
    "sparkles": "Destellos / brillos",
    "magic": "Magia (estrellas y aura)",
    "fire": "Fuego",
    "smoke": "Humo",
    "rain": "Lluvia",
    "water_splash": "Salpicadura de agua",
    "waves": "Olas",
    "snow": "Nieve",
    "lightning": "Rayos",
    "explosion": "Explosión",
    "energy": "Aura de energía",
    "energy_beam": "Rayo de energía",
    "confetti": "Confeti",
    "hearts": "Corazones",
    "bubbles": "Burbujas",
    "speedlines": "Líneas de velocidad (anime)",
    "fog": "Niebla",
    "fireflies": "Luciérnagas",
    "leaves": "Hojas cayendo",
}

GLOWY = {"sparkles", "magic", "fire", "lightning", "explosion", "energy", "energy_beam", "fireflies"}


def _star(d, x, y, r, col):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.28
        a = math.radians(i * 45)
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=col)


def _heart(d, x, y, s, col):
    pts = []
    for i in range(24):
        tt = i / 24 * 2 * math.pi
        hx = 16 * math.sin(tt) ** 3
        hy = -(13 * math.cos(tt) - 5 * math.cos(2 * tt) - 2 * math.cos(3 * tt) - math.cos(4 * tt))
        pts.append((x + hx * s / 16, y + hy * s / 16))
    d.polygon(pts, fill=col)


def _bolt(r, x0, y0, x1, y1, disp, depth=6):
    pts = [(x0, y0), (x1, y1)]
    for _ in range(depth):
        new = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            mx, my = (a[0] + b[0]) / 2 + r.uniform(-disp, disp), (a[1] + b[1]) / 2
            new += [(mx, my), b]
        pts = new
        disp *= 0.55
    return pts


def draw_effect(layer: Image.Image, glow: Image.Image, fx: dict, t: float, anchor=None, duration=5.0):
    """Dibuja un efecto en ``layer`` (nítido) y ``glow`` (se difumina después)."""
    W, H = layer.size
    kind = fx.get("type", "sparkles")
    start = fx.get("start", 0.0)
    end = fx.get("end") if fx.get("end") is not None else duration + 99
    if t < start or t > end:
        return
    lt = t - start
    inten = fx.get("intensity", 1.0)
    sc = fx.get("scale", 1.0) * H / 720
    ax, ay = anchor if anchor else (fx.get("x", 0.5) * W, fx.get("y", 0.6) * H)
    d = ImageDraw.Draw(layer, "RGBA")
    g = ImageDraw.Draw(glow, "RGBA")
    seed = fx.get("seed", kind)

    if kind in ("sparkles", "magic"):
        n = int(40 * inten)
        base = fx.get("color", (255, 215, 64) if kind == "sparkles" else (186, 104, 255))
        for i in range(n):
            r = rng(f"{seed}{i}")
            life = r.uniform(0.6, 1.4)
            age = (lt + r.uniform(0, life)) % life
            k = age / life
            ang = r.uniform(0, 2 * math.pi) + (lt * 1.5 if kind == "magic" else 0)
            rad = r.uniform(30, 140) * sc * (0.6 + 0.6 * k if kind == "magic" else 1)
            x, y = ax + math.cos(ang) * rad, ay - 60 * sc + math.sin(ang) * rad * 0.8 - k * 40 * sc
            s = (1 - abs(2 * k - 1)) * r.uniform(6, 14) * sc
            col = mix(base, (255, 255, 255), r.uniform(0, 0.6))
            _star(d, x, y, s, (*col, 255))
            g.ellipse([x - s * 2, y - s * 2, x + s * 2, y + s * 2], fill=(*base, 120))
        if kind == "magic":
            pr = (60 + 10 * math.sin(lt * 6)) * sc
            g.ellipse([ax - pr * 1.6, ay - 60 * sc - pr, ax + pr * 1.6, ay - 60 * sc + pr], fill=(*base, 60))
    elif kind == "fire":
        n = int(70 * inten)
        w = fx.get("width", 60) * sc
        for i in range(n):
            r = rng(f"{seed}{i}")
            life = r.uniform(0.5, 1.0)
            age = (lt + r.uniform(0, life)) % life
            k = age / life
            x = ax + r.uniform(-w, w) * (1 - k) + math.sin(lt * 8 + i) * 6 * sc
            y = ay - k * r.uniform(120, 220) * sc * inten
            s = (1 - k) * r.uniform(14, 30) * sc
            col = mix((255, 245, 157), (255, 112, 0), clamp(k * 1.6)) if k < 0.6 else mix((255, 112, 0), (183, 28, 28), (k - 0.6) / 0.4)
            a = int(255 * (1 - k) ** 0.7)
            d.ellipse([x - s, y - s * 1.3, x + s, y + s], fill=(*col, a))
            g.ellipse([x - s * 2, y - s * 2, x + s * 2, y + s * 2], fill=(255, 150, 30, int(a * 0.5)))
    elif kind == "smoke":
        n = int(26 * inten)
        for i in range(n):
            r = rng(f"{seed}{i}")
            life = r.uniform(2.0, 3.5)
            age = (lt + r.uniform(0, life)) % life
            k = age / life
            x = ax + r.uniform(-30, 30) * sc + k * r.uniform(-60, 120) * sc
            y = ay - k * r.uniform(200, 340) * sc
            s = (20 + k * 80) * sc * r.uniform(0.7, 1.2)
            gray = int(r.uniform(90, 160))
            d.ellipse([x - s, y - s, x + s, y + s], fill=(gray, gray, gray + 5, int(120 * (1 - k) * inten)))
    elif kind == "rain":
        n = int(220 * inten)
        for i in range(n):
            r = rng(f"{seed}{i}")
            sp = r.uniform(900, 1400) * H / 720
            x0 = r.uniform(-0.1, 1.1) * W
            y = (r.uniform(0, H) + lt * sp) % (H * 1.1) - H * 0.05
            x = x0 + y * 0.12
            d.line([(x, y), (x + 4 * sc, y + 22 * sc)], fill=(200, 220, 255, 150), width=max(1, int(2 * sc)))
            if y > H * 0.82 and r.random() < 0.3:
                d.ellipse([x - 8 * sc, H * 0.83, x + 8 * sc, H * 0.83 + 4 * sc], outline=(220, 235, 255, 120))
    elif kind == "snow":
        n = int(140 * inten)
        for i in range(n):
            r = rng(f"{seed}{i}")
            sp = r.uniform(40, 110) * H / 720
            y = (r.uniform(0, H) + lt * sp) % (H * 1.05)
            x = r.uniform(0, W) + math.sin(lt * r.uniform(0.5, 1.5) + i) * 20 * sc
            s = r.uniform(2, 6) * sc
            d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 255, 230))
    elif kind == "water_splash":
        n = int(60 * inten)
        period = fx.get("period", 1.6)
        for i in range(n):
            r = rng(f"{seed}{i}")
            age = (lt + r.uniform(0, 0.25)) % period
            vx, vy = r.uniform(-260, 260) * sc, r.uniform(-620, -300) * sc
            x, y = ax + vx * age, ay + vy * age + 0.5 * 1500 * sc * age * age
            if y > ay + 5:
                continue
            s = r.uniform(4, 9) * sc
            d.ellipse([x - s, y - s * 1.3, x + s, y + s], fill=(129, 212, 250, 220))
        ring = (lt % period) / period
        rr = ring * 160 * sc
        d.ellipse([ax - rr, ay - rr * 0.2, ax + rr, ay + rr * 0.2], outline=(225, 245, 254, int(200 * (1 - ring))), width=max(2, int(4 * sc)))
    elif kind == "waves":
        for j in range(4):
            yb = H * (0.86 + j * 0.035)
            pts = [(x, yb + math.sin(x / (60 * sc) + lt * (2 + j) + j) * 8 * sc) for x in range(0, W + 10, 10)]
            d.polygon(pts + [(W, H), (0, H)], fill=(3 + j * 10, 136 - j * 10, 209 - j * 15, 140))
            d.line(pts, fill=(225, 245, 254, 200), width=max(2, int(3 * sc)))
    elif kind == "lightning":
        period = fx.get("period", 2.0)
        ph = lt % period
        if ph < 0.35:
            r = rng(f"{seed}{int(lt / period)}")
            x0 = fx.get("x", r.uniform(0.2, 0.8)) * W
            pts = _bolt(r, x0 + r.uniform(-100, 100), 0, ax if anchor else x0, ay, 120 * sc)
            flick = 1 if (int(ph * 30) % 3) != 1 else 0.4
            d.line(pts, fill=(255, 255, 255, int(255 * flick)), width=max(2, int(5 * sc)))
            g.line(pts, fill=(160, 200, 255, int(220 * flick)), width=max(6, int(26 * sc)))
            if ph < 0.08:
                d.rectangle([0, 0, W, H], fill=(235, 240, 255, 120))
    elif kind == "explosion":
        k = clamp(lt / fx.get("length", 1.6))
        if k < 1:
            if lt < 0.08:
                d.rectangle([0, 0, W, H], fill=(255, 255, 240, int(200 * (1 - lt / 0.08))))
            rr = ease(k) * 220 * sc * inten
            for i in range(26):
                r = rng(f"{seed}{i}")
                a = r.uniform(0, 2 * math.pi)
                dist = rr * r.uniform(0.2, 0.9)
                s = (1 - k) * r.uniform(40, 80) * sc
                col = mix((255, 241, 118), (230, 74, 25), clamp(k * 1.3 + r.uniform(0, 0.3)))
                x, y = ax + math.cos(a) * dist, ay + math.sin(a) * dist * 0.7 - k * 60 * sc
                d.ellipse([x - s, y - s, x + s, y + s], fill=(*col, int(255 * (1 - k))))
                g.ellipse([x - s * 1.5, y - s * 1.5, x + s * 1.5, y + s * 1.5], fill=(255, 160, 40, int(160 * (1 - k))))
            ring = rr * 1.4
            d.ellipse([ax - ring, ay - ring * 0.5, ax + ring, ay + ring * 0.5], outline=(255, 255, 255, int(220 * (1 - k))), width=max(2, int(8 * sc * (1 - k))))
            for i in range(30):
                r = rng(f"d{seed}{i}")
                a = r.uniform(math.pi, 2 * math.pi)
                v = r.uniform(300, 700) * sc
                x = ax + math.cos(a) * v * lt
                y = ay + math.sin(a) * v * lt + 900 * sc * lt * lt
                d.rectangle([x - 4 * sc, y - 4 * sc, x + 4 * sc, y + 4 * sc], fill=(80, 60, 50, int(255 * (1 - k))))
        sm = dict(fx, type="smoke", start=0, intensity=1.2 * inten, seed=f"exs{seed}")
        if lt > 0.4:
            draw_effect(layer, glow, sm, lt - 0.4, (ax, ay), duration)
    elif kind == "energy":
        col = fx.get("color", (79, 195, 247))
        pulse = 0.5 + 0.5 * math.sin(lt * 10)
        cy = ay - 70 * sc
        for j in range(3):
            rr = (90 + j * 25 + pulse * 15) * sc
            g.ellipse([ax - rr * 0.8, cy - rr, ax + rr * 0.8, cy + rr], fill=(*col, int(70 - j * 18)))
        for i in range(int(16 * inten)):
            r = rng(f"{seed}{i}")
            life = r.uniform(0.4, 0.8)
            age = (lt + r.uniform(0, life)) % life
            k = age / life
            x = ax + r.uniform(-60, 60) * sc
            y = cy + 70 * sc - k * 220 * sc
            d.line([(x, y), (x, y + 30 * sc * (1 - k))], fill=(*mix(col, (255, 255, 255), 0.5), int(255 * (1 - k))), width=max(2, int(4 * sc)))
        r = rng(f"{seed}{int(lt * 12)}")
        for _ in range(2):
            a = r.uniform(0, 2 * math.pi)
            pts = _bolt(r, ax, cy, ax + math.cos(a) * 110 * sc, cy + math.sin(a) * 120 * sc, 25 * sc, 4)
            d.line(pts, fill=(255, 255, 255, 230), width=max(1, int(2 * sc)))
    elif kind == "energy_beam":
        col = fx.get("color", (100, 255, 218))
        dirx = fx.get("dir", 1)
        k = clamp(lt / 0.3)
        x1 = ax + dirx * W * k
        cy = ay - 60 * sc
        wv = (18 + 6 * math.sin(lt * 40)) * sc
        g.rectangle([min(ax, x1), cy - wv * 2.5, max(ax, x1), cy + wv * 2.5], fill=(*col, 140))
        d.rectangle([min(ax, x1), cy - wv * 0.5, max(ax, x1), cy + wv * 0.5], fill=(255, 255, 255, 255))
        d.ellipse([ax - wv * 2, cy - wv * 2, ax + wv * 2, cy + wv * 2], fill=(*col, 255))
    elif kind == "confetti":
        for i in range(int(120 * inten)):
            r = rng(f"{seed}{i}")
            y = (r.uniform(-H, 0) + lt * r.uniform(150, 300) * H / 720)
            if y < -20 or y > H:
                continue
            x = r.uniform(0, W) + math.sin(lt * 3 + i) * 25 * sc
            a = lt * r.uniform(3, 8) + i
            w, h = 10 * sc * abs(math.cos(a)) + 2, 6 * sc
            c = r.choice([(244, 67, 54), (33, 150, 243), (255, 235, 59), (76, 175, 80), (156, 39, 176), (255, 152, 0)])
            d.rectangle([x - w, y - h, x + w, y + h], fill=(*c, 240))
    elif kind == "hearts":
        for i in range(int(14 * inten)):
            r = rng(f"{seed}{i}")
            life = r.uniform(1.5, 2.5)
            age = (lt + r.uniform(0, life)) % life
            k = age / life
            x = ax + r.uniform(-120, 120) * sc + math.sin(lt * 2 + i) * 15 * sc
            y = ay - 80 * sc - k * 200 * sc
            _heart(d, x, y, r.uniform(10, 20) * sc, (*r.choice([(244, 67, 54), (236, 64, 122), (255, 128, 171)]), int(255 * (1 - k))))
    elif kind == "bubbles":
        for i in range(int(40 * inten)):
            r = rng(f"{seed}{i}")
            sp = r.uniform(60, 140) * H / 720
            y = H - (r.uniform(0, H) + lt * sp) % (H * 1.1)
            x = r.uniform(0, W) + math.sin(lt * 2 + i) * 12 * sc
            s = r.uniform(4, 14) * sc
            d.ellipse([x - s, y - s, x + s, y + s], outline=(225, 245, 254, 200), width=max(1, int(2 * sc)))
            d.ellipse([x - s * 0.5, y - s * 0.6, x - s * 0.1, y - s * 0.2], fill=(255, 255, 255, 200))
    elif kind == "speedlines":
        r = rng(f"{seed}{int(lt * 12)}")
        cx, cy = W / 2, H / 2
        for _ in range(int(60 * inten)):
            a = r.uniform(0, 2 * math.pi)
            r0 = r.uniform(0.35, 0.55) * max(W, H)
            r1 = max(W, H)
            w = r.uniform(1, 4) * sc
            d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r1, cy + math.sin(a) * r1)], fill=(255, 255, 255, 200), width=int(w) + 1)
    elif kind == "fog":
        for i in range(10):
            r = rng(f"{seed}{i}")
            x = (r.uniform(0, W) + lt * r.uniform(10, 30)) % (W * 1.4) - W * 0.2
            y = H * r.uniform(0.6, 0.9)
            g.ellipse([x - W * 0.25, y - H * 0.06, x + W * 0.25, y + H * 0.06], fill=(200, 210, 220, int(70 * inten)))
    elif kind == "fireflies":
        for i in range(int(30 * inten)):
            r = rng(f"{seed}{i}")
            x = r.uniform(0, W) + math.sin(lt * r.uniform(0.3, 0.8) + i) * 40 * sc
            y = r.uniform(0.3, 0.85) * H + math.cos(lt * r.uniform(0.3, 0.8) + i) * 30 * sc
            a = 0.5 + 0.5 * math.sin(lt * r.uniform(2, 4) + i)
            s = 3 * sc
            d.ellipse([x - s, y - s, x + s, y + s], fill=(255, 255, 160, int(255 * a)))
            g.ellipse([x - s * 5, y - s * 5, x + s * 5, y + s * 5], fill=(255, 241, 118, int(120 * a)))
    elif kind == "leaves":
        for i in range(int(30 * inten)):
            r = rng(f"{seed}{i}")
            y = (r.uniform(0, H) + lt * r.uniform(50, 100) * H / 720) % (H * 1.05)
            x = r.uniform(0, W) + math.sin(lt + i) * 50 * sc
            a = lt * 2 + i
            s = 9 * sc
            c = r.choice([(255, 143, 0), (230, 81, 0), (255, 193, 7), (139, 195, 74)])
            d.ellipse([x - s, y - s * abs(math.sin(a)) * 0.6 - 1, x + s, y + s * abs(math.sin(a)) * 0.6 + 1], fill=(*c, 230))


def ease(k):
    return 1 - (1 - k) ** 3


def render_effects(size, effects, t, anchors=None, duration=5.0, layer_filter=None):
    """Devuelve una capa RGBA con todos los efectos (incluye bloom)."""
    W, H = size
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    used_glow = False
    for fx in effects:
        if layer_filter and fx.get("layer", "front") != layer_filter:
            continue
        anchor = None
        if anchors and fx.get("on") in anchors:
            anchor = anchors[fx["on"]]
        draw_effect(layer, glow, fx, t, anchor, duration)
        used_glow |= fx.get("type") in GLOWY or fx.get("type") == "fog"
    if used_glow:
        small = glow.resize((max(1, W // 4), max(1, H // 4)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6))
        glow = small.resize((W, H), Image.BILINEAR)
        glow.alpha_composite(layer)
        return glow
    return layer
