"""Pipeline de render 2D: proyecto (JSON) -> MP4 con audio.

Etapas: hojas de personaje -> voces + lip-sync -> línea de tiempo -> frames
(en paralelo) -> FFmpeg -> mezcla de audio -> mux -> miniatura, GIF, storyboard,
subtítulos .srt y control de calidad.
"""
from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import subprocess
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import audio as A
from .backgrounds import build_background
from .characters import character_sheet, make_character, render_character
from .core import PROJECTS_DIR, canvas_size, clamp, ease_in_out, font, slugify
from .effects import render_effects
from .motion import action_at, actor_position, emotion_at, pose_for
from .planner import normalize
from .styles import STYLES, char_style, post_process, stop_motion_jitter

TRANSITION = 0.45


def _log(cb, stage, frac, msg):
    if cb:
        cb(stage, frac, msg)
    else:
        print(f"[{stage}] {int(frac * 100):3d}% {msg}", flush=True)


# ---------------------------------------------------------------- preparación
def prepare(spec: dict, out: Path, cb=None) -> dict:
    spec = normalize(spec)
    out.mkdir(parents=True, exist_ok=True)
    (out / "characters").mkdir(exist_ok=True)
    (out / "audio").mkdir(exist_ok=True)
    style = spec["style"]
    chars = {c["id"]: c for c in spec["characters"]}
    for i, c in enumerate(spec["characters"]):
        _log(cb, "personajes", i / max(1, len(chars)), f"hoja de {c['name']}")
        character_sheet(c, char_style(style), out / "characters" / f"{c['id']}_sheet.png")
    fps = int(spec["fps"])
    # voces y lip-sync
    lines = []
    for si, s in enumerate(spec["scenes"]):
        cursor = 0.4
        for li, d in enumerate(s["dialogue"]):
            path = out / "audio" / f"s{si + 1}_l{li + 1}_{d['character']}.wav"
            if d.get("audio_file"):
                # voz grabada por el usuario (cualquier formato que lea FFmpeg)
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(d["audio_file"]), "-ar", str(A.SR), "-ac", "2", str(path)], check=True)
                dur = A.duration_of(path)
                vis = A.lipsync_track(d["text"], path, fps)
            elif spec.get("voices", True):
                _log(cb, "voces", si / len(spec["scenes"]), f"{chars[d['character']]['name']}: {d['text']}")
                A.tts(d["text"], path, A.voice_for(chars[d["character"]]), spec.get("tts_provider", "auto"))
                dur = A.duration_of(path)
                vis = A.lipsync_track(d["text"], path, fps)
            else:
                dur = max(1.0, len(d["text"]) * 0.065)
                vis = ["A" if (i // 3) % 2 else "E" for i in range(int(dur * fps))]
                path = None
            start = d.get("start", cursor)
            d["start"], d["duration"], d["audio"], d["visemes"] = start, dur, str(path) if path else None, vis
            cursor = start + dur + 0.3
        s["duration"] = max(s["duration"], cursor + 0.4 if s["dialogue"] else s["duration"])
    # línea de tiempo
    t = 0.0
    td = 0.0 if spec.get("transition") == "cut" else TRANSITION
    for i, s in enumerate(spec["scenes"]):
        s["start"] = t
        t += s["duration"] - (td if i < len(spec["scenes"]) - 1 else 0)
    spec["total_duration"] = round(t, 3)
    spec["transition_duration"] = td
    return spec


# ---------------------------------------------------------------- render de escena
class SceneRenderer:
    def __init__(self, spec, quality="hd"):
        self.spec = spec
        self.W, self.H = canvas_size(spec["format"], quality)
        self.style = spec["style"]
        self.cstyle = char_style(self.style)
        self.chars = {c["id"]: c for c in spec["characters"]}
        self._bg = {}
        self.tempo = A.MOODS.get(spec.get("mood", "happy"), A.MOODS["happy"])["bpm"]
        self.hold = 2 if self.style in ("clay", "stopmotion", "paper") else 1

    def bg(self, s):
        k = (s["background"], s["time_of_day"])
        if k not in self._bg:
            self._bg[k] = build_background(s["background"], self.W, self.H, s["time_of_day"], self.style, seed=k[0])
        return self._bg[k]

    def camera(self, s, lt):
        cam = s["camera"].get("type", "static")
        k = ease_in_out(lt / s["duration"])
        cam_x, zoom, sx, sy = 0.0, 1.0, 0.0, 0.0
        if cam == "pan":
            cam_x = -0.6 + 1.2 * k
        elif cam == "pan_left":
            cam_x = 0.6 - 1.2 * k
        elif cam == "zoom_in":
            zoom = 1.0 + 0.15 * k
        elif cam == "zoom_out":
            zoom = 1.15 - 0.15 * k
        elif cam == "dolly_in":
            zoom = 1.0 + 0.28 * k
        elif cam == "shake":
            r = np.random.default_rng(int(lt * 60))
            amp = self.H * 0.008
            sx, sy = r.uniform(-amp, amp), r.uniform(-amp, amp)
            zoom = 1.04
        return cam_x, zoom, sx, sy

    def frame(self, s, lt, frame_idx):
        W, H = self.W, self.H
        if self.hold > 1:
            q = 1.0 / 12
            lt = math.floor(lt / q) * q
        cam_x, zoom, sx, sy = self.camera(s, lt)
        img = self.bg(s).render(cam_x, lt).convert("RGBA")
        n_act = max(1, len(s["actors"]))
        base_h = min(W, H) * (0.46 if n_act <= 2 else 0.38)
        if W < H:
            base_h = W * 0.42
        anchors = {}
        jx, jy, jr = stop_motion_jitter(self.style, frame_idx, self.hold)
        order = sorted(range(len(s["actors"])), key=lambda i: s["actors"][i]["from"][1])
        talking = {}
        for d in s["dialogue"]:
            if d["start"] <= lt < d["start"] + d["duration"]:
                fi = int((lt - d["start"]) * self.spec["fps"])
                talking[d["character"]] = d["visemes"][fi] if fi < len(d["visemes"]) else "X"
        for i in order:
            a = s["actors"][i]
            spec = self.chars[a["character"]]
            if a.get("transform_to") and lt >= a.get("transform_at", s["duration"] / 2):
                spec = dict(make_character(a["transform_to"], spec["name"]), id=spec["id"])
            x, y = actor_position(a, lt, s["duration"])
            act = action_at(a, lt)
            em = emotion_at(a, lt)
            if a["character"] in talking and act == "idle":
                act = "talk"
            pose = pose_for(act, lt, em, self.tempo, seed=i * 0.37)
            pose.facing = a.get("facing", 1)
            if a["character"] in talking:
                pose.viseme = talking[a["character"]]
            if act in ("walk", "run") and a["to"][0] != a["from"][0]:
                pose.facing = 1 if a["to"][0] > a["from"][0] else -1
            scale = a.get("scale", 1.0)
            if a.get("transform_to"):
                ta = a.get("transform_at", s["duration"] / 2)
                dt = lt - ta
                if abs(dt) < 0.3:
                    scale *= 1 + 0.25 * (1 - abs(dt) / 0.3)
            pose.tilt += jr
            cim, (ax, ay) = render_character(spec, pose, int(base_h * scale), self.cstyle)
            px = x * W - cam_x * 0.2 * W + jx
            py = y * H + jy
            # sombra
            sh = Image.new("RGBA", (int(base_h * 0.7), int(base_h * 0.14)), (0, 0, 0, 0))
            shd = ImageDraw.Draw(sh)
            k = clamp(1 - pose.body_dy * 1.6, 0.3, 1)
            shd.ellipse([sh.width * (1 - k) / 2, 0, sh.width * (1 + k) / 2, sh.height], fill=(0, 0, 0, int(70 * k)))
            img.alpha_composite(sh, (int(px - sh.width / 2), int(py - sh.height / 2)))
            img.alpha_composite(cim, (int(px - ax), int(py - ay)))
            anchors[a["character"]] = (px, py - base_h * 0.15)
            if a.get("transform_to"):
                ta = a.get("transform_at", s["duration"] / 2)
                if abs(lt - ta) < 0.25:
                    fl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                    r = base_h * 0.8 * (1 - abs(lt - ta) / 0.25)
                    ImageDraw.Draw(fl).ellipse([px - r, py - base_h * 0.5 - r, px + r, py - base_h * 0.5 + r], fill=(255, 255, 255, 220))
                    img.alpha_composite(fl.filter(ImageFilter.GaussianBlur(base_h * 0.08)))
        if s["effects"]:
            img.alpha_composite(render_effects((W, H), s["effects"], lt, anchors, s["duration"]))
        if zoom != 1.0 or sx or sy:
            cw, ch = W / zoom, H / zoom
            focus = s["camera"].get("focus", [0.5, 0.55])
            cx = clamp(focus[0] * W + sx, cw / 2, W - cw / 2)
            cy = clamp(focus[1] * H + sy, ch / 2, H - ch / 2)
            img = img.resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
        return img.convert("RGB")

    def overlays(self, img, T, frame_idx):
        """Subtítulos, rótulos y título (se aplican tras el post-procesado)."""
        W, H = img.size
        d = ImageDraw.Draw(img, "RGBA")
        big = self.spec.get("subtitles") == "big" or W < H
        # título inicial
        if T < 2.2 and self.spec.get("show_title", True):
            a = clamp(min(T / 0.4, (2.2 - T) / 0.5))
            f = font(int(H * (0.07 if W > H else 0.045)))
            txt = self.spec["title"]
            tw = d.textlength(txt, font=f)
            y = H * 0.12
            d.rounded_rectangle([W / 2 - tw / 2 - 24, y - 12, W / 2 + tw / 2 + 24, y + f.size + 20], radius=18, fill=(0, 0, 0, int(140 * a)))
            d.text((W / 2 - tw / 2, y), txt, font=f, fill=(255, 255, 255, int(255 * a)))
        for s in self.spec["scenes"]:
            lt = T - s["start"]
            if not (0 <= lt < s["duration"]):
                continue
            cap = s.get("caption")
            if cap and 0.3 < lt < min(s["duration"], 3.0) and not (T < 2.2 and s is self.spec["scenes"][0]):
                f = font(int(H * (0.055 if W > H else 0.04)))
                yy = H * 0.14
                for ln in _wrap(d, cap, f, W * 0.88):
                    tw = d.textlength(ln, font=f)
                    d.text((W / 2 - tw / 2, yy), ln, font=f, fill=(255, 255, 255), stroke_width=max(2, f.size // 12), stroke_fill=(20, 20, 30))
                    yy += f.size * 1.2
            if not self.spec.get("subtitles"):
                continue
            for dl in s["dialogue"]:
                if dl["start"] <= lt < dl["start"] + dl["duration"] + 0.2:
                    name = self.chars[dl["character"]]["name"]
                    txt = dl["text"] if big else f"{name}: {dl['text']}"
                    f = font(int(H * (0.042 if not big else 0.034 if W < H else 0.06)))
                    lines = _wrap(d, txt, f, W * 0.86)
                    # en vertical los personajes ocupan la franja 55-90 %: subtítulos en el tercio medio superior
                    base = 0.86 if not big else (0.44 if W < H else 0.7)
                    y = H * base - len(lines) * f.size * 1.2
                    for ln in lines:
                        tw = d.textlength(ln, font=f)
                        if big:
                            d.text((W / 2 - tw / 2, y), ln, font=f, fill=(255, 235, 59), stroke_width=max(3, f.size // 9), stroke_fill=(0, 0, 0))
                        else:
                            d.rounded_rectangle([W / 2 - tw / 2 - 14, y - 4, W / 2 + tw / 2 + 14, y + f.size * 1.2], radius=8, fill=(0, 0, 0, 150))
                            d.text((W / 2 - tw / 2, y), ln, font=f, fill=(255, 255, 255))
                        y += f.size * 1.25
        return img

    def at(self, T, frame_idx):
        scenes = self.spec["scenes"]
        active = [s for s in scenes if s["start"] <= T < s["start"] + s["duration"]] or [scenes[-1]]
        a = active[0]
        img = self.frame(a, T - a["start"], frame_idx)
        if len(active) > 1:
            b = active[1]
            k = clamp((T - b["start"]) / max(0.01, self.spec["transition_duration"]))
            imb = self.frame(b, T - b["start"], frame_idx)
            img = transition(img, imb, k, b.get("transition", self.spec.get("transition", "fade")))
        img = post_process(img, self.style, T, frame_idx, letterbox=self.spec.get("letterbox"))
        return self.overlays(img, T, frame_idx)


def _wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) > maxw and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def transition(a: Image.Image, b: Image.Image, k: float, kind="fade") -> Image.Image:
    k = ease_in_out(k)
    W, H = a.size
    if kind == "wipe":
        out = a.copy()
        x = int(W * k)
        out.paste(b.crop((0, 0, x, H)), (0, 0))
        return out
    if kind == "slide":
        out = Image.new("RGB", (W, H))
        out.paste(a, (int(-W * k), 0))
        out.paste(b, (int(W * (1 - k)), 0))
        return out
    if kind == "circle":
        mask = Image.new("L", (W, H), 0)
        r = math.hypot(W, H) / 2 * k
        ImageDraw.Draw(mask).ellipse([W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r], fill=255)
        return Image.composite(b, a, mask)
    if kind == "dip":
        black = Image.new("RGB", (W, H))
        return Image.blend(a, black, k * 2) if k < 0.5 else Image.blend(black, b, (k - 0.5) * 2)
    return Image.blend(a, b, k)


# ---------------------------------------------------------------- multiproceso
_R = None


def _init_worker(spec, quality):
    global _R
    _R = SceneRenderer(spec, quality)


def _render_one(i):
    T = i / _R.spec["fps"]
    return _R.at(T, i).tobytes()


def render_frames_to_video(spec, path, quality="hd", cb=None, workers=None):
    W, H = canvas_size(spec["format"], quality)
    fps = spec["fps"]
    n = int(math.ceil(spec["total_duration"] * fps))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    workers = workers or max(1, min(os.cpu_count() or 2, 8))
    t0 = time.time()
    if workers > 1:
        ctx = mp.get_context("fork") if hasattr(os, "fork") else mp.get_context("spawn")
        with ctx.Pool(workers, initializer=_init_worker, initargs=(spec, quality)) as pool:
            for k, buf in enumerate(pool.imap(_render_one, range(n), chunksize=4)):
                proc.stdin.write(buf)
                if k % 12 == 0:
                    _log(cb, "frames", k / n, f"frame {k}/{n} ({time.time() - t0:.0f}s)")
    else:
        _init_worker(spec, quality)
        for k in range(n):
            proc.stdin.write(_render_one(k))
            if k % 12 == 0:
                _log(cb, "frames", k / n, f"frame {k}/{n}")
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("FFmpeg falló al codificar el video")
    return n


# ---------------------------------------------------------------- audio
def build_audio(spec, out: Path, cb=None) -> Path:
    total = spec["total_duration"]
    clips = []
    fps = spec["fps"]
    for s in spec["scenes"]:
        st = s["start"]
        for d in s["dialogue"]:
            if d.get("audio"):
                clips.append(dict(audio=A.read_wav(d["audio"]), start=st + d["start"], gain=1.0, kind="voice"))
        for a in s["actors"]:
            act = a["action"]
            pan = (a["from"][0] - 0.5) * 1.2
            if act in ("walk", "run"):
                step = 1 / (2 * (1.6 if act == "walk" else 2.6))
                t = 0.1
                fs = A.synth_sfx("footstep")
                while t < s["duration"]:
                    clips.append(dict(audio=fs, start=st + t, gain=0.5, pan=pan))
                    t += step
            elif act == "jump":
                t = 0.24
                while t < s["duration"]:
                    clips.append(dict(audio=A.synth_sfx("jump"), start=st + t, gain=0.6, pan=pan))
                    t += 1.2
            elif act in ("punch", "kick"):
                t = 0.25
                while t < s["duration"]:
                    clips.append(dict(audio=A.synth_sfx("punch", seed=int(t * 10)), start=st + t, gain=0.7, pan=pan))
                    t += 0.7
            elif act == "celebrate":
                clips.append(dict(audio=A.synth_sfx("boing"), start=st + 0.1, gain=0.4, pan=pan))
            if a.get("transform_to"):
                clips.append(dict(audio=A.synth_sfx("transform"), start=st + a.get("transform_at", s["duration"] / 2) - 0.3, gain=0.8))
        for fx in s["effects"]:
            name = A.EFFECT_SFX.get(fx["type"])
            if not name:
                continue
            fst = st + fx.get("start", 0)
            if name in A.LOOPING:
                clips.append(dict(audio=A.synth_sfx(name, dur=s["duration"] - fx.get("start", 0)), start=fst, gain=0.5))
            elif fx["type"] == "lightning":
                t = 0.0
                while t < s["duration"]:
                    clips.append(dict(audio=A.synth_sfx("thunder", seed=int(t)), start=fst + t + 0.05, gain=0.8))
                    t += fx.get("period", 2.0)
            else:
                clips.append(dict(audio=A.synth_sfx(name), start=fst, gain=0.6))
        if s is not spec["scenes"][0] and spec["transition_duration"]:
            clips.append(dict(audio=A.synth_sfx("whoosh"), start=st, gain=0.35))
    music = A.synth_music(spec.get("mood", "happy"), total + 0.5, seed=spec["title"]) if spec.get("music", True) else None
    _log(cb, "audio", 0.8, "mezclando voces, efectos y música")
    mix = A.mix_timeline(total, clips, music, music_gain=spec.get("music_gain", 0.4))
    path = out / "audio" / "mezcla.wav"
    A.write_wav(path, mix)
    if music is not None:
        A.write_wav(out / "audio" / "musica.wav", music)
    return path


def write_srt(spec, path):
    def ts(t):
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s % 1) * 1000):03d}"
    n = 1
    lines = []
    chars = {c["id"]: c["name"] for c in spec["characters"]}
    for s in spec["scenes"]:
        for d in s["dialogue"]:
            a = s["start"] + d["start"]
            lines += [str(n), f"{ts(a)} --> {ts(a + d['duration'])}", f"{chars[d['character']]}: {d['text']}", ""]
            n += 1
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def storyboard(spec, out: Path, quality="preview"):
    r = SceneRenderer(spec, quality)
    thumbs = []
    for s in spec["scenes"]:
        for k in (0.15, 0.6):
            T = s["start"] + s["duration"] * k
            thumbs.append((s, r.at(T, int(T * spec["fps"]))))
    tw = 360 if r.W >= r.H else 200
    th = int(tw * r.H / r.W)
    cols = 4 if r.W >= r.H else 6
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * (tw + 16) + 16, rows * (th + 46) + 70), (245, 243, 238))
    d = ImageDraw.Draw(sheet)
    d.text((16, 18), f"Storyboard — {spec['title']}", fill=(30, 30, 30), font=font(28))
    for i, (s, im) in enumerate(thumbs):
        x, y = 16 + (i % cols) * (tw + 16), 70 + (i // cols) * (th + 46)
        sheet.paste(im.resize((tw, th)), (x, y))
        acts = ", ".join(f"{a['action']}" for a in s["actors"])
        d.text((x, y + th + 4), f"{s['id']} · {s['background']} · {s['camera']['type']}", fill=(60, 60, 60), font=font(13, False))
        d.text((x, y + th + 22), acts[:48], fill=(110, 110, 110), font=font(12, False))
    sheet.save(out / "storyboard.jpg", quality=90)


def render_project(spec: dict, out_dir=None, quality=None, cb=None, preview_only=False) -> dict:
    t0 = time.time()
    quality = quality or spec.get("quality", "hd")
    out = Path(out_dir) if out_dir else PROJECTS_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{slugify(spec.get('title', 'proyecto'))}"
    spec = prepare(spec, out, cb)
    if spec.get("engine") == "3d":
        from .blender_bridge import render_3d
        return render_3d(spec, out, quality, cb)
    _log(cb, "storyboard", 0.0, "creando storyboard")
    storyboard(spec, out)
    if preview_only:
        _save_spec(spec, out)
        return {"dir": str(out), "storyboard": str(out / "storyboard.jpg")}
    silent = out / "video_sin_audio.mp4"
    n = render_frames_to_video(spec, silent, quality, cb)
    audio_path = build_audio(spec, out, cb)
    final = out / "final.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(audio_path), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(final)], check=True)
    silent.unlink(missing_ok=True)
    write_srt(spec, out / "subtitulos.srt")
    from .exporter import gif_preview, thumbnail
    thumbnail(final, out / "miniatura.jpg", at=min(2.5, spec["total_duration"] / 2))
    gif_preview(final, out / "vista_previa.gif")
    from .qc import check_video
    report = check_video(final, expected_duration=spec["total_duration"], expect_audio=True)
    (out / "qc_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    _save_spec(spec, out)
    _log(cb, "listo", 1.0, f"{final} ({n} frames, {time.time() - t0:.1f}s)")
    return {"dir": str(out), "video": str(final), "frames": n, "seconds": round(time.time() - t0, 1), "qc": report,
            "duration": spec["total_duration"]}


def _save_spec(spec, out):
    clean = json.loads(json.dumps(spec, default=str))
    for s in clean["scenes"]:
        for d in s["dialogue"]:
            d.pop("visemes", None)
    (out / "project.json").write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
