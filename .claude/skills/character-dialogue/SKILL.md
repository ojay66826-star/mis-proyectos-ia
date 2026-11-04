---
name: character-dialogue
description: Escribe y escenifica diálogos: turnos de palabra, voces distintas, reacciones de quien escucha, subtítulos y ritmo de escena. Úsala para 'conversación', 'que hablen entre ellos', 'diálogo', 'entrevista animada'.
---

# Diálogos de personajes

**Categoría:** Personajes · **Skills relacionadas:** `character-lip-sync`, `animation-scripting`, `story-animation`

Cada línea de `dialogue` genera su voz, se coloca secuencialmente con 0.3 s de pausa y la escena se alarga automáticamente para que quepa. El personaje que habla pasa a `talk` si estaba en `idle`; quien escucha conserva su acción (usa `think` o emociones para reaccionar).

## Cuándo usar esta Skill

- Conversaciones entre 2+ personajes.
- Videos explicativos con presentador.

## Principios profesionales

- Líneas cortas y con subtexto; una idea por línea.
- Alternar plano/encuadre o posición cada 2–3 líneas.
- El oyente reacciona (asiente, sorpresa) — no estatua.
- Voz = personaje: tono agudo para frutas pequeñas, grave para monstruos.

## Procedimiento paso a paso

1. Escribe el intercambio (o usa `--ai`).
2. Coloca a los personajes enfrentados (`facing` 1 y -1).
3. Añade reacciones con `emotions` en quien escucha.
4. Edita textos en la interfaz (Ver guion) y renderiza.

## Comandos del estudio

```bash
python -m studio plan "Una naranja y un limón discuten quién es más ácido" -o dialogo.json
python -m studio render dialogo.json
```

## Fragmento de proyecto (project.json)

```json
{"actors": [{"character": "naranja", "action": "idle", "emotion": "happy", "from": [0.3, 0.82], "facing": 1},
            {"character": "limon", "action": "idle", "emotion": "angry", "from": [0.7, 0.82], "facing": -1}],
 "dialogue": [{"character": "naranja", "text": "¡Yo soy la más dulce del frutero!"},
              {"character": "limon", "text": "Pero yo soy el más fuerte."}]}
```

## Ejemplo completo

Entrevista: presentador `persona` y entrevistado `robot`, 3 escenas con 2 líneas cada una, subtítulos grandes para Shorts (`--format 9:16`).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| TTS espeak-ng (voces por tipo) | voces locales | ✅ instalado y probado |
| Claude (opcional) | diálogos creativos | 🔑 requiere clave API |
| ElevenLabs | voces actorales | 🔑 requiere clave API |

## Control de calidad

- [ ] Ninguna línea queda cortada al final de escena.
- [ ] Turnos claros (subtítulo con nombre).
- [ ] Volumen de voces homogéneo.

## Errores comunes y cómo evitarlos

- Más de 4 líneas por escena saturan: divide en escenas.
- Dos voces iguales: el estudio varía el tono por id; para más contraste define `voice`.

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
