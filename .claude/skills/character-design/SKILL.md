---
name: character-design
description: Diseña personajes originales y mantiene su apariencia idéntica en todas las escenas mediante fichas JSON (character sheet) y hojas de modelo con poses, expresiones y visemas. Úsala para 'crea un personaje', 'diseña una mascota', 'hoja de personaje', 'que el personaje se vea igual siempre'.
---

# Diseño de personajes (consistente)

**Categoría:** Personajes · **Skills relacionadas:** `character-expressions`, `mascot-animation`, `animation-workflow`, `3d-modeling`

La **ficha** (`id, name, species, kind, shape, color, accent, eyes, accessory, hair, hair_color, skin, voice, personality, height`) es la única fuente de verdad: el renderizador procedural dibuja siempre igual a partir de ella. Especies disponibles: frutas: manzana, platano, naranja, fresa, uva, sandia, pina, limon, pera, cereza, aguacate; animales: gato, perro, conejo, oso, rana, pinguino, zorro, panda; otros: robot, nino, nina, persona, mago, mascota, fantasma, monstruo, estrella. Accesorios: none, hat, bow, glasses, crown, cap, wizard, scarf.

## Cuándo usar esta Skill

- Crear o personalizar un personaje.
- Garantizar consistencia en una serie de videos.
- Generar referencias para IA de imagen (prompt fijo).

## Principios profesionales

- Silueta reconocible en negro.
- Paleta de 2–3 colores principales + acento.
- Forma = personalidad: redondo amable, anguloso agresivo, alargado torpe/elegante.
- Una característica memorable (accesorio, color de ojos).
- Documentar todo en la ficha y reutilizarla.

## Procedimiento paso a paso

1. Define personalidad y rol (protagonista, amigo, rival).
2. Elige especie y color: `python -m studio character <especie> --name … --color … --accessory …`.
3. Revisa la hoja generada (`*_hoja.png`): 8 poses, 10 emociones, 6 visemas.
4. Guarda la ficha `.json` junto al proyecto y pásala en `characters` del project.json.
5. Para IA de imagen usa `character_prompt(spec)` + semilla fija para reproducir el mismo diseño.

## Comandos del estudio

```bash
python -m studio character manzana --name "Rojita" --color "#d32f2f" --accessory bow --style cute
python -m studio character robot --name "Bolt" --color "#26a69a" --eyes anime --style anime
python -c "from studio.characters import make_character, character_prompt; print(character_prompt(make_character('gato','Michi'), 'anime'))"
```

## Fragmento de proyecto (project.json)

```json
{"characters": [{"id": "rojita", "name": "Rojita", "species": "manzana", "color": "#d32f2f",
  "accessory": "bow", "eyes": "round", "personality": "curiosa y valiente"}]}
```

## Ejemplo completo

«Crea una mascota para mi panadería»: especie `estrella` color `#ffb300` con `cap`, estilo `cute`; entregar hoja PNG, ficha JSON, versión 3D (`character3d estrella`) y logo animado con su nombre.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Renderizador procedural | hojas de modelo | ✅ motor propio del estudio |
| Blender | versión 3D del personaje | ✅ instalado y probado |
| FLUX/SDXL (HF, Replicate) + IP-Adapter | diseños IA con referencia | 🔑 requiere clave API |
| Krita | bocetos y retoques | 💻 programa externo recomendado |

## Control de calidad

- [ ] La hoja muestra todas las expresiones correctamente.
- [ ] Mismo `id` en todas las escenas.
- [ ] Contraste suficiente con los fondos elegidos.

## Errores comunes y cómo evitarlos

- Cambiar el color entre escenas rompe la continuidad: edita la ficha, no la escena.
- Dos personajes del mismo color se confunden: el planificador varía el color si repites especie.

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
