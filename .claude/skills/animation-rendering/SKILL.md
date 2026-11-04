---
name: animation-rendering
description: Renderiza con calidad y eficiencia: niveles de calidad (preview/hd/fullhd), render paralelo multinúcleo, motores 3D (Workbench/EEVEE/Cycles), codificación H.264/AAC, frames PNG, tiempos estimados y recuperación de errores. Úsala para 'renderizar', 'render final', 'exportar en 1080p', 'el render tarda/falla'.
---

# Renderizado de animación

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-optimization`, `animation-quality-control`, `blender-animation`

El motor 2D renderiza frames en paralelo (`multiprocessing`, hasta 8 procesos) y los envía por tubería a FFmpeg (libx264 CRF 19, yuv420p) sin escribir PNGs; luego mezcla audio y hace mux con faststart. Referencia medida: ~15 s de video 720p en ~80 s con 4 núcleos; preview ~4× más rápido. 3D en CPU sin GPU: EEVEE ≈ 3–6 s/frame a 640×360.

## Cuándo usar esta Skill

- Render final, cambios de calidad, problemas de rendimiento.

## Principios profesionales

- Iterar en preview, entregar en hd/fullhd.
- No recodificar varias veces (pérdida).
- yuv420p y dimensiones pares para compatibilidad.
- Registrar tiempos para estimar.

## Procedimiento paso a paso

1. Elige calidad: `--quality preview|hd|fullhd`.
2. 2D: `python -m studio render project.json --quality hd`.
3. 3D: elige `--engine rapido|eevee|cycles`; usa preview para iterar.
4. Si falla: revisa el mensaje; en 3D mira `frames3d/blender.log`.
5. Verifica con `qc`.

## Comandos del estudio

```bash
python -m studio render projects/<…>/project.json --quality fullhd
python -m studio make "<idea>" --3d --engine eevee --quality preview
tail -50 projects/<…>/frames3d/blender.log
```

## Ejemplo completo

Entrega 1080p de una historia de 30 s: preview (≈40 s) → correcciones → fullhd (≈4–5 min en 4 núcleos) → QC → export youtube.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| render.py (multiproceso) | render 2D | ✅ motor propio del estudio |
| FFmpeg libx264/libvpx-vp9 | codificación | ✅ instalado y probado |
| Blender EEVEE/Cycles | render 3D | ✅ instalado y probado |
| GPU NVIDIA + Blender oficial | render 3D 10–50× más rápido | 💻 programa externo recomendado |

## Control de calidad

- [ ] Duración y fps correctos.
- [ ] Sin frames corruptos ni negros.
- [ ] Audio sincronizado.

## Errores comunes y cómo evitarlos

- fullhd en borradores (lento).
- Disco lleno con frames 3D: borra `frames3d/*.png` tras montar si no se necesitan.

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
