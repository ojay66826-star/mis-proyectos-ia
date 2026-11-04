---
name: music-video-animation
description: Videoclips animados sincronizados con música: BPM, cortes en el beat, baile, efectos al ritmo, letras animadas y visualización; con música procedural del estudio o una canción del usuario. Úsala para 'videoclip', 'video musical', 'animación para mi canción', 'lyric video'.
---

# Videoclips animados

**Categoría:** Videos y contenido · **Skills relacionadas:** `character-dancing`, `kinetic-typography`, `animation-sound-design`

La música procedural (9 moods con BPM) sincroniza el baile automáticamente. Para una canción del usuario: detecta BPM (`sox`/`librosa` si se instala), fija `mood`/BPM, renderiza sin música (`music: false`) y mezcla la canción con `exporter.add_audio`.

## Cuándo usar esta Skill

- Canciones propias, lyric videos, visualizadores.

## Principios profesionales

- Cortes y acentos en el beat (múltiplos de 60/BPM s).
- Secciones: intro, estrofa, estribillo (más energía), puente, final.
- Letras sincronizadas y legibles.
- Paleta y efectos según el género musical.

## Procedimiento paso a paso

1. Determina BPM y estructura.
2. Duración de escenas = n compases × (4 × 60/BPM).
3. Render con `music: false` si usarás audio propio.
4. Une audio: `python -c "from studio.exporter import add_audio; add_audio('final.mp4','cancion.mp3','clip.mp4')"`.
5. Lyric video: `python -m studio text "<letra>" --mode pop` por frase.

## Comandos del estudio

```bash
python -m studio make "Las frutas bailan en una fiesta en el escenario" --mood dance --duration 30
python -c "from studio.exporter import add_audio; add_audio('projects/<…>/final.mp4', 'mi_cancion.mp3', 'videoclip.mp4')"
```

## Fragmento de proyecto (project.json)

```json
{"mood": "dance", "music": false, "scenes": [{"duration": 7.74}, {"duration": 7.74}, {"duration": 7.74}]}
```

## Ejemplo completo

Canción a 124 BPM: compás = 1.935 s; escenas de 4 compases (7.74 s); render sin música; añadir la canción; cortes caen en el beat.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Música procedural (audio.synth_music) | pistas libres de derechos | ✅ motor propio del estudio |
| sox | análisis/edición de audio | ✅ instalado y probado |
| librosa / aubio | detección de BPM | 💻 programa externo recomendado |

## Control de calidad

- [ ] Cortes alineados al beat (±1 frame).
- [ ] Letras sincronizadas.
- [ ] Sin clipping al mezclar la canción.

## Errores comunes y cómo evitarlos

- Canciones con copyright sin licencia.
- Escenas que no son múltiplo del compás desincronizan.

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
