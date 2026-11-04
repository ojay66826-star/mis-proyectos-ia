"""Prueba de humo de TODO el estudio: ejecuta cada comando real y reporta resultados.

Uso:
    python tests/smoke_test.py            # pruebas rápidas (~5-8 min en 4 núcleos)
    python tests/smoke_test.py --slow     # incluye 3D completo (Blender) y Remotion
Genera tests/resultados/REPORTE.md (no se versiona) con lo que pasó y lo que no.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "resultados"
SLOW = "--slow" in sys.argv
PY = [sys.executable, "-m", "studio"]
results = []


def run(name, args, expect=None, slow=False, timeout=900):
    if slow and not SLOW:
        results.append((name, "omitida", 0, "usa --slow"))
        return
    t0 = time.time()
    try:
        r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        ok = r.returncode == 0
        detail = ""
        if ok and expect:
            for e in ([expect] if isinstance(expect, (str, Path)) else expect):
                p = Path(e)
                if not p.exists() or p.stat().st_size == 0:
                    ok, detail = False, f"no se creó {p.name}"
        if not ok and not detail:
            detail = (r.stderr or r.stdout).strip().splitlines()[-1][:160] if (r.stderr or r.stdout).strip() else f"código {r.returncode}"
        results.append((name, "OK" if ok else "FALLO", time.time() - t0, detail))
    except subprocess.TimeoutExpired:
        results.append((name, "FALLO", time.time() - t0, "tiempo agotado"))


def latest_project():
    ds = sorted((p for p in (ROOT / "projects").iterdir() if p.is_dir() and (p / "final.mp4").exists()), key=lambda p: p.stat().st_mtime)
    return ds[-1] if ds else None


def main():
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(parents=True)
    o = lambda n: str(OUT / n)  # noqa: E731
    run("doctor", PY + ["doctor"])
    run("check-skills", PY + ["check-skills"])
    run("hoja de personaje", PY + ["character", "fresa", "--name", "Fresita", "--accessory", "bow", "-o", o("fresita.png")], o("fresita.png"))
    run("plan (local)", PY + ["plan", "Haz una historia con frutas animadas", "-o", o("plan.json")], o("plan.json"))
    run("plan --ai (sin clave → local)", PY + ["plan", "Una fábula de un conejo", "--ai", "-o", o("plan_ai.json")], o("plan_ai.json"))
    prompts = [
        ("caricatura", "Crea una caricatura animada de una manzana que saluda en el parque", []),
        ("anime + magia", "Haz una animación estilo anime de una niña con magia en un castillo", []),
        ("historia frutas", "Haz una historia con frutas animadas", []),
        ("cinematográfica", "Crea una animación cinematográfica de un robot en la ciudad de noche", ["--transition", "dip"]),
        ("TikTok baile", "Crea una animación para TikTok de un plátano que baila", []),
        ("pelea + explosión", "Un perro y un gato pelean en el dojo con explosiones", []),
        ("terror", "Un fantasma asusta a un niño en un bosque embrujado", []),
        ("emociones", "Un oso feliz, luego sorprendido y después enamorado", []),
        ("transformación", "Un mago se transforma en estrella con magia", []),
        ("pixel", "Un zorro corre por el bosque", ["--style", "pixel"]),
        ("plastilina", "Un conejo camina en la nieve", ["--style", "clay"]),
        ("cómic", "Un robot salva la ciudad", ["--style", "comic"]),
    ]
    for name, p, extra in prompts:
        d = OUT / f"make_{name.split()[0]}"
        run(f"make: {name}", PY + ["make", p, "--quality", "preview", "-o", str(d)] + extra, [d / "final.mp4", d / "storyboard.jpg"])
    run("render desde JSON", PY + ["render", o("plan.json"), "--quality", "preview", "-o", o("render_json")], OUT / "render_json" / "final.mp4")
    run("imagen local", PY + ["image", "un gato astronauta en el espacio", "--provider", "local", "-o", o("img_local.png")], o("img_local.png"))
    run("imagen auto (IA si hay red/clave; si no, local)", PY + ["image", "un dragón tierno", "--provider", "auto", "-o", o("img_auto.png")], o("img_auto.png"))
    for mv in ("zoom_in", "parallax", "orbit"):
        run(f"img2video {mv}", PY + ["img2video", o("img_local.png"), "--move", mv, "--effects", "sparkles", "--duration", "3", "--quality", "preview",
                                     "-o", o(f"i2v_{mv}.mp4")], o(f"i2v_{mv}.mp4"))
    run("texto cinético", PY + ["text", "Crea animaciones increíbles", "--duration", "4", "-o", o("texto.mp4")], o("texto.mp4"))
    run("logo animado", PY + ["logo", "Estudio IA", "--tagline", "Animación", "-o", o("logo.mp4")], o("logo.mp4"))
    run("infografía", PY + ["infographic", "A=10,B=25,C=17", "--title", "Prueba", "-o", o("info.mp4")], o("info.mp4"))
    for k in ("blobs", "particles"):
        run(f"fondo en bucle {k}", PY + ["background", k, "--duration", "3", "-o", o(f"bg_{k}.mp4")], o(f"bg_{k}.mp4"))
    run("Lottie JSON", PY + ["lottie", "-o", o("lottie.json")], o("lottie.json"))
    for t in ("gsap-logo", "svg-css-character", "lottie-player", "kinetic-type", "interactive", "three-scene"):
        run(f"web: {t}", PY + ["web", t, "--duration", "1.5", "--fps", "12", "--width", "640", "--height", "360", "-o", o(f"web_{t}.mp4")], o(f"web_{t}.mp4"))
    src = OUT / "make_caricatura" / "final.mp4"
    for preset in ("tiktok", "whatsapp", "webm", "gif"):
        ext = {"webm": ".webm", "gif": ".gif"}.get(preset, ".mp4")
        run(f"export {preset}", PY + ["export", str(src), "--preset", preset, "-o", o(f"exp_{preset}.mp4")], o(f"exp_{preset}{ext}") if ext != ".mp4" else o(f"exp_{preset}.mp4"))
    run("upscale x2", PY + ["upscale", o("texto.mp4"), "--factor", "2", "-o", o("upscale.mp4")], o("upscale.mp4"))
    run("interpolar 48fps", PY + ["interpolate", o("bg_blobs.mp4"), "--fps", "48", "-o", o("interp.mp4")], o("interp.mp4"))
    run("bucle perfecto", PY + ["loop", o("bg_blobs.mp4"), "-o", o("loop.mp4")], o("loop.mp4"))
    run("QC", PY + ["qc", str(src)])
    run("personaje 3D (Blender rápido)", PY + ["character3d", "gato", "--action", "wave", "--duration", "1", "--engine", "rapido", "-o", o("gato3d")],
        [OUT / "gato3d" / "gato.glb", OUT / "gato3d" / "gato_3d.mp4"])
    run("animación 3D completa (EEVEE)", PY + ["make", "Un robot saluda en el parque", "--3d", "--duration", "3", "--quality", "preview", "-o", o("make3d")],
        OUT / "make3d" / "final.mp4", slow=True, timeout=1800)
    run("Remotion (React)", PY + ["remotion", "Un conejo tierno camina en la nieve", "-o", o("remotion.mp4")], o("remotion.mp4"), slow=True)

    ok = sum(1 for r in results if r[1] == "OK")
    fail = [r for r in results if r[1] == "FALLO"]
    lines = ["# Reporte de pruebas del estudio", "", f"Fecha: {time.strftime('%Y-%m-%d %H:%M')} · OK: {ok} · Fallos: {len(fail)} · Omitidas: {sum(1 for r in results if r[1] == 'omitida')}", "",
             "| Prueba | Resultado | Tiempo | Detalle |", "|---|---|---|---|"]
    for n, st, t, d in results:
        lines.append(f"| {n} | {'✅' if st == 'OK' else ('⏭️' if st == 'omitida' else '❌')} {st} | {t:.1f}s | {d} |")
    (OUT / "REPORTE.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
