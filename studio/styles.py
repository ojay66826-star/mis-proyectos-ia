"""Estilos de animación: preajustes + post-procesado por frame."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

STYLES = {
    "cartoon": dict(label="Caricatura", desc="Contornos gruesos, colores vivos, brazos de goma", fps=24, hold=1),
    "anime": dict(label="Anime", desc="Ojos grandes brillantes, cel-shading, líneas de velocidad", fps=24, hold=2),
    "pixel": dict(label="Pixel art", desc="Resolución baja, paleta limitada, estética retro 16-bit", fps=12, hold=1),
    "minimalist": dict(label="Minimalista", desc="Formas planas, sin contornos, paleta reducida", fps=24, hold=1),
    "cute": dict(label="Tierno (kawaii)", desc="Pastel, mejillas rosadas, ojos grandes", fps=24, hold=1),
    "cinematic": dict(label="Cinematográfico", desc="Bandas negras, gradación teal-orange, grano, viñeta", fps=24, hold=1),
    "horror": dict(label="Terror", desc="Desaturado, viñeta fuerte, parpadeo, grano", fps=24, hold=1),
    "fantasy": dict(label="Fantasía", desc="Brillos mágicos, tonos violeta-dorado, bloom", fps=24, hold=1),
    "paper": dict(label="Papel recortado", desc="Textura de papel, sombras proyectadas, movimiento a saltos", fps=12, hold=1),
    "clay": dict(label="Plastilina", desc="Textura de arcilla, stop-motion a 12 fps con temblor", fps=12, hold=1),
    "stopmotion": dict(label="Stop-motion", desc="A 12 fps (on twos) con micro-temblor entre poses", fps=12, hold=1),
    "realistic": dict(label="Realista (suave)", desc="Sombreado suave, profundidad de campo; foto-realismo real requiere IA externa", fps=24, hold=1),
    "comic": dict(label="Cómic animado", desc="Tramas de puntos, viñetas, contornos marcados", fps=12, hold=1),
    "retro": dict(label="Retro VHS", desc="Aberración cromática, líneas de escaneo", fps=24, hold=1),
}

CHAR_STYLE = {"stopmotion": "clay", "retro": "cartoon"}


def char_style(style: str) -> str:
    return CHAR_STYLE.get(style, style)


_tex_cache = {}


def _noise(size, seed, scale=1, blur=0):
    key = (size, seed, scale, blur)
    if key not in _tex_cache:
        import zlib
        r = np.random.default_rng(zlib.crc32(str(seed).encode()))
        w, h = size
        n = r.random((max(1, h // scale), max(1, w // scale))).astype(np.float32)
        im = Image.fromarray((n * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        if blur:
            im = im.filter(ImageFilter.GaussianBlur(blur))
        _tex_cache[key] = np.asarray(im).astype(np.float32) / 255.0
    return _tex_cache[key]


def _vignette(w, h, strength):
    key = ("vig", w, h, strength)
    if key not in _tex_cache:
        y, x = np.ogrid[-1:1:h * 1j, -1:1:w * 1j]
        r = np.sqrt(x * x * 0.8 + y * y)
        _tex_cache[key] = np.clip(1 - strength * np.clip(r - 0.45, 0, None) ** 1.5, 0, 1)[..., None]
    return _tex_cache[key]


def post_process(img: Image.Image, style: str, t: float, frame: int, letterbox: bool = None) -> Image.Image:
    w, h = img.size
    if style in ("cartoon", "minimalist", "cute") and not letterbox:
        if style == "cute":
            a = np.asarray(img).astype(np.float32)
            a = a * 0.88 + 255 * 0.12
            return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        return img
    if style == "pixel":
        f = max(3, w // 240)
        small = img.resize((w // f, h // f), Image.BILINEAR).quantize(colors=40, method=Image.Quantize.MEDIANCUT).convert("RGB")
        return small.resize((w, h), Image.NEAREST)
    a = np.asarray(img).astype(np.float32) / 255.0
    if style == "anime":
        lum = a.mean(axis=2, keepdims=True)
        a = np.clip(lum + (a - lum) * 1.15, 0, 1)
        bright = Image.fromarray((np.clip(a - 0.7, 0, 1) / 0.3 * 255).astype(np.uint8))
        bloom = np.asarray(bright.resize((w // 4, h // 4)).filter(ImageFilter.GaussianBlur(4)).resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
        a = 1 - (1 - a) * (1 - bloom * 0.25)
    elif style == "cinematic":
        lum = a.mean(axis=2, keepdims=True)
        shadows = np.clip(1 - lum * 2, 0, 1)
        highs = np.clip(lum * 2 - 1, 0, 1)
        a = a + shadows * np.array([-0.04, 0.02, 0.06]) + highs * np.array([0.06, 0.02, -0.05])
        a = np.clip((a - 0.5) * 1.1 + 0.5, 0, 1)
        a *= _vignette(w, h, 0.9)
        a += (_noise((w, h), f"g{frame % 8}") - 0.5)[..., None] * 0.04
        letterbox = True if letterbox is None else letterbox
    elif style == "horror":
        lum = a.mean(axis=2, keepdims=True)
        a = lum + (a - lum) * 0.35
        a = a * np.array([1.0, 0.85, 0.85]) + np.array([0.03, -0.02, -0.01])
        flick = 0.85 + 0.15 * (np.sin(t * 37) * np.sin(t * 13) > 0.6)
        a *= _vignette(w, h, 1.6) * flick
        a += (_noise((w, h), f"g{frame % 6}") - 0.5)[..., None] * 0.09
    elif style == "fantasy":
        a = a * np.array([1.02, 0.96, 1.08]) + np.array([0.02, 0.0, 0.04])
        bright = Image.fromarray((np.clip(a - 0.65, 0, 1) / 0.35 * 255).astype(np.uint8))
        bloom = np.asarray(bright.resize((w // 4, h // 4)).filter(ImageFilter.GaussianBlur(5)).resize((w, h), Image.BILINEAR)).astype(np.float32) / 255
        a = 1 - (1 - a) * (1 - bloom * 0.4)
        a *= _vignette(w, h, 0.5)
    elif style == "paper":
        tex = _noise((w, h), "paper", 2, 1)
        fib = _noise((w, h), "fibers", 1, 0)
        a = a * (0.9 + 0.1 * tex[..., None]) * (0.97 + 0.03 * fib[..., None])
        a = a * 0.95 + np.array([0.04, 0.035, 0.02])
    elif style in ("clay", "stopmotion"):
        tex = _noise((w, h), "clay", 3, 1.5)
        a = a * (0.9 + 0.12 * tex[..., None])
        a *= _vignette(w, h, 0.4)
    elif style == "realistic":
        a = np.clip((a - 0.5) * 1.05 + 0.5, 0, 1)
        a *= _vignette(w, h, 0.5)
        a += (_noise((w, h), f"g{frame % 8}") - 0.5)[..., None] * 0.02
    elif style == "comic":
        lum = a.mean(axis=2)
        cell = max(4, w // 200)
        yy, xx = np.mgrid[0:h, 0:w]
        cx, cy = (xx % cell) - cell / 2, (yy % cell) - cell / 2
        dot = np.sqrt(cx ** 2 + cy ** 2) / (cell * 0.7)
        mask = (dot < (1 - lum) * 0.9)[..., None]
        a = np.where(mask, a * 0.7, np.clip(a * 1.08, 0, 1))
    elif style == "retro":
        r = np.roll(a[..., 0], 3, axis=1)
        b = np.roll(a[..., 2], -3, axis=1)
        a = np.stack([r, a[..., 1], b], axis=2)
        a[::3] *= 0.85
        a += (_noise((w, h), f"g{frame % 5}") - 0.5)[..., None] * 0.06
    a = np.clip(a, 0, 1)
    out = Image.fromarray((a * 255).astype(np.uint8))
    if letterbox:
        d = ImageDraw.Draw(out)
        bar = int(h * 0.11) if w > h else int(h * 0.06)
        d.rectangle([0, 0, w, bar], fill=(0, 0, 0))
        d.rectangle([0, h - bar, w, h], fill=(0, 0, 0))
    return out


def stop_motion_jitter(style: str, frame: int, hold: int):
    """Desplazamiento (dx, dy, rot) para simular stop-motion."""
    if style not in ("clay", "stopmotion", "paper"):
        return 0, 0, 0
    r = np.random.default_rng(frame // max(1, hold) + 7)
    return float(r.uniform(-1.5, 1.5)), float(r.uniform(-1, 1)), float(r.uniform(-0.6, 0.6))
