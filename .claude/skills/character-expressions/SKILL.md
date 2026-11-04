---
name: character-expressions
description: Controla expresiones faciales: neutral, feliz, alegría, triste, enojado, sorprendido, asustado, enamorado, dormido, emocionado y confundido, con cejas, párpados, pupilas, boca, rubor, lágrimas, sudor y venas. Úsala para 'expresión', 'cara de…', 'que ponga cara triste/feliz'.
---

# Expresiones faciales de personajes

**Categoría:** Personajes · **Skills relacionadas:** `character-emotions`, `character-lip-sync`, `character-design`

Cada emoción modifica 6 rasgos: tamaño de ojos y pupilas, párpados (sleepy, angry), ángulo de cejas, forma de boca, extras (rubor, lágrima, gota de sudor, vena de enfado) y, en `excited`/`love`, pupilas en forma de estrella o corazón.

## Cuándo usar esta Skill

- Reacciones de personajes.
- Primeros planos emotivos.
- Hojas de expresiones para referencia.

## Principios profesionales

- La expresión empieza en las cejas y los ojos, la boca confirma.
- Transición de emoción con un pequeño 'take' (sorpresa) intermedio.
- Contraste emocional entre personajes en la misma escena.
- Exagerar en estilo cartoon, sutilizar en realista.

## Procedimiento paso a paso

1. Asigna `emotion` al actor o una lista `emotions` con tiempos.
2. Combina con una acción coherente (sad + idle, joy + celebrate).
3. Para ver todas: `python -m studio character <especie>` (fila 2 y 3 de la hoja).

## Comandos del estudio

```bash
python -m studio make "Un oso feliz, luego sorprendido y después enamorado" --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"character": "oso", "action": "idle", "emotion": "happy",
 "emotions": [{"t": 0, "emotion": "happy"}, {"t": 1.6, "emotion": "surprised"}, {"t": 3.2, "emotion": "love"}]}
```

## Ejemplo completo

El planificador detecta varias emociones en el texto («feliz, luego sorprendido y enamorado») y crea una escena con fondo de estudio y cambios cada 1.6 s.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Rig facial procedural | 11 emociones | ✅ motor propio del estudio |
| Blender shape keys | expresiones 3D | ✅ instalado y probado |
| Live2D | rig facial 2D avanzado | 💻 programa externo recomendado |

## Control de calidad

- [ ] La emoción se reconoce en miniatura.
- [ ] Sin cambios de emoción en mitad de una palabra.
- [ ] Extras (lágrima/sudor) no tapan los ojos.

## Errores comunes y cómo evitarlos

- Cambiar emoción cada <0.5 s parece glitch.
- `joy` cierra los ojos: no la uses en planos donde deba mirar a algo.

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
