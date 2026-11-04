---
name: animation-upscaling
description: Aumenta resolución y fluidez: upscaling Lanczos + nitidez, Real-ESRGAN (anime/video) si está instalado, interpolación de frames a 60 fps (minterpolate) y restauración de clips IA de baja resolución. Úsala para 'mejorar calidad', 'subir resolución', 'upscale', '4K', '60 fps', 'más fluido'.
---

# Upscaling e interpolación

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-optimization`, `ai-video-generation`, `animation-rendering`

`exporter.upscale(factor, method)` con `lanczos` (siempre disponible) o `realesrgan` (requiere el binario `realesrgan-ncnn-vulkan` y GPU Vulkan, modelo realesr-animevideov3 ideal para animación); `exporter.interpolate(fps)` usa `minterpolate` con compensación de movimiento (MCI, AOBMC).

## Cuándo usar esta Skill

- Clips IA a 480–720p que hay que llevar a 1080p/4K.
- Animaciones a 12–24 fps que se quieren a 60 fps.

## Principios profesionales

- Mejor renderizar a la resolución final si el contenido es del estudio (fullhd).
- Upscale IA para contenido externo o generado por IA.
- Interpolación no conviene en estilos de 12 fps intencionales (stop-motion, anime on twos).
- Revisar artefactos en bordes y texto.

## Procedimiento paso a paso

1. Contenido propio: re-render en `fullhd`.
2. Externo: `python -m studio upscale clip.mp4 --factor 2 --method lanczos` (o `realesrgan`).
3. Fluidez: `python -m studio interpolate clip.mp4 --fps 60`.
4. QC y comparación lado a lado.

## Comandos del estudio

```bash
python -m studio upscale clip_ia.mp4 --factor 2
python -m studio upscale clip_ia.mp4 --factor 4 --method realesrgan       # si está instalado
python -m studio interpolate projects/<…>/final.mp4 --fps 60
```

## Ejemplo completo

Clip de IA de 720p → `upscale --factor 2` (1440p) → `export --preset youtube` (1080p con más detalle) → `interpolate` opcional.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| FFmpeg Lanczos + unsharp | upscale clásico | ✅ instalado y probado |
| minterpolate | interpolación | ✅ instalado y probado |
| Real-ESRGAN ncnn (open source) | upscale IA | 💻 programa externo recomendado |
| RIFE / FILM | interpolación IA | 💻 programa externo recomendado |

## Control de calidad

- [ ] Sin halos ni sobre-nitidez.
- [ ] Interpolación sin 'morphing' en movimientos rápidos.
- [ ] Audio intacto.

## Errores comunes y cómo evitarlos

- minterpolate es lento y produce artefactos en cortes de escena.
- Upscale ×4 de material muy comprimido amplifica artefactos.

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
