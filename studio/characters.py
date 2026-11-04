"""Renderizador procedural de personajes 2D.

Cada personaje se describe con un diccionario (la "ficha" o character sheet) y se
dibuja siempre con las mismas reglas, por lo que su apariencia es 100 %
consistente entre escenas.  La pose (emoción, visema, ángulos de extremidades…)
llega en un objeto ``Pose`` calculado por ``motion.py``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .core import font, hex2rgb, mix, rgba, shade

SS = 2  # supersampling para antialiasing

# --------------------------------------------------------------------------
# Catálogo de especies (nombre en español -> datos por defecto)
# --------------------------------------------------------------------------
SPECIES = {
    # frutas
    "manzana": dict(kind="fruit", shape="apple", color="#e53935", label="Manzana"),
    "platano": dict(kind="fruit", shape="banana", color="#fdd835", label="Plátano"),
    "naranja": dict(kind="fruit", shape="orange", color="#fb8c00", label="Naranja"),
    "fresa": dict(kind="fruit", shape="strawberry", color="#e8344e", label="Fresa"),
    "uva": dict(kind="fruit", shape="grape", color="#7e57c2", label="Uva"),
    "sandia": dict(kind="fruit", shape="watermelon", color="#43a047", label="Sandía"),
    "pina": dict(kind="fruit", shape="pineapple", color="#fbc02d", label="Piña"),
    "limon": dict(kind="fruit", shape="lemon", color="#f7e83a", label="Limón"),
    "pera": dict(kind="fruit", shape="pear", color="#c0ca33", label="Pera"),
    "cereza": dict(kind="fruit", shape="cherry", color="#c62828", label="Cereza"),
    "aguacate": dict(kind="fruit", shape="avocado", color="#558b2f", label="Aguacate"),
    # animales (estilo chibi)
    "gato": dict(kind="animal", shape="cat", color="#ff9800", label="Gato"),
    "perro": dict(kind="animal", shape="dog", color="#a1887f", label="Perro"),
    "conejo": dict(kind="animal", shape="bunny", color="#f3f0f5", label="Conejo"),
    "oso": dict(kind="animal", shape="bear", color="#8d6e63", label="Oso"),
    "rana": dict(kind="animal", shape="frog", color="#66bb6a", label="Rana"),
    "pinguino": dict(kind="animal", shape="penguin", color="#37474f", label="Pingüino"),
    "zorro": dict(kind="animal", shape="fox", color="#f4511e", label="Zorro"),
    "panda": dict(kind="animal", shape="panda", color="#fafafa", label="Panda"),
    # otros
    "robot": dict(kind="robot", shape="robot", color="#90a4ae", label="Robot"),
    "nino": dict(kind="human", shape="human", color="#42a5f5", label="Niño", hair="short"),
    "nina": dict(kind="human", shape="human", color="#ec407a", label="Niña", hair="long"),
    "persona": dict(kind="human", shape="human", color="#5c6bc0", label="Persona", hair="short"),
    "mascota": dict(kind="blob", shape="blob", color="#4fc3f7", label="Mascota"),
    "fantasma": dict(kind="blob", shape="ghost", color="#eceff1", label="Fantasma"),
    "monstruo": dict(kind="blob", shape="monster", color="#8e24aa", label="Monstruo"),
    "estrella": dict(kind="blob", shape="star", color="#ffd54f", label="Estrella"),
    "mago": dict(kind="human", shape="human", color="#5e35b1", label="Mago", hair="short", accessory="wizard"),
}

EMOTIONS = ["neutral", "happy", "joy", "sad", "angry", "surprised", "scared", "love", "sleepy", "excited", "confused"]
VISEMES = ["X", "A", "E", "O", "U", "M", "F"]
ACCESSORIES = ["none", "hat", "bow", "glasses", "crown", "cap", "wizard", "scarf"]

SKIN_TONES = ["#f1c27d", "#e0ac69", "#c68642", "#8d5524", "#ffdbac"]


def make_character(species: str, name: str | None = None, **over) -> dict:
    base = SPECIES.get(species, SPECIES["mascota"])
    spec = dict(
        id=over.pop("id", None) or (name or base["label"]).lower().replace(" ", "_"),
        name=name or base["label"],
        species=species if species in SPECIES else "mascota",
        kind=base["kind"],
        shape=base["shape"],
        color=base["color"],
        accent=None,
        eyes="round",
        accessory=base.get("accessory", "none"),
        hair=base.get("hair", "short"),
        hair_color="#4e342e",
        skin="#f1c27d",
        voice=None,
        personality="",
        height=1.0,
    )
    spec.update({k: v for k, v in over.items() if v is not None})
    return spec


def character_prompt(spec: dict, style: str = "cartoon") -> str:
    """Descripción fija para generadores de imagen IA (consistencia de personaje)."""
    acc = "" if spec.get("accessory", "none") == "none" else f", wearing a {spec['accessory']}"
    return (f"{spec['name']}, a cute anthropomorphic {spec.get('shape')} character, "
            f"main color {spec['color']}, big expressive eyes, small arms and legs{acc}, "
            f"{style} style, consistent character design, clean background")


@dataclass
class Pose:
    emotion: str = "neutral"
    viseme: str = "X"
    blink: float = 0.0
    look: tuple = (0.0, 0.0)
    arm_back: tuple = (12.0, 8.0)     # (hombro, codo) grados; 0 = abajo, + = hacia fuera/arriba
    arm_front: tuple = (12.0, 8.0)
    leg_back: tuple = (0.0, 0.0)
    leg_front: tuple = (0.0, 0.0)
    body_dy: float = 0.0              # elevación en unidades de altura
    squash: float = 1.0               # >1 aplastado, <1 estirado
    tilt: float = 0.0                 # grados
    facing: int = 1
    extras: list = field(default_factory=list)


# --------------------------------------------------------------------------
class _Ctx:
    """Mapea coordenadas locales (x derecha, y arriba, en unidades de altura)."""

    def __init__(self, H, pose, ox, oy):
        self.H, self.pose, self.ox, self.oy = H, pose, ox, oy
        s = pose.squash
        self.sx, self.sy = s ** 0.5, 1 / (s ** 0.5)

    def P(self, x, y):
        return (self.ox + x * self.H * self.sx, self.oy - (y + self.pose.body_dy) * self.H * self.sy)

    def E(self, cx, cy, rx, ry):
        x, y = self.P(cx, cy)
        rx *= self.H * self.sx
        ry *= self.H * self.sy
        return [x - rx, y - ry, x + rx, y + ry]

    def L(self, v):
        return v * self.H


def _limb(d, ctx, root, angles, lens, color, outline, width, hand=None, foot=None, glove=None):
    a1, a2 = angles
    x0, y0 = root
    r1, r2 = math.radians(a1), math.radians(a1 + a2)
    x1, y1 = x0 + math.sin(r1) * lens[0], y0 - math.cos(r1) * lens[0]
    x2, y2 = x1 + math.sin(r2) * lens[1], y1 - math.cos(r2) * lens[1]
    pts = [ctx.P(x0, y0), ctx.P(x1, y1), ctx.P(x2, y2)]
    w = max(2, int(ctx.L(width)))
    ow = int(w + ctx.L(0.022)) if outline else w
    if outline:
        d.line(pts, fill=outline, width=ow, joint="curve")
        for p in pts:
            d.ellipse([p[0] - ow / 2, p[1] - ow / 2, p[0] + ow / 2, p[1] + ow / 2], fill=outline)
    d.line(pts, fill=color, width=w, joint="curve")
    for p in pts[:2]:
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=color)
    if hand:
        hr = ctx.L(hand)
        c = glove or color
        bb = [pts[2][0] - hr, pts[2][1] - hr, pts[2][0] + hr, pts[2][1] + hr]
        d.ellipse(bb, fill=c, outline=outline, width=max(1, int(ctx.L(0.012))) if outline else 0)
    if foot:
        fw, fh = ctx.L(foot[0]), ctx.L(foot[1])
        fx = pts[2][0] + fw * 0.35
        bb = [fx - fw, pts[2][1] - fh, fx + fw, pts[2][1] + fh * 0.6]
        d.ellipse(bb, fill=foot[2], outline=outline, width=max(1, int(ctx.L(0.012))) if outline else 0)


def _polygon_smooth(points, steps=8):
    """Curva cerrada Catmull-Rom a partir de puntos de control."""
    out = []
    n = len(points)
    for i in range(n):
        p0, p1, p2, p3 = points[i - 1], points[i], points[(i + 1) % n], points[(i + 2) % n]
        for s in range(steps):
            t = s / steps
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    return out


def _star_points(cx, cy, r1, r2, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


# --------------------------------------------------------------------------
def _layout(spec):
    if spec["kind"] == "human":
        return dict(face=(0.0, 0.84), fs=0.17, shoulder=(0.14, 0.64), arm=(0.15, 0.14), hip=(0.07, 0.38),
                    leg=(0.19, 0.19), limbw=0.055, hand=0.035)
    if spec["shape"] in ("banana", "pineapple"):
        return dict(face=(0.0, 0.6), fs=0.26, shoulder=(0.2, 0.52), arm=(0.16, 0.15), hip=(0.09, 0.26),
                    leg=(0.13, 0.13), limbw=0.028, hand=0.04)
    if spec["shape"] in ("ghost",):
        return dict(face=(0.0, 0.62), fs=0.28, shoulder=(0.3, 0.52), arm=(0.13, 0.12), hip=(0.1, 0.2),
                    leg=(0.0, 0.0), limbw=0.07, hand=0.0)
    return dict(face=(0.0, 0.58), fs=0.3, shoulder=(0.31, 0.5), arm=(0.16, 0.15), hip=(0.11, 0.26),
                leg=(0.13, 0.13), limbw=0.028, hand=0.045)


def _draw_body(d, ctx, spec, col, style):
    """Dibuja la silueta principal. Devuelve lista de detalles a dibujar encima."""
    sh = spec["shape"]
    dark = shade(col, -0.35)
    if sh == "apple":
        d.ellipse(ctx.E(-0.13, 0.52, 0.22, 0.27), fill=col)
        d.ellipse(ctx.E(0.13, 0.52, 0.22, 0.27), fill=col)
        d.ellipse(ctx.E(0, 0.46, 0.3, 0.22), fill=col)
    elif sh in ("orange", "blob", "monster"):
        d.ellipse(ctx.E(0, 0.53, 0.33, 0.31), fill=col)
    elif sh == "lemon":
        d.ellipse(ctx.E(0, 0.53, 0.33, 0.27), fill=col)
        d.polygon([ctx.P(0.3, 0.6), ctx.P(0.4, 0.53), ctx.P(0.3, 0.46)], fill=col)
        d.polygon([ctx.P(-0.3, 0.6), ctx.P(-0.4, 0.53), ctx.P(-0.3, 0.46)], fill=col)
    elif sh == "cherry":
        d.ellipse(ctx.E(0, 0.5, 0.3, 0.28), fill=col)
    elif sh == "grape":
        for gx, gy in [(-0.2, 0.78), (0.0, 0.82), (0.2, 0.78), (-0.29, 0.6), (0.29, 0.6), (-0.24, 0.4), (0.24, 0.4), (0, 0.3)]:
            d.ellipse(ctx.E(gx, gy, 0.13, 0.13), fill=shade(col, -0.08))
        d.ellipse(ctx.E(0, 0.56, 0.29, 0.29), fill=col)
    elif sh == "watermelon":
        d.ellipse(ctx.E(0, 0.53, 0.35, 0.3), fill=col)
    elif sh == "strawberry":
        pts = [(0, 0.24), (0.2, 0.36), (0.33, 0.62), (0.22, 0.82), (0, 0.8), (-0.22, 0.82), (-0.33, 0.62), (-0.2, 0.36)]
        d.polygon([ctx.P(*p) for p in _polygon_smooth(pts)], fill=col)
    elif sh == "pear":
        d.ellipse(ctx.E(0, 0.45, 0.31, 0.24), fill=col)
        d.ellipse(ctx.E(0, 0.74, 0.18, 0.2), fill=col)
    elif sh == "avocado":
        d.ellipse(ctx.E(0, 0.46, 0.3, 0.25), fill=col)
        d.ellipse(ctx.E(0, 0.72, 0.2, 0.22), fill=col)
    elif sh == "banana":
        outer = [(0.16 + 0.12 * math.sin(math.radians(i * 9)), 0.2 + i * 0.032) for i in range(21)]
        inner = [(-0.16 + 0.12 * math.sin(math.radians(i * 9)), 0.2 + i * 0.032) for i in range(20, -1, -1)]
        d.polygon([ctx.P(*p) for p in _polygon_smooth((outer + inner)[::2], 6)], fill=col)
        d.ellipse(ctx.E(0.0, 0.87, 0.045, 0.04), fill=(110, 80, 40))
    elif sh == "pineapple":
        d.ellipse(ctx.E(0, 0.52, 0.28, 0.32), fill=col)
    elif sh == "robot":
        d.rounded_rectangle(ctx.E(0, 0.52, 0.31, 0.27), radius=ctx.L(0.08), fill=col)
        d.line([ctx.P(0, 0.79), ctx.P(0, 0.92)], fill=dark, width=int(ctx.L(0.02)))
        d.ellipse(ctx.E(0, 0.94, 0.04, 0.04), fill=(255, 80, 80))
    elif sh == "ghost":
        pts = [(-0.3, 0.2), (-0.32, 0.6), (-0.2, 0.86), (0, 0.9), (0.2, 0.86), (0.32, 0.6), (0.3, 0.2),
               (0.18, 0.26), (0.08, 0.18), (-0.04, 0.26), (-0.16, 0.18)]
        d.polygon([ctx.P(*p) for p in _polygon_smooth(pts)], fill=col)
    elif sh == "star":
        x, y = ctx.P(0, 0.54)
        d.polygon(_star_points(x, y, ctx.L(0.4), ctx.L(0.2)), fill=col)
        d.ellipse(ctx.E(0, 0.54, 0.24, 0.22), fill=col)
    elif spec["kind"] == "animal":
        ear = shade(col, -0.12)
        if sh in ("cat", "fox"):
            for s in (-1, 1):
                d.polygon([ctx.P(0.12 * s, 0.78), ctx.P(0.3 * s, 0.98), ctx.P(0.32 * s, 0.68)], fill=col)
        elif sh == "dog":
            for s in (-1, 1):
                d.ellipse(ctx.E(0.31 * s, 0.6, 0.08, 0.17), fill=shade(col, -0.25))
        elif sh == "bunny":
            for s in (-1, 1):
                d.ellipse(ctx.E(0.12 * s, 0.98, 0.07, 0.22), fill=col)
                d.ellipse(ctx.E(0.12 * s, 0.98, 0.035, 0.16), fill=(248, 187, 208))
        elif sh in ("bear", "panda"):
            for s in (-1, 1):
                d.ellipse(ctx.E(0.24 * s, 0.82, 0.09, 0.09), fill=(30, 30, 30) if sh == "panda" else ear)
        elif sh == "frog":
            for s in (-1, 1):
                d.ellipse(ctx.E(0.15 * s, 0.78, 0.11, 0.1), fill=col)
        d.ellipse(ctx.E(0, 0.53, 0.33, 0.3), fill=col)
    else:
        d.ellipse(ctx.E(0, 0.53, 0.33, 0.31), fill=col)


def _draw_pattern(d, ctx, spec, col):
    """Texturas internas que se recortan a la silueta del cuerpo."""
    sh = spec["shape"]
    if sh == "watermelon":
        for i in range(-3, 4):
            x = i * 0.09
            d.line([ctx.P(x * 0.8, 0.27), ctx.P(x, 0.53), ctx.P(x * 0.8, 0.8)], fill=shade(col, -0.3), width=int(ctx.L(0.025)), joint="curve")
    elif sh == "pineapple":
        for i in range(-3, 4):
            d.line([ctx.P(i * 0.08 - 0.15, 0.25), ctx.P(i * 0.08 + 0.15, 0.8)], fill=shade(col, -0.25), width=int(ctx.L(0.012)))
            d.line([ctx.P(i * 0.08 + 0.15, 0.25), ctx.P(i * 0.08 - 0.15, 0.8)], fill=shade(col, -0.25), width=int(ctx.L(0.012)))


def _draw_details(d, ctx, spec, col, style):
    sh = spec["shape"]
    green = (76, 175, 80)
    brown = (121, 85, 72)
    if sh == "apple":
        d.line([ctx.P(0, 0.72), ctx.P(0.03, 0.86)], fill=brown, width=int(ctx.L(0.03)))
        d.ellipse(ctx.E(0.1, 0.84, 0.08, 0.04), fill=green)
    elif sh == "orange":
        r = __import__("random").Random(3)
        for _ in range(14):
            a, rr = r.uniform(0, 6.28), r.uniform(0.1, 0.28)
            x, y = math.cos(a) * rr, 0.53 + math.sin(a) * rr
            if abs(x) < 0.2 and 0.4 < y < 0.7:
                continue
            d.ellipse(ctx.E(x, y, 0.008, 0.008), fill=shade(col, -0.15))
        d.ellipse(ctx.E(0.06, 0.86, 0.07, 0.035), fill=green)
    elif sh == "cherry":
        d.line([ctx.P(0, 0.76), ctx.P(0.08, 1.0)], fill=(85, 139, 47), width=int(ctx.L(0.025)))
        d.ellipse(ctx.E(0.15, 0.98, 0.08, 0.035), fill=green)
    elif sh == "strawberry":
        r = __import__("random").Random(5)
        for _ in range(16):
            x, y = r.uniform(-0.24, 0.24), r.uniform(0.32, 0.72)
            if abs(x) < 0.2 and 0.42 < y < 0.68:
                continue
            d.ellipse(ctx.E(x, y, 0.012, 0.018), fill=(255, 235, 130))
        for a in range(-60, 61, 30):
            ra = math.radians(a)
            d.polygon([ctx.P(-0.06, 0.8), ctx.P(math.sin(ra) * 0.22, 0.8 + math.cos(ra) * 0.1), ctx.P(0.06, 0.8)], fill=green)
    elif sh == "pineapple":
        for a in (-40, -20, 0, 20, 40):
            ra = math.radians(a)
            d.polygon([ctx.P(-0.05, 0.82), ctx.P(math.sin(ra) * 0.2, 0.82 + math.cos(ra) * 0.24), ctx.P(0.05, 0.82)], fill=(56, 142, 60))
    elif sh in ("pear", "avocado", "lemon"):
        if sh == "avocado":
            d.ellipse(ctx.E(0, 0.38, 0.12, 0.12), fill=(141, 98, 66))
        top = 0.93 if sh != "lemon" else 0.8
        if sh != "lemon":
            d.line([ctx.P(0, top - 0.02), ctx.P(0.02, top + 0.06)], fill=brown, width=int(ctx.L(0.025)))
        else:
            d.ellipse(ctx.E(0.05, 0.82, 0.07, 0.03), fill=green)
    elif sh == "grape":
        d.line([ctx.P(0, 0.92), ctx.P(0.03, 1.02)], fill=brown, width=int(ctx.L(0.03)))
        d.ellipse(ctx.E(0.12, 1.0, 0.1, 0.04), fill=green)
    elif sh == "robot":
        d.rounded_rectangle(ctx.E(0, 0.56, 0.24, 0.17), radius=ctx.L(0.05), fill=(38, 50, 56))
        for s in (-1, 1):
            d.ellipse(ctx.E(0.33 * s, 0.52, 0.03, 0.06), fill=shade(hex2rgb(spec["color"]), -0.3))
    elif sh == "penguin":
        d.ellipse(ctx.E(0, 0.48, 0.22, 0.22), fill=(250, 250, 250))
        d.polygon([ctx.P(-0.05, 0.5), ctx.P(0.05, 0.5), ctx.P(0, 0.44)], fill=(255, 167, 38))
    elif sh in ("cat", "dog", "bear", "fox", "panda", "frog", "bunny"):
        belly = (255, 255, 255) if sh in ("fox", "cat") else shade(col, 0.35)
        d.ellipse(ctx.E(0, 0.36, 0.17, 0.1), fill=belly)
        if sh == "panda":
            for s in (-1, 1):
                d.ellipse(ctx.E(0.11 * s, 0.6, 0.085, 0.1), fill=(40, 40, 40))
        if sh in ("cat", "dog", "bear", "fox", "panda", "bunny"):
            d.ellipse(ctx.E(0, 0.5, 0.035, 0.025), fill=(60, 40, 40))
        if sh == "cat":
            for s in (-1, 1):
                for k in (-1, 1):
                    d.line([ctx.P(0.12 * s, 0.48 + k * 0.01), ctx.P(0.3 * s, 0.5 + k * 0.04)], fill=(60, 40, 40), width=int(ctx.L(0.008)))
    elif sh == "monster":
        for s in (-1, 1):
            d.polygon([ctx.P(0.12 * s, 0.8), ctx.P(0.22 * s, 1.0), ctx.P(0.26 * s, 0.76)], fill=(255, 241, 118))


def _draw_human(d, ctx, spec, col, style):
    skin = hex2rgb(spec.get("skin", "#f1c27d"))
    hair = hex2rgb(spec.get("hair_color", "#4e342e"))
    if spec.get("hair") == "long":
        d.rounded_rectangle(ctx.E(0, 0.8, 0.19, 0.16), radius=ctx.L(0.08), fill=hair)
    d.rounded_rectangle(ctx.E(0, 0.53, 0.15, 0.16), radius=ctx.L(0.06), fill=col)
    d.ellipse(ctx.E(0, 0.84, 0.17, 0.17), fill=skin)
    d.chord(ctx.E(0, 0.86, 0.18, 0.17), 180, 360, fill=hair)
    d.ellipse(ctx.E(-0.06, 0.95, 0.09, 0.06), fill=hair)


def _draw_face(d, ctx, spec, pose, style, H):
    lay = _layout(spec)
    fx, fy = lay["face"]
    fs = lay["fs"]
    cx, cy = ctx.P(fx, fy)
    u = ctx.L(fs)
    em = pose.emotion
    eye_type = spec.get("eyes", "round")
    if style == "anime":
        eye_type = "anime"
    elif style == "minimalist":
        eye_type = "dot"
    ink = (33, 25, 30)
    white = (255, 255, 255)
    iris = hex2rgb(spec.get("eye_color", "#3e2723" if eye_type != "anime" else "#1e88e5"))
    ex = 0.38 * u
    ey = cy - 0.06 * u
    big = 1.18 if em in ("surprised", "scared") else 1.0
    if style == "cute":
        big *= 1.12
    pupil_s = 0.6 if em in ("surprised", "scared") else 1.0
    lx, ly = pose.look[0] * 0.07 * u, pose.look[1] * 0.05 * u
    blink = max(pose.blink, 0.55 if em == "sleepy" else 0.0)

    for side in (-1, 1):
        x = cx + side * ex
        if eye_type == "dot":
            r = 0.085 * u * big
            if blink > 0.85 or em == "joy":
                d.arc([x - r * 1.4, ey - r, x + r * 1.4, ey + r * 1.6], 200, 340, fill=ink, width=max(2, int(0.05 * u)))
            else:
                d.ellipse([x - r + lx, ey - r * (1 - blink) + ly, x + r + lx, ey + r * (1 - blink) + ly], fill=ink)
            continue
        rx = (0.2 if eye_type == "round" else 0.23) * u * big
        ry = (0.25 if eye_type == "round" else 0.33) * u * big
        if em == "joy" or (em == "excited" and eye_type == "dot"):
            d.arc([x - rx, ey - ry * 0.6, x + rx, ey + ry * 0.9], 200, 340, fill=ink, width=max(2, int(0.07 * u)))
            continue
        if blink > 0.85:
            d.line([(x - rx, ey), (x + rx, ey)], fill=ink, width=max(2, int(0.06 * u)))
            continue
        top = ey - ry + 2 * ry * blink
        d.ellipse([x - rx, ey - ry, x + rx, ey + ry], fill=white, outline=ink, width=max(1, int(0.035 * u)))
        pr = rx * (0.62 if eye_type == "round" else 0.78) * pupil_s
        px, py = x + lx, ey + ly + ry * 0.12
        if em == "love":
            hp = []
            for i in range(30):
                tt = i / 30 * 2 * math.pi
                hx = 16 * math.sin(tt) ** 3
                hy = -(13 * math.cos(tt) - 5 * math.cos(2 * tt) - 2 * math.cos(3 * tt) - math.cos(4 * tt))
                hp.append((px + hx * pr / 16, py + hy * pr / 16))
            d.polygon(hp, fill=(229, 57, 53))
        elif em == "excited":
            d.polygon(_star_points(px, py, pr * 1.1, pr * 0.5), fill=(255, 193, 7))
        elif eye_type == "anime":
            d.ellipse([px - pr, py - pr * 1.25, px + pr, py + pr * 1.25], fill=iris)
            d.ellipse([px - pr * 0.75, py - pr * 0.3, px + pr * 0.75, py + pr * 1.2], fill=shade(iris, 0.3))
            d.ellipse([px - pr * 0.45, py - pr * 0.55, px + pr * 0.45, py + pr * 0.55], fill=ink)
            d.ellipse([px - pr * 0.75, py - pr * 1.0, px - pr * 0.05, py - pr * 0.3], fill=white)
            d.ellipse([px + pr * 0.25, py + pr * 0.45, px + pr * 0.6, py + pr * 0.8], fill=white)
        else:
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=ink)
            d.ellipse([px - pr * 0.55, py - pr * 0.65, px - pr * 0.05, py - pr * 0.15], fill=white)
        if blink > 0.02:
            lid = shade(hex2rgb(spec["color"] if spec["kind"] != "human" else spec.get("skin", "#f1c27d")), -0.1)
            d.rectangle([x - rx * 1.05, ey - ry * 1.08, x + rx * 1.05, top], fill=lid)
            d.line([(x - rx, top), (x + rx, top)], fill=ink, width=max(2, int(0.04 * u)))
        # párpado de enfado (triángulo sobre la parte interior del ojo)
        if em == "angry":
            lid = hex2rgb(spec["color"] if spec["kind"] != "human" else spec.get("skin", "#f1c27d"))
            inner = x - side * rx * 1.1
            outer = x + side * rx * 1.1
            d.polygon([(inner, ey - ry * 1.15), (outer, ey - ry * 1.15), (inner, ey - ry * 0.05)], fill=lid)

    # cejas
    brow = {"happy": (6, -0.02), "joy": (6, -0.06), "sad": (-22, -0.0), "angry": (24, 0.06), "surprised": (0, -0.12),
            "scared": (-18, -0.1), "confused": (12, 0.0), "love": (5, -0.04), "excited": (4, -0.08)}.get(em, (0, 0))
    if eye_type != "dot" or em in ("angry", "sad", "confused"):
        for side in (-1, 1):
            ang = brow[0] * (-1 if (em == "confused" and side == 1) else 1)
            x = cx + side * ex
            y = ey - 0.36 * u * big + brow[1] * u
            w = 0.18 * u
            dy = w * math.sin(math.radians(ang))
            inner = (x - side * w, y + dy)
            outer = (x + side * w, y - dy)
            d.line([inner, outer], fill=ink, width=max(2, int(0.055 * u)))

    # boca
    mx, my = cx, cy + 0.42 * u
    mw = 0.3 * u
    vis = pose.viseme
    mouth_dark = (90, 20, 35)
    tongue = (240, 98, 146)
    lw = max(2, int(0.05 * u))
    if vis in ("X", "M"):
        if em in ("happy", "joy", "love", "excited"):
            d.chord([mx - mw, my - mw * 0.75, mx + mw, my + mw * 0.75], 0, 180, fill=mouth_dark, outline=ink, width=lw) if em in ("joy", "excited") else \
                d.arc([mx - mw, my - mw * 0.7, mx + mw, my + mw * 0.6], 20, 160, fill=ink, width=lw)
            if em in ("joy", "excited"):
                d.chord([mx - mw * 0.5, my + mw * 0.2, mx + mw * 0.5, my + mw * 0.75], 0, 180, fill=tongue)
        elif em == "sad":
            d.arc([mx - mw * 0.8, my, mx + mw * 0.8, my + mw * 1.0], 200, 340, fill=ink, width=lw)
        elif em == "angry":
            d.rounded_rectangle([mx - mw * 0.7, my - mw * 0.12, mx + mw * 0.7, my + mw * 0.22], radius=mw * 0.1, fill=white, outline=ink, width=lw)
            d.line([(mx - mw * 0.7, my + mw * 0.05), (mx + mw * 0.7, my + mw * 0.05)], fill=ink, width=max(1, lw // 2))
        elif em in ("surprised",):
            d.ellipse([mx - mw * 0.25, my - mw * 0.2, mx + mw * 0.25, my + mw * 0.35], fill=mouth_dark, outline=ink, width=lw)
        elif em == "scared":
            pts = [(mx - mw * 0.7 + i * mw * 0.2, my + (mw * 0.08 if i % 2 else -mw * 0.08)) for i in range(8)]
            d.line(pts, fill=ink, width=lw, joint="curve")
        elif em == "confused":
            d.line([(mx - mw * 0.5, my + mw * 0.1), (mx + mw * 0.5, my - mw * 0.1)], fill=ink, width=lw)
        elif em == "sleepy":
            d.ellipse([mx - mw * 0.15, my - mw * 0.1, mx + mw * 0.15, my + mw * 0.15], fill=mouth_dark)
        else:
            d.arc([mx - mw * 0.6, my - mw * 0.4, mx + mw * 0.6, my + mw * 0.35], 30, 150, fill=ink, width=lw)
    else:
        shapes = {"A": (0.55, 0.55), "E": (0.65, 0.3), "O": (0.32, 0.45), "U": (0.22, 0.3), "F": (0.5, 0.18)}
        sw, sh_ = shapes.get(vis, (0.4, 0.3))
        bb = [mx - mw * sw, my - mw * sh_ * 0.5, mx + mw * sw, my + mw * sh_ * 1.2]
        d.ellipse(bb, fill=mouth_dark, outline=ink, width=lw)
        if vis in ("A", "E"):
            d.chord([bb[0] + mw * 0.1, (bb[1] + bb[3]) / 2, bb[2] - mw * 0.1, bb[3]], 0, 180, fill=tongue)
        if vis in ("F", "E"):
            d.rectangle([mx - mw * sw * 0.6, bb[1] + lw * 0.5, mx + mw * sw * 0.6, bb[1] + mw * 0.12], fill=white)

    # extras emocionales
    if em in ("love", "happy", "joy") or style == "cute" or "blush" in pose.extras:
        for side in (-1, 1):
            x = cx + side * ex * 1.25
            d.ellipse([x - 0.14 * u, my - 0.2 * u, x + 0.14 * u, my - 0.06 * u], fill=(255, 120, 150, 120))
    if em == "sad" or "tear" in pose.extras:
        x = cx + ex + 0.05 * u
        d.polygon([(x, ey + 0.2 * u), (x - 0.07 * u, ey + 0.38 * u), (x + 0.07 * u, ey + 0.38 * u)], fill=(100, 181, 246))
        d.ellipse([x - 0.07 * u, ey + 0.32 * u, x + 0.07 * u, ey + 0.46 * u], fill=(100, 181, 246))
    if em in ("scared", "confused") or "sweat" in pose.extras:
        x, y = cx + ex * 1.6, ey - 0.4 * u
        d.polygon([(x, y), (x - 0.06 * u, y + 0.14 * u), (x + 0.06 * u, y + 0.14 * u)], fill=(144, 202, 249))
        d.ellipse([x - 0.06 * u, y + 0.08 * u, x + 0.06 * u, y + 0.2 * u], fill=(144, 202, 249))
    if em == "angry":
        x, y = cx + ex * 1.4, ey - 0.55 * u
        for a in (45, 135, 225, 315):
            ra = math.radians(a)
            d.arc([x + math.cos(ra) * 0.1 * u - 0.08 * u, y + math.sin(ra) * 0.1 * u - 0.08 * u,
                   x + math.cos(ra) * 0.1 * u + 0.08 * u, y + math.sin(ra) * 0.1 * u + 0.08 * u],
                  a + 90, a + 270, fill=(229, 57, 53), width=max(2, int(0.04 * u)))


def _draw_accessory(d, ctx, spec):
    acc = spec.get("accessory", "none")
    if acc in (None, "none"):
        return
    lay = _layout(spec)
    fx, fy = lay["face"]
    fs = lay["fs"]
    top = fy + fs * 1.0
    ink = (33, 25, 30)
    if acc == "hat":
        d.rectangle(ctx.E(0, top, 0.22, 0.02), fill=ink)
        d.rectangle(ctx.E(0, top + 0.12, 0.13, 0.12), fill=ink)
        d.rectangle(ctx.E(0, top + 0.04, 0.13, 0.025), fill=(198, 40, 40))
    elif acc == "cap":
        d.chord(ctx.E(0, top - 0.02, 0.2, 0.12), 180, 360, fill=(30, 136, 229))
        d.ellipse(ctx.E(0.16, top - 0.03, 0.14, 0.03), fill=(21, 101, 192))
    elif acc == "bow":
        x, y = ctx.P(0.12, top - 0.02)
        r = ctx.L(0.07)
        d.polygon([(x, y), (x - r * 1.4, y - r), (x - r * 1.4, y + r)], fill=(236, 64, 122))
        d.polygon([(x, y), (x + r * 1.4, y - r), (x + r * 1.4, y + r)], fill=(236, 64, 122))
        d.ellipse([x - r * 0.4, y - r * 0.4, x + r * 0.4, y + r * 0.4], fill=(216, 27, 96))
    elif acc == "crown":
        x, y = ctx.P(0, top + 0.02)
        w, h = ctx.L(0.14), ctx.L(0.12)
        d.polygon([(x - w, y), (x - w, y - h), (x - w / 2, y - h * 0.5), (x, y - h * 1.2), (x + w / 2, y - h * 0.5),
                   (x + w, y - h), (x + w, y)], fill=(255, 202, 40), outline=(245, 127, 23))
    elif acc == "wizard":
        x, y = ctx.P(0, top - 0.03)
        w, h = ctx.L(0.2), ctx.L(0.42)
        d.polygon([(x - w, y), (x + w, y), (x + w * 0.2, y - h)], fill=(69, 39, 160))
        d.ellipse([x - w * 1.25, y - ctx.L(0.03), x + w * 1.25, y + ctx.L(0.03)], fill=(49, 27, 146))
        d.polygon(_star_points(x, y - h * 0.45, ctx.L(0.045), ctx.L(0.02)), fill=(255, 235, 59))
    elif acc == "glasses":
        cx, cy = ctx.P(fx, fy)
        u = ctx.L(fs)
        for s in (-1, 1):
            x = cx + s * 0.38 * u
            d.ellipse([x - 0.27 * u, cy - 0.33 * u, x + 0.27 * u, cy + 0.21 * u], outline=ink, width=max(2, int(0.06 * u)))
        d.line([(cx - 0.12 * u, cy - 0.08 * u), (cx + 0.12 * u, cy - 0.08 * u)], fill=ink, width=max(2, int(0.05 * u)))
    elif acc == "scarf":
        d.rounded_rectangle(ctx.E(0, fy - fs * 0.85, 0.24, 0.035), radius=ctx.L(0.03), fill=(211, 47, 47))
        d.rectangle(ctx.E(0.12, fy - fs * 0.85 - 0.1, 0.035, 0.09), fill=(211, 47, 47))


STYLE_DEFAULTS = {
    "cartoon": dict(outline=0.022, cel=True, highlight=True),
    "anime": dict(outline=0.012, cel=True, highlight=True),
    "minimalist": dict(outline=0.0, cel=False, highlight=False),
    "cute": dict(outline=0.016, cel=True, highlight=True),
    "pixel": dict(outline=0.03, cel=True, highlight=False),
    "horror": dict(outline=0.02, cel=True, highlight=False),
    "cinematic": dict(outline=0.01, cel=True, highlight=True),
    "realistic": dict(outline=0.0, cel=True, highlight=True),
    "paper": dict(outline=0.0, cel=False, highlight=False),
    "clay": dict(outline=0.0, cel=True, highlight=True),
    "fantasy": dict(outline=0.016, cel=True, highlight=True),
    "comic": dict(outline=0.03, cel=True, highlight=False),
}


def render_character(spec: dict, pose: Pose, height_px: int, style: str = "cartoon"):
    """Devuelve (imagen RGBA, (ancla_x, ancla_y)) con el ancla en los pies."""
    H = int(height_px * SS * spec.get("height", 1.0))
    W, Hh = int(H * 1.6), int(H * 1.75)
    ox, oy = W / 2, Hh - H * 0.08
    img = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    ctx = _Ctx(H, pose, ox, oy)
    col = hex2rgb(spec["color"])
    sd = STYLE_DEFAULTS.get(style, STYLE_DEFAULTS["cartoon"])
    ink = (30, 22, 28)
    outline_on = sd["outline"] > 0
    lay = _layout(spec)
    human = spec["kind"] == "human"
    if human:
        limb_col = hex2rgb(spec.get("skin", "#f1c27d"))
        leg_col = (55, 71, 79)
        glove = None
        shoe = (66, 66, 66)
    elif spec["kind"] in ("animal",):
        limb_col = shade(col, -0.1)
        leg_col = limb_col
        glove = None
        shoe = shade(col, -0.2)
    elif spec["kind"] == "robot":
        limb_col = shade(col, -0.25)
        leg_col = limb_col
        glove = (220, 220, 220)
        shoe = (69, 90, 100)
    else:  # frutas y mascotas: brazos de "manguera" con guantes blancos
        limb_col = ink
        leg_col = ink
        glove = (255, 255, 255)
        shoe = (120, 72, 50) if style != "cute" else (244, 143, 177)
    limb_out = ink if outline_on and limb_col != ink else None
    sxr, syr = lay["shoulder"]
    hx, hy = lay["hip"]
    w = lay["limbw"] if not human else 0.05

    # extremidades traseras
    if lay["leg"][0] > 0:
        _limb(d, ctx, (-hx, hy), pose.leg_back, lay["leg"], shade(leg_col, -0.12) if leg_col != ink else ink,
              limb_out, w * 1.15, foot=(0.075, 0.035, shade(shoe, -0.15)))
    _limb(d, ctx, (-sxr * 0.85, syr), (-pose.arm_back[0], -pose.arm_back[1]), lay["arm"], shade(limb_col, -0.12) if limb_col != ink else ink,
          limb_out, w, hand=lay["hand"], glove=shade(glove, -0.1) if glove else None)
    if lay["leg"][0] > 0:
        _limb(d, ctx, (hx, hy), pose.leg_front, lay["leg"], leg_col, limb_out, w * 1.15, foot=(0.075, 0.035, shoe))

    if "hands_front" not in pose.extras:
        _limb(d, ctx, (sxr * 0.85, syr), pose.arm_front, lay["arm"], limb_col, limb_out, w, hand=lay["hand"], glove=glove)

    # cuerpo en capa propia para sombreado
    body = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body, "RGBA")
    if human:
        _draw_human(bd, ctx, spec, col, style)
    else:
        _draw_body(bd, ctx, spec, col, style)
        pat = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
        _draw_pattern(ImageDraw.Draw(pat, "RGBA"), ctx, spec, col)
        pat.putalpha(ImageChops.multiply(pat.getchannel("A"), body.getchannel("A")))
        body = Image.alpha_composite(body, pat)
    if sd["cel"]:
        a = body.getchannel("A")
        shifted = ImageChops.offset(a, int(-H * 0.06), int(-H * 0.05))
        crescent = ImageChops.subtract(a, shifted)
        if style in ("realistic", "clay", "cinematic"):
            crescent = crescent.filter(ImageFilter.GaussianBlur(H * 0.04))
            crescent = ImageChops.multiply(crescent, a)
        shade_layer = Image.new("RGBA", (W, Hh), (*shade(col, -0.28), 0))
        shade_layer.putalpha(crescent.point(lambda v: int(v * 0.55)))
        body = Image.alpha_composite(body, shade_layer)
    if sd["highlight"] and not human:
        hl = Image.new("RGBA", (W, Hh), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hl)
        hd.ellipse(ctx.E(-0.17, 0.7, 0.07, 0.045), fill=(255, 255, 255, 150))
        hl.putalpha(ImageChops.multiply(hl.getchannel("A"), body.getchannel("A")))
        body = Image.alpha_composite(body, hl)
    img = Image.alpha_composite(img, body)
    d = ImageDraw.Draw(img, "RGBA")
    _draw_details(d, ctx, spec, col, style)
    _draw_face(d, ctx, spec, pose, style, H)
    _draw_accessory(d, ctx, spec)
    if "hands_front" in pose.extras:
        _limb(d, ctx, (sxr * 0.85, syr), pose.arm_front, lay["arm"], limb_col, limb_out, w, hand=lay["hand"], glove=glove)

    if outline_on:
        a = img.getchannel("A")
        r = max(1, H * sd["outline"])
        grown = a.filter(ImageFilter.MaxFilter(3)) if r < 2 else a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: 255 if v > 18 else 0)
        base = Image.new("RGBA", (W, Hh), (*ink, 0))
        base.putalpha(grown)
        img = Image.alpha_composite(base, img)

    if pose.facing < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if abs(pose.tilt) > 0.1:
        img = img.rotate(pose.tilt * -pose.facing, resample=Image.BICUBIC, center=(ox, oy))
    out = img.resize((W // SS, Hh // SS), Image.LANCZOS)
    return out, (ox / SS, oy / SS)


def character_sheet(spec: dict, style: str = "cartoon", path=None):
    """Hoja de personaje: poses, expresiones y visemas (referencia de consistencia)."""
    from .motion import pose_for
    cell = 230
    emotions = ["neutral", "happy", "joy", "sad", "angry", "surprised", "scared", "love", "sleepy", "excited"]
    visemes = ["X", "A", "E", "O", "U", "F"]
    actions = ["idle", "walk", "run", "jump", "dance", "wave", "punch", "celebrate"]
    cols = 8
    rows = 4
    W, H = cols * cell, rows * cell + 90
    sheet = Image.new("RGB", (W, H), (250, 248, 244))
    d = ImageDraw.Draw(sheet)
    d.text((20, 18), f"{spec['name']} — hoja de personaje ({style})", fill=(40, 40, 40), font=font(34))
    d.text((20, 58), f"especie: {spec['species']} · color: {spec['color']} · accesorio: {spec.get('accessory')}",
           fill=(100, 100, 100), font=font(18, False))
    items = []
    for a in actions:
        items.append((a, pose_for(a, 0.35, emotion="happy")))
    for e in emotions[:8]:
        items.append((e, pose_for("idle", 0.0, emotion=e)))
    for e in emotions[8:]:
        items.append((e, pose_for("idle", 0.0, emotion=e)))
    for v in visemes:
        p = pose_for("idle", 0.0, emotion="neutral")
        p.viseme = v
        items.append((f"visema {v}", p))
    for i, (label, pose) in enumerate(items[: cols * rows]):
        cx, cy = (i % cols) * cell, 90 + (i // cols) * cell
        im, (ax, ay) = render_character(spec, pose, int(cell * 0.72), style)
        sheet.paste(im, (int(cx + cell / 2 - ax), int(cy + cell - 30 - ay)), im)
        d.text((cx + 8, cy + cell - 26), label, fill=(80, 80, 80), font=font(16, False))
    if path:
        sheet.save(path)
    return sheet
