"""Genera .claude/skills/<nombre>/SKILL.md a partir de los datos de scripts/skills/data_*.py.

Uso:  python scripts/skills/build.py
Los SKILL.md generados son la fuente que lee Claude Code; este script solo
facilita mantener un formato homogéneo. Puedes editar los SKILL.md a mano.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / ".claude" / "skills"

CATEGORIES = {
    "data_2d": "Animación 2D",
    "data_3d": "Animación 3D",
    "data_characters": "Personajes",
    "data_vfx": "Efectos visuales",
    "data_video": "Videos y contenido",
    "data_styles": "Estilos especiales",
    "data_motion": "Diseño y movimiento",
    "data_production": "Producción profesional",
}

COMMON_PIPELINE = """## Cómo encaja en el estudio (trabajo en equipo entre Skills)

El estudio sigue un único pipeline y **todas las Skills comparten el mismo proyecto JSON** (`project.json`), así que se combinan sin conversiones:

```
idea → animation-scripting → character-design → animation-storyboarding → scene-composition
     → (animación 2D/3D + personajes + efectos) → animation-sound-design → video-editing
     → animation-rendering → animation-quality-control → animation-optimization / exportación
```

- Orquestador general: Skill `animation-workflow` (decide qué Skills intervienen y en qué orden).
- Motor: `python -m studio …` (ver `docs/CLI.md`). Interfaz: `python -m studio serve` → http://127.0.0.1:8765
- Salida estándar de un proyecto: `projects/<fecha>-<titulo>/` con `final.mp4`, `storyboard.jpg`, `miniatura.jpg`,
  `vista_previa.gif`, `subtitulos.srt`, `characters/*_sheet.png`, `audio/*.wav`, `project.json`, `qc_report.json`.
"""

COMMON_RULES = """## Reglas del estudio

1. **Primero lo local y gratuito** (motor 2D, Blender, FFmpeg, espeak-ng, Three.js, GSAP, Lottie, Remotion). Usa APIs de pago
   solo si el usuario lo pide o si la calidad exigida lo requiere, y avisa antes de gastar créditos.
2. **Nunca inventes resultados**: ejecuta el comando, revisa el archivo generado (abre un frame o el storyboard) y reporta
   rutas reales. Si algo requiere una clave que no existe (`python -m studio doctor`), dilo y ofrece la alternativa local.
3. **Consistencia de personajes**: reutiliza siempre la ficha JSON del personaje (mismo `id`, `color`, `species`, `accessory`).
4. **No subas secretos**: las claves viven en `.env` (ignorado por git).
5. Termina con `python -m studio qc <video>` y comunica qué pasó y qué no.
"""


def load(mod_name):
    spec = importlib.util.spec_from_file_location(mod_name, HERE / f"{mod_name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SKILLS


def bullet(items):
    return "\n".join(f"- {x}" for x in items)


def numbered(items):
    return "\n".join(f"{i}. {x}" for i, x in enumerate(items, 1))


def render(name, d, category):
    tools = "\n".join(f"| {t[0]} | {t[1]} | {t[2]} |" for t in d["tools"])
    related = ", ".join(f"`{r}`" for r in d["related"])
    parts = [
        "---",
        f"name: {name}",
        f"description: {d['description']}",
        "---",
        "",
        f"# {d['title']}",
        "",
        f"**Categoría:** {category} · **Skills relacionadas:** {related}",
        "",
        d["intro"].strip(),
        "",
        "## Cuándo usar esta Skill",
        "",
        bullet(d["when"]),
        "",
        "## Principios profesionales",
        "",
        bullet(d["principles"]),
        "",
        "## Procedimiento paso a paso",
        "",
        numbered(d["steps"]),
        "",
        "## Comandos del estudio",
        "",
        "```bash",
        d["commands"].strip(),
        "```",
        "",
    ]
    if d.get("spec"):
        parts += ["## Fragmento de proyecto (project.json)", "", "```json", d["spec"].strip(), "```", ""]
    parts += [
        "## Ejemplo completo",
        "",
        d["example"].strip(),
        "",
        "## Herramientas recomendadas",
        "",
        "| Herramienta | Uso | Estado en el estudio |",
        "|---|---|---|",
        tools,
        "",
        "## Control de calidad",
        "",
        "\n".join(f"- [ ] {x}" for x in d["qc"]),
        "",
        "## Errores comunes y cómo evitarlos",
        "",
        bullet(d["pitfalls"]),
        "",
        COMMON_PIPELINE,
        COMMON_RULES,
    ]
    return "\n".join(parts)


EXPECTED = 80
REQUIRED = ["title", "description", "intro", "when", "principles", "steps", "commands", "example", "tools", "qc", "pitfalls", "related"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    allskills = {}
    for mod, cat in CATEGORIES.items():
        for name, d in load(mod).items():
            allskills[name] = (d, cat)
    problems = []
    for name, (d, cat) in allskills.items():
        for k in REQUIRED:
            if not d.get(k):
                problems.append(f"{name}: falta {k}")
        for r in d.get("related", []):
            if r not in allskills:
                problems.append(f"{name}: skill relacionada inexistente '{r}'")
    if len(allskills) != EXPECTED:
        problems.append(f"se esperaban {EXPECTED} skills y hay {len(allskills)}")
    if problems:
        print("\n".join(problems))
        return 0
    for mod, cat in CATEGORIES.items():
        skills = load(mod)
        for name, d in skills.items():
            folder = OUT / name
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "SKILL.md").write_text(render(name, d, cat), encoding="utf-8")
            total += 1
    print(f"{total} Skills generadas en {OUT}")
    return total


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
