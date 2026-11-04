---
name: animated-logos
description: Anima logotipos: trazo del contorno, monograma con rebote elástico, letras escalonadas, eslogan, destello de brillo y sonido de marca; versiones Python, GSAP y Lottie. Úsala para 'logo animado', 'animar mi logo', 'intro de marca', 'logo reveal'.
---

# Logos animados

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `motion-graphics`, `mascot-animation`, `lottie-animation`

`python -m studio logo` genera: anillo que se dibuja (0–0.9 s), disco con monograma y rebote elástico, nombre letra a letra con `out_back`, eslogan con fundido y barrido de brillo, + whoosh/ding/sparkle. La plantilla `gsap-logo.html` hace lo mismo en web (SVG + GSAP) y acepta `text`, `tag`, `color`.

## Cuándo usar esta Skill

- Intros de marca, firmas al final de videos, presentaciones.

## Principios profesionales

- Duración 2.5–5 s.
- El logo final queda estático ≥ 1 s.
- Movimiento que refleje la personalidad de la marca.
- Sonido corto y reconocible.

## Procedimiento paso a paso

1. Reúne nombre, eslogan y color HEX.
2. Versión rápida: `python -m studio logo …`.
3. Versión web/vectorial: `python -m studio web gsap-logo --query …`.
4. Si hay un logo SVG propio, sustituir el SVG de la plantilla gsap-logo y animar sus paths con stroke-dashoffset.

## Comandos del estudio

```bash
python -m studio logo "Panadería Sol" --tagline "Pan con amor desde 1990" --color "#f59e0b"
python -m studio web gsap-logo --query "text=Panadería Sol&tag=Pan con amor&color=%23f59e0b" -o logo_web.mp4
```

## Ejemplo completo

Logo para cierre de YouTube en 16:9 y 9:16; concatenado al final de cada episodio con `concat(..., 'fade', 0.4)`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| motiongraphics.animated_logo | logo reveal | ✅ motor propio del estudio |
| gsap-logo.html | logo web/SVG | ✅ instalado y probado |
| Lottie | logo vectorial para apps | ✅ motor propio del estudio |

## Control de calidad

- [ ] Logo legible y centrado.
- [ ] Colores exactos.
- [ ] Termina en reposo.

## Errores comunes y cómo evitarlos

- Monograma de iniciales poco legible con nombres de una sola palabra larga.
- Animar logos de terceros sin permiso.

## Cómo encaja en el estudio (trabajo en equipo entre Skills)

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

## Reglas del estudio

1. **Primero lo local y gratuito** (motor 2D, Blender, FFmpeg, espeak-ng, Three.js, GSAP, Lottie, Remotion). Usa APIs de pago
   solo si el usuario lo pide o si la calidad exigida lo requiere, y avisa antes de gastar créditos.
2. **Nunca inventes resultados**: ejecuta el comando, revisa el archivo generado (abre un frame o el storyboard) y reporta
   rutas reales. Si algo requiere una clave que no existe (`python -m studio doctor`), dilo y ofrece la alternativa local.
3. **Consistencia de personajes**: reutiliza siempre la ficha JSON del personaje (mismo `id`, `color`, `species`, `accessory`).
4. **No subas secretos**: las claves viven en `.env` (ignorado por git).
5. Termina con `python -m studio qc <video>` y comunica qué pasó y qué no.
