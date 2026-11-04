---
name: youtube-animation
description: Produce animaciones para YouTube: horizontales 16:9 1080p, Shorts 9:16, intro/outro con mascota, miniatura llamativa, capítulos y subtítulos SRT. Úsala para 'para YouTube', 'video de YouTube', 'YouTube Shorts', 'intro para mi canal', 'miniatura'.
---

# Animación para YouTube (videos y Shorts)

**Categoría:** Videos y contenido · **Skills relacionadas:** `short-video-animation`, `mascot-animation`, `animation-optimization`

Entregables: `final.mp4` → preset `youtube` (1920×1080, CRF 18, AAC 192k, faststart) o `youtube_shorts` (1080×1920), `miniatura.jpg` (extraída del momento clave; se puede regenerar), `subtitulos.srt` para subir como CC y sonoridad ≈ -14 LUFS verificada por QC.

## Cuándo usar esta Skill

- El destino es YouTube.

## Principios profesionales

- Miniatura: personaje con emoción fuerte + 3–4 palabras grandes.
- Intro ≤ 5 s; valor en los primeros 15 s.
- Subtítulos SRT (mejoran alcance).
- Audio normalizado ≈ -14 LUFS.

## Procedimiento paso a paso

1. Render en `fullhd` 16:9 (o 9:16 para Shorts).
2. Exporta preset y sube con el `.srt`.
3. Miniatura personalizada: `python -m studio image "<personaje> sorprendido, fondo colorido" --provider local` y añade texto.
4. Intro/outro: Skill `mascot-animation` + `animated-logos`.

## Comandos del estudio

```bash
python -m studio make "Clase educativa: un robot explica en el aula los planetas" --quality fullhd
python -m studio export projects/<…>/final.mp4 --preset youtube
python -m studio make "Un gato hace un truco de magia" --format 9:16 && python -m studio export <final.mp4> --preset youtube_shorts
```

## Ejemplo completo

Episodio de 45 s para canal infantil: historia de 4 escenas en fullhd, SRT, miniatura, intro de mascota de 4 s concatenada (`exporter.concat`).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| exporter presets youtube/youtube_shorts | codificación recomendada | ✅ motor propio del estudio |
| qc (ebur128) | sonoridad | ✅ instalado y probado |
| YouTube Studio | publicación | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] 1080p, 24/30 fps, H.264 + AAC.
- [ ] SRT sincronizado.
- [ ] Miniatura 1280×720 legible en pequeño.

## Errores comunes y cómo evitarlos

- Subir el MP4 'hd' 720p en vez de exportar 1080p.
- Música con copyright de terceros: usa la del estudio (procedural, libre).

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
