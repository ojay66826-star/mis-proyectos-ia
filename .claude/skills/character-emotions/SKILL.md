---
name: character-emotions
description: Diseña el viaje emocional del personaje a lo largo de la historia (de triste a feliz, de miedo a valentía) combinando expresión, postura, ritmo, color, música y cámara. Úsala para 'que exprese emociones', 'emotivo', 'que pase de triste a feliz', 'escena conmovedora'.
---

# Arcos emocionales de personajes

**Categoría:** Personajes · **Skills relacionadas:** `character-expressions`, `animated-storytelling`, `animation-sound-design`

Mientras `character-expressions` controla la cara, esta Skill orquesta la emoción completa: acción corporal (sad → idle lento; joy → celebrate), música (`sad`, `calm`, `happy`), hora del día (sunset para nostalgia), cámara (dolly_in en el momento clave) y efectos (hearts, sparkles, rain).

## Cuándo usar esta Skill

- Historias con giro emocional.
- Videos de mensajes (cumpleaños, ánimo, despedida).

## Principios profesionales

- Mostrar, no decir: la emoción en la acción antes que en el diálogo.
- Contraste: la alegría pega más tras la tristeza.
- Color y luz acompañan: fríos/oscuros → cálidos/brillantes.
- Música cambia con la emoción dominante.

## Procedimiento paso a paso

1. Escribe el arco en 3 estados (inicio → giro → final).
2. Asigna emoción + acción + entorno a cada escena.
3. Usa `emotions` dentro de una escena para el giro.
4. Elige `mood` de música acorde (o por escena con proyectos separados unidos con `concat`).

## Comandos del estudio

```bash
python -m studio make "Un pingüino triste en la nieve encuentra un amigo y se pone feliz" --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"scenes": [
 {"background": "snow", "time_of_day": "sunset", "effects": [{"type": "snow"}], "actors": [{"character": "pinguino", "action": "idle", "emotion": "sad"}]},
 {"background": "snow", "camera": {"type": "dolly_in"}, "actors": [{"character": "pinguino", "action": "idle", "emotion": "surprised",
   "emotions": [{"t": 1.5, "emotion": "happy"}]}]},
 {"background": "snow", "effects": [{"type": "hearts"}], "actors": [{"character": "pinguino", "action": "celebrate", "emotion": "joy"}]}]}
```

## Ejemplo completo

Mensaje de ánimo: personaje triste bajo la lluvia → aparece el sol (escena 2 sin lluvia, sunset) → celebra con corazones; música `calm`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D | emoción + acción + entorno | ✅ motor propio del estudio |
| Música procedural por mood | acompañamiento | ✅ motor propio del estudio |

## Control de calidad

- [ ] El cambio emocional es claro en el storyboard.
- [ ] La música no contradice la emoción.
- [ ] Ritmo más lento en momentos tristes.

## Errores comunes y cómo evitarlos

- Cambios emocionales sin causa visible confunden.
- Música alegre en escena triste.

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
