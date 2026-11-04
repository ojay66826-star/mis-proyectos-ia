---
name: animation-storyboarding
description: Crea storyboards y animatics: viñetas por escena con fondo, acciones y cámara, hoja de contacto automática, timing por plano y animatic de baja resolución para validar antes del render final. Úsala para 'storyboard', 'guion gráfico', 'animatic', 'planificar las escenas visualmente'.
---

# Storyboard de animación

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-scripting`, `scene-composition`, `animation-workflow`

`render.storyboard()` genera `storyboard.jpg`: dos fotogramas por escena (15 % y 60 % de su duración) con etiqueta de escena, fondo, cámara y acciones. `--storyboard-only` lo crea sin renderizar el video; `--quality preview` produce un animatic rápido (media resolución).

## Cuándo usar esta Skill

- Antes de cualquier render largo.
- Para aprobar una historia con el usuario.

## Principios profesionales

- Un panel por cambio de idea/plano.
- Indicar movimiento (cámara y personajes).
- Timing anotado por panel.
- Validar legibilidad: ¿se entiende la historia solo con los paneles?

## Procedimiento paso a paso

1. `python -m studio make "<idea>" --storyboard-only` (o `plan` + `render --quality preview`).
2. Abre `storyboard.jpg` y revisa composición y continuidad.
3. Ajusta `project.json` (posiciones, cámaras, duraciones).
4. Animatic: `render --quality preview` y revisa `vista_previa.gif`.

## Comandos del estudio

```bash
python -m studio make "Un robot y una niña exploran el espacio" --storyboard-only
python -m studio render projects/<…>/project.json --quality preview
```

## Ejemplo completo

Aprobación con cliente: entregar `storyboard.jpg` + animatic preview; tras feedback, render final.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| render.storyboard | hoja de contacto | ✅ motor propio del estudio |
| Storyboarder (Wonder Unit, gratis) | storyboard dibujado | 💻 programa externo recomendado |
| Krita | paneles a mano | 💻 programa externo recomendado |

## Control de calidad

- [ ] Todas las escenas presentes.
- [ ] Continuidad de personajes y dirección de mirada.
- [ ] Duraciones razonables.

## Errores comunes y cómo evitarlos

- Aprobar solo con texto: siempre mostrar el storyboard.
- Ignorar la regla de 180° entre paneles.

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
