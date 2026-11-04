---
name: video-transitions
description: Transiciones entre escenas y clips: fundido, a negro (dip), barrido, deslizamiento, iris circular, corte, y las 40+ transiciones xfade de FFmpeg; con whoosh sincronizado. Úsala para 'transición', 'pasar de una escena a otra', 'fundido', 'efecto de cambio de escena'.
---

# Transiciones de video

**Categoría:** Videos y contenido · **Skills relacionadas:** `video-editing`, `scene-composition`, `animation-workflow`

En el motor 2D las escenas se solapan 0.45 s y se mezclan con `transition`: `fade`, `dip`, `wipe`, `slide`, `circle` o `cut` (global o por escena). Para clips externos, `exporter.concat(videos, out, transition, dur)` usa `xfade` de FFmpeg (fade, wipeleft, slideup, circleopen, pixelize, radial, …).

## Cuándo usar esta Skill

- Cambiar de escena o unir clips.

## Principios profesionales

- La transición comunica: corte = continuidad; fundido = paso de tiempo; dip = cambio de acto; barrido/slide = energía.
- Duración 0.3–0.8 s.
- Un mismo tipo predominante por video.
- Sonido de transición sutil.

## Procedimiento paso a paso

1. Elige `transition` global (`--transition`) o por escena (`"transition": "circle"`).
2. Para clips: `concat([...], 'out.mp4', 'wipeleft', 0.5)`.
3. Revisa que la transición no corte diálogos.

## Comandos del estudio

```bash
python -m studio make "Un conejo viaja del bosque a la playa" --transition circle
python -c "from studio.exporter import concat; concat(['a.mp4','b.mp4','c.mp4'], 'unido.mp4', 'slideleft', 0.5)"
```

## Ejemplo completo

Viaje en 3 lugares con `slide` (energía), y `dip` al final antes de 'Fin'.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| render.transition | 6 transiciones nativas | ✅ motor propio del estudio |
| FFmpeg xfade | 40+ transiciones | ✅ instalado y probado |
| GSAP/Remotion | transiciones a medida | ✅ instalado y probado |

## Control de calidad

- [ ] Sin frames negros inesperados.
- [ ] El diálogo no se corta en la transición.

## Errores comunes y cómo evitarlos

- xfade requiere mismo tamaño, fps y formato de píxel en todos los clips.
- Mezclar muchos tipos distintos parece amateur.

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
