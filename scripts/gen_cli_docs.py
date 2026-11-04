"""Genera docs/CLI.md a partir de la ayuda real de `python -m studio`."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CMDS = ["make", "plan", "render", "character", "character3d", "image", "img2video", "text", "logo", "infographic", "background",
        "lottie", "web", "remotion", "export", "upscale", "interpolate", "loop", "qc", "doctor", "serve", "check-skills"]
out = ["# Referencia de la línea de comandos", "", "Todos los comandos se ejecutan desde la carpeta del repositorio con `python -m studio <comando>`.",
       "Los resultados se guardan en `projects/` (o en la ruta de `-o`).", ""]
for c in CMDS:
    h = subprocess.run([sys.executable, "-m", "studio", c, "--help"], cwd=ROOT, capture_output=True, text=True).stdout
    out += [f"## `{c}`", "", "```text", h.strip(), "```", ""]
(ROOT / "docs" / "CLI.md").write_text("\n".join(out), encoding="utf-8")
print("docs/CLI.md generado")
