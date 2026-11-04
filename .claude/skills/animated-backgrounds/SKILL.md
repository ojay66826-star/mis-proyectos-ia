---
name: animated-backgrounds
description: Fondos animados en bucle perfecto (manchas fluidas, degradados, partículas, rejilla retro) y escenarios con paralaje y nubes en movimiento para personajes, streams, webs y presentaciones. Úsala para 'fondo animado', 'background', 'fondo en movimiento', 'fondo para stream'.
---

# Fondos animados

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `seamless-loop-animation`, `motion-graphics`, `3d-environment-animation`

`animated_background` produce loops matemáticamente perfectos (todas las funciones con periodo = duración): `blobs`, `gradient`, `particles`, `grid`. Los escenarios del motor 2D (15 tipos × 3 horas del día) tienen capas de paralaje y nubes animadas.

## Cuándo usar esta Skill

- Fondos de stream/presentación/web.
- Escenarios para animaciones.

## Principios profesionales

- Fondo subordinado al contenido: menos contraste y saturación.
- Movimiento lento (periodos ≥ 6 s).
- Bucle invisible.
- Paleta coherente con la marca.

## Procedimiento paso a paso

1. Elige tipo y paleta: `python -m studio background blobs --palette pastel --duration 8`.
2. Para escenarios: `background` en el project.json + cámara `pan` para paralaje.
3. Exporta MP4 o GIF/WebM según destino.

## Comandos del estudio

```bash
python -m studio background blobs --palette pastel --duration 8 -o fondo.mp4
python -m studio background grid --palette neon --format 9:16
python -m studio export fondo.mp4 --preset webm
```

## Ejemplo completo

Fondo para OBS: `background particles --palette oscuro --duration 10` → WebM VP9 ligero en bucle.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| animated_background | loops perfectos | ✅ motor propio del estudio |
| backgrounds.py | 15 escenarios con paralaje | ✅ motor propio del estudio |
| CSS/GSAP | fondos web nativos | ✅ instalado y probado |

## Control de calidad

- [ ] Bucle sin salto.
- [ ] No distrae del contenido.
- [ ] Peso de archivo adecuado.

## Errores comunes y cómo evitarlos

- Fondos muy saturados detrás de texto.
- Duraciones no enteras en GIF pueden saltar.

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
