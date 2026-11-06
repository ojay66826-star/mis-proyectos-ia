"""Paquete para CapCut: separa un proyecto renderizado en capas editables.

CapCut no tiene API pública, así que el puente es un paquete de archivos que se
importa a mano (o se sube a Google Drive y se abre desde el móvil):

    capcut/
      video/video_limpio.mp4     video sin título, rótulos ni subtítulos (y sin audio)
      video/video_con_texto.mp4  el final.mp4 original, como referencia
      audio/voces.wav            solo diálogos
      audio/efectos.wav          solo efectos de sonido
      audio/musica.wav           solo música (con el ducking de la mezcla)
      audio/mezcla.wav           voces + efectos + música
      audio/voces_sueltas/       cada línea de diálogo por separado
      subtitulos.srt             para "Subtítulos > Importar" en CapCut
      personajes/*.png           cada personaje en varias expresiones, fondo transparente
      LEEME.txt                  cómo montarlo en CapCut
    <proyecto>_capcut.zip        todo lo anterior en un zip

Las pistas de audio comparten la misma escala, así que voces + efectos + música
suman exactamente la mezcla original.
"""
from __future__ import annotations

import copy
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np

from . import audio as A

EXPRESSIONS = ["neutral", "happy", "joy", "sad", "angry", "surprised", "scared", "love"]
ACTIONS = ["idle", "wave", "jump", "dance", "celebrate"]


def _log(msg):
    print(f"[capcut] {msg}", flush=True)


def _project_dir(src) -> Path:
    p = Path(src)
    d = p if p.is_dir() else p.parent
    if not (d / "project.json").exists():
        raise FileNotFoundError(f"No encuentro project.json en {d}: el preset capcut necesita la carpeta de un proyecto "
                                "renderizado por el estudio (o su final.mp4).")
    return d


def _resolve_audio(path, project_dir: Path):
    """Las rutas de project.json son absolutas; si el proyecto se movió, se busca en audio/."""
    if not path:
        return None
    p = Path(path)
    if p.exists():
        return p
    alt = project_dir / "audio" / p.name
    return alt if alt.exists() else None


def load_spec(project_dir: Path) -> dict:
    spec = json.loads((project_dir / "project.json").read_text(encoding="utf-8"))
    fps = int(spec["fps"])
    for s in spec["scenes"]:
        for d in s["dialogue"]:
            wav = _resolve_audio(d.get("audio"), project_dir)
            d["audio"] = str(wav) if wav else None
            if wav:
                d["visemes"] = A.lipsync_track(d["text"], wav, fps)
            else:
                d["visemes"] = ["A" if (i // 3) % 2 else "E" for i in range(int(d.get("duration", 1) * fps))]
    return spec


# ---------------------------------------------------------------- audio
def audio_stems(spec, out: Path) -> dict:
    from .render import audio_clips
    total = spec["total_duration"]
    clips, music = audio_clips(spec)
    voice = [c for c in clips if c.get("kind") == "voice"]
    sfx = [c for c in clips if c.get("kind") != "voice"]
    gain = spec.get("music_gain", 0.4)
    v = A.mix_timeline(total, voice, None, normalize=False)
    e = A.mix_timeline(total, sfx, None, normalize=False)
    # música con el mismo ducking que la mezcla: (voces + música ducked) - voces
    m = (A.mix_timeline(total, voice, music, music_gain=gain, normalize=False) - v) if music is not None else np.zeros_like(v)
    full = v + e + m
    k = max(1.0, (np.max(np.abs(full)) or 1) / 0.95)  # misma escala que mix_timeline
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    present = dict(voces=bool(voice), efectos=bool(sfx), musica=music is not None, mezcla=True)
    for name, buf in (("voces", v), ("efectos", e), ("musica", m), ("mezcla", full)):
        if not present[name]:
            continue
        files[name] = out / f"{name}.wav"
        A.write_wav(files[name], (buf / k).astype(np.float32))
    loose = out / "voces_sueltas"
    names = {c["id"]: c["name"] for c in spec["characters"]}
    for si, s in enumerate(spec["scenes"]):
        for li, d in enumerate(s["dialogue"]):
            if d.get("audio"):
                loose.mkdir(exist_ok=True)
                t = s["start"] + d["start"]
                shutil.copy(d["audio"], loose / f"{t:07.2f}s_{names.get(d['character'], d['character'])}_e{si + 1}l{li + 1}.wav")
    return files


# ---------------------------------------------------------------- video
def clean_video(spec, out_path: Path, quality=None, project_dir: Path | None = None) -> tuple[Path, bool]:
    """Re-renderiza sin capas de texto. Devuelve (ruta, limpio?). En 3D usa el final sin audio."""
    from .render import render_frames_to_video
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if spec.get("engine") == "3d":
        src = project_dir / "final.mp4"
        subprocess_ff("-i", src, "-an", "-c:v", "copy", out_path)
        return out_path, False
    clean = copy.deepcopy(spec)
    clean["subtitles"] = False
    clean["show_title"] = False
    for s in clean["scenes"]:
        s["caption"] = None
    render_frames_to_video(clean, out_path, quality or _quality_of(spec, project_dir))
    return out_path, True


def _quality_of(spec, project_dir) -> str:
    """Calidad con la que se renderizó final.mp4 (para que el video limpio tenga la misma resolución)."""
    from .core import canvas_size
    from .exporter import probe
    final = project_dir / "final.mp4" if project_dir else None
    if final and final.exists():
        info = probe(final)
        for q in ("preview", "hd", "fullhd"):
            if canvas_size(spec["format"], q) == (info["width"], info["height"]):
                return q
    return spec.get("quality", "hd")


def subprocess_ff(*args):
    from .exporter import ff
    ff(*args)


# ---------------------------------------------------------------- personajes
def character_pngs(spec, out: Path, height=720) -> list[Path]:
    from .characters import render_character
    from .motion import pose_for
    from .styles import char_style
    out.mkdir(parents=True, exist_ok=True)
    style = char_style(spec["style"])
    files = []
    for c in spec["characters"]:
        items = [(e, pose_for("idle", 0.0, emotion=e)) for e in EXPRESSIONS]
        items += [(a, pose_for(a, 0.35, emotion="happy")) for a in ACTIONS if a != "idle"]
        for label, pose in items:
            im, _ = render_character(c, pose, height, style)
            box = im.getbbox()
            if box:
                im = im.crop(box)
            # render_character trabaja sobremuestreado: se baja a la altura pedida
            if im.height > height:
                im = im.resize((max(1, round(im.width * height / im.height)), height), resample=1)
            f = out / f"{_safe(c['name'])}_{label}.png"
            im.save(f)
            files.append(f)
    return files


def _safe(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name).strip("_") or "personaje"


# ---------------------------------------------------------------- paquete
README = """PAQUETE PARA CAPCUT — {title}
{rule}
Duración: {dur:.1f} s · {w}x{h} · {fps} fps

CÓMO MONTARLO (CapCut escritorio o móvil)
1. Nuevo proyecto → Importar → video/video_limpio.mp4 (pista principal).
   {clean_note}
2. Importa como audio, cada uno en su pista y empezando en 0:00:
     audio/voces.wav · audio/efectos.wav · audio/musica.wav
   Juntas suenan igual que la mezcla original. Si no quieres tocar el audio,
   usa solo audio/mezcla.wav.
   En voces_sueltas/ está cada frase por separado; el nombre empieza por el
   segundo exacto donde va (p. ej. 0003.20s_… → 0:03.20).
3. Texto → Subtítulos → Importar archivo local → subtitulos.srt
   (en móvil, si no aparece la opción, usa "Subtítulos automáticos" sobre voces.wav).
4. Superposición → personajes/*.png para stickers, miniaturas o escenas extra
   (fondo transparente).
5. Exporta desde CapCut. Referencia del original: video/video_con_texto.mp4

Generado por el Estudio de Animación IA (python -m studio export --preset capcut).
"""


def capcut_package(src, out=None, quality=None, make_zip=True) -> dict:
    project_dir = _project_dir(src)
    out = Path(out) if out else project_dir / "capcut"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    _log("cargando proyecto")
    spec = load_spec(project_dir)

    _log("pistas de audio separadas")
    stems = audio_stems(spec, out / "audio")

    _log("video limpio (sin título, rótulos ni subtítulos)")
    vid, is_clean = clean_video(spec, out / "video" / "video_limpio.mp4", quality, project_dir)
    if (project_dir / "final.mp4").exists():
        shutil.copy(project_dir / "final.mp4", out / "video" / "video_con_texto.mp4")

    srt = project_dir / "subtitulos.srt"
    if srt.exists() and srt.stat().st_size:
        shutil.copy(srt, out / "subtitulos.srt")
    else:
        from .render import write_srt
        write_srt(spec, out / "subtitulos.srt")

    _log("personajes en PNG transparente")
    pngs = character_pngs(spec, out / "personajes")
    for sheet in (project_dir / "characters").glob("*_sheet.png"):
        shutil.copy(sheet, out / "personajes" / sheet.name)

    from .exporter import probe
    info = probe(vid)
    (out / "LEEME.txt").write_text(README.format(
        title=spec["title"], rule="=" * (22 + len(spec["title"])), dur=spec["total_duration"], w=info["width"],
        h=info["height"], fps=spec["fps"],
        clean_note="Ya no lleva textos encima: añádelos y edítalos en CapCut." if is_clean else
        "Proyecto 3D: este video conserva los textos del render (no se puede re-renderizar sin ellos aquí)."),
        encoding="utf-8")

    result = dict(dir=str(out), video=str(vid), clean=is_clean, stems={k: str(v) for k, v in stems.items()},
                  subtitles=str(out / "subtitulos.srt"), characters=len(pngs))
    if make_zip:
        z = project_dir / f"{project_dir.name}_capcut.zip"
        with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(out.rglob("*")):
                if f.is_file():
                    zf.write(f, Path("capcut") / f.relative_to(out))
        result["zip"] = str(z)
    _log(f"listo: {out}")
    return result
