---
name: video-editing
description: Monta, corta, une, recorta, cambia velocidad, añade audio, subtítulos, texto y logos a videos con FFmpeg y las utilidades del estudio. Úsala para 'edita el video', 'une estos videos', 'corta', 'recorta', 'acelera', 'añade música/subtítulos/marca de agua'.
---

# Edición y montaje de video

**Categoría:** Videos y contenido · **Skills relacionadas:** `video-transitions`, `animation-rendering`, `animation-optimization`

Recetas FFmpeg verificadas + funciones `exporter` (concat con xfade, add_audio, export_preset, loop, upscale, interpolate) y `probe` para inspeccionar. Todo se valida al final con `python -m studio qc`.

## Cuándo usar esta Skill

- Post-producción de cualquier video del estudio o del usuario.

## Principios profesionales

- Editar sobre copias; nunca sobrescribir el original.
- Mantener fps, resolución y formato de píxel homogéneos.
- Recodificar lo mínimo (`-c copy` cuando se pueda).
- Comprobar sincronía audio/video tras cada paso.

## Procedimiento paso a paso

1. Inspecciona: `python -c "from studio.exporter import probe; print(probe('v.mp4'))"`.
2. Aplica la receta necesaria (abajo).
3. Ejecuta `qc` sobre el resultado.

## Comandos del estudio

```bash
ffmpeg -ss 2 -to 8 -i in.mp4 -c copy recorte.mp4                                  # cortar sin recodificar
ffmpeg -i in.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" rapido.mp4       # x2 velocidad
ffmpeg -i in.mp4 -i logo.png -filter_complex "overlay=W-w-24:24" marca.mp4          # marca de agua
ffmpeg -i in.mp4 -vf subtitles=subtitulos.srt subtitulado.mp4                        # quemar SRT
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih" vertical.mp4                                  # 16:9 → 9:16 (recorte)
python -c "from studio.exporter import concat; concat(['intro.mp4','ep.mp4'], 'final.mp4', 'fade', 0.4)"
```

## Ejemplo completo

«Une mi intro con el episodio y pon mi logo»: `concat` intro+episodio con fade → overlay del logo PNG → `qc` → export youtube.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| FFmpeg 6.1 | edición por comandos | ✅ instalado y probado |
| exporter.py | utilidades del estudio | ✅ motor propio del estudio |
| Kdenlive / Shotcut / DaVinci Resolve | edición visual | 💻 programa externo recomendado |

## Control de calidad

- [ ] Sin desincronía audio/video.
- [ ] Duración final esperada.
- [ ] QC aprobado.

## Errores comunes y cómo evitarlos

- `-c copy` con cortes fuera de keyframe puede dar frames congelados al inicio: recodifica si pasa.
- Concat de clips con distinto sample rate de audio.

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
