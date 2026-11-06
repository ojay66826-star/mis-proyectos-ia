"""Montaje de planos ya generados (video IA, clips propios) en un corto terminado.

Une los clips en orden (corte seco o fundido por plano), los normaliza a la misma
resolución/fps, añade cartela de título sobre el primer plano y cartela final,
música de fondo procedural que baja sola bajo los diálogos (ducking por
sidechain), fundidos de entrada/salida y sonoridad para redes (-14 LUFS).

    python -m studio assemble plano1.mp4 plano2.mp4 … --title "Mi corto" \
        --end "Fin" --music happy --fade-into 9 -o final.mp4
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from . import audio as A
from .core import font


def _probe(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(p)],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    has_a = any(s["codec_type"] == "audio" for s in d["streams"])
    return float(d["format"]["duration"]), has_a


def _card(text, sub, W, H, out, bg=False):
    """Cartela PNG transparente (título) o sobre negro (final)."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255 if bg else 0))
    d = ImageDraw.Draw(im)
    f = font(int(H * 0.085))
    tw = d.textlength(text, font=f)
    y = H * (0.40 if bg else 0.70)
    if not bg:  # sombra suave para leer sobre la imagen
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text(((W - tw) / 2 + 4, y + 5), text, font=f, fill=(0, 0, 0, 200))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(H * 0.008)))
    d.text(((W - tw) / 2, y), text, font=f, fill=(255, 248, 230, 255), stroke_width=max(2, int(H * 0.004)),
           stroke_fill=(70, 40, 20, 255))
    if sub:
        f2 = font(int(H * 0.035), False)
        sw = d.textlength(sub, font=f2)
        d.text(((W - sw) / 2, y + f.size * 1.35), sub, font=f2, fill=(255, 240, 220, 235))
    im.save(out)
    return out


def assemble(clips, out, title=None, subtitle=None, end_text=None, music="happy", music_gain=0.18, fade_into=(),
             width=1920, height=1080, fps=24, xfade=0.6, end_secs=2.5, srt=None, work=None) -> dict:
    clips = [Path(c) for c in clips]
    out = Path(out)
    work = Path(work) if work else out.parent / "_montaje"
    work.mkdir(parents=True, exist_ok=True)
    W, H = width, height
    # 1) normaliza cada plano (misma resolución, fps, audio estéreo 48k; silencio si no trae audio)
    norm, durs = [], []
    for i, c in enumerate(clips):
        d, has_a = _probe(c)
        n = work / f"n{i + 1:02d}.mp4"
        vf = f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={fps},format=yuv420p,setsar=1"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(c)]
        if not has_a:
            cmd += ["-f", "lavfi", "-t", f"{d:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        cmd += ["-vf", vf, "-af" if has_a else "-filter:a", "aresample=48000,aformat=channel_layouts=stereo",
                "-map", "0:v", "-map", "0:a" if has_a else "1:a", "-c:v", "libx264", "-crf", "16", "-preset", "medium",
                "-c:a", "pcm_s16le", "-t", f"{d:.3f}", str(n.with_suffix(".mov"))]
        subprocess.run(cmd, check=True)
        norm.append(n.with_suffix(".mov"))
        durs.append(d)
    # 2) cartela final sobre negro
    if end_text:
        card = _card(end_text, None, W, H, work / "final_card.png", bg=True)
        e = work / "nfin.mov"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-t", f"{end_secs}", "-i", str(card),
                        "-f", "lavfi", "-t", f"{end_secs}", "-i", "anullsrc=r=48000:cl=stereo",
                        "-vf", f"fps={fps},format=yuv420p,fade=t=in:st=0:d=0.6,fade=t=out:st={end_secs - 0.6}:d=0.6",
                        "-c:v", "libx264", "-crf", "16", "-c:a", "pcm_s16le", "-shortest", str(e)], check=True)
        norm.append(e)
        durs.append(end_secs)
    # 3) unión: corte seco salvo los planos marcados (fundido cruzado hacia ese plano)
    fade_into = {int(x) for x in fade_into}
    inputs, fc = [], []
    for p in norm:
        inputs += ["-i", str(p)]
    for i in range(len(norm)):  # misma base de tiempo en todas las entradas (xfade/concat lo exigen)
        fc.append(f"[{i}:v]fps={fps},setpts=PTS-STARTPTS,settb=AVTB[iv{i}]")
        fc.append(f"[{i}:a]asetpts=PTS-STARTPTS[ia{i}]")
    vlast, alast, t = "[iv0]", "[ia0]", durs[0]
    for i in range(1, len(norm)):
        shot_no = i + 1
        fade = (shot_no in fade_into) or (end_text and i == len(norm) - 1)
        if fade:
            off = t - xfade
            fc.append(f"{vlast}[iv{i}]xfade=transition=fade:duration={xfade}:offset={off:.3f}[v{i}]")
            fc.append(f"{alast}[ia{i}]acrossfade=d={xfade}[a{i}]")
            t = t + durs[i] - xfade
        else:
            fc.append(f"{vlast}{alast}[iv{i}][ia{i}]concat=n=2:v=1:a=1[v{i}][a{i}]")
            t = t + durs[i]
        vlast, alast = f"[v{i}]", f"[a{i}]"
    total = t
    # título sobre el primer plano con fundido
    if title:
        card = _card(title, subtitle, W, H, work / "title_card.png")
        inputs += ["-loop", "1", "-t", "6", "-i", str(card)]
        k = len(norm)
        fc.append(f"[{k}:v]fps={fps},format=rgba,settb=AVTB,fade=t=in:st=0.6:d=0.8:alpha=1,fade=t=out:st=4.2:d=0.8:alpha=1[tc]")
        fc.append(f"{vlast}[tc]overlay=0:0:eof_action=pass[vt]")
        vlast = "[vt]"
    fc.append(f"{vlast}fade=t=in:st=0:d=0.8[vout]")
    # 4) música procedural con ducking bajo diálogos/efectos de los planos
    if music:
        mus = A.synth_music(music, total + 1.0, seed=title or "montaje")
        mpath = work / "musica.wav"
        A.write_wav(mpath, mus)
        inputs += ["-i", str(mpath)]
        m = len(norm) + (1 if title else 0)
        fc.append(f"[{m}:a]aresample=48000,volume={music_gain},afade=t=in:d=1.5,afade=t=out:st={max(0, total - 2.5):.2f}:d=2.5[mus]")
        fc.append(f"{alast}asplit=2[dlg][key]")
        fc.append("[mus][key]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=400[mduck]")
        fc.append("[dlg][mduck]amix=inputs=2:duration=first:normalize=0[mix]")
        alast = "[mix]"
    fc.append(f"{alast}loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-t", f"{total:.3f}", str(out)]
    subprocess.run(cmd, check=True)
    res = dict(video=str(out), duration=round(total, 2), clips=len(clips))
    if srt:
        res["srt"] = str(srt)
    return res
