---
name: character-lip-sync
description: Sincroniza la boca de los personajes con la voz: TTS por personaje, extracción de envolvente de amplitud, mapeo de letras a visemas (A, E, O, U, M, F, X) y suavizado. Úsala para 'que hable', 'lip sync', 'sincronizar boca', 'doblaje'.
---

# Sincronización labial (lip-sync)

**Categoría:** Personajes · **Skills relacionadas:** `character-dialogue`, `3d-facial-animation`, `animation-sound-design`

`audio.lipsync_track(text, wav, fps)` combina el texto (vocales y labiales del español) con la energía real del audio: si el RMS cae por debajo del umbral la boca se cierra. Funciona con voces de espeak-ng y también con archivos de voz propios o de ElevenLabs.

## Cuándo usar esta Skill

- Cualquier diálogo.
- Doblar un audio grabado por el usuario.

## Principios profesionales

- La boca se cierra en M/B/P y en silencios.
- Vocales abiertas (A, O) en sílabas acentuadas.
- Evitar cambios de 1 frame (el estudio los filtra).
- Voces distintas por personaje (tono y timbre).

## Procedimiento paso a paso

1. Escribe el diálogo en `dialogue` (máx. ~12 palabras por línea).
2. Render: el estudio genera la voz, calcula visemas y anima.
3. Voz propia (grabada o de ElevenLabs): añade a la línea `"audio_file": "ruta/voz.mp3"`; el estudio la usa en lugar del TTS y calcula los visemas con ese audio.
4. Para visemas de máxima precisión instala Rhubarb Lip Sync y usa su salida.

## Comandos del estudio

```bash
python -m studio make "Un robot explica en el aula cómo funciona el sol" --quality preview
python -c "from studio.audio import tts, lipsync_track; tts('Hola, ¿cómo estás?', 'v.wav'); print(lipsync_track('Hola, ¿cómo estás?', 'v.wav', 24))"
# voz propia en project.json: {"character": "manzana", "text": "Hola a todos", "audio_file": "mi_voz.mp3"}
```

## Ejemplo completo

«Haz que la manzana diga mi texto»: añadir `{"character":"manzana","text":"<texto>"}` a la escena; el visema por frame queda en el proyecto y el video incluye subtítulos.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| espeak-ng | TTS local en español (es-419) | ✅ instalado y probado |
| lipsync_track | visemas desde texto + audio | ✅ motor propio del estudio |
| Rhubarb Lip Sync | visemas profesionales | 💻 programa externo recomendado |
| ElevenLabs / OpenAI TTS | voces naturales (STUDIO_TTS=elevenlabs) | 🔑 requiere clave API |
| Wav2Lip / SadTalker | lip-sync sobre caras reales | 💻 programa externo recomendado |

## Control de calidad

- [ ] Boca cerrada cuando no hay voz.
- [ ] Desfase audio-boca ≤ 2 frames.
- [ ] Subtítulos coinciden con lo dicho.

## Errores comunes y cómo evitarlos

- Textos con números o siglas se leen raro: escríbelos con letras.
- Frases sin puntuación suenan monótonas en espeak.

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
