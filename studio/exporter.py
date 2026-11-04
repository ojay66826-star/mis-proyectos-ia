"""Exportación, optimización, upscaling, interpolación y bucles (FFmpeg)."""
from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

from .core import which

PRESETS = {
    "youtube": dict(desc="YouTube 1080p H.264 alta calidad", scale="1920:1080", crf=18, ab="192k"),
    "youtube_shorts": dict(desc="YouTube Shorts 1080x1920", scale="1080:1920", crf=19, ab="192k"),
    "tiktok": dict(desc="TikTok / Reels 1080x1920", scale="1080:1920", crf=20, ab="160k"),
    "instagram": dict(desc="Instagram post 1080x1080", scale="1080:1080", crf=20, ab="160k"),
    "web": dict(desc="Web ligero 720p (CRF 28)", scale="-2:720", crf=28, ab="96k"),
    "whatsapp": dict(desc="WhatsApp < 16 MB, 480p", scale="-2:480", crf=30, ab="64k"),
}


def ff(*args):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", *map(str, args)]
    subprocess.run(cmd, check=True)


def thumbnail(video, out, at=1.0):
    ff("-ss", at, "-i", video, "-frames:v", 1, "-q:v", 2, out)
    return Path(out)


def gif_preview(video, out, width=480, fps=12, max_seconds=8):
    pal = Path(out).with_suffix(".palette.png")
    vf = f"fps={fps},scale={width}:-1:flags=lanczos"
    ff("-t", max_seconds, "-i", video, "-vf", vf + ",palettegen=stats_mode=diff", pal)
    ff("-t", max_seconds, "-i", video, "-i", pal, "-lavfi", vf + " [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=4", out)
    pal.unlink(missing_ok=True)
    return Path(out)


def export_preset(video, out, preset="youtube"):
    p = PRESETS[preset]
    w, h = p["scale"].split(":")
    if w != "-2" and h != "-2":
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black"
    else:
        vf = f"scale={p['scale']}:flags=lanczos"
    ff("-i", video, "-vf", vf, "-c:v", "libx264", "-preset", "slow", "-crf", p["crf"], "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", p["ab"], "-movflags", "+faststart", out)
    return Path(out)


def to_webm(video, out, crf=33):
    ff("-i", video, "-c:v", "libvpx-vp9", "-b:v", 0, "-crf", crf, "-row-mt", 1, "-c:a", "libopus", "-b:a", "96k", out)
    return Path(out)


def upscale(video, out, factor=2, method="lanczos"):
    """Upscaling. 'realesrgan' usa realesrgan-ncnn-vulkan si está instalado."""
    if method == "realesrgan" and which("realesrgan-ncnn-vulkan"):
        tmp = Path(out).parent / "_frames_up"
        src = Path(out).parent / "_frames_src"
        for d in (tmp, src):
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir()
        ff("-i", video, src / "%06d.png")
        subprocess.run(["realesrgan-ncnn-vulkan", "-i", str(src), "-o", str(tmp), "-n", "realesr-animevideov3", "-s", str(factor)], check=True)
        fps = probe(video)["fps"]
        ff("-framerate", fps, "-i", tmp / "%06d.png", "-i", video, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264",
           "-crf", 18, "-pix_fmt", "yuv420p", "-c:a", "copy", out)
        shutil.rmtree(tmp)
        shutil.rmtree(src)
        return Path(out)
    ff("-i", video, "-vf", f"scale=iw*{factor}:ih*{factor}:flags={method},unsharp=5:5:0.6:5:5:0.0",
       "-c:v", "libx264", "-crf", 18, "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "copy", out)
    return Path(out)


def interpolate(video, out, fps=60):
    """Interpolación de movimiento (frame interpolation) con minterpolate."""
    ff("-i", video, "-vf", f"minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:vsbmc=1", "-c:v", "libx264", "-crf", 18,
       "-pix_fmt", "yuv420p", "-c:a", "copy", out)
    return Path(out)


def make_loop(video, out, crossfade=0.5):
    """Bucle perfecto: funde el final con el principio."""
    d = probe(video)["duration"]
    cf = min(crossfade, d / 3)
    ff("-i", video, "-filter_complex",
       f"[0:v]split[a][b];[a]trim=start={cf},setpts=PTS-STARTPTS[main];[b]trim=0:{cf},setpts=PTS-STARTPTS[head];"
       f"[main][head]xfade=transition=fade:duration={cf}:offset={d - 2 * cf}[v]",
       "-map", "[v]", "-an", "-c:v", "libx264", "-crf", 19, "-pix_fmt", "yuv420p", out)
    return Path(out)


def concat(videos, out, transition="fade", dur=0.5):
    """Une varios clips con transiciones xfade (todos deben tener el mismo tamaño/fps)."""
    if len(videos) == 1:
        shutil.copy(videos[0], out)
        return Path(out)
    durs = [probe(v)["duration"] for v in videos]
    inputs = []
    for v in videos:
        inputs += ["-i", v]
    fc, last, off = [], "[0:v]", 0.0
    for i in range(1, len(videos)):
        off += durs[i - 1] - dur
        lbl = f"[v{i}]"
        fc.append(f"{last}[{i}:v]xfade=transition={transition}:duration={dur}:offset={off:.3f}{lbl}")
        last = lbl
    ff(*inputs, "-filter_complex", ";".join(fc), "-map", last, "-c:v", "libx264", "-crf", 19, "-pix_fmt", "yuv420p", out)
    return Path(out)


def add_audio(video, audio, out, volume=1.0):
    ff("-i", video, "-i", audio, "-filter_complex", f"[1:a]volume={volume}[a]", "-map", "0:v", "-map", "[a]",
       "-c:v", "copy", "-c:a", "aac", "-shortest", out)
    return Path(out)


def probe(video) -> dict:
    import json
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(video)],
                       capture_output=True, text=True, check=True)
    data = json.loads(r.stdout)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), {})
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    return dict(duration=float(data["format"].get("duration", 0)), width=v.get("width"), height=v.get("height"),
                fps=round(float(num) / float(den or 1), 3) if float(den or 1) else 0, vcodec=v.get("codec_name"),
                acodec=a.get("codec_name") if a else None, size_bytes=int(data["format"].get("size", 0)))


def zip_project(project_dir, out=None) -> Path:
    project_dir = Path(project_dir)
    out = Path(out) if out else project_dir.with_suffix(".zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in project_dir.rglob("*"):
            if f.is_file() and "_frames" not in f.parts:
                z.write(f, f.relative_to(project_dir.parent))
    return out
