---
name: animation-sound-design
description: Diseña y mezcla el audio: voces TTS por personaje, música procedural por estado de ánimo (9 moods con BPM), efectos sincronizados (pasos, saltos, golpes, magia, truenos, explosiones, lluvia, fuego), ducking bajo diálogos, normalización y stems. Úsala para 'música', 'efectos de sonido', 'voces', 'audio', 'sonido', 'mezcla'.
---

# Diseño de sonido para animación

**Categoría:** Producción profesional · **Skills relacionadas:** `character-lip-sync`, `music-video-animation`, `animation-quality-control`

`audio.py` sintetiza todo sin samples externos (libre de derechos): música con progresiones de acordes, bajo, melodía y batería por mood (happy, cute, sad, epic, spooky, dance, action, calm, fantasy); 17 SFX (whoosh, pop, boing, footstep, explosion, magic, thunder, fire, punch, splash, sparkle, rain, jump, ding, transform, energy, wind); `mix_timeline` con ducking de música bajo las voces. `build_audio` coloca SFX automáticamente según acciones y efectos.

## Cuándo usar esta Skill

- Cualquier video (el audio se genera automáticamente).
- Cambiar música, añadir una canción propia o voces profesionales.

## Principios profesionales

- Jerarquía: voz > SFX > música (ducking 55 %).
- Sincronía SFX-acción al frame.
- Música que refuerza la emoción, no la contradice.
- Sonoridad final ≈ -14 LUFS para redes, picos ≤ -1 dBFS.

## Procedimiento paso a paso

1. Elige `mood` (o deja que el planificador lo deduzca).
2. Voces: espeak local; para naturales define `STUDIO_TTS=elevenlabs|openai` + clave.
3. Renderiza; stems en `audio/` (mezcla.wav, musica.wav, voces por línea).
4. Canción propia: `music: false` + `add_audio`.
5. QC revisa LUFS y picos.

## Comandos del estudio

```bash
python -m studio make "Un monstruo tierno baila" --mood dance
python -c "from studio.audio import synth_music, write_wav; write_wav('epica.wav', synth_music('epic', 20))"
python -c "from studio.audio import synth_sfx, write_wav; write_wav('magia.wav', synth_sfx('magic'))"
```

## Ejemplo completo

Escena de tormenta: lluvia en bucle + trueno sincronizado con cada rayo + música `spooky` con drone + voz con ducking. Todo automático a partir de los efectos del JSON.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| audio.py (síntesis) | música/SFX/mezcla | ✅ motor propio del estudio |
| espeak-ng | voces locales | ✅ instalado y probado |
| sox | procesado (reverb, pitch, normalize) | ✅ instalado y probado |
| ElevenLabs / OpenAI TTS | voces naturales | 🔑 requiere clave API |
| ElevenLabs (conector) | voces/música generativas | 🔌 conector MCP (si está conectado en Claude) |
| Freesound / Pixabay Music | bancos CC | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Voces inteligibles sobre la música.
- [ ] Sin clipping.
- [ ] LUFS en rango (-24 a -8; ideal -14).

## Errores comunes y cómo evitarlos

- Música con copyright de terceros.
- SFX en bucle que no paran al acabar el efecto: usa `end`.

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
