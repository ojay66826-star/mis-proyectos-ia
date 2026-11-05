"""Post-producción de una escena fight3d: hit-stop, fotogramas de impacto, líneas de velocidad, rótulos, gradación,
sonido sincronizado (campana, barridos, golpes, público, música) y codificación final.

    python scripts/fight3d/post.py projects/<escena>/frames projects/<escena>/eventos.json projects/<escena>
Salida: <escena>/final.mp4 (1920×1080), <escena>/audio/mezcla.wav, <escena>/post_frames/*.png
"""
import json
import math
import random
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from studio import audio as A  # noqa: E402

FRAMES, EVENTS, OUT = Path(sys.argv[1]), json.load(open(sys.argv[2])), Path(sys.argv[3])
FPS = EVENTS["fps"]
N = EVENTS["frames"]
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
HOLD = {"block": 2, "hit": 4, "big": 8, "land": 3, "whiff": 0}
ev = EVENTS["events"]
impacts = {e["frame"]: e for e in ev if e["kind"] in HOLD}

# ------------------------------------------------------------------ secuencia con hit-stop
seq = []          # (frame_render, efecto, datos)
out_index = {}    # frame de render -> primer índice de salida
for f in range(1, N + 1):
    out_index[f] = len(seq)
    seq.append((f, None, None))
    e = impacts.get(f)
    if e and HOLD[e["kind"]]:
        for h in range(HOLD[e["kind"]]):
            seq.append((f, e["kind"], {"h": h, "screen": e["screen"]}))


def to_out_time(render_frame):
    return out_index[render_frame] / FPS


# ventanas de golpe para las líneas de velocidad (desde el barrido hasta el impacto)
strike_windows = []
for w in (e for e in ev if e["kind"] == "whoosh"):
    nxt = min((f for f in impacts if f >= w["frame"]), default=None)
    if nxt:
        strike_windows.append((w["frame"], nxt, impacts[nxt]["screen"], impacts[nxt]["kind"]))


def speed_lines(img, center, strength, seed):
    W, H = img.size
    cx, cy = center[0] * W, center[1] * H
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    rnd = random.Random(seed)
    n = int(70 * strength) + 20
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi)
        r0 = rnd.uniform(0.22, 0.42) * W
        r1 = 1.3 * W
        w = rnd.uniform(1.5, 5.5) * strength
        p0 = (cx + r0 * math.cos(a), cy + r0 * math.sin(a))
        p1 = (cx + r1 * math.cos(a - w / r1), cy + r1 * math.sin(a - w / r1))
        p2 = (cx + r1 * math.cos(a + w / r1 * 3), cy + r1 * math.sin(a + w / r1 * 3))
        d.polygon([p0, p1, p2], fill=(255, 255, 255, int(rnd.uniform(90, 190) * min(1, strength))))
    return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")


def flash(img, center, amount):
    W, H = img.size
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.sqrt((xx - center[0] * W) ** 2 + (yy - center[1] * H) ** 2) / W
    glow = np.clip(1.0 - dist / 0.35, 0, 1)[..., None] * amount
    a = np.asarray(img).astype(np.float32) / 255
    a = a + (1 - a) * np.clip(glow + amount * 0.35, 0, 1)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def impact_bw(img):
    g = np.asarray(img.convert("L")).astype(np.float32) / 255
    on = g > 0.42
    out = np.where(on[..., None], np.array([250, 244, 232]), np.array([18, 10, 22])).astype(np.uint8)
    return Image.fromarray(out)


def zoom(img, center, z):
    W, H = img.size
    cw, ch = W / z, H / z
    cx = min(max(center[0] * W, cw / 2), W - cw / 2)
    cy = min(max(center[1] * H, ch / 2), H - ch / 2)
    return img.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.LANCZOS)


def grade(img, vign):
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.12)
    a = np.asarray(img).astype(np.float32) * vign
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def title(img, text, style, k, nframes):
    W, H = img.size
    size = int(H * (0.2 if style == "round" else 0.34))
    font = ImageFont.truetype(FONT, size)
    tw, th = font.getbbox(text)[2:]
    pad = size // 3
    layer = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if style == "round":
        d.text((pad, pad), text, font=font, fill=(255, 255, 255, 255), stroke_width=size // 12, stroke_fill=(20, 12, 24, 255))
    else:
        d.text((pad, pad), text, font=font, fill=(255, 214, 64, 255), stroke_width=size // 10, stroke_fill=(190, 20, 30, 255))
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0.22, -0.11 * layer.size[1], 0, 1, 0), Image.BICUBIC)
    slam = 1.0 + 0.35 * max(0.0, 1 - k / 4) ** 2
    if k >= nframes - 6:
        alpha = max(0.0, (nframes - k) / 6)
    else:
        alpha = 1.0
    lw, lh = int(layer.size[0] * slam), int(layer.size[1] * slam)
    layer = layer.resize((lw, lh), Image.LANCZOS)
    if alpha < 1:
        layer.putalpha(Image.fromarray((np.asarray(layer.getchannel("A")) * alpha).astype(np.uint8)))
    jx = int(math.sin(k * 7.1) * 6 * max(0, 1 - k / 8)) if style == "ko" else 0
    base = img.convert("RGBA")
    base.alpha_composite(layer, ((W - lw) // 2 + jx, int(H * (0.12 if style == "round" else 0.3)) - (lh - layer.size[1]) // 2))
    return base.convert("RGB")


def build_frames():
    pf = OUT / "post_frames"
    pf.mkdir(exist_ok=True)
    for old in pf.glob("*.png"):
        old.unlink()
    W, H = Image.open(FRAMES / "f0001.png").size
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vign = np.clip(1.08 - 0.35 * r ** 2.2, 0.55, 1.0)[..., None]
    titles = [e for e in ev if e["kind"] == "title"]
    for i, (f, fx, data) in enumerate(seq):
        img = Image.open(FRAMES / f"f{f:04d}.png").convert("RGB")
        for (a, b, scr, kind) in strike_windows:
            if a <= f <= b and fx is None:
                u = (f - a) / max(1, b - a)
                if kind == "big" or u > 0.5:
                    img = speed_lines(img, scr, 0.5 + 0.6 * u, f)
        if fx:
            h, scr = data["h"], data["screen"]
            if fx == "big":
                if h == 0:
                    img = impact_bw(img)
                elif h == 1:
                    img = ImageOps.invert(img)
                else:
                    img = speed_lines(zoom(img, scr, 1.0 + 0.07 * (1 - (h - 2) / 6)), scr, 1.4, f * 10 + h)
                    img = flash(img, scr, 0.35 * (1 - (h - 2) / 6))
            elif fx == "hit":
                img = flash(img, scr, 0.75 if h == 0 else 0.3)
                img = speed_lines(zoom(img, scr, 1.04), scr, 1.0, f * 10 + h)
            elif fx in ("block", "land"):
                img = flash(img, scr, 0.45 if h == 0 else 0.15)
        img = grade(img, vign)
        for t in titles:
            if t["frame"] <= f <= t["end_frame"]:
                k = i - out_index[t["frame"]]
                img = title(img, t["text"], t["style"], k, out_index[t["end_frame"]] - out_index[t["frame"]])
        img.save(pf / f"{i:04d}.png")
    return pf, len(seq)


# ------------------------------------------------------------------ sonido

def pitch(sig, factor):
    """factor > 1 = más grave y más largo."""
    idx = np.arange(0, len(sig), 1 / factor)
    return np.interp(idx, np.arange(len(sig)), sig).astype(np.float32)


def crowd(dur, seed):
    nz = A.noise(dur, seed)
    band = A.smooth(nz, 6) - A.smooth(nz, 60)
    t = np.arange(len(band)) / A.SR
    mod = 0.6 + 0.25 * np.sin(2 * np.pi * 0.31 * t) + 0.15 * np.sin(2 * np.pi * 0.73 * t + 1)
    return (band * mod * 3.0).astype(np.float32)


def cheer(seed, dur=1.6):
    nz = A.noise(dur, seed)
    band = A.smooth(nz, 4) - A.smooth(nz, 30)
    t = np.arange(len(band)) / A.SR
    env = np.minimum(t / 0.08, 1) * np.exp(-t * 1.6)
    return (band * env * 6.0).astype(np.float32)


def build_audio(total):
    clips = []
    for e in ev:
        if e["kind"] == "bell":
            clips.append({"audio": pitch(A.synth_sfx("ding"), 1.25), "start": to_out_time(e["frame"]), "gain": 0.8})
        elif e["kind"] == "whoosh":
            d = max(0.12, to_out_time(e["end_frame"]) - to_out_time(e["frame"]))
            clips.append({"audio": A.synth_sfx("whoosh", d, seed=e["frame"]), "start": to_out_time(e["frame"]), "gain": 0.5})
    for f, e in impacts.items():
        t = to_out_time(f)
        k = e["kind"]
        if k == "block":
            clips += [{"audio": pitch(A.synth_sfx("punch"), 0.9), "start": t, "gain": 1.1},
                      {"audio": A.synth_sfx("footstep", seed=f), "start": t, "gain": 0.6}]
        elif k == "hit":
            clips += [{"audio": pitch(A.synth_sfx("punch"), 1.35), "start": t, "gain": 1.0},
                      {"audio": A.synth_sfx("punch", seed=3), "start": t + 0.01, "gain": 0.7},
                      {"audio": cheer(f, 1.4), "start": t + 0.15, "gain": 0.35}]
        elif k == "big":
            clips += [{"audio": pitch(A.synth_sfx("punch"), 1.7), "start": t, "gain": 1.0},
                      {"audio": A.synth_sfx("explosion", 1.2, seed=5), "start": t, "gain": 0.55},
                      {"audio": pitch(A.synth_sfx("thunder", 2.0, seed=9), 1.3), "start": t + 0.05, "gain": 0.3},
                      {"audio": cheer(f, 2.6), "start": t + 0.35, "gain": 0.7}]
        elif k == "land":
            clips += [{"audio": pitch(A.synth_sfx("punch", seed=8), 1.5), "start": t, "gain": 0.9},
                      {"audio": A.synth_sfx("footstep", seed=11), "start": t + 0.03, "gain": 0.9},
                      {"audio": A.synth_sfx("explosion", 0.6, seed=12), "start": t, "gain": 0.25}]
        elif k == "whiff":
            pass
    # público de fondo y música, con silencio justo antes de la patada decisiva
    n = int(total * A.SR) + 1
    bed = np.zeros(n, dtype=np.float32)
    c = crowd(total + 0.5, 21)[:n]
    bed[:len(c)] = c * 0.18
    music = A.synth_music("action", total + 0.5, seed=4)[:n]
    env = np.ones(n, dtype=np.float32)
    big = [to_out_time(f) for f, e in impacts.items() if e["kind"] == "big"]
    def ramp(i0, i1, v0, v1):
        i0, i1 = max(0, min(n, i0)), max(0, min(n, i1))
        if i1 > i0:
            env[i0:i1] = np.minimum(env[i0:i1], np.linspace(v0, v1, i1 - i0))

    for t in big:
        a, b = int((t - 0.45) * A.SR), int(t * A.SR)
        ramp(a, b, 1.0, 0.08)
        ramp(b, int((t + 0.9) * A.SR), 0.08, 1.0)
    for f, e in impacts.items():
        t = int(to_out_time(f) * A.SR)
        if e["kind"] in ("hit", "block", "land"):
            ramp(t, t + int(0.35 * A.SR), 0.45, 1.0)
    clips.append({"audio": bed * env, "start": 0, "gain": 1.0})
    music = music * env[:len(music), None]
    mix = A.mix_timeline(total, clips, music=music, music_gain=0.3, duck=False)
    return mix


def main():
    pf, nout = build_frames()
    total = nout / FPS
    (OUT / "audio").mkdir(exist_ok=True)
    wav = OUT / "audio" / "mezcla.wav"
    A.write_wav(wav, build_audio(total))
    final = OUT / "final.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(pf / "%04d.png"), "-i", str(wav),
                    "-vf", "scale=1920:1080:flags=lanczos", "-c:v", "libx264", "-crf", "18", "-preset", "slow",
                    "-pix_fmt", "yuv420p", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    print(json.dumps({"final": str(final), "frames": nout, "seconds": round(total, 2),
                      "hitstop_frames": nout - N}, ensure_ascii=False))


if __name__ == "__main__":
    main()
