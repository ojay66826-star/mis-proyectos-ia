---
name: anime-animation
description: Crea animaciones con estética anime/manga: ojos grandes brillantes con doble reflejo, cel-shading, bloom suave, líneas de velocidad, animación 'on twos' y planos dramáticos. Úsala para 'estilo anime', 'manga', 'chibi', 'estilo japonés'.
---

# Animación estilo anime

**Categoría:** Animación 2D · **Skills relacionadas:** `character-design`, `magic-effects`, `energy-effects`, `character-fighting`

El estilo `anime` cambia los ojos de todos los personajes al tipo anime (iris degradado + dos brillos), usa contorno fino, cel-shading, saturación +15 % y bloom en altas luces. Combínalo con `speedlines`, `energy` y cámara `zoom_in`/`dolly_in` para momentos dramáticos.

## Cuándo usar esta Skill

- Peticiones 'anime', 'manga', 'chibi', 'opening de anime', 'escena de transformación'.
- Historias de magia, peleas o drama juvenil.

## Principios profesionales

- Limited animation: poses fuertes y holds; movimiento en capas (pelo, efectos) sobre poses estáticas.
- Planos de impacto: zoom rápido + speedlines + flash blanco de 1–2 frames.
- Paleta: cielos saturados, sombras con tinte frío, highlights cálidos.
- Expresiones icónicas: sudor (scared/confused), venas de enfado (angry), brillo en ojos (excited).

## Procedimiento paso a paso

1. Define el momento clave (transformación, golpe, confesión) y construye 2 escenas previas que lo preparen.
2. Planifica con `--style anime`; para niñas/niños usa `nina`/`nino`, para magia `mago` o efecto `magic`.
3. Añade `speedlines` en acciones rápidas y `energy` con `on: <id>` para auras.
4. Usa cámara `dolly_in` en el plano clave y `shake` en impactos.
5. Renderiza; revisa que los ojos anime se vean en el storyboard.

## Comandos del estudio

```bash
python -m studio make "Haz una animación estilo anime de una niña con magia en un castillo" --style anime
python -m studio character nina --eyes anime --style anime --name Sakura
```

## Fragmento de proyecto (project.json)

```json
{"style": "anime", "scenes": [{"background": "castle", "camera": {"type": "dolly_in"},
  "actors": [{"character": "sakura", "action": "wave", "emotion": "excited", "transform_to": "estrella", "transform_at": 2.0}],
  "effects": [{"type": "magic", "on": "sakura"}, {"type": "speedlines", "intensity": 0.6}]}]}
```

## Ejemplo completo

«Haz un opening de anime con un robot y un zorro peleando» → `python -m studio make "Un robot y un zorro pelean en el dojo" --style anime --format 16:9`.
Resultado: escena de tensión (idle angry), pelea con speedlines + aura de energía, explosión final y música `action`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (style anime) | ojos anime, cel-shading, bloom | ✅ motor propio del estudio |
| Stable Diffusion + LoRA anime (vía HF/Replicate) | fondos ilustrados | 🔑 requiere clave API |
| Krita + OpenToonz | anime dibujado a mano | 💻 programa externo recomendado |

## Control de calidad

- [ ] Ojos con iris y dos brillos visibles.
- [ ] Speedlines no tapan la cara.
- [ ] Momento clave con zoom o flash.

## Errores comunes y cómo evitarlos

- Abusar de speedlines en todas las escenas resta impacto.
- Fondos demasiado detallados compiten con los personajes.

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
