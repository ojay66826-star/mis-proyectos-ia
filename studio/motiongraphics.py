"""Motion graphics: tipografía cinética, logos animados, infografías y fondos en bucle."""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import audio as A
from .core import canvas_size, clamp, ease_in_out, ease_out_back, ease_out_elastic, font, hex2rgb, mix, rng

PALETTES = {
    "vibrante": ["#ff006e", "#fb5607", "#ffbe0b", "#3a86ff", "#8338ec"],
    "pastel": ["#ffadad", "#ffd6a5", "#fdffb6", "#caffbf", "#a0c4ff"],
    "oscuro": ["#0d1b2a", "#1b263b", "#415a77", "#778da9", "#e0e1dd"],
    "neon": ["#08f7fe", "#09fbd3", "#fe53bb", "#f5d300", "#7122fa"],
    "corporativo": ["#003049", "#d62828", "#f77f00", "#fcbf49", "#eae2b7"],
}


class _Enc:
    def __init__(self, path, W, H, fps):
        self.path = Path(path)
        self.silent = self.path.with_suffix(".silent.mp4")
        self.p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                   "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(self.silent)],
                                  stdin=subprocess.PIPE)

    def write(self, img):
        self.p.stdin.write(img.convert("RGB").tobytes())

    def close(self, music=None, duration=None, sfx=None):
        self.p.stdin.close()
        self.p.wait()
        if music or sfx:
            mus = A.synth_music(music, duration + 0.2, seed=str(self.path)) if music else None
            wav = self.path.with_suffix(".wav")
            A.write_wav(wav, A.mix_timeline(duration, sfx or [], mus, 0.6))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(self.silent), "-i", str(wav), "-c:v", "copy",
                            "-c:a", "aac", "-shortest", "-movflags", "+faststart", str(self.path)], check=True)
            wav.unlink(missing_ok=True)
            self.silent.unlink(missing_ok=True)
        else:
            self.silent.replace(self.path)
        return self.path


def _gradient_bg(W, H, c1, c2, t, period):
    a = 2 * math.pi * t / period
    img = Image.new("RGB", (2, 2))
    img.putpixel((0, 0), c1)
    img.putpixel((1, 1), c1)
    img.putpixel((1, 0), mix(c1, c2, 0.5 + 0.5 * math.sin(a)))
    img.putpixel((0, 1), mix(c2, c1, 0.5 + 0.5 * math.cos(a)))
    return img.resize((W, H), Image.BICUBIC)


def animated_background(out, kind="blobs", duration=6.0, fmt="16:9", fps=30, palette="vibrante", quality="hd"):
    """Fondo en bucle PERFECTO (todas las funciones son periódicas en ``duration``)."""
    W, H = canvas_size(fmt, quality)
    cols = [hex2rgb(c) for c in PALETTES.get(palette, PALETTES["vibrante"])]
    enc = _Enc(out, W, H, fps)
    n = int(duration * fps)
    r = rng(kind)
    blobs = [(r.uniform(0, 1), r.uniform(0, 1), r.uniform(0.2, 0.45), r.choice([1, 2]), r.uniform(0, 6.28), cols[i % len(cols)]) for i in range(6)]
    parts = [(r.uniform(0, 1), r.uniform(0, 1), r.uniform(1, 4), r.choice([1, 2, 3])) for _ in range(120)]
    for i in range(n):
        t = i / fps
        ph = 2 * math.pi * t / duration
        if kind == "gradient":
            img = _gradient_bg(W, H, cols[0], cols[3], t, duration)
        elif kind == "grid":
            img = Image.new("RGB", (W, H), mix(cols[0], (0, 0, 0), 0.6))
            d = ImageDraw.Draw(img)
            step = H / 10
            off = (t / duration) * step
            for x in np.arange(-step, W + step, step):
                d.line([(x + off, 0), (x + off, H)], fill=cols[2], width=1)
            for y in np.arange(-step, H + step, step):
                d.line([(0, y + off), (W, y + off)], fill=cols[2], width=1)
            img = img.filter(ImageFilter.GaussianBlur(0.6))
        elif kind == "particles":
            img = _gradient_bg(W, H, mix(cols[4], (0, 0, 0), 0.5), mix(cols[3], (0, 0, 0), 0.6), t, duration)
            d = ImageDraw.Draw(img, "RGBA")
            for (x, y, s, sp) in parts:
                yy = (y - sp * t / duration) % 1.0
                xx = x + 0.02 * math.sin(ph * sp + x * 10)
                s2 = s * H / 720
                d.ellipse([xx * W - s2, yy * H - s2, xx * W + s2, yy * H + s2], fill=(255, 255, 255, 160))
        else:  # blobs
            img = Image.new("RGB", (W, H), mix(cols[0], (255, 255, 255), 0.85))
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(lay)
            for (x, y, rr, f, p0, c) in blobs:
                cx = (x + 0.15 * math.cos(ph * f + p0)) * W
                cy = (y + 0.15 * math.sin(ph * f + p0)) * H
                R = rr * H
                d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(*c, 170))
            lay = lay.resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BICUBIC)
            img.paste(lay, (0, 0), lay)
        enc.write(img)
    return enc.close()


def kinetic_typography(text, out, mode="pop", duration=None, fmt="9:16", fps=30, palette="vibrante", music="dance", quality="hd"):
    """Tipografía cinética: cada palabra entra con animación propia y ritmo musical."""
    W, H = canvas_size(fmt, quality)
    cols = [hex2rgb(c) for c in PALETTES.get(palette, PALETTES["vibrante"])]
    words = text.split()
    per = 60 / A.MOODS.get(music or "dance", A.MOODS["dance"])["bpm"]  # una palabra por pulso
    duration = duration or max(3.0, len(words) * per + 1.5)
    enc = _Enc(out, W, H, fps)
    n = int(duration * fps)
    maxw = W * 0.84
    fsize = int(min(W, H) * 0.16)
    # agrupa palabras en "pantallas" de hasta 3 palabras
    groups, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w.endswith((".", "!", "?", ",")):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    timings = []
    t = 0.2
    for g in groups:
        timings.append((t, g))
        t += per * len(g) + per * 0.5
    sfx = []
    for gi, (t0, g) in enumerate(timings):
        for wi in range(len(g)):
            sfx.append(dict(audio=A.synth_sfx("pop" if mode == "pop" else "whoosh"), start=t0 + wi * per, gain=0.35))
    for i in range(n):
        t = i / fps
        img = _gradient_bg(W, H, cols[0], cols[4], t, duration)
        d = ImageDraw.Draw(img, "RGBA")
        active = [x for x in timings if x[0] <= t]
        if active:
            t0, g = active[-1]
            nxt = timings[timings.index(active[-1]) + 1][0] if active[-1] != timings[-1] else duration + 1
            f = font(fsize)
            while max(d.textlength(w, font=f) for w in g) > maxw and f.size > 20:
                f = font(int(f.size * 0.9))
            total_h = len(g) * f.size * 1.15
            y0 = H / 2 - total_h / 2
            for wi, w in enumerate(g):
                ts = t0 + wi * per
                if t < ts:
                    continue
                k = clamp((t - ts) / 0.35)
                out_k = clamp((t - (nxt - 0.2)) / 0.2)
                tw = d.textlength(w.upper(), font=f)
                col = cols[(wi + timings.index(active[-1])) % len(cols)]
                col = mix(col, (255, 255, 255), 0.25)
                if mode == "typewriter":
                    shown = w.upper()[: max(1, int(len(w) * clamp((t - ts) / 0.3)))]
                    layer_img, x, y = None, W / 2 - tw / 2, y0 + wi * f.size * 1.15
                    d.text((x, y), shown, font=f, fill=(*col, 255), stroke_width=4, stroke_fill=(0, 0, 0))
                    continue
                s = ease_out_back(k) if mode == "pop" else 1.0
                s *= (1 - out_k)
                if s <= 0.02:
                    continue
                fs = font(max(8, int(f.size * s)))
                tws = d.textlength(w.upper(), font=fs)
                x = W / 2 - tws / 2
                y = y0 + wi * f.size * 1.15 + (f.size - fs.size) / 2
                if mode == "slide":
                    x += (1 - ease_in_out(k)) * W * (1 if wi % 2 else -1)
                elif mode == "wave":
                    y += math.sin(t * 6 + wi) * f.size * 0.08
                d.text((x + 6, y + 6), w.upper(), font=fs, fill=(0, 0, 0, 90))
                d.text((x, y), w.upper(), font=fs, fill=(*col, 255), stroke_width=max(2, fs.size // 18), stroke_fill=(20, 20, 30))
        enc.write(img)
    return enc.close(music, duration, sfx)


def animated_logo(name, out, tagline="", color="#3a86ff", duration=4.0, fmt="16:9", fps=30, quality="hd", music="epic"):
    """Logo animado: anillo que se dibuja, monograma con rebote, nombre escalonado y brillo."""
    W, H = canvas_size(fmt, quality)
    c = hex2rgb(color)
    enc = _Enc(out, W, H, fps)
    n = int(duration * fps)
    R = min(W, H) * 0.16
    cx, cy = W / 2, H * 0.42
    initials = "".join(w[0] for w in name.split()[:2]).upper() or "A"
    f_big = font(int(R * 1.0))
    f_name = font(int(min(W, H) * 0.075))
    f_tag = font(int(min(W, H) * 0.035), False)
    sfx = [dict(audio=A.synth_sfx("whoosh"), start=0.0, gain=0.5), dict(audio=A.synth_sfx("ding"), start=0.9, gain=0.6),
           dict(audio=A.synth_sfx("sparkle"), start=2.2, gain=0.5)]
    for i in range(n):
        t = i / fps
        img = Image.new("RGB", (W, H), (14, 16, 24))
        d = ImageDraw.Draw(img, "RGBA")
        k1 = ease_in_out(clamp(t / 0.9))
        d.arc([cx - R, cy - R, cx + R, cy + R], -90, -90 + 360 * k1, fill=c, width=int(R * 0.12))
        k2 = clamp((t - 0.7) / 0.6)
        if k2 > 0:
            s = ease_out_elastic(k2)
            rr = R * 0.82 * s
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c)
            fs = font(max(6, int(f_big.size * s)))
            tw = d.textlength(initials, font=fs)
            d.text((cx - tw / 2, cy - fs.size * 0.62), initials, font=fs, fill=(255, 255, 255))
        name_u = name.upper()
        x = W / 2 - d.textlength(name_u, font=f_name) / 2
        for li, ch in enumerate(name_u):
            k3 = clamp((t - 1.4 - li * 0.04) / 0.4)
            if k3 <= 0:
                break
            y = cy + R * 1.35 + (1 - ease_out_back(k3)) * 30
            d.text((x, y), ch, font=f_name, fill=(255, 255, 255, int(255 * k3)))
            x += d.textlength(ch, font=f_name)
        if tagline:
            k4 = clamp((t - 2.2) / 0.5)
            tw = d.textlength(tagline, font=f_tag)
            d.text((W / 2 - tw / 2, cy + R * 1.35 + f_name.size * 1.4), tagline, font=f_tag, fill=(180, 190, 210, int(255 * k4)))
        k5 = clamp((t - 2.0) / 0.8)
        if 0 < k5 < 1:
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sx = W * (-0.2 + 1.4 * k5)
            ImageDraw.Draw(sh).polygon([(sx, 0), (sx + W * 0.06, 0), (sx - W * 0.1, H), (sx - W * 0.16, H)], fill=(255, 255, 255, 50))
            img.paste(sh, (0, 0), sh)
        enc.write(img)
    return enc.close(music, duration, sfx)


def infographic(data: dict, out, title="Datos", duration=6.0, fmt="16:9", fps=30, palette="vibrante", quality="hd", unit=""):
    """Gráfico de barras animado con contadores (infografía educativa)."""
    W, H = canvas_size(fmt, quality)
    cols = [hex2rgb(c) for c in PALETTES.get(palette, PALETTES["vibrante"])]
    enc = _Enc(out, W, H, fps)
    n = int(duration * fps)
    items = list(data.items())
    vmax = max(v for _, v in items) or 1
    ft, fl, fv = font(int(H * 0.07)), font(int(H * 0.035), False), font(int(H * 0.04))
    left, right, top, bottom = W * 0.12, W * 0.92, H * 0.25, H * 0.85
    bw = (right - left) / len(items)
    sfx = [dict(audio=A.synth_sfx("pop"), start=0.6 + i * 0.25, gain=0.4) for i in range(len(items))]
    for i in range(n):
        t = i / fps
        img = Image.new("RGB", (W, H), (248, 247, 242))
        d = ImageDraw.Draw(img)
        a = clamp(t / 0.5)
        tw = d.textlength(title, font=ft)
        d.text((W / 2 - tw / 2, H * 0.06 + (1 - a) * 20), title, font=ft, fill=mix((248, 247, 242), (30, 30, 40), a))
        d.line([(left, bottom), (right, bottom)], fill=(120, 120, 120), width=3)
        for j, (label, v) in enumerate(items):
            k = ease_out_back(clamp((t - 0.6 - j * 0.25) / 0.9))
            h = (bottom - top) * v / vmax * k
            x0 = left + j * bw + bw * 0.18
            x1 = left + (j + 1) * bw - bw * 0.18
            d.rounded_rectangle([x0, bottom - max(2, h), x1, bottom], radius=int(bw * 0.08), fill=cols[j % len(cols)])
            val = v * clamp(k)
            txt = f"{val:.0f}{unit}" if float(v).is_integer() else f"{val:.1f}{unit}"
            vw = d.textlength(txt, font=fv)
            d.text(((x0 + x1) / 2 - vw / 2, bottom - h - fv.size * 1.3), txt, font=fv, fill=(40, 40, 50))
            lw = d.textlength(str(label), font=fl)
            d.text(((x0 + x1) / 2 - lw / 2, bottom + 10), str(label), font=fl, fill=(70, 70, 80))
        enc.write(img)
    return enc.close("calm", duration, sfx)
