---
name: ai-video-generation
description: Genera video con modelos de IA (texto→video, imagen→video) usando proveedores reales (Replicate: MiniMax, Wan, Kling, Luma…; conector ElevenLabs en Claude) o el motor local cuando no hay clave. Úsala para 'video con IA', 'genera un video realista', 'texto a video', 'Sora/Kling/Runway', 'convierte esta imagen en video con IA'.
---

# Generación de video con IA

**Categoría:** Videos y contenido · **Skills relacionadas:** `video-editing`, `animation-upscaling`, `realistic-animation`, `animation-workflow`

El estudio ofrece tres caminos: (1) **local y gratis**: motor 2D/3D e `img2video` (Ken Burns, paralaje 2.5D, efectos); (2) **Replicate** (`REPLICATE_API_TOKEN`, modelo en `REPLICATE_VIDEO_MODEL`, por defecto `minimax/video-01`) vía `providers.generate_video_replicate`; (3) si Claude tiene el **conector ElevenLabs** activo, sus herramientas `creative_generate_video`/`creative_generate_image` generan clips en la cuenta del usuario (gastan créditos: confirmar antes de videos largos). Las integraciones cloud siguen la documentación oficial pero solo se consideran verificadas tras `python -m studio doctor --online` en el equipo del usuario.

## Cuándo usar esta Skill

- Se pide realismo fotográfico o movimiento que el motor procedural no logra.
- El usuario tiene clave/créditos y acepta el coste.

## Principios profesionales

- Prompt estructurado: sujeto + acción + entorno + cámara + luz + estilo + duración.
- Para consistencia, partir de un primer frame (imagen→video) generado o renderizado por el estudio.
- Clips cortos (4–6 s) unidos en edición > un clip largo.
- Revisar derechos y políticas de cada proveedor; no usar personas reales sin permiso.

## Procedimiento paso a paso

1. Comprueba proveedores: `python -m studio doctor` (claves) y `--online` (conectividad).
2. Sin clave → camino local: `python -m studio make …` o `img2video`.
3. Con Replicate: `python -m studio img2video frame.png --provider replicate --prompt "…"`.
4. Con el conector ElevenLabs en Claude: crear un flow, generar imagen de referencia, luego video desde ella; descargar y pasar por `qc`.
5. Unir clips con `video-editing` y añadir audio del estudio.

## Comandos del estudio

```bash
python -m studio doctor --online
python -m studio image "un dragón tierno volando sobre un castillo al atardecer" --provider auto -o ref.png
python -m studio img2video ref.png --provider replicate --prompt "the dragon flaps its wings, slow cinematic push in" -o dragon_ai.mp4
python -m studio img2video ref.png --move parallax --effects sparkles -o dragon_local.mp4   # alternativa gratuita
```

## Ejemplo completo

«Convierte esta imagen en un video realista»: si hay `REPLICATE_API_TOKEN` → imagen→video con prompt de cámara; si no → `img2video --move parallax --style cinematic` y explicar al usuario qué clave haría falta para movimiento generativo.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| img2video local | Ken Burns / paralaje 2.5D | ✅ motor propio del estudio |
| Replicate API | MiniMax, Wan, Kling, Luma, etc. | 🔑 requiere clave API |
| ElevenLabs (conector) | imagen/video/voz generativos | 🔌 conector MCP (si está conectado en Claude) |
| Wan 2.x / LTX-Video / CogVideoX (open source) | texto→video local con GPU NVIDIA ≥ 12 GB | 💻 programa externo recomendado |
| ComfyUI | flujos de video IA locales | 💻 programa externo recomendado |

## Control de calidad

- [ ] Sin deformaciones graves (manos, caras).
- [ ] Duración/resolución como se pidió.
- [ ] Coste comunicado al usuario.
- [ ] QC del estudio aprobado tras añadir audio.

## Errores comunes y cómo evitarlos

- Nombres de modelos cambian con frecuencia: el modelo de Replicate es configurable por variable de entorno.
- Prometer resultados de un proveedor sin haberlo ejecutado.

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
