---
name: animation-scripting
description: Escribe guiones para animación: logline, estructura, escenas con acción y diálogo, duración por escena, tono y público; los convierte al project.json; con planificador local o Claude (salida estructurada). Úsala para 'guion', 'escribe la historia', 'diálogos', 'script', 'idea para un video'.
---

# Guion de animación

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-storyboarding`, `story-animation`, `character-dialogue`

`planner.plan()` analiza la petición (español/inglés) detectando personajes (27 especies y grupos como 'frutas'), estilo, formato, escenario, acciones, emociones y efectos, y construye la estructura según el género (historia, baile, pelea, magia, terror, acción simple). Con `--ai` y ANTHROPIC_API_KEY, Claude escribe el guion con JSON Schema estricto y el estudio lo normaliza.

## Cuándo usar esta Skill

- Antes de producir cualquier animación con narrativa.
- Para convertir un texto/cuento del usuario en escenas.

## Principios profesionales

- Formato de guion de animación: acción visual primero, diálogo breve.
- Duración: ~2.5 palabras de diálogo por segundo.
- Cada escena con objetivo y cambio.
- Escribir para el oído (TTS): frases simples y puntuadas.

## Procedimiento paso a paso

1. Logline + público + duración.
2. `python -m studio plan "<petición>" -o guion.json` (añade `--ai` si hay clave).
3. Edita textos/acciones en el JSON o en la interfaz.
4. Valida duración total y legibilidad; pasa a storyboard.

## Comandos del estudio

```bash
python -m studio plan "Una manzana valiente rescata a un gatito en la ciudad" -o guion.json
python -m studio plan "Una manzana valiente rescata a un gatito en la ciudad" --ai -o guion_ai.json   # con Claude
python -c "import json; d=json.load(open('guion.json')); [print(s['id'], [x['text'] for x in s['dialogue']]) for s in d['scenes']]"
```

## Ejemplo completo

Del cuento del usuario (texto largo) → resumirlo en 4–6 beats → `plan` con ese resumen y `--ai` → revisar diálogos para TTS (sin abreviaturas).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| planner.py | guion local por reglas | ✅ motor propio del estudio |
| Claude API (claude-opus-5-5, structured outputs) | guion creativo | 🔑 requiere clave API |
| Fountain / WriterSolo | guion en formato profesional | 💻 programa externo recomendado |

## Control de calidad

- [ ] Personajes de los diálogos existen en el reparto.
- [ ] Duración total como se pidió.
- [ ] Diálogos naturales al oírlos.

## Errores comunes y cómo evitarlos

- Diálogos largos para TTS.
- Acciones imposibles para el catálogo: usar las disponibles (ver `planner.catalog()`).

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
