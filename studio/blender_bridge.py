"""Puente Python -> Blender (render 3D en segundo plano)."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from .core import STUDIO_DIR, canvas_size, which

SCRIPT = STUDIO_DIR / "blender" / "scene3d.py"
ENGINES = {"rapido": "WORKBENCH", "eevee": "EEVEE", "calidad": "EEVEE", "cycles": "CYCLES"}


def _run_blender(job: dict, cb=None):
    exe = which("blender")
    if not exe:
        raise RuntimeError("Blender no está instalado (sudo apt install blender o descarga en blender.org)")
    jp = Path(job["out_dir"]) / "job3d.json"
    Path(job["out_dir"]).mkdir(parents=True, exist_ok=True)
    jp.write_text(json.dumps(job, ensure_ascii=False, default=str), encoding="utf-8")
    log = Path(job["out_dir"]) / "blender.log"
    with open(log, "w") as lf:
        r = subprocess.run([exe, "-b", "--factory-startup", "-noaudio", "-P", str(SCRIPT), "--", str(jp)], stdout=lf, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        raise RuntimeError(f"Blender falló; revisa {log}")
    return log


def render_3d(spec, out: Path, quality="hd", cb=None, engine=None):
    """Renderiza el proyecto completo en 3D y lo convierte en MP4 con audio."""
    from .render import _log, _save_spec, build_audio, write_srt
    t0 = time.time()
    W, H = canvas_size(spec["format"], quality if quality != "fullhd" else "hd")
    engine = ENGINES.get(engine or spec.get("render_engine", "eevee"), "EEVEE")
    frames_dir = out / "frames3d"
    job = dict(mode="scenes", width=W, height=H, fps=spec["fps"], engine=engine, samples=spec.get("samples", 64 if engine == "CYCLES" else 8),
               out_dir=str(frames_dir), characters=spec["characters"], scenes=spec["scenes"],
               glb=str(out / "personaje.glb"), save_blend=spec.get("save_blend", True), tempo=110)
    _log(cb, "blender", 0.1, f"renderizando en Blender ({engine})…")
    _run_blender(job, cb)
    # rótulos, título y subtítulos (mismo aspecto que en 2D)
    from PIL import Image
    from .render import SceneRenderer
    ov = SceneRenderer(spec, quality if quality != "fullhd" else "hd")
    for si, s in enumerate(spec["scenes"]):
        for f in sorted(frames_dir.glob(f"s{si + 1:02d}_*.png")):
            i = int(f.stem.split("_")[1]) - 1
            T = s["start"] + i / spec["fps"]
            ov.overlays(Image.open(f).convert("RGB"), T, int(T * spec["fps"])).save(f)
    clips = []
    for si, s in enumerate(spec["scenes"]):
        clip = out / f"_s{si + 1}.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(spec["fps"]), "-i", str(frames_dir / f"s{si + 1:02d}_%04d.png"),
                        "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", str(clip)], check=True)
        clips.append(clip)
    from .exporter import concat, gif_preview, thumbnail
    silent = out / "video_sin_audio.mp4"
    concat(clips, silent, "fade", spec.get("transition_duration", 0.45) or 0.01)
    for c in clips:
        c.unlink(missing_ok=True)
    audio = build_audio(spec, out, cb)
    final = out / "final.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(audio), "-c:v", "copy", "-c:a", "aac",
                    "-shortest", "-movflags", "+faststart", str(final)], check=True)
    silent.unlink(missing_ok=True)
    write_srt(spec, out / "subtitulos.srt")
    thumbnail(final, out / "miniatura.jpg", at=min(2.0, spec["total_duration"] / 2))
    gif_preview(final, out / "vista_previa.gif")
    from .qc import check_video
    rep = check_video(final, spec["total_duration"], True)
    (out / "qc_report.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    _save_spec(spec, out)
    _log(cb, "listo", 1.0, f"{final} ({time.time() - t0:.0f}s)")
    return {"dir": str(out), "video": str(final), "glb": str(out / "personaje.glb"), "qc": rep, "seconds": round(time.time() - t0, 1),
            "duration": spec["total_duration"]}


def character_3d(spec: dict, out_dir, action="dance", duration=4.0, engine="eevee", fps=24, size=(960, 960)):
    """Personaje 3D aislado: exporta GLB animado + video turntable."""
    out = Path(out_dir)
    frames = out / "turntable"
    job = dict(mode="character", width=size[0], height=size[1], fps=fps, engine=ENGINES.get(engine, "EEVEE"), samples=64 if engine == "cycles" else 8,
               out_dir=str(frames), characters=[spec], action=action, duration=duration, glb=str(out / f"{spec['id']}.glb"))
    _run_blender(job)
    vid = out / f"{spec['id']}_3d.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "turn_%04d.png"),
                    "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", str(vid)], check=True)
    return {"video": str(vid), "glb": str(out / f"{spec['id']}.glb")}
