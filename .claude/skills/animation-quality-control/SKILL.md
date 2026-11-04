---
name: animation-quality-control
description: Verifica entregas: validez del archivo, códec, dimensiones, duración, pista de audio, tramos negros, congelamientos, sonoridad (LUFS), picos, más revisión visual de frames y checklist artística. Úsala para 'revisa el video', 'control de calidad', 'QC', 'comprueba que esté bien', o al terminar cualquier render.
---

# Control de calidad (QC)

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-rendering`, `animation-optimization`, `animation-workflow`

`python -m studio qc` usa ffprobe + filtros de FFmpeg (`blackdetect`, `freezedetect`, `ebur128`) y emite `qc_report.json` (también automático tras cada render). Complementa con inspección visual: extraer 3 frames y mirarlos.

## Cuándo usar esta Skill

- Siempre al final de un render.
- Antes de publicar o entregar.

## Principios profesionales

- Automatizar lo técnico, mirar lo artístico.
- Errores bloquean; avisos se comunican.
- Verificar contra lo pedido (formato, duración, estilo).
- Nunca afirmar que algo está bien sin comprobarlo.

## Procedimiento paso a paso

1. `python -m studio qc final.mp4 --duration <esperada>`.
2. Extrae frames: `ffmpeg -ss 1 -i final.mp4 -frames:v 1 f1.png` (y a mitad/final) y revísalos.
3. Checklist artístico: personajes consistentes, sin cortes, subtítulos legibles, audio claro.
4. Corrige y repite hasta aprobar.

## Comandos del estudio

```bash
python -m studio qc projects/<…>/final.mp4
ffmpeg -loglevel error -ss 3 -i projects/<…>/final.mp4 -frames:v 1 frame_3s.png
cat projects/<…>/qc_report.json
```

## Ejemplo completo

QC de un Short: aprobado técnicamente pero subtítulo tapado por la UI de TikTok → subir subtítulos (`big` ya los coloca al 70 %) → re-render → QC final.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| qc.py (ffprobe/ebur128/blackdetect/freezedetect) | QC técnico | ✅ motor propio del estudio |
| FFmpeg | extracción de frames | ✅ instalado y probado |
| tests/ui_test.mjs | prueba end-to-end de la interfaz | ✅ instalado y probado |

## Control de calidad

- [ ] qc_report `passed: true`.
- [ ] Frames revisados visualmente.
- [ ] Requisitos del usuario cumplidos.

## Errores comunes y cómo evitarlos

- freezedetect avisa en escenas estáticas intencionales (logos): es aviso, no error.
- LUFS bajo en videos sin música (normal).

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
