"""Convertir una imagen fija en video.

Modo local (siempre disponible): movimiento de cámara Ken Burns con subpíxel,
falso 2.5D (paralaje entre primer plano y fondo por desenfoque de bordes),
"respiración", efectos de partículas, gradación de estilo y música.
Modo IA (opcional): Replicate imagen→video (``provider='replicate'``).
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

from . import audio as A
from .core import canvas_size, ease_in_out
from .effects import render_effects
from .styles import post_process

MOVES = ["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "orbit", "parallax", "breathe"]


def _fit(img, W, H, margin=1.25):
    """Escala la imagen para cubrir el lienzo con margen para mover la cámara."""
    tw, th = int(W * margin), int(H * margin)
    return ImageOps.fit(img.convert("RGB"), (tw, th), Image.LANCZOS)


def image_to_video(image_path, out_path, duration=6.0, move="zoom_in", fmt="16:9", fps=24, effects=None,
                   style="cinematic", music="calm", quality="hd", provider="local", prompt="", cb=None):
    out_path = Path(out_path)
    if provider == "replicate":
        from .providers import generate_video_replicate
        return generate_video_replicate(prompt or "subtle cinematic camera motion, animate the scene", out_path, image_path)
    W, H = canvas_size(fmt, quality)
    src = Image.open(image_path)
    big = _fit(src, W, H, 1.3)
    BW, BH = big.size
    fg_mask = None
    bg_blur = None
    if move == "parallax":
        # máscara de "sujeto" aproximada: centro de la imagen con más detalle (bordes)
        edges = np.asarray(big.convert("L").filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(25))).astype(np.float32)
        yy, xx = np.mgrid[0:BH, 0:BW]
        center = np.exp(-(((xx - BW / 2) / (BW * 0.3)) ** 2 + ((yy - BH * 0.55) / (BH * 0.35)) ** 2))
        m = edges / (edges.max() + 1e-6) * 0.5 + center * 0.7
        fg_mask = Image.fromarray((np.clip((m - 0.45) * 4, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(20))
        bg_blur = big.filter(ImageFilter.GaussianBlur(3))
    n = int(duration * fps)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", str(out_path.with_suffix(".silent.mp4"))]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fx = [f if isinstance(f, dict) else {"type": f} for f in (effects or [])]
    for i in range(n):
        t = i / fps
        k = ease_in_out(t / duration)
        zoom, cx, cy, rot = 1.0, 0.5, 0.5, 0.0
        if move == "zoom_in":
            zoom = 1.0 + 0.22 * k
        elif move == "zoom_out":
            zoom = 1.22 - 0.22 * k
        elif move == "pan_left":
            cx, zoom = 0.62 - 0.24 * k, 1.05
        elif move == "pan_right":
            cx, zoom = 0.38 + 0.24 * k, 1.05
        elif move == "pan_up":
            cy, zoom = 0.62 - 0.24 * k, 1.05
        elif move == "orbit":
            cx, cy = 0.5 + 0.08 * math.cos(2 * math.pi * t / duration), 0.5 + 0.06 * math.sin(2 * math.pi * t / duration)
            zoom, rot = 1.08, 1.2 * math.sin(2 * math.pi * t / duration)
        elif move == "breathe":
            zoom = 1.04 + 0.03 * math.sin(2 * math.pi * t / 4)
        elif move == "parallax":
            zoom = 1.05 + 0.1 * k
            cx = 0.45 + 0.1 * k
        cw, ch = W * 1.0 / zoom * (BW / (W * 1.3)), H * 1.0 / zoom * (BH / (H * 1.3))
        px, py = cx * BW, cy * BH
        box = (px - cw / 2, py - ch / 2, px + cw / 2, py + ch / 2)
        if move == "parallax":
            bgf = bg_blur.resize((W, H), Image.BICUBIC, box=box)
            sh = 0.06 * k * BW
            box2 = (box[0] + sh, box[1], box[2] + sh, box[3])
            fg = big.resize((W, H), Image.BICUBIC, box=box2)
            msk = fg_mask.resize((W, H), Image.BICUBIC, box=box2)
            frame = Image.composite(fg, bgf, msk)
        else:
            frame = big.resize((W, H), Image.BICUBIC, box=box)
        if rot:
            frame = frame.rotate(rot, Image.BICUBIC, expand=False).resize((W, H))
        if fx:
            fr = frame.convert("RGBA")
            fr.alpha_composite(render_effects((W, H), fx, t, None, duration))
            frame = fr.convert("RGB")
        if style and style != "none":
            frame = post_process(frame, style, t, i, letterbox=False)
        proc.stdin.write(frame.tobytes())
        if cb and i % 24 == 0:
            cb("imagen→video", i / n, f"frame {i}/{n}")
    proc.stdin.close()
    proc.wait()
    silent = out_path.with_suffix(".silent.mp4")
    if music:
        mus = A.synth_music(music, duration + 0.2, seed=str(image_path))
        clips = [dict(audio=A.synth_sfx(A.EFFECT_SFX[f["type"]], dur=duration), start=0, gain=0.5) for f in fx if A.EFFECT_SFX.get(f["type"])]
        wav = out_path.with_suffix(".wav")
        A.write_wav(wav, A.mix_timeline(duration, clips, mus, 0.6))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                        "-shortest", "-movflags", "+faststart", str(out_path)], check=True)
        wav.unlink(missing_ok=True)
        silent.unlink(missing_ok=True)
    else:
        silent.rename(out_path)
    return out_path
