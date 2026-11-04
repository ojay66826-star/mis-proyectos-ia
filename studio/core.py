"""Utilidades compartidas del motor: easing, color, fuentes, rutas."""
from __future__ import annotations

import math
import os
import random
import shutil
from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

ROOT = Path(__file__).resolve().parent.parent
STUDIO_DIR = Path(__file__).resolve().parent
ASSETS = STUDIO_DIR / "assets"
PROJECTS_DIR = Path(os.environ.get("STUDIO_PROJECTS_DIR", ROOT / "projects"))

FORMATS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (960, 960),
    "4:5": (864, 1080),
}
FORMATS_FULLHD = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:5": (1080, 1350),
}


def canvas_size(fmt: str, quality: str = "hd") -> tuple[int, int]:
    table = FORMATS_FULLHD if quality == "fullhd" else FORMATS
    w, h = table.get(fmt, table["16:9"])
    if quality == "preview":
        w, h = w // 2, h // 2
    return (w - w % 2, h - h % 2)


# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out_back(t, s=1.70158):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def ease_out_elastic(t):
    t = clamp(t)
    if t in (0, 1):
        return t
    return 2 ** (-10 * t) * math.sin((t - 0.075) * (2 * math.pi) / 0.3) + 1


def ease_out_bounce(t):
    t = clamp(t)
    n, d = 7.5625, 2.75
    if t < 1 / d:
        return n * t * t
    if t < 2 / d:
        t -= 1.5 / d
        return n * t * t + 0.75
    if t < 2.5 / d:
        t -= 2.25 / d
        return n * t * t + 0.9375
    t -= 2.625 / d
    return n * t * t + 0.984375


EASINGS = {
    "linear": lambda t: clamp(t),
    "in_out": ease_in_out,
    "out_back": ease_out_back,
    "elastic": ease_out_elastic,
    "bounce": ease_out_bounce,
}


# ---------------------------------------------------------------- color
def hex2rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c) -> str:
    return "#%02x%02x%02x" % tuple(int(clamp(v, 0, 255)) for v in c[:3])


def mix(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1[:3], c2[:3]))


def shade(c, f):
    """f<0 oscurece, f>0 aclara."""
    c = c[:3]
    return mix(c, (0, 0, 0), -f) if f < 0 else mix(c, (255, 255, 255), f)


def rgba(c, a=255):
    return (int(c[0]), int(c[1]), int(c[2]), int(a))


# ---------------------------------------------------------------- fonts
@lru_cache(maxsize=64)
def font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = ASSETS / "fonts" / name
    try:
        return ImageFont.truetype(str(path), max(6, int(size)))
    except OSError:
        return ImageFont.load_default()


def rng(seed) -> random.Random:
    return random.Random(str(seed))


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def slugify(text: str, maxlen: int = 40) -> str:
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return (t[:maxlen].strip("-")) or "proyecto"
