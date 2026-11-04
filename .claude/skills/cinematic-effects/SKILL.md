---
name: cinematic-effects
description: Look de cine: bandas negras (letterbox 2.39:1), gradación teal & orange, viñeta, grano de película, bloom, profundidad de campo, temblor de cámara, transiciones a negro y títulos. Úsala para 'cinematográfico', 'look de película', 'épico', 'tráiler'.
---

# Efectos cinematográficos

**Categoría:** Efectos visuales · **Skills relacionadas:** `cinematic-video`, `animation-lighting`, `3d-camera-animation`

El estilo `cinematic` aplica post-procesado por frame (numpy): grading teal en sombras y naranja en altas luces, contraste +10 %, viñeta, grano animado y letterbox; `letterbox: true/false` se puede forzar en el proyecto. Combínalo con cámara dolly/orbit, transición `dip` y música `epic`.

## Cuándo usar esta Skill

- Tráileres, intros épicas, escenas dramáticas, cortos con ambición visual.

## Principios profesionales

- Grading consistente en todo el video.
- Movimiento de cámara lento y motivado.
- Silencio antes del clímax.
- Títulos sobrios, centrados, con fundido.

## Procedimiento paso a paso

1. Planifica con `--style cinematic` y `--transition dip`.
2. Usa cámaras `dolly_in`/`pan`; evita `shake` salvo impactos.
3. Música `epic`; al final título con `python -m studio logo` o `text --mode typewriter`.
4. Exporta en `fullhd`.

## Comandos del estudio

```bash
python -m studio make "Crea una animación cinematográfica de un robot en la ciudad de noche" --style cinematic --transition dip --quality fullhd
```

## Fragmento de proyecto (project.json)

```json
{"style": "cinematic", "letterbox": true, "transition": "dip", "mood": "epic"}
```

## Ejemplo completo

Tráiler de 20 s: 4 escenas (ciudad noche dolly_in, pelea shake, explosión, título final) + música épica + grading cine.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| styles.post_process cinematic | grading + grano + letterbox | ✅ motor propio del estudio |
| DaVinci Resolve (gratis) | grading profesional | 💻 programa externo recomendado |
| LUTs .cube + FFmpeg lut3d | grading con LUT | ✅ instalado y probado |

## Control de calidad

- [ ] Negros no aplastados (detalle en sombras).
- [ ] Letterbox simétrico.
- [ ] Grano sutil (no ruido).

## Errores comunes y cómo evitarlos

- Letterbox en 9:16 resta espacio: el estudio usa barras finas en vertical.
- Grading exagerado da piel/colores irreales.

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
