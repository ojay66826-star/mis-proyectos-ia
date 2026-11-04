---
name: 3d-facial-animation
description: Anima caras 3D: parpadeo, apertura de boca por visemas sincronizada con la voz, mirada y expresiones mediante escalas o shape keys. Úsala para 'que hable en 3D', 'expresiones 3D', 'lip sync 3D', 'cara 3D'.
---

# Animación facial 3D

**Categoría:** Animación 3D · **Skills relacionadas:** `character-lip-sync`, `character-expressions`, `3d-rigging`

En 3D la boca escala según visemas (`VIS_OPEN`: A=1.6, O=1.4, E=1.0, U=0.9, F=0.6, M=0.15) calculados de la voz real (`audio.lipsync_track`), y los ojos/pupilas se escalan en Z para parpadear. Para caras orgánicas se recomiendan shape keys.

## Cuándo usar esta Skill

- Diálogos en escenas 3D.
- Primeros planos de personaje 3D.

## Principios profesionales

- Boca anticipa 1–2 frames al sonido.
- Parpadeo cada 3–4 s, más en nervios.
- Mirada guía la atención: el personaje mira a quien habla.
- Exagerar ligeramente la apertura en estilizado.

## Procedimiento paso a paso

1. Añade diálogo al actor en el JSON; el render 3D usa automáticamente sus visemas.
2. Para shape keys: crea claves 'A','E','O','U','M','F' y conecta con un driver al valor del visema.
3. Revisa un primer plano con cámara `zoom_in`.

## Comandos del estudio

```bash
python -m studio make "Un robot 3D saluda y dice hola a sus amigos" --3d --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"actors": [{"character": "robot", "action": "talk", "emotion": "happy", "from": [0.5, 0.82]}],
 "dialogue": [{"character": "robot", "text": "¡Hola! Soy un robot muy simpático."}], "camera": {"type": "zoom_in"}}
```

## Ejemplo completo

Primer plano 3D hablando: escena con `camera: zoom_in`, actor `talk` y una línea; el render keyframea la boca por frame.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender shape keys / drivers | caras orgánicas | ✅ instalado y probado |
| Rhubarb Lip Sync (open source) | visemas precisos desde audio | 💻 programa externo recomendado |
| NVIDIA Audio2Face | facial realista | 💻 programa externo recomendado |

## Control de calidad

- [ ] Boca cerrada en silencios.
- [ ] Sin parpadeo durante gritos.
- [ ] Sincronía audio-boca ±2 frames.

## Errores comunes y cómo evitarlos

- Visemas cambiando cada frame parecen tics: el estudio elimina cambios de 1 frame.
- Voces cloud (ElevenLabs) cambian la duración: re-planificar tras generar voces.

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
