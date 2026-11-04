---
name: character-transformations
description: Transforma un personaje en otro (o cambia de forma) con anticipación, destello, partículas mágicas, escalado elástico y sonido de transformación. Úsala para 'se transforma en', 'se convierte en', 'metamorfosis', 'cambio de forma', 'transformación mágica'.
---

# Transformaciones de personajes

**Categoría:** Personajes · **Skills relacionadas:** `magic-effects`, `fantasy-animation`, `particle-effects`

Un actor con `transform_to: <especie>` y `transform_at: <segundos>` cambia de ficha en ese instante: el render escala el personaje (+25 % elástico) durante ±0.3 s, añade un destello blanco difuminado y el audio inserta el arpegio `transform`. Combínalo con `magic`/`sparkles` anclados al personaje.

## Cuándo usar esta Skill

- Magia, superhéroes, evoluciones, gags de cambio.
- Revelaciones (de oruga a mariposa conceptual).

## Principios profesionales

- Anticipación: concentrar energía 0.5–1 s antes.
- Ocultar el cambio en el pico del destello.
- Mantener el nombre y la posición para continuidad.
- Celebración o reacción después.

## Procedimiento paso a paso

1. Elige personaje origen y especie destino.
2. Añade `transform_to` y `transform_at` al actor.
3. Añade efecto `magic` con `on` = id del actor.
4. Render y verifica el destello en el instante correcto.

## Comandos del estudio

```bash
python -m studio make "Un mago se transforma en estrella con magia" --style fantasy
```

## Fragmento de proyecto (project.json)

```json
{"actors": [{"character": "mago", "action": "wave", "emotion": "excited", "from": [0.5, 0.82],
  "transform_to": "estrella", "transform_at": 2.0}],
 "effects": [{"type": "magic", "on": "mago"}, {"type": "sparkles", "on": "mago", "start": 1.0}]}
```

## Ejemplo completo

«Que la rana se convierta en príncipe»: `transform_to: "persona"` + accesorio corona en la nueva ficha (editar `make_character('persona', accessory='crown')`).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (transform_to) | cambio de ficha + destello | ✅ motor propio del estudio |
| Blender shape keys / Geometry Nodes | morph 3D | ✅ instalado y probado |

## Control de calidad

- [ ] El destello cubre el cambio.
- [ ] Sonido coincide con el destello.
- [ ] El personaje transformado conserva la posición.

## Errores comunes y cómo evitarlos

- Transformar en el primer segundo: no da tiempo a reconocer al personaje original.
- Olvidar el efecto mágico: el cambio parece un corte.

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
