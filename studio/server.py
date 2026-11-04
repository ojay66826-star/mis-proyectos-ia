"""Servidor web de la interfaz del estudio (FastAPI).

Arranque:  python -m studio serve   ->  http://127.0.0.1:8765
Cada tarea pesada (render, imagen→video, etc.) corre en un subproceso
``python -m studio …`` independiente; el progreso se lee de su salida.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .core import PROJECTS_DIR, ROOT, slugify

app = FastAPI(title="Estudio de Animación IA")
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS = PROJECTS_DIR / "subidas"
UPLOADS.mkdir(exist_ok=True)
JOBS: dict[str, dict] = {}
PROG = re.compile(r"^\[(?P<stage>[^\]]+)\]\s+(?P<pct>\d+)%\s*(?P<msg>.*)$")


def url_for(path) -> str | None:
    if not path:
        return None
    p = Path(path).resolve()
    try:
        return "/projects/" + str(p.relative_to(PROJECTS_DIR.resolve())).replace("\\", "/")
    except ValueError:
        return None


def _run_job(job_id: str, args: list[str], out_dir: Path, outputs: list[str]):
    job = JOBS[job_id]
    job.update(status="running", started=time.time())
    log = []
    try:
        proc = subprocess.Popen([sys.executable, "-m", "studio", *args], cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, bufsize=1)
        job["pid"] = proc.pid
        for line in proc.stdout:
            line = line.rstrip()
            log.append(line)
            m = PROG.match(line)
            if m:
                job.update(stage=m["stage"], progress=int(m["pct"]), message=m["msg"])
            elif line:
                job["message"] = line[:200]
        proc.wait()
        job["log"] = log[-60:]
        if proc.returncode != 0:
            raise RuntimeError("\n".join(log[-12:]))
        files = {}
        for name in outputs:
            for f in sorted(out_dir.glob(name)):
                files[f.name] = url_for(f)
        job.update(status="done", progress=100, stage="listo", message="terminado", files=files, dir=url_for(out_dir))
        qc = out_dir / "qc_report.json"
        if qc.exists():
            job["qc"] = json.loads(qc.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        job.update(status="error", error=str(e)[-2000:])
    job["finished"] = time.time()


def start_job(kind: str, args: list[str], out_dir: Path, outputs: list[str]) -> dict:
    jid = uuid.uuid4().hex[:10]
    JOBS[jid] = dict(id=jid, kind=kind, status="queued", progress=0, stage="en cola", message="", created=time.time())
    threading.Thread(target=_run_job, args=(jid, args, out_dir, outputs), daemon=True).start()
    return JOBS[jid]


def new_dir(title: str) -> Path:
    d = PROJECTS_DIR / f"{time.strftime('%Y%m%d-%H%M%S')}-{slugify(title)}"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ------------------------------------------------------------------ API
@app.get("/api/status")
def api_status():
    from .providers import status
    return status()


@app.get("/api/options")
def api_options():
    from .audio import MOODS
    from .backgrounds import BACKGROUNDS
    from .characters import ACCESSORIES, EMOTIONS, SPECIES
    from .effects import EFFECTS
    from .exporter import PRESETS
    from .image2video import MOVES
    from .motion import ACTIONS
    from .styles import STYLES
    return dict(styles={k: {"label": v["label"], "desc": v["desc"]} for k, v in STYLES.items()},
                species={k: v["label"] for k, v in SPECIES.items()}, species_kind={k: v["kind"] for k, v in SPECIES.items()},
                backgrounds=BACKGROUNDS, effects=EFFECTS, actions=ACTIONS, emotions=EMOTIONS, accessories=ACCESSORIES,
                moods=list(MOODS), presets={k: v["desc"] for k, v in PRESETS.items()}, moves=MOVES,
                templates=sorted(p.stem for p in (ROOT / "templates" / "web").glob("*.html")),
                formats={"16:9": "YouTube / horizontal", "9:16": "TikTok / Shorts / Reels", "1:1": "Instagram cuadrado", "4:5": "Instagram vertical"})


def _plan_from(body: dict) -> dict:
    from .characters import make_character
    from .planner import plan
    chars = None
    if body.get("characters"):
        chars = [make_character(c.get("species", "mascota"), c.get("name") or None, color=c.get("color") or None,
                                accessory=c.get("accessory") or None, eyes=c.get("eyes") or None) for c in body["characters"]]
    spec = plan(body.get("prompt", ""), style=body.get("style") or None, fmt=body.get("format") or None,
                background=body.get("background") or None, characters=chars, effects=body.get("effects") or None,
                use_ai=bool(body.get("ai")), duration=body.get("duration") or None, mood=body.get("mood") or None)
    if body.get("three_d"):
        spec["engine"] = "3d"
    if body.get("voices") is False:
        spec["voices"] = False
    if body.get("music") is False:
        spec["music"] = False
    if body.get("transition"):
        spec["transition"] = body["transition"]
    return spec


@app.post("/api/plan")
def api_plan(body: dict):
    return _plan_from(body)


@app.post("/api/render")
def api_render(body: dict):
    spec = body.get("spec") or _plan_from(body)
    out = new_dir(spec.get("title", "proyecto"))
    pj = out / "project_input.json"
    pj.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    args = ["render", str(pj), "-o", str(out), "--quality", body.get("quality", "hd")]
    return start_job("animacion", args, out, ["final.mp4", "miniatura.jpg", "vista_previa.gif", "storyboard.jpg",
                                              "subtitulos.srt", "project.json", "*.glb", "characters/*.png"])


@app.post("/api/character/preview")
def api_character(body: dict):
    from .characters import character_sheet, make_character
    spec = make_character(body.get("species", "mascota"), body.get("name") or None, color=body.get("color") or None,
                          accessory=body.get("accessory") or None, eyes=body.get("eyes") or None)
    d = PROJECTS_DIR / "personajes"
    d.mkdir(exist_ok=True)
    f = d / f"{spec['id']}_{body.get('style', 'cartoon')}_{uuid.uuid4().hex[:6]}.png"
    character_sheet(spec, body.get("style", "cartoon"), f)
    f.with_suffix(".json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"sheet": url_for(f), "spec": spec}


@app.post("/api/character3d")
def api_character3d(body: dict):
    out = new_dir(f"3d-{body.get('species', 'mascota')}")
    args = ["character3d", body.get("species", "mascota"), "--action", body.get("action", "dance"), "--duration",
            str(body.get("duration", 3)), "--engine", body.get("engine", "eevee"), "-o", str(out)]
    if body.get("color"):
        args += ["--color", body["color"]]
    return start_job("personaje 3D", args, out, ["*.mp4", "*.glb"])


@app.post("/api/image")
def api_image(body: dict):
    out = new_dir("imagen-" + body.get("prompt", "")[:30])
    f = out / "imagen.png"
    args = ["image", body.get("prompt", ""), "--provider", body.get("provider", "auto"), "-o", str(f)]
    if body.get("style"):
        args += ["--style", body["style"]]
    if body.get("format"):
        args += ["--format", body["format"]]
    return start_job("imagen", args, out, ["*.png"])


@app.post("/api/img2video")
async def api_img2video(file: UploadFile = File(...), move: str = Form("zoom_in"), effects: str = Form(""),
                        style: str = Form("cinematic"), format: str = Form("16:9"), duration: float = Form(6),
                        music: str = Form("calm"), provider: str = Form("local"), prompt: str = Form("")):
    out = new_dir("img2video")
    ext = Path(file.filename or "img.png").suffix.lower() or ".png"
    src = out / f"original{ext}"
    with open(src, "wb") as fh:
        shutil.copyfileobj(file.file, fh)
    args = ["img2video", str(src), "--move", move, "--effects", effects, "--style", style, "--format", format,
            "--duration", str(duration), "--music", music, "--provider", provider, "-o", str(out / "video.mp4")]
    if prompt:
        args += ["--prompt", prompt]
    return start_job("imagen→video", args, out, ["video.mp4", "original*"])


@app.post("/api/motion")
def api_motion(body: dict):
    kind = body.get("kind", "text")
    out = new_dir(kind)
    f = out / f"{kind}.mp4"
    if kind == "text":
        args = ["text", body.get("text", "Hola"), "--mode", body.get("mode", "pop"), "--format", body.get("format", "9:16"),
                "--palette", body.get("palette", "vibrante"), "-o", str(f)]
    elif kind == "logo":
        args = ["logo", body.get("text", "Mi Marca"), "--tagline", body.get("tagline", ""), "--color", body.get("color", "#3a86ff"),
                "--format", body.get("format", "16:9"), "-o", str(f)]
    elif kind == "infographic":
        args = ["infographic", body.get("data", "A=10,B=20,C=15"), "--title", body.get("title", "Datos"),
                "--format", body.get("format", "16:9"), "-o", str(f)]
    elif kind == "background":
        args = ["background", body.get("style", "blobs"), "--format", body.get("format", "16:9"),
                "--palette", body.get("palette", "vibrante"), "-o", str(f)]
    else:
        raise HTTPException(400, "tipo desconocido")
    return start_job(kind, args, out, ["*.mp4"])


@app.post("/api/web")
def api_web(body: dict):
    tpl = body.get("template", "gsap-logo")
    out = new_dir("web-" + tpl)
    w, h = {"16:9": (1280, 720), "9:16": (720, 1280), "1:1": (960, 960)}.get(body.get("format", "16:9"), (1280, 720))
    args = ["web", tpl, "-o", str(out / f"{tpl}.mp4"), "--width", str(w), "--height", str(h), "--query", body.get("query", "")]
    if body.get("duration"):
        args += ["--duration", str(body["duration"])]
    return start_job("web", args, out, ["*.mp4"])


@app.post("/api/export")
def api_export(body: dict):
    video = _local_path(body["video"])
    preset = body.get("preset", "youtube")
    out = video.parent / "exportados"
    out.mkdir(exist_ok=True)
    cmd = body.get("op", "export")
    target = out / f"{video.stem}_{preset if cmd == 'export' else cmd}.mp4"
    if cmd == "export":
        args = ["export", str(video), "--preset", preset, "-o", str(target)]
    elif cmd == "upscale":
        args = ["upscale", str(video), "--factor", "2", "-o", str(target)]
    elif cmd == "interpolate":
        args = ["interpolate", str(video), "--fps", "60", "-o", str(target)]
    elif cmd == "loop":
        args = ["loop", str(video), "-o", str(target)]
    else:
        raise HTTPException(400, "operación desconocida")
    return start_job(cmd, args, out, [target.stem + ".*"])


def _local_path(url: str) -> Path:
    if not url.startswith("/projects/"):
        raise HTTPException(400, "ruta inválida")
    p = (PROJECTS_DIR / url[len("/projects/"):]).resolve()
    if PROJECTS_DIR.resolve() not in p.parents:
        raise HTTPException(400, "ruta fuera de proyectos")
    return p


@app.get("/api/jobs/{jid}")
def api_job(jid: str):
    if jid not in JOBS:
        raise HTTPException(404, "trabajo no encontrado")
    return {k: v for k, v in JOBS[jid].items() if k != "log"} | {"log_tail": JOBS[jid].get("log", [])[-8:]}


@app.get("/api/jobs")
def api_jobs():
    return sorted(({k: v for k, v in j.items() if k != "log"} for j in JOBS.values()), key=lambda j: -j["created"])[:30]


@app.get("/api/projects")
def api_projects():
    items = []
    for d in sorted(PROJECTS_DIR.iterdir(), reverse=True):
        if not d.is_dir() or d.name in ("subidas", "personajes", "sueltos"):
            continue
        vids = sorted(d.glob("*.mp4"))
        if not vids:
            continue
        thumb = d / "miniatura.jpg"
        title = d.name
        pj = d / "project.json"
        if pj.exists():
            try:
                title = json.loads(pj.read_text(encoding="utf-8")).get("title", title)
            except Exception:  # noqa: BLE001
                pass
        items.append(dict(name=d.name, title=title, video=url_for(vids[0]), thumb=url_for(thumb) if thumb.exists() else None,
                          files={f.name: url_for(f) for f in d.iterdir() if f.is_file()}))
    return items[:100]


@app.get("/api/projects/{name}/zip")
def api_zip(name: str):
    from .exporter import zip_project
    d = (PROJECTS_DIR / name).resolve()
    if PROJECTS_DIR.resolve() not in d.parents or not d.is_dir():
        raise HTTPException(404)
    z = zip_project(d, PROJECTS_DIR / f"{name}.zip")
    return FileResponse(z, filename=z.name)


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html")


@app.exception_handler(Exception)
async def err(_, exc):
    return JSONResponse({"error": str(exc)}, status_code=500)


app.mount("/projects", StaticFiles(directory=PROJECTS_DIR), name="projects")
app.mount("/web", StaticFiles(directory=ROOT / "web"), name="web")
app.mount("/templates", StaticFiles(directory=ROOT / "templates"), name="templates")
if (ROOT / "node_modules").exists():
    app.mount("/node_modules", StaticFiles(directory=ROOT / "node_modules"), name="node_modules")
