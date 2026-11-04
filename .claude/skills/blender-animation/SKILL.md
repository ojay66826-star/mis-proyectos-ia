---
name: blender-animation
description: Automatiza Blender desde línea de comandos: scripts bpy, render headless, Grease Pencil, keyframes, modificadores, exportación GLB/FBX, y depuración de errores típicos (EGL, OIDN, numpy). Úsala para 'usa Blender', 'script de Blender', 'render en Blender', '.blend'.
---

# Animación con Blender (automatización bpy)

**Categoría:** Animación 3D · **Skills relacionadas:** `3d-animation`, `animation-rendering`, `3d-modeling`

Blender está instalado y probado en el estudio (Blender 4.0.2 (headless) con EEVEE por software; Cycles sin denoiser en la build de Ubuntu). `studio/blender_bridge.py` lanza `blender -b --factory-startup -noaudio -P scene3d.py -- job.json`, registra `blender.log` y convierte frames a video.

## Cuándo usar esta Skill

- Cualquier tarea que requiera Blender.
- Diagnosticar fallos de render 3D.

## Principios profesionales

- Siempre `--factory-startup` para resultados reproducibles.
- Pasar parámetros por JSON tras `--`.
- Guardar `.blend` de cada escena para edición manual posterior.
- Revisar `blender.log` ante cualquier fallo.

## Procedimiento paso a paso

1. Escribe el script bpy (ver `studio/blender/scene3d.py` como referencia).
2. Ejecuta `blender -b --factory-startup -P script.py -- args`.
3. Si falla EGL: instala `libegl1 libgl1-mesa-dri` (render por software).
4. Si falla glTF por numpy: `apt install python3-numpy`.
5. Si falla Cycles por OIDN: desactiva denoising (por defecto en el estudio).

## Comandos del estudio

```bash
blender --version
blender -b --factory-startup -noaudio -P studio/blender/scene3d.py -- projects/<…>/frames3d/job3d.json
blender -b archivo.blend -E BLENDER_EEVEE -s 1 -e 48 -a              # render de un .blend existente
```

## Ejemplo completo

Re-renderizar una escena editada a mano: abrir `escena_1.blend`, ajustar, guardar, y `blender -b escena_1.blend -a`; luego `ffmpeg -framerate 24 -i s01_%04d.png …`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender 4.0.2 | 3D completo | ✅ instalado y probado |
| Grease Pencil | 2D dentro de Blender | ✅ instalado y probado |
| Blender oficial (blender.org) | OIDN, GPU, versión más reciente | 💻 programa externo recomendado |

## Control de calidad

- [ ] `blender.log` sin 'Error:'.
- [ ] Número de PNG = duración × fps.
- [ ] Colores correctos (AgX).

## Errores comunes y cómo evitarlos

- Python de Blender ≠ Python del estudio: no importes PIL/numpy del proyecto dentro de bpy.
- Rutas relativas en Blender usan `//`.

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
