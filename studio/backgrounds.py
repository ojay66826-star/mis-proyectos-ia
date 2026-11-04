"""Escenarios procedurales con capas de paralaje.

``build_background(kind, W, H, time_of_day, style, seed)`` devuelve un objeto
``Background`` con capas RGBA (cielo, lejano, medio, suelo) más anchas que el
lienzo para permitir paneos de cámara con paralaje.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageFilter

from .core import font, hex2rgb, mix, rng, shade

BACKGROUNDS = {
    "park": "Parque soleado",
    "city": "Ciudad",
    "forest": "Bosque",
    "beach": "Playa",
    "space": "Espacio exterior",
    "kitchen": "Cocina",
    "stage": "Escenario / discoteca",
    "castle": "Castillo de fantasía",
    "underwater": "Fondo del mar",
    "desert": "Desierto",
    "snow": "Montañas nevadas",
    "haunted": "Bosque embrujado",
    "classroom": "Aula / pizarra",
    "studio": "Estudio liso (minimalista)",
    "dojo": "Dojo / arena de pelea",
}

PALETTES = {
    "day": dict(sky=("#5ec8f8", "#c9efff"), light=1.0),
    "sunset": dict(sky=("#ff7e5f", "#feb47b"), light=0.85),
    "night": dict(sky=("#0b1026", "#2b3a67"), light=0.45),
}

GROUND_Y = 0.82


class Background:
    def __init__(self, W, H, layers, kind, ground_y):
        self.W, self.H = W, H
        self.layers = layers  # lista de (imagen, factor_paralaje)
        self.kind = kind
        self.ground_y = ground_y
        self.clouds = []

    def render(self, cam_x=0.0, t=0.0):
        """cam_x en [-1, 1]: desplazamiento horizontal de cámara."""
        out = Image.new("RGB", (self.W, self.H))
        for img, fac in self.layers:
            extra = img.width - self.W
            off = int(extra / 2 + cam_x * extra / 2 * fac)
            off = max(0, min(extra, off))
            crop = img.crop((off, 0, off + self.W, self.H))
            if crop.mode == "RGBA":
                out.paste(crop, (0, 0), crop)
            else:
                out.paste(crop)
        # nubes animadas
        if self.clouds:
            d = ImageDraw.Draw(out, "RGBA")
            for (x, y, s, speed, col) in self.clouds:
                xx = (x * self.W + t * speed * self.W * 0.02 - cam_x * 40) % (self.W * 1.4) - self.W * 0.2
                _cloud(d, xx, y * self.H, s * self.H, col)
        return out


def _grad(W, H, top, bottom):
    top, bottom = hex2rgb(top) if isinstance(top, str) else top, hex2rgb(bottom) if isinstance(bottom, str) else bottom
    col = Image.new("RGB", (1, 256))
    for i in range(256):
        col.putpixel((0, i), mix(top, bottom, i / 255))
    return col.resize((W, H), Image.BICUBIC)


def _cloud(d, x, y, s, col=(255, 255, 255, 230)):
    for dx, dy, r in [(0, 0, 0.5), (0.45, 0.1, 0.38), (-0.45, 0.12, 0.36), (0.2, -0.22, 0.38), (-0.2, -0.18, 0.32)]:
        d.ellipse([x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s], fill=col)


def _hills(W, H, base_y, amp, color, seed, n=3):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = rng(seed)
    ph = [r.uniform(0, 6.28) for _ in range(n)]
    fr = [r.uniform(1.0, 3.5) for _ in range(n)]
    pts = [(0, H)]
    for x in range(0, W + 8, 8):
        y = base_y
        for i in range(n):
            y -= amp * math.sin(x / W * fr[i] * 2 * math.pi + ph[i]) / (i + 1)
        pts.append((x, y))
    pts.append((W, H))
    d.polygon(pts, fill=color)
    return img


def _tree(d, x, ground, h, col, trunk=(109, 76, 65), kind="round"):
    tw = h * 0.08
    d.rectangle([x - tw, ground - h * 0.45, x + tw, ground], fill=trunk)
    if kind == "pine":
        for i in range(3):
            w = h * (0.32 - i * 0.07)
            top = ground - h * (0.35 + i * 0.22)
            d.polygon([(x - w, top + h * 0.28), (x + w, top + h * 0.28), (x, top - h * 0.15)], fill=shade(col, -0.05 * i))
    elif kind == "dead":
        for a, l in [(-40, 0.35), (35, 0.3), (-10, 0.45), (60, 0.2)]:
            ra = math.radians(a)
            sx, sy = x, ground - h * 0.4
            ex, ey = sx + math.sin(ra) * h * l, sy - math.cos(ra) * h * l
            d.line([(sx, sy), (ex, ey)], fill=trunk, width=max(2, int(tw * 0.7)))
            d.line([(ex, ey), (ex + h * 0.08 * (1 if a > 0 else -1), ey - h * 0.08)], fill=trunk, width=max(1, int(tw * 0.35)))
        d.rectangle([x - tw, ground - h * 0.75, x + tw * 0.6, ground], fill=trunk)
    elif kind == "palm":
        d.line([(x, ground), (x + h * 0.1, ground - h * 0.5), (x + h * 0.05, ground - h * 0.9)], fill=trunk, width=int(tw * 1.4), joint="curve")
        cx, cy = x + h * 0.05, ground - h * 0.9
        for a in range(0, 360, 50):
            ra = math.radians(a)
            d.line([(cx, cy), (cx + math.cos(ra) * h * 0.35, cy + math.sin(ra) * h * 0.18 + h * 0.05)], fill=col, width=int(tw * 1.2))
    else:
        for dx, dy, r in [(0, -0.62, 0.3), (-0.18, -0.5, 0.22), (0.18, -0.5, 0.22), (0, -0.78, 0.2)]:
            d.ellipse([x + (dx - r) * h, ground + (dy - r) * h, x + (dx + r) * h, ground + (dy + r) * h], fill=col)
        d.ellipse([x - 0.12 * h, ground - 0.85 * h, x + 0.0 * h, ground - 0.73 * h], fill=shade(col, 0.15))


def build_background(kind: str, W: int, H: int, time_of_day: str = "day", style: str = "cartoon", seed=1) -> Background:
    kind = kind if kind in BACKGROUNDS else "park"
    if kind == "haunted":
        time_of_day = "night"
    if kind == "space":
        time_of_day = "night"
    pal = PALETTES.get(time_of_day, PALETTES["day"])
    WW = int(W * 1.4)
    gy = int(H * GROUND_Y)
    r = rng(f"{kind}-{seed}")
    layers = []
    night = time_of_day == "night"
    light = pal["light"]

    def lit(c):
        c = hex2rgb(c) if isinstance(c, str) else c
        if time_of_day == "sunset":
            c = mix(c, (255, 140, 90), 0.18)
        return shade(c, -(1 - light) * 0.9) if light < 1 else c

    if style == "minimalist" or kind == "studio":
        base = {"day": ("#f5f0e8", "#e4ddd2"), "sunset": ("#fde3d0", "#f6c1a6"), "night": ("#1f2333", "#2e3450")}[time_of_day if time_of_day in PALETTES else "day"]
        sky = _grad(WW, H, *base)
        g = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
        ImageDraw.Draw(g).rectangle([0, gy, WW, H], fill=(*shade(hex2rgb(base[1]), -0.08), 255))
        bg = Background(W, H, [(sky, 0.0), (g, 1.0)], kind, GROUND_Y)
        return bg

    # ---------------- cielo
    if kind == "underwater":
        sky = _grad(WW, H, "#0277bd", "#01335a")
    elif kind == "space":
        sky = _grad(WW, H, "#05010f", "#1a0b3a")
    elif kind in ("kitchen", "classroom", "stage", "dojo"):
        sky = None
    else:
        sky = _grad(WW, H, *pal["sky"]) if kind != "castle" else _grad(WW, H, "#4a148c" if night else "#7e57c2", "#f8bbd0")
    if sky is not None:
        d = ImageDraw.Draw(sky)
        if night or kind == "space":
            for _ in range(int(WW * H / 4000)):
                x, y = r.uniform(0, WW), r.uniform(0, gy * 0.9)
                s = r.choice([1, 1, 1, 2, 2, 3])
                d.ellipse([x, y, x + s, y + s], fill=(255, 255, 240))
            if kind != "underwater":
                mx, my = WW * 0.72, H * 0.18
                d.ellipse([mx - H * 0.07, my - H * 0.07, mx + H * 0.07, my + H * 0.07], fill=(250, 245, 220))
                if kind == "space":
                    for _ in range(3):
                        px, py, pr = r.uniform(0, WW), r.uniform(H * 0.1, H * 0.6), r.uniform(H * 0.04, H * 0.12)
                        pc = r.choice([(239, 108, 0), (126, 87, 194), (38, 166, 154), (236, 64, 122)])
                        d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=pc)
                        d.ellipse([px - pr * 0.6, py - pr * 0.7, px + pr * 0.1, py - pr * 0.1], fill=shade(pc, 0.2))
                        if pr > H * 0.08:
                            d.arc([px - pr * 1.7, py - pr * 0.35, px + pr * 1.7, py + pr * 0.35], 0, 180, fill=(255, 224, 178), width=4)
        elif kind not in ("underwater",):
            sx, sy = WW * 0.78, H * 0.17
            col = (255, 236, 130) if time_of_day == "day" else (255, 200, 120)
            glow = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).ellipse([sx - H * 0.16, sy - H * 0.16, sx + H * 0.16, sy + H * 0.16], fill=(*col, 90))
            sky.paste(glow.filter(ImageFilter.GaussianBlur(H * 0.04)), (0, 0), glow.filter(ImageFilter.GaussianBlur(H * 0.04)))
            d.ellipse([sx - H * 0.08, sy - H * 0.08, sx + H * 0.08, sy + H * 0.08], fill=col)
        layers.append((sky, 0.1))

    far = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
    mid = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
    grd = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
    fd, md, gd = ImageDraw.Draw(far), ImageDraw.Draw(mid), ImageDraw.Draw(grd)
    clouds = []

    if kind in ("park", "forest", "haunted", "castle"):
        far = _hills(WW, H, gy - H * 0.12, H * 0.07, lit("#81c784" if kind != "haunted" else "#263238"), seed)
        fd = ImageDraw.Draw(far)
        if kind == "castle":
            cx, base = WW * 0.55, gy - H * 0.1
            cc = lit("#9575cd")
            fd.rectangle([cx - H * 0.16, base - H * 0.25, cx + H * 0.16, base], fill=cc)
            for tx in (-0.2, 0.2):
                fd.rectangle([cx + tx * H - H * 0.05, base - H * 0.38, cx + tx * H + H * 0.05, base], fill=shade(cc, -0.1))
                fd.polygon([(cx + tx * H - H * 0.07, base - H * 0.38), (cx + tx * H + H * 0.07, base - H * 0.38), (cx + tx * H, base - H * 0.52)], fill=lit("#e91e63"))
            fd.rectangle([cx - H * 0.04, base - H * 0.1, cx + H * 0.04, base], fill=(60, 30, 80))
        mid = _hills(WW, H, gy - H * 0.03, H * 0.04, lit("#66bb6a" if kind != "haunted" else "#37474f"), f"{seed}-7")
        md = ImageDraw.Draw(mid)
        n = 14 if kind == "forest" else 7
        for i in range(n):
            x = r.uniform(0, WW)
            h = r.uniform(H * 0.25, H * 0.45) * (1.3 if kind == "forest" else 1)
            tk = "dead" if kind == "haunted" else ("pine" if kind == "forest" and r.random() < 0.6 else "round")
            _tree(md, x, gy - H * 0.01, h, lit(r.choice(["#388e3c", "#43a047", "#2e7d32"])) if kind != "haunted" else (30, 30, 40),
                  trunk=lit("#6d4c41") if kind != "haunted" else (25, 20, 30), kind=tk)
        gd.rectangle([0, gy, WW, H], fill=lit("#7cb342" if kind != "haunted" else "#212121"))
        if kind == "park":
            gd.polygon([(WW * 0.35, H), (WW * 0.65, H), (WW * 0.55, gy), (WW * 0.45, gy)], fill=lit("#d7ccc8"))
        for _ in range(int(WW / 14)):
            x, y = r.uniform(0, WW), r.uniform(gy, H)
            gd.line([(x, y), (x + r.uniform(-3, 3), y - r.uniform(5, 12))], fill=lit("#558b2f" if kind != "haunted" else "#37474f"), width=2)
        if kind == "park":
            for _ in range(18):
                x, y = r.uniform(0, WW), r.uniform(gy + 8, H)
                c = r.choice([(255, 235, 59), (244, 143, 177), (255, 255, 255)])
                gd.ellipse([x - 4, y - 4, x + 4, y + 4], fill=c)
        if not night:
            clouds = [(r.uniform(0, 1.2), r.uniform(0.08, 0.32), r.uniform(0.06, 0.1), r.uniform(0.5, 1.5), (255, 255, 255, 225)) for _ in range(4)]
    elif kind == "city":
        for layer, dd, fac, top in ((far, fd, 0.6, 0.35), (mid, md, 0.8, 0.5)):
            x = 0
            while x < WW:
                bw = r.uniform(H * 0.12, H * 0.24)
                bh = r.uniform(H * 0.25, H * 0.6) * (1 if layer is mid else 1.15)
                c = lit(r.choice(["#546e7a", "#607d8b", "#78909c", "#455a64"])) if layer is mid else lit("#90a4ae")
                dd.rectangle([x, gy - bh, x + bw, gy], fill=c)
                if layer is mid:
                    for wy in range(int(gy - bh + 12), int(gy - 10), 22):
                        for wx in range(int(x + 8), int(x + bw - 12), 18):
                            lit_on = r.random() < (0.6 if night else 0.25)
                            dd.rectangle([wx, wy, wx + 9, wy + 12], fill=(255, 224, 130) if lit_on else shade(c, -0.25))
                x += bw + r.uniform(2, 12)
        gd.rectangle([0, gy, WW, H], fill=lit("#424242"))
        gd.rectangle([0, gy, WW, gy + H * 0.025], fill=lit("#9e9e9e"))
        for x in range(0, WW, int(H * 0.16)):
            gd.rectangle([x, gy + (H - gy) * 0.55, x + H * 0.08, gy + (H - gy) * 0.6], fill=(250, 250, 250))
        if not night:
            clouds = [(r.uniform(0, 1.2), r.uniform(0.06, 0.2), r.uniform(0.05, 0.08), r.uniform(0.5, 1.2), (255, 255, 255, 210)) for _ in range(3)]
    elif kind == "beach":
        sea_top = gy - H * 0.16
        fd.rectangle([0, sea_top, WW, gy], fill=lit("#039be5"))
        for i in range(10):
            y = sea_top + i * (gy - sea_top) / 10
            for x in range(0, WW, 60):
                fd.arc([x + (i % 2) * 30, y, x + 40 + (i % 2) * 30, y + 8], 0, 180, fill=lit("#81d4fa"), width=2)
        gd.rectangle([0, gy - H * 0.01, WW, H], fill=lit("#ffe0a3"))
        for _ in range(3):
            _tree(md, r.uniform(0, WW), gy, r.uniform(H * 0.35, H * 0.5), lit("#2e7d32"), kind="palm")
        clouds = [(r.uniform(0, 1.2), r.uniform(0.08, 0.25), r.uniform(0.05, 0.09), r.uniform(0.5, 1.2), (255, 255, 255, 220)) for _ in range(3)]
    elif kind == "desert":
        far = _hills(WW, H, gy - H * 0.08, H * 0.05, lit("#ffcc80"), seed)
        mid = _hills(WW, H, gy - H * 0.02, H * 0.03, lit("#ffb74d"), f"{seed}-3")
        md = ImageDraw.Draw(mid)
        for _ in range(4):
            x, h = r.uniform(0, WW), r.uniform(H * 0.15, H * 0.25)
            c = lit("#558b2f")
            md.rounded_rectangle([x - h * 0.1, gy - h, x + h * 0.1, gy], radius=h * 0.1, fill=c)
            md.rounded_rectangle([x - h * 0.35, gy - h * 0.75, x - h * 0.2, gy - h * 0.35], radius=h * 0.07, fill=c)
            md.rectangle([x - h * 0.3, gy - h * 0.45, x, gy - h * 0.35], fill=c)
        gd.rectangle([0, gy, WW, H], fill=lit("#ffca7a"))
    elif kind == "snow":
        for i, (base, c) in enumerate([(gy - H * 0.05, "#b0bec5"), (gy, "#90a4ae")]):
            dd = fd if i == 0 else md
            x = -H * 0.2
            while x < WW:
                w = r.uniform(H * 0.35, H * 0.6)
                ht = r.uniform(H * 0.3, H * 0.5) * (1 - 0.3 * i)
                dd.polygon([(x, base), (x + w / 2, base - ht), (x + w, base)], fill=lit(c))
                dd.polygon([(x + w / 2 - w * 0.12, base - ht * 0.76), (x + w / 2, base - ht), (x + w / 2 + w * 0.12, base - ht * 0.76)], fill=(250, 250, 255))
                x += w * 0.7
        gd.rectangle([0, gy, WW, H], fill=lit("#f5f9ff"))
    elif kind == "space":
        gd.ellipse([-WW * 0.2, gy, WW * 1.2, gy + H * 0.9], fill=(120, 110, 140))
        for _ in range(12):
            x, y, cr = r.uniform(0, WW), r.uniform(gy + 10, H), r.uniform(6, 22)
            gd.ellipse([x - cr, y - cr * 0.5, x + cr, y + cr * 0.5], fill=(95, 85, 115))
    elif kind == "underwater":
        for _ in range(10):
            x, h = r.uniform(0, WW), r.uniform(H * 0.15, H * 0.35)
            pts = [(x + 10 * math.sin(i * 0.8), gy - h * i / 8) for i in range(9)]
            md.line(pts, fill=(46, 125, 50), width=10, joint="curve")
        for _ in range(8):
            x, y = r.uniform(0, WW), r.uniform(gy - H * 0.03, gy + 10)
            md.ellipse([x - 22, y - 14, x + 22, y + 14], fill=r.choice([(255, 112, 67), (240, 98, 146), (171, 71, 188)]))
        gd.rectangle([0, gy, WW, H], fill=(215, 190, 140))
        light = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(light)
        for i in range(6):
            x = r.uniform(0, WW)
            ld.polygon([(x, 0), (x + 60, 0), (x + 200, gy), (x + 120, gy)], fill=(255, 255, 255, 22))
        layers.append((light, 0.3))
    elif kind in ("kitchen", "classroom", "stage", "dojo"):
        wall = {"kitchen": "#fff3e0", "classroom": "#e8f5e9", "stage": "#1a0f2e", "dojo": "#efebe9"}[kind]
        back = Image.new("RGB", (WW, H), lit(wall))
        bd = ImageDraw.Draw(back)
        if kind == "kitchen":
            for y in range(0, gy - int(H * 0.18), 40):
                for x in range(0, WW, 40):
                    bd.rectangle([x + 1, y + 1, x + 38, y + 38], outline=lit("#ffe0b2"), width=2)
            wx = WW * 0.5
            bd.rectangle([wx - H * 0.22, H * 0.1, wx + H * 0.22, H * 0.42], fill=lit("#81d4fa"), outline=lit("#8d6e63"), width=10)
            bd.line([(wx, H * 0.1), (wx, H * 0.42)], fill=lit("#8d6e63"), width=8)
            for x in (WW * 0.18, WW * 0.82):
                bd.rectangle([x - H * 0.12, H * 0.12, x + H * 0.12, H * 0.3], fill=lit("#a1887f"))
            back.paste(lit("#8d6e63"), [0, int(gy - H * 0.2), WW, gy])
            bd.rectangle([0, gy - H * 0.2, WW, gy - H * 0.17], fill=lit("#d7ccc8"))
            for x in range(0, WW, int(H * 0.3)):
                bd.rectangle([x + 10, gy - H * 0.15, x + H * 0.3 - 10, gy - 6], outline=lit("#6d4c41"), width=3)
            gd.rectangle([0, gy, WW, H], fill=lit("#bcaaa4"))
            for x in range(0, WW, 60):
                gd.line([(x, gy), (x - 40, H)], fill=lit("#a1887f"), width=2)
        elif kind == "classroom":
            bx = WW * 0.5
            bd.rectangle([bx - H * 0.5, H * 0.12, bx + H * 0.5, H * 0.55], fill=(46, 94, 66), outline=lit("#8d6e63"), width=14)
            f = font(int(H * 0.05))
            bd.text((bx - H * 0.4, H * 0.18), "2 + 2 = 4   ABC", fill=(235, 235, 220), font=f)
            gd.rectangle([0, gy, WW, H], fill=lit("#a1887f"))
        elif kind == "stage":
            for x in range(0, WW, 30):
                bd.rectangle([x, 0, x + 26, gy], fill=(120 + (x // 30 % 2) * 20, 20, 50))
            bd.rectangle([0, 0, WW, H * 0.08], fill=(150, 20, 50))
            spot = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(spot)
            for i, c in enumerate([(255, 82, 82), (64, 196, 255), (255, 235, 59)]):
                x = WW * (0.3 + 0.2 * i)
                sd.polygon([(x - 20, 0), (x + 20, 0), (x + H * 0.25, gy), (x - H * 0.25, gy)], fill=(*c, 45))
            back = back.convert("RGBA")
            back.alpha_composite(spot.filter(ImageFilter.GaussianBlur(10)))
            back = back.convert("RGB")
            gd.rectangle([0, gy, WW, H], fill=(40, 26, 20))
            for x in range(0, WW, 50):
                gd.rectangle([x, gy, x + 48, H], fill=(70 + (x // 50 % 2) * 30, 30, 90))
        else:  # dojo
            for x in range(0, WW, int(H * 0.2)):
                bd.rectangle([x, H * 0.08, x + H * 0.19, gy], fill=lit("#fff8e1"), outline=lit("#5d4037"), width=6)
                bd.line([(x, H * 0.4), (x + H * 0.19, H * 0.4)], fill=lit("#5d4037"), width=4)
            gd.rectangle([0, gy, WW, H], fill=lit("#c8a96a"))
            for x in range(0, WW, int(H * 0.25)):
                gd.line([(x, gy), (x, H)], fill=lit("#a1887f"), width=3)
        layers.append((back, 0.2))

    if kind == "haunted":
        fog = Image.new("RGBA", (WW, H), (0, 0, 0, 0))
        fgd = ImageDraw.Draw(fog)
        for _ in range(12):
            x, y = r.uniform(0, WW), r.uniform(gy - H * 0.1, gy + H * 0.05)
            fgd.ellipse([x - H * 0.3, y - H * 0.05, x + H * 0.3, y + H * 0.05], fill=(180, 200, 210, 60))
        mid = Image.alpha_composite(mid, fog.filter(ImageFilter.GaussianBlur(20)))

    if not any(l[0] is far for l in layers):
        layers.append((far, 0.35))
    layers.append((mid, 0.6))
    layers.append((grd, 1.0))
    bg = Background(W, H, layers, kind, GROUND_Y)
    bg.clouds = clouds
    return bg
