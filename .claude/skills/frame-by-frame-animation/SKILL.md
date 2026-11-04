---
name: frame-by-frame-animation
description: Animación tradicional dibujo por dibujo: poses clave, intercalados, hojas de exposición y exportación de secuencias PNG. Úsala para 'frame a frame', 'animación tradicional', 'dibujado a mano', 'flipbook', o cuando haya que intervenir frames individuales.
---

# Animación frame a frame

**Categoría:** Animación 2D · **Skills relacionadas:** `2d-animation`, `sprite-animation`, `stop-motion`, `animation-workflow`

El estudio puede trabajar frame a frame de dos formas: (1) exportando cada frame del motor a PNG para retocarlo en Krita/Photoshop y re-ensamblarlo con FFmpeg, y (2) componiendo secuencias PNG propias (dibujos del usuario) en un video con timing controlado (on ones/twos).

## Cuándo usar esta Skill

- El usuario aporta dibujos propios o quiere retocar frames.
- Se pide estética 'hecha a mano', boiling lines o flipbook.

## Principios profesionales

- Primero keys (poses extremas), luego breakdowns, luego intercalados.
- Animar 'on twos' (12 dibujos/s) da el look tradicional; 'on ones' para acciones rápidas.
- Hoja de exposición: lista de qué dibujo va en cada frame y cuánto dura.
- Line boil (ligero temblor) da vida a holds largos.

## Procedimiento paso a paso

1. Extrae frames: `ffmpeg -i final.mp4 frames/%04d.png`.
2. Retoca/dibuja en Krita (Animación → Importar secuencia) u OpenToonz.
3. Re-ensambla a 12 fps duplicando frames para 24 fps: `ffmpeg -framerate 12 -i frames/%04d.png -r 24 -pix_fmt yuv420p out.mp4`.
4. Añade el audio original: `python -m studio export … ` o `ffmpeg -i out.mp4 -i audio/mezcla.wav -c:v copy -c:a aac final.mp4`.
5. Para line boil en el motor, usa `style: paper` o `stopmotion` (temblor por frame).

## Comandos del estudio

```bash
ffmpeg -i projects/<…>/final.mp4 -vf fps=12 frames/%04d.png          # exportar a 12 fps
ffmpeg -framerate 12 -i frames/%04d.png -r 24 -c:v libx264 -pix_fmt yuv420p dibujado.mp4
python -m studio loop dibujado.mp4                                          # flipbook en bucle
```

## Ejemplo completo

«Tengo 8 dibujos de un pájaro volando, anímalos»: renombrar `pajaro_0001.png…0008.png`,
`ffmpeg -framerate 8 -stream_loop 3 -i pajaro_%04d.png -c:v libx264 -pix_fmt yuv420p vuelo.mp4`, y `python -m studio qc vuelo.mp4 --no-audio`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| FFmpeg | ensamblar secuencias PNG | ✅ instalado y probado |
| Krita (gratis) | dibujo frame a frame con papel cebolla | 💻 programa externo recomendado |
| OpenToonz (gratis) | hojas de exposición profesionales | 💻 programa externo recomendado |
| Blender Grease Pencil | dibujo 2D en Blender | ✅ instalado y probado |

## Control de calidad

- [ ] Numeración continua de frames sin huecos.
- [ ] Mismo tamaño en todos los frames (dimensiones pares).
- [ ] Timing coherente (on twos estable).

## Errores comunes y cómo evitarlos

- Frames de distinto tamaño rompen FFmpeg: normaliza con `-vf scale=1280:720`.
- Mezclar ones y twos sin intención produce tirones.

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
