---
name: animation-optimization
description: Optimiza para cada plataforma: presets (YouTube, Shorts, TikTok, Instagram, web, WhatsApp), WebM VP9, GIF con paleta, tamaño de archivo, faststart, velocidad de render y peso de assets web (Lottie, SVG). Úsala para 'exportar', 'comprimir', 'que pese menos', 'formato para Instagram/WhatsApp', 'GIF'.
---

# Optimización y exportación

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-rendering`, `animation-upscaling`, `youtube-animation`

`exporter.PRESETS`: youtube (1920×1080 CRF 18), youtube_shorts y tiktok (1080×1920), instagram (1080×1080), web (720p CRF 28), whatsapp (480p CRF 30) con pad negro si la proporción no coincide; además `to_webm`, `gif_preview` (palettegen+paletteuse) y `zip_project`.

## Cuándo usar esta Skill

- Antes de publicar.
- Archivos demasiado grandes o incompatibles.

## Principios profesionales

- Exportar desde el master de mayor calidad.
- Elegir la proporción nativa de la plataforma (evitar barras).
- faststart para streaming web.
- GIF solo para clips cortos (≤ 8 s); preferir MP4/WebM.

## Procedimiento paso a paso

1. Elige preset por destino.
2. `python -m studio export final.mp4 --preset <preset>`.
3. Comprueba peso/duración con `qc`.
4. Para web, también WebM: `--preset webm`.

## Comandos del estudio

```bash
python -m studio export projects/<…>/final.mp4 --preset tiktok
python -m studio export projects/<…>/final.mp4 --preset whatsapp
python -m studio export projects/<…>/final.mp4 --preset webm
python -m studio export projects/<…>/final.mp4 --preset gif
python -m studio export projects/<…> --preset zip
```

## Ejemplo completo

Mismo video para 4 redes: render 16:9 fullhd para YouTube; render 9:16 aparte (recomposición) para TikTok/Shorts; preset instagram 1:1 para el feed; whatsapp para compartir.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| exporter.py presets | codificación por plataforma | ✅ motor propio del estudio |
| FFmpeg (x264, VP9, Opus, palettegen) | códecs | ✅ instalado y probado |
| HandBrake | compresión manual | 💻 programa externo recomendado |

## Control de calidad

- [ ] Reproducción correcta en móvil.
- [ ] Peso dentro de límites (WhatsApp ≤ 16 MB).
- [ ] Audio presente tras exportar.

## Errores comunes y cómo evitarlos

- Convertir 16:9 a 9:16 con pad deja barras enormes: mejor re-renderizar en 9:16.
- Recomprimir un archivo ya comprimido varias veces.

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
