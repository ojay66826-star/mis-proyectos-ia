"""Línea de comandos del Estudio de Animación IA.

Ejemplos:
  python -m studio make "Haz una historia con frutas animadas"
  python -m studio make "Crea una animación estilo anime de un gato que baila" --format 9:16
  python -m studio img2video foto.jpg --move zoom_in --effects sparkles
  python -m studio doctor
  python -m studio serve           # interfaz web en http://localhost:8765
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

from .core import PROJECTS_DIR, ROOT, slugify


def _out(path, default_name):
    if path:
        p = Path(path)
    else:
        d = PROJECTS_DIR / "sueltos"
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{time.strftime('%Y%m%d-%H%M%S')}-{default_name}"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def cmd_make(a):
    from .planner import plan
    from .render import render_project
    spec = plan(a.prompt, style=a.style, fmt=a.format, background=a.background, use_ai=a.ai, duration=a.duration, mood=a.mood)
    if a.three_d:
        spec["engine"] = "3d"
    if a.engine:
        spec["render_engine"] = a.engine
    if a.no_voice:
        spec["voices"] = False
    if a.transition:
        spec["transition"] = a.transition
    res = render_project(spec, a.output, quality=a.quality, preview_only=a.storyboard_only)
    print(json.dumps({k: v for k, v in res.items() if k != "qc"}, indent=2, ensure_ascii=False))
    if "qc" in res:
        print("Control de calidad:", "APROBADO" if res["qc"]["passed"] else "CON ERRORES",
              f"({res['qc']['warnings']} avisos)")


def cmd_plan(a):
    from .planner import plan
    spec = plan(a.prompt, style=a.style, fmt=a.format, background=a.background, use_ai=a.ai, duration=a.duration)
    out = Path(a.output or f"{slugify(spec['title'])}.json")
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Proyecto guardado en {out}. Edítalo y renderiza con: python -m studio render {out}")


def cmd_render(a):
    from .render import render_project
    spec = json.loads(Path(a.project).read_text(encoding="utf-8"))
    res = render_project(spec, a.output, quality=a.quality)
    print(json.dumps({k: v for k, v in res.items() if k != "qc"}, indent=2, ensure_ascii=False))


def cmd_character(a):
    from .characters import character_sheet, make_character
    spec = make_character(a.species, a.name, color=a.color, accessory=a.accessory, eyes=a.eyes)
    out = _out(a.output, f"{spec['id']}_hoja.png")
    character_sheet(spec, a.style, out)
    out.with_suffix(".json").write_text(json.dumps(spec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Hoja de personaje: {out}\nFicha (para reutilizar y mantener consistencia): {out.with_suffix('.json')}")


def cmd_character3d(a):
    from .blender_bridge import character_3d
    from .characters import make_character
    spec = make_character(a.species, a.name, color=a.color)
    out = _out(a.output, f"{spec['id']}_3d")
    out.mkdir(parents=True, exist_ok=True)
    print(json.dumps(character_3d(spec, out, a.action, a.duration, a.engine), indent=2))


def cmd_image(a):
    from .providers import generate_image
    out = _out(a.output, slugify(a.prompt) + ".png")
    if a.provider != "local":
        try:
            p = generate_image(a.prompt, out, a.width, a.height, a.seed, a.provider)
            print(f"Imagen IA: {p}")
            return
        except Exception as e:  # noqa: BLE001
            if a.provider != "auto":
                raise
            print(f"[aviso] {e}\n→ Uso el generador local (ilustración procedural).")
    from .planner import plan
    from .render import SceneRenderer, prepare
    spec = plan(a.prompt, style=a.style, fmt=a.format)
    spec["voices"] = False
    spec["show_title"] = False
    spec["subtitles"] = False
    tmp = out.parent / "_tmp_img"
    spec = prepare(spec, tmp)
    r = SceneRenderer(spec, "fullhd")
    s = spec["scenes"][0]
    img = r.at(s["start"] + min(1.0, s["duration"] / 2), 24)
    img.save(out.with_suffix(".png"))
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"Ilustración local: {out.with_suffix('.png')}")


def cmd_img2video(a):
    from .image2video import image_to_video
    out = _out(a.output, Path(a.image).stem + "_video.mp4")
    fx = [f for f in (a.effects or "").split(",") if f]
    p = image_to_video(a.image, out, a.duration, a.move, a.format, a.fps, fx, a.style, a.music or None, a.quality,
                       a.provider, a.prompt or "")
    print(f"Video: {p}")


def cmd_text(a):
    from .motiongraphics import kinetic_typography
    out = _out(a.output, "texto_animado.mp4")
    print(kinetic_typography(a.text, out, a.mode, a.duration, a.format, 30, a.palette, a.music))


def cmd_logo(a):
    from .motiongraphics import animated_logo
    out = _out(a.output, f"logo_{slugify(a.name)}.mp4")
    print(animated_logo(a.name, out, a.tagline, a.color, a.duration, a.format))


def cmd_infographic(a):
    from .motiongraphics import infographic
    data = {}
    for part in a.data.split(","):
        k, v = part.split("=")
        data[k.strip()] = float(v)
    out = _out(a.output, "infografia.mp4")
    print(infographic(data, out, a.title, a.duration, a.format, unit=a.unit))


def cmd_background(a):
    from .motiongraphics import animated_background
    out = _out(a.output, f"fondo_{a.kind}.mp4")
    print(animated_background(out, a.kind, a.duration, a.format, 30, a.palette))


def cmd_lottie(a):
    from .lottie import bouncing_character
    out = _out(a.output, "personaje.json")
    print(bouncing_character(out, a.color))


def cmd_web(a):
    tpl = Path(a.template)
    if not tpl.exists():
        tpl = ROOT / "templates" / "web" / (a.template if a.template.endswith(".html") else a.template + ".html")
    out = _out(a.output, tpl.stem + ".mp4")
    cmd = ["node", str(ROOT / "scripts" / "capture.mjs"), str(tpl), str(out), "--fps", str(a.fps), "--width", str(a.width),
           "--height", str(a.height)]
    if a.duration:
        cmd += ["--duration", str(a.duration)]
    if a.query:
        cmd += ["--query", a.query]
    subprocess.run(cmd, check=True)


def cmd_remotion(a):
    from .planner import plan
    from .remotion_bridge import render_story
    if a.source.endswith(".json") and Path(a.source).exists():
        spec = json.loads(Path(a.source).read_text(encoding="utf-8"))
    else:
        spec = plan(a.source, style=a.style, fmt=a.format)
    out = _out(a.output, slugify(spec.get("title", "historia")) + "_remotion.mp4")
    print(render_story(spec, out))


def cmd_export(a):
    from . import exporter
    out = _out(a.output, Path(a.video).stem + f"_{a.preset}.mp4")
    if a.preset == "webm":
        print(exporter.to_webm(a.video, out.with_suffix(".webm")))
    elif a.preset == "gif":
        print(exporter.gif_preview(a.video, out.with_suffix(".gif"), max_seconds=60))
    elif a.preset == "zip":
        print(exporter.zip_project(a.video))
    else:
        print(exporter.export_preset(a.video, out, a.preset))


def cmd_upscale(a):
    from .exporter import upscale
    print(upscale(a.video, _out(a.output, Path(a.video).stem + f"_x{a.factor}.mp4"), a.factor, a.method))


def cmd_interpolate(a):
    from .exporter import interpolate
    print(interpolate(a.video, _out(a.output, Path(a.video).stem + f"_{a.fps}fps.mp4"), a.fps))


def cmd_loop(a):
    from .exporter import make_loop
    print(make_loop(a.video, _out(a.output, Path(a.video).stem + "_loop.mp4"), a.crossfade))


def cmd_qc(a):
    from .qc import check_video
    rep = check_video(a.video, a.duration, not a.no_audio)
    for c in rep["checks"]:
        print(("✔" if c["ok"] else ("⚠" if c["severity"] == "warning" else "✘")), c["check"], "—", c["detail"])
    print("RESULTADO:", "APROBADO" if rep["passed"] else "FALLÓ")


def cmd_doctor(a):
    from .providers import KEYS, status
    st = status()
    print("== Herramientas locales ==")
    for k, v in st["tools"].items():
        print(f"  {'✔' if v else '✘'} {k}")
    print("== Claves de API (opcionales, en .env) ==")
    for k, v in st["keys"].items():
        print(f"  {'✔' if v else '·'} {k:22s} {KEYS[k]}")
    if a.online:
        import requests
        print("== Conectividad ==")
        for name, url in [("Pollinations (imágenes gratis)", "https://image.pollinations.ai/prompt/test?width=64&height=64&nologo=true"),
                          ("Hugging Face", "https://huggingface.co/api/models?limit=1"), ("Replicate", "https://api.replicate.com/v1/"),
                          ("ElevenLabs", "https://api.elevenlabs.io/v1/models"), ("Anthropic", "https://api.anthropic.com/v1/models")]:
            try:
                r = requests.get(url, timeout=20)
                print(f"  ✔ {name}: HTTP {r.status_code}")
            except Exception as e:  # noqa: BLE001
                print(f"  ✘ {name}: {type(e).__name__}")


def cmd_serve(a):
    import uvicorn
    print(f"Estudio en http://{a.host}:{a.port}")
    uvicorn.run("studio.server:app", host=a.host, port=a.port, reload=False)


def cmd_check_skills(a):
    d = ROOT / ".claude" / "skills"
    skills = sorted(p for p in d.iterdir() if p.is_dir())
    bad = []
    own = 0
    for s in skills:
        f = s / "SKILL.md"
        if not f.exists():
            bad.append((s.name, "falta SKILL.md"))
            continue
        txt = f.read_text(encoding="utf-8")
        head = txt.split("---")[1] if txt.startswith("---") else ""
        if not txt.startswith("---") or not re.search(rf"^name:\s*['\"]?{re.escape(s.name)}['\"]?\s*$", head, re.M):
            bad.append((s.name, "frontmatter inválido"))
        # La longitud mínima solo aplica a las Skills generadas por el estudio (scripts/skills/build.py);
        # las Skills de terceros (ver THIRD_PARTY_SKILLS.md) se instalan tal cual, sin rellenarlas.
        if "**Categoría:**" in txt:
            own += 1
            if len(txt) < 2500:
                bad.append((s.name, f"contenido corto ({len(txt)} caracteres)"))
    print(f"Skills encontradas: {len(skills)} ({own} del estudio, {len(skills) - own} de terceros)")
    for b in bad:
        print("  ✘", *b)
    print("OK" if not bad else f"{len(bad)} problema(s)")
    sys.exit(1 if bad else 0)


def main(argv=None):
    p = argparse.ArgumentParser(prog="python -m studio", description="Estudio de Animación con IA")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, fmt="16:9"):
        sp.add_argument("--style", default=None, help="cartoon, anime, pixel, minimalist, cute, cinematic, horror, fantasy, paper, clay, stopmotion, realistic, comic, retro")
        sp.add_argument("--format", default=None, help="16:9 | 9:16 | 1:1 | 4:5")
        sp.add_argument("--background", default=None)

    s = sub.add_parser("make", help="instrucción en lenguaje natural -> video terminado")
    s.add_argument("prompt")
    common(s)
    s.add_argument("--duration", type=float)
    s.add_argument("--mood")
    s.add_argument("--quality", default="hd", choices=["preview", "hd", "fullhd"])
    s.add_argument("--ai", action="store_true", help="usar Claude para escribir el guion (requiere ANTHROPIC_API_KEY)")
    s.add_argument("--3d", dest="three_d", action="store_true", help="renderizar en 3D con Blender")
    s.add_argument("--engine", choices=["rapido", "eevee", "cycles"])
    s.add_argument("--transition", choices=["fade", "wipe", "slide", "circle", "dip", "cut"])
    s.add_argument("--no-voice", action="store_true")
    s.add_argument("--storyboard-only", action="store_true")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_make)

    s = sub.add_parser("plan", help="crear el proyecto JSON sin renderizar")
    s.add_argument("prompt")
    common(s)
    s.add_argument("--duration", type=float)
    s.add_argument("--ai", action="store_true")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_plan)

    s = sub.add_parser("render", help="renderizar un proyecto JSON")
    s.add_argument("project")
    s.add_argument("--quality", default="hd", choices=["preview", "hd", "fullhd"])
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_render)

    s = sub.add_parser("character", help="hoja de personaje (poses, expresiones, visemas)")
    s.add_argument("species")
    s.add_argument("--name")
    s.add_argument("--color")
    s.add_argument("--accessory")
    s.add_argument("--eyes", choices=["round", "anime", "dot"])
    s.add_argument("--style", default="cartoon")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_character)

    s = sub.add_parser("character3d", help="personaje 3D en Blender (GLB + video)")
    s.add_argument("species")
    s.add_argument("--name")
    s.add_argument("--color")
    s.add_argument("--action", default="dance")
    s.add_argument("--duration", type=float, default=4)
    s.add_argument("--engine", default="eevee", choices=["rapido", "eevee", "cycles"])
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_character3d)

    s = sub.add_parser("image", help="generar imagen (IA si hay proveedor; si no, ilustración local)")
    s.add_argument("prompt")
    common(s)
    s.add_argument("--provider", default="auto", help="auto | local | pollinations | huggingface | openai | stability")
    s.add_argument("--width", type=int, default=1280)
    s.add_argument("--height", type=int, default=720)
    s.add_argument("--seed", type=int, default=42)
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_image)

    s = sub.add_parser("img2video", help="convertir una imagen en video")
    s.add_argument("image")
    s.add_argument("--move", default="zoom_in", help="zoom_in, zoom_out, pan_left, pan_right, pan_up, orbit, parallax, breathe")
    s.add_argument("--effects", default="", help="lista separada por comas: sparkles,rain,snow,fire,fog…")
    s.add_argument("--style", default="cinematic")
    s.add_argument("--format", default="16:9")
    s.add_argument("--duration", type=float, default=6)
    s.add_argument("--fps", type=int, default=24)
    s.add_argument("--music", default="calm")
    s.add_argument("--quality", default="hd")
    s.add_argument("--provider", default="local", choices=["local", "replicate"])
    s.add_argument("--prompt")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_img2video)

    s = sub.add_parser("text", help="tipografía cinética")
    s.add_argument("text")
    s.add_argument("--mode", default="pop", choices=["pop", "slide", "wave", "typewriter"])
    s.add_argument("--format", default="9:16")
    s.add_argument("--duration", type=float)
    s.add_argument("--palette", default="vibrante")
    s.add_argument("--music", default="dance")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_text)

    s = sub.add_parser("logo", help="logo animado")
    s.add_argument("name")
    s.add_argument("--tagline", default="")
    s.add_argument("--color", default="#3a86ff")
    s.add_argument("--duration", type=float, default=4)
    s.add_argument("--format", default="16:9")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_logo)

    s = sub.add_parser("infographic", help="infografía animada")
    s.add_argument("data", help='"Lunes=10,Martes=25,Miércoles=17"')
    s.add_argument("--title", default="Datos")
    s.add_argument("--unit", default="")
    s.add_argument("--duration", type=float, default=6)
    s.add_argument("--format", default="16:9")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_infographic)

    s = sub.add_parser("background", help="fondo animado en bucle perfecto")
    s.add_argument("kind", choices=["blobs", "gradient", "grid", "particles"])
    s.add_argument("--duration", type=float, default=6)
    s.add_argument("--format", default="16:9")
    s.add_argument("--palette", default="vibrante")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_background)

    s = sub.add_parser("lottie", help="generar animación Lottie JSON")
    s.add_argument("--color", default="#e53935")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_lottie)

    s = sub.add_parser("web", help="capturar plantilla web (GSAP/CSS/SVG/Lottie/Three.js) a MP4")
    s.add_argument("template", help="gsap-logo | svg-css-character | lottie-player | kinetic-type | interactive | three-scene | ruta.html")
    s.add_argument("--duration", type=float)
    s.add_argument("--fps", type=int, default=30)
    s.add_argument("--width", type=int, default=1280)
    s.add_argument("--height", type=int, default=720)
    s.add_argument("--query", default="")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_web)

    s = sub.add_parser("remotion", help="montar un proyecto (o instrucción) como video React con Remotion")
    s.add_argument("source", help="project.json o instrucción en texto")
    s.add_argument("--style")
    s.add_argument("--format")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_remotion)

    s = sub.add_parser("export", help="exportar para plataformas")
    s.add_argument("video")
    s.add_argument("--preset", default="youtube", help="youtube, youtube_shorts, tiktok, instagram, web, whatsapp, webm, gif, zip")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_export)

    s = sub.add_parser("upscale", help="aumentar resolución")
    s.add_argument("video")
    s.add_argument("--factor", type=int, default=2)
    s.add_argument("--method", default="lanczos", choices=["lanczos", "bicubic", "realesrgan"])
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_upscale)

    s = sub.add_parser("interpolate", help="interpolar frames (más fluidez)")
    s.add_argument("video")
    s.add_argument("--fps", type=int, default=60)
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_interpolate)

    s = sub.add_parser("loop", help="convertir en bucle perfecto")
    s.add_argument("video")
    s.add_argument("--crossfade", type=float, default=0.5)
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_loop)

    s = sub.add_parser("qc", help="control de calidad de un video")
    s.add_argument("video")
    s.add_argument("--duration", type=float)
    s.add_argument("--no-audio", action="store_true")
    s.set_defaults(fn=cmd_qc)

    s = sub.add_parser("doctor", help="comprobar herramientas y claves")
    s.add_argument("--online", action="store_true")
    s.set_defaults(fn=cmd_doctor)

    s = sub.add_parser("serve", help="interfaz web")
    s.add_argument("--port", type=int, default=8765)
    s.add_argument("--host", default="127.0.0.1")
    s.set_defaults(fn=cmd_serve)

    s = sub.add_parser("check-skills", help="verificar las Skills")
    s.set_defaults(fn=cmd_check_skills)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
