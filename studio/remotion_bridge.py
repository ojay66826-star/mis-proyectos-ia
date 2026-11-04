"""Puente estudio -> Remotion: monta un proyecto como video React (composición "Historia")."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from .core import ROOT, which

REMOTION = ROOT / "remotion"


def chromium_path() -> str | None:
    for p in sorted(Path("/opt/pw-browsers").glob("chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell")):
        return str(p)
    for exe in ("chromium", "chromium-browser", "google-chrome"):
        if which(exe):
            return which(exe)
    return None  # Remotion descargará su propio Chrome Headless Shell


def render_story(spec: dict, out_mp4, accent="#6d28d9") -> Path:
    """Renderiza un fotograma limpio por escena con el motor 2D y lo anima en Remotion."""
    from .planner import normalize
    from .render import SceneRenderer, prepare
    from .styles import post_process
    if not (REMOTION / "node_modules" / "remotion").exists():
        raise RuntimeError("Remotion no está instalado: cd remotion && npm install")
    spec = dict(normalize(spec), voices=False)
    work = REMOTION / "public" / "proyecto"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    spec = prepare(spec, work / "_prep")
    r = SceneRenderer(spec, "hd")
    scenes = []
    for i, s in enumerate(spec["scenes"]):
        lt = s["duration"] * 0.5
        img = post_process(r.frame(s, lt, i), spec["style"], lt, i)
        name = f"proyecto/escena_{i + 1}.jpg"
        img.save(REMOTION / "public" / name, quality=92)
        caption = s.get("caption") or (s["dialogue"][0]["text"] if s["dialogue"] else "")
        scenes.append({"image": name, "caption": caption or " ", "seconds": round(s["duration"], 2)})
    shutil.rmtree(work / "_prep", ignore_errors=True)
    props = {"title": spec["title"], "scenes": scenes, "vertical": spec["format"] == "9:16", "accent": accent}
    pf = work / "props.json"
    pf.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    cmd = ["npx", "remotion", "render", "src/index.ts", "Historia", str(Path(out_mp4).resolve()), f"--props={pf}"]
    ch = chromium_path()
    if ch:
        cmd.append(f"--browser-executable={ch}")
    subprocess.run(cmd, cwd=REMOTION, check=True)
    return Path(out_mp4)
