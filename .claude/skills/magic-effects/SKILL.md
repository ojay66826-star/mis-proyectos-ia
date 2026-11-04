---
name: magic-effects
description: Magia animada: estrellas de 8 puntas que orbitan y suben, aura brillante pulsante, destellos, polvo de hada, hechizos y transformaciones. Úsala para 'magia', 'hechizo', 'varita', 'hada', 'brillos mágicos', 'poderes mágicos'.
---

# Efectos mágicos

**Categoría:** Efectos visuales · **Skills relacionadas:** `fantasy-animation`, `character-transformations`, `particle-effects`

`magic` dibuja estrellas que orbitan con rotación temporal y suben mientras aparecen/desaparecen (vida 0.6–1.4 s) más un aura elíptica pulsante; `sparkles` es la versión dorada sin órbita. Color configurable (`color`). Audio: arpegio de campanas.

## Cuándo usar esta Skill

- Fantasía, magos, hadas, transformaciones, momentos 'wow'.

## Principios profesionales

- Color simbólico: violeta misterio, dorado bondad, verde naturaleza, rojo peligro.
- La magia sale de una fuente (mano/varita/personaje).
- Crescendo: empieza sutil, culmina con destello.
- Combinar con estilo `fantasy` (bloom violeta-dorado).

## Procedimiento paso a paso

1. Ancla `magic` al personaje con `on`.
2. Añade `sparkles` con `start` posterior para el clímax.
3. Si hay transformación, usa `transform_to` (Skill character-transformations).

## Comandos del estudio

```bash
python -m studio make "Haz una animación estilo anime de una niña con magia en un castillo" --style anime
```

## Fragmento de proyecto (project.json)

```json
{"effects": [{"type": "magic", "on": "nina", "color": [255, 128, 220]}, {"type": "sparkles", "on": "nina", "start": 1.2, "intensity": 1.4}]}
```

## Ejemplo completo

Hada que ilumina el bosque: `fireflies` + `magic` verde (`color:[120,255,160]`) en el hada, escena `forest` de noche.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py magic/sparkles | magia 2D | ✅ motor propio del estudio |
| Three.js / GSAP | magia web interactiva | ✅ instalado y probado |

## Control de calidad

- [ ] La fuente de la magia es clara.
- [ ] El color de la magia es coherente en toda la historia.

## Errores comunes y cómo evitarlos

- Magia en cada escena pierde valor.
- Colores mágicos similares al fondo (castillo violeta + magia violeta).

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
