"""Personajes y fondos ilustrados (por IA o a mano) animados por el motor.

Modo híbrido: una IA de imagen crea UNA vez el arte de alta calidad (fondo por
escena y personaje con variantes) y el motor lo anima de forma determinista:

* Personaje = juego de PNG transparentes con el mismo encuadre::

      "sprite": {"base": "miso.png",            # boca cerrada, ojos abiertos
                 "talk": "miso_boca.png",       # boca abierta (lip-sync)
                 "blink": "miso_ojos.png",      # ojos cerrados (parpadeo)
                 "expressions": {"sad": "miso_triste.png", "joy": "miso_feliz.png"},
                 "facing": 1}                   # hacia dónde mira el dibujo

  Se anima con deformación de malla (mesh warp): squash & stretch con volumen
  constante, respiración, flexión del cuerpo con follow-through según la
  velocidad, rebote al caminar, saltos con anticipación y aterrizaje, balanceo
  al ritmo en el baile, giro al cambiar de dirección y temblor de miedo. Las
  curvas salen de ``motion.pose_for``, así que todas las acciones del catálogo
  funcionan igual que con los personajes procedurales.

* Fondo = imagen por escena (``"background_image"``) con paneo/zoom de cámara,
  luz que respira y motas de luz flotando.
"""
from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from .core import clamp

OPEN_VISEMES = {"A", "E", "O", "U"}
BANDS = 28  # bandas horizontales de la malla de deformación


# ---------------------------------------------------------------- recorte de fondo
def cutout(src, out=None, tol=26, feather=1.2) -> Image.Image:
    """Quita un fondo liso (blanco o de color uniforme) por relleno desde los bordes.

    Pensado para personajes generados "sobre fondo blanco liso" con contorno: el
    relleno no atraviesa el contorno, así que los blancos interiores (ojos,
    barriga) se conservan.
    """
    im = Image.open(src).convert("RGBA")
    if im.getextrema()[3][0] < 250:  # ya trae transparencia
        res = im
    else:
        rgb = np.asarray(im.convert("RGB")).astype(np.int16)
        h, w, _ = rgb.shape
        border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
        bgc = np.median(border, axis=0)
        near = (np.abs(rgb - bgc).max(axis=2) <= tol).astype(np.uint8) * 255
        # relleno desde los bordes sobre la máscara de píxeles "parecidos al fondo"
        mask = Image.fromarray(near, "L")
        seed = Image.new("L", (w + 2, h + 2), 255)
        seed.paste(mask, (1, 1))
        for xy in ((0, 0),):
            ImageDraw.floodfill(seed, xy, 128, thresh=0)
        bg = (np.asarray(seed)[1:-1, 1:-1] == 128)
        alpha = np.where(bg, 0, 255).astype(np.uint8)
        a = Image.fromarray(alpha, "L").filter(ImageFilter.MinFilter(3))  # come el halo blanco
        if feather:
            a = a.filter(ImageFilter.GaussianBlur(feather))
        res = im.copy()
        res.putalpha(a)
    box = res.getbbox()
    if box:
        res = res.crop(box)
    if out:
        res.save(out)
    return res


# ---------------------------------------------------------------- juego de sprites
class SpriteSet:
    """Variantes de un personaje normalizadas a la misma altura y ancladas en los pies."""

    def __init__(self, cfg: dict, root: Path | None = None):
        def load(p):
            p = Path(p)
            if root and not p.is_absolute() and not p.exists():
                p = root / p
            im = Image.open(p).convert("RGBA")
            box = im.getbbox()
            return im.crop(box) if box else im

        self.base = load(cfg["base"])
        self.facing = cfg.get("facing", 1)
        H = self.base.height
        W = self.base.width
        self.variants = {"base": self.base}
        for key in ("talk", "blink", "talk_blink"):
            if cfg.get(key):
                self.variants[key] = self._match(load(cfg[key]), W, H)
        for em, p in (cfg.get("expressions") or {}).items():
            self.variants["em:" + em] = self._match(load(p), W, H)
        for em, p in (cfg.get("expressions_talk") or {}).items():
            self.variants["emtalk:" + em] = self._match(load(p), W, H)

    @staticmethod
    def _match(im, W, H):
        """Iguala altura y centra en un lienzo del mismo tamaño que la base (pies abajo)."""
        if im.height != H:
            im = im.resize((max(1, round(im.width * H / im.height)), H), Image.LANCZOS)
        canvas = Image.new("RGBA", (max(W, im.width), H), (0, 0, 0, 0))
        canvas.alpha_composite(im, ((canvas.width - im.width) // 2, 0))
        if canvas.width != W:
            canvas = canvas.crop(((canvas.width - W) // 2, 0, (canvas.width - W) // 2 + W, H))
        return canvas

    def pick(self, emotion: str, talking: bool, blink: bool) -> Image.Image:
        v = self.variants
        if talking and f"emtalk:{emotion}" in v:
            return v[f"emtalk:{emotion}"]
        if emotion != "neutral" and f"em:{emotion}" in v and not talking:
            return v[f"em:{emotion}"]
        if talking and blink and "talk_blink" in v:
            return v["talk_blink"]
        if talking and "talk" in v:
            return v["talk"]
        if blink and "blink" in v:
            return v["blink"]
        return v["base"]


@lru_cache(maxsize=32)
def _sprite_cached(key: str, root: str) -> SpriteSet:
    import json
    return SpriteSet(json.loads(key), Path(root) if root else None)


def sprite_set(cfg: dict, root=None) -> SpriteSet:
    import json
    return _sprite_cached(json.dumps(cfg, sort_keys=True), str(root or ""))


_SCALED: dict = {}


def _scaled(img_id: int, img: Image.Image, h: int) -> Image.Image:
    k = (img_id, h)
    if k not in _SCALED:
        if len(_SCALED) > 256:
            _SCALED.clear()
        _SCALED[k] = img.resize((max(1, round(img.width * h / img.height)), h), Image.LANCZOS)
    return _SCALED[k]


# ---------------------------------------------------------------- deformación
def warp(img: Image.Image, stretch=1.0, lean=0.0, bend=0.0, shift_x=0.0, flip=False) -> tuple[Image.Image, tuple]:
    """Deforma un sprite anclado en los pies.

    stretch: >1 estira en vertical (volumen constante: el ancho se divide por sqrt).
    lean:    desplazamiento horizontal de la cabeza en fracción de la altura (inclinación).
    bend:    curvatura extra (follow-through): la parte alta se retrasa más que la media.
    shift_x: desplazamiento horizontal ondulante (temblor) en fracción de la altura.
    Devuelve (imagen, (ancla_x, ancla_y)) con el ancla en los pies.
    """
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    w, h = img.size
    sx = 1 / math.sqrt(max(0.3, stretch))
    Ht = h * stretch
    off = lambda t: (lean * t + bend * t * t + shift_x * math.sin(t * math.pi * 3)) * h  # noqa: E731
    max_off = max(abs(off(t / 10)) for t in range(11))
    pad = int(max_off + w * abs(1 - sx) + 4)
    Wo, Ho = int(w * sx + 2 * pad + w * 0.1), int(math.ceil(Ht)) + 2
    cx = Wo / 2
    mesh = []
    for b in range(BANDS):
        # banda de salida [y0, y1] (y desde arriba)
        y0 = Ho - Ht * (b + 1) / BANDS
        y1 = Ho - Ht * b / BANDS
        t_top, t_bot = (b + 1) / BANDS, b / BANDS
        sy_top, sy_bot = h * (1 - t_top), h * (1 - t_bot)
        # x_salida = cx + (x_src - w/2) * sx + off(t)  ->  x_src = (x_salida - cx - off)/sx + w/2
        def src_x(xo, t):
            return (xo - cx - off(t)) / sx + w / 2
        box = (0, int(math.floor(y0)), Wo, int(math.ceil(y1)))
        quad = (src_x(0, t_top), sy_top, src_x(0, t_bot), sy_bot, src_x(Wo, t_bot), sy_bot, src_x(Wo, t_top), sy_top)
        mesh.append((box, quad))
    out = img.transform((Wo, Ho), Image.MESH, mesh, resample=Image.BICUBIC)
    return out, (cx, Ho - 1)


# ---------------------------------------------------------------- actor animado
def animate_sprite(sset: SpriteSet, pose, action: str, lt: float, height_px: int, velocity: float = 0.0,
                   accel: float = 0.0, tint=None) -> tuple[Image.Image, tuple]:
    """Convierte la pose procedural (curvas de motion.pose_for) en un sprite deformado."""
    talking = getattr(pose, "viseme", "X") in OPEN_VISEMES
    blink = getattr(pose, "blink", 0) > 0.5
    src = sset.pick(pose.emotion, talking, blink)
    base = _scaled(id(src), src, max(8, int(height_px)))

    # squash & stretch: pose.squash >1 = aplastado
    stretch = 1 / max(0.5, pose.squash)
    # respiración (más rápida si está asustado o emocionado)
    br = 2.4 if pose.emotion in ("scared", "excited", "angry") else 1.25
    stretch *= 1 + 0.012 * math.sin(lt * br * 2 * math.pi)
    # inclinación: tilt (grados) de la pose + inclinarse hacia donde se mueve
    lean = math.sin(math.radians(pose.tilt)) * 0.6 * (pose.facing or 1)
    lean += clamp(velocity * 0.35, -0.12, 0.12)
    # follow-through: al acelerar/frenar la cabeza se retrasa y luego rebota
    bend = clamp(-accel * 0.05, -0.08, 0.08)
    shake = 0.0
    if action == "scared_shake" or pose.emotion == "scared":
        shake = 0.006 * math.sin(lt * 55)
    if action == "dance":
        bend += 0.05 * math.sin(lt * 2 * math.pi * 0.9)
    if action == "talk":
        lean += 0.015 * math.sin(lt * 3.1)
    flip = (pose.facing or 1) != sset.facing
    img, (ax, ay) = warp(base, stretch, lean, bend, shake, flip)
    if tint is not None:
        img = _tint(img, tint)
    # elevación (saltos, rebote al caminar)
    ay += pose.body_dy * height_px * 0.6  # saltos más cortos: el sprite ocupa más cuadro que el procedural
    return img, (ax, ay)


def _tint(img: Image.Image, color, amount=0.18) -> Image.Image:
    """Integra el personaje con la luz del fondo (multiplica suavemente por el color ambiente)."""
    r, g, b = [c / 255 for c in color]
    m = max(r, g, b) or 1
    lut = []
    for c in (r / m, g / m, b / m):
        f = 1 - amount + amount * c
        lut += [int(clamp(i * f, 0, 255)) for i in range(256)]
    a = img.getchannel("A")
    out = img.convert("RGB").point(lut)
    out.putalpha(a)
    return out


def contact_shadow(width: int, lift: float, strength=90) -> Image.Image:
    k = clamp(1 - lift * 1.6, 0.3, 1)
    w, h = max(4, int(width * 0.75)), max(3, int(width * 0.13))
    sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([w * (1 - k) / 2, 0, w * (1 + k) / 2, h], fill=(20, 15, 25, int(strength * k)))
    return sh.filter(ImageFilter.GaussianBlur(h * 0.25))


# ---------------------------------------------------------------- fondo ilustrado
class ImageBackground:
    """Fondo a partir de una ilustración: cobertura con margen para paneo, luz viva y motas."""

    def __init__(self, path, W, H, seed=0, time_of_day="day", motes=True):
        self.W, self.H = W, H
        im = Image.open(path).convert("RGB")
        # cubre W*1.25 x H*1.06 para poder panear y "respirar" sin bordes
        k = max(W * 1.25 / im.width, H * 1.06 / im.height)
        self.img = im.resize((int(im.width * k + 0.5), int(im.height * k + 0.5)), Image.LANCZOS)
        self.ambient = tuple(int(c) for c in np.asarray(self.img.resize((8, 8))).reshape(-1, 3).mean(axis=0))
        r = np.random.default_rng(abs(hash((str(path), seed))) % 2**32)
        self.motes = [(r.uniform(0, 1), r.uniform(0.1, 0.9), r.uniform(0.6, 1.8), r.uniform(0.2, 1.0), r.uniform(0, 6.28))
                      for _ in range(26 if motes else 0)]
        self.night = time_of_day == "night"
        self.ground_y = 0.82

    def render(self, cam_x=0.0, t=0.0) -> Image.Image:
        W, H = self.W, self.H
        ex, ey = self.img.width - W, self.img.height - H
        # paneo de cámara + deriva lenta (el plano nunca está muerto)
        ox = ex / 2 + cam_x * ex / 2 + math.sin(t * 0.21) * ex * 0.04
        oy = ey / 2 + math.sin(t * 0.17 + 1) * ey * 0.25
        ox, oy = clamp(ox, 0, ex), clamp(oy, 0, ey)
        out = self.img.crop((int(ox), int(oy), int(ox) + W, int(oy) + H)).convert("RGBA")
        if self.motes:
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            col = (200, 220, 255) if self.night else (255, 244, 205)
            for (x, y, s, sp, ph) in self.motes:
                xx = ((x + t * 0.012 * sp + 0.02 * math.sin(t * 0.7 + ph) - cam_x * 0.05) % 1.1 - 0.05) * W
                yy = (y + 0.03 * math.sin(t * 0.5 * sp + ph)) * H
                a = int(90 * (0.5 + 0.5 * math.sin(t * 1.3 * sp + ph)))
                rr = s * H * 0.004
                d.ellipse([xx - rr * 1.8, yy - rr * 1.8, xx + rr * 1.8, yy + rr * 1.8], fill=(*col, a // 3))
                d.ellipse([xx - rr, yy - rr, xx + rr, yy + rr], fill=(*col, a))
            out.alpha_composite(lay)
        return out.convert("RGB")


# ---------------------------------------------------------------- cámara que sigue al que habla
def speaker_camera(s, lt, positions: dict, talking_id):
    """Encuadre automático: acerca suavemente la cámara a quien habla (plano/contraplano)."""
    if not talking_id or talking_id not in positions:
        return None
    x, y = positions[talking_id]
    return [clamp(x, 0.3, 0.7), clamp(y - 0.22, 0.35, 0.65)]


@lru_cache(maxsize=8)
def _light_layers(W, H, time_of_day):
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if time_of_day in ("day", "sunset"):
        col = (255, 214, 150) if time_of_day == "sunset" else (255, 240, 200)
        d = ImageDraw.Draw(rays)
        for i in range(3):
            x = W * (0.62 + 0.12 * i)
            d.polygon([(x, -H * 0.1), (x + W * 0.07, -H * 0.1), (x - W * 0.32, H * 1.1), (x - W * 0.42, H * 1.1)], fill=(*col, 40))
        rays = rays.filter(ImageFilter.GaussianBlur(W * 0.03))
    vg = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vg).ellipse([-W * 0.15, -H * 0.2, W * 1.15, H * 1.2], fill=255)
    vg = ImageChops.invert(vg.filter(ImageFilter.GaussianBlur(W * 0.08)))
    dark = Image.new("RGBA", (W, H), (10, 8, 20, 0))
    dark.putalpha(vg.point(lambda v: int(v * 0.55)))
    return rays, dark


def lighting_overlay(W, H, time_of_day="day", t=0.0, strength=1.0) -> Image.Image:
    """Luz de ambiente: rayos cálidos diagonales que respiran + viñeta suave (capas cacheadas)."""
    rays, dark = _light_layers(W, H, time_of_day)
    f = (0.75 + 0.25 * math.sin(t * 0.6)) * strength
    lay = rays.copy()
    lay.putalpha(rays.getchannel("A").point(lambda v: int(v * f)))
    lay.alpha_composite(dark)
    return lay


# ---------------------------------------------------------------- variantes por parche
def _on_white(im: Image.Image) -> np.ndarray:
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    bg.alpha_composite(im.convert("RGBA"))
    return np.asarray(bg.convert("RGB")).astype(np.float32)


def _paste(canvas_shape, arr, x, y, fill=255.0):
    """Coloca arr (h,w[,c]) en un lienzo del tamaño dado con recorte."""
    out = np.full(canvas_shape, fill, dtype=np.float32)
    H, W = canvas_shape[:2]
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 > x0 and y1 > y0:
        out[y0:y1, x0:x1] = arr[y0 - y:y1 - y, x0 - x:x1 - x]
    return out


def _align_head(base: Image.Image, var: Image.Image, head: float):
    """Mejor (escala, x, y) para que la cabeza de la variante coincida con la de la base."""
    W, H = base.size
    hh = int(H * head)
    best = None
    for res, scales, rng_px, center in ((200, np.linspace(0.88, 1.12, 13), 0.12, None), (480, None, 0.012, True)):
        k = res / W
        bh = _on_white(base.crop((0, 0, W, hh)).resize((res, max(1, int(hh * k))), Image.BILINEAR)).mean(axis=2)
        ba = np.asarray(base.crop((0, 0, W, hh)).getchannel("A").resize(bh.shape[::-1], Image.BILINEAR)) > 128
        if center:
            sc0, x0, y0 = best[1:]
            scales = np.linspace(sc0 - 0.01, sc0 + 0.01, 5)
        for sc in scales:
            vh = H * sc
            vw = var.width * vh / var.height
            vs = var.resize((max(1, round(vw * k)), max(1, round(vh * k))), Image.BILINEAR)
            g = _on_white(vs).mean(axis=2)
            if center:
                cx, cy = round(x0 * k), round(y0 * k)
            else:
                cx, cy = round((W - vw) / 2 * k), round((H - vh) * k)
            r = max(2, int(res * rng_px))
            step = 1 if center else 2
            for dx in range(-r, r + 1, step):
                for dy in range(-r, r + 1, step):
                    c = _paste(bh.shape, g, cx + dx, cy + dy)
                    err = float(np.abs(c - bh)[ba].mean())
                    if best is None or err < best[0]:
                        best = (err, float(sc), (cx + dx) / k, (cy + dy) / k)
    return best


def face_patch(base_path, variant_paths, out=None, head=0.42, thresh=55, grow=0.035) -> tuple[Image.Image, dict]:
    """Crea una variante (boca abierta, ojos cerrados...) pegando SOLO lo que cambia sobre el dibujo base.

    Los editores IA redibujan al personaje entero con pequeñas diferencias (bufanda, postura,
    escala); intercambiar imágenes completas lo haría "saltar". Aquí se alinea la CABEZA de
    cada candidata con la base (escala + desplazamiento), se elige la que mejor encaja y se
    pega solo la zona que cambia de verdad (ojos/boca) con borde suave.
    """
    base = Image.open(base_path).convert("RGBA")
    W, H = base.size
    hh = int(H * head)
    cands = []
    for vp in variant_paths:
        v = Image.open(vp).convert("RGBA")
        box = v.getbbox()
        v = v.crop(box) if box else v
        err, sc, x, y = _align_head(base, v, head)
        cands.append((err, vp, v, sc, x, y))
    err, vp, v, sc, x, y = min(cands, key=lambda c: c[0])
    vs = v.resize((max(1, round(v.width * H * sc / v.height)), max(1, round(H * sc))), Image.LANCZOS)
    aligned = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    aligned.alpha_composite(vs, (int(round(x)), int(round(y))))
    blur = lambda im: _on_white(im.filter(ImageFilter.GaussianBlur(max(1, W * 0.004))))  # noqa: E731
    diff = np.abs(blur(aligned) - blur(base)).max(axis=2)
    diff[hh:] = 0
    inside = (np.asarray(base.getchannel("A")) > 200) & (np.asarray(aligned.getchannel("A")) > 200)
    diff[~inside] = 0
    m = Image.fromarray(((diff > thresh) * 255).astype(np.uint8), "L")
    m = m.filter(ImageFilter.MinFilter(5))  # quita trazos sueltos de pelaje
    # cierre (rellena huecos) + crecimiento: el borde suave debe caer FUERA de los rasgos viejos
    m = m.filter(ImageFilter.MaxFilter(int(W * grow * 2) | 1)).filter(ImageFilter.MinFilter(int(W * grow) | 1))
    m = m.filter(ImageFilter.GaussianBlur(W * grow * 0.3))
    ma = np.minimum(np.asarray(m), np.asarray(base.getchannel("A")))
    patch = aligned.copy()
    patch.putalpha(Image.fromarray(ma.astype(np.uint8), "L"))
    res = base.copy()
    res.alpha_composite(patch)
    if out:
        res.save(out)
    head_px = int((np.asarray(base.getchannel("A"))[:hh] > 128).sum())
    info = dict(variant=Path(vp).name, err=round(err, 2), scale=round(sc, 3),
                mask_pct_head=round(100 * float((ma[:hh] > 128).sum()) / max(1, head_px), 1),
                errors={Path(c[1]).name: round(c[0], 2) for c in cands})
    return res, info
