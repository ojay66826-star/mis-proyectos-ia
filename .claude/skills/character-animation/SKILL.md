---
name: character-animation
description: Anima personajes con acciones creíbles (caminar, correr, saltar, saludar, hablar, bailar, pelear, celebrar) y transiciones entre acciones y emociones en una misma escena. Úsala cuando la petición se centre en lo que HACE un personaje: 'haz que camine/baile/hable/salte'.
---

# Animación de personajes

**Categoría:** Animación 2D · **Skills relacionadas:** `character-movement`, `character-emotions`, `character-lip-sync`, `character-dancing`, `character-fighting`

El rig 2D del estudio tiene cuerpo con squash & stretch, brazos y piernas de dos segmentos (hombro/codo, cadera/rodilla), cara con ojos, cejas, párpados y boca con visemas. `motion.py` genera las poses procedurales y el render admite cambios de acción y emoción en el tiempo (`actions`, `emotions`).

## Cuándo usar esta Skill

- 'Haz que el personaje camine / baile / hable / salte / salude / pelee'.
- Secuencias donde un personaje encadena acciones (camina → se detiene → saluda).

## Principios profesionales

- Ciclos de caminar a ~1.6 Hz (paso cada 0.31 s) con bote vertical y brazos opuestos.
- Peso: el cuerpo baja en el contacto y sube en el paso (body_dy).
- Encadenar acciones con 0.2–0.3 s de transición; nunca cambiar de pose sin anticipación.
- La emoción guía la acción: triste = hombros caídos y ritmo lento; feliz = saltos y brazos arriba.

## Procedimiento paso a paso

1. Lista las acciones en orden con su tiempo aproximado.
2. En `project.json`, dentro del actor usa `actions: [{t:0, action:'walk'}, {t:2.5, action:'wave'}]`.
3. Define desplazamiento con `from`/`to` y `move_start`/`move_end` para que solo se mueva mientras camina.
4. Añade cambios de emoción con `emotions: [{t:0,'emotion':'happy'},{t:3,'emotion':'surprised'}]`.
5. Revisa la hoja de personaje (`characters/<id>_sheet.png`) para ver todas las poses disponibles.

## Comandos del estudio

```bash
python -m studio character gato --name Michi          # ver todas las poses y expresiones
python -m studio make "Un gato camina y luego saluda feliz" --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"character": "michi", "from": [0.1, 0.82], "to": [0.55, 0.82], "move_start": 0, "move_end": 2.4,
 "actions": [{"t": 0, "action": "walk"}, {"t": 2.4, "action": "wave"}, {"t": 4.0, "action": "celebrate"}],
 "emotions": [{"t": 0, "emotion": "happy"}, {"t": 4.0, "emotion": "joy"}]}
```

## Ejemplo completo

«Haz que el plátano camine, se asuste y huya»: actor con acciones walk (0–2 s) → scared_shake (2–3 s) → run (3–5 s)
con `to` fuera de cuadro (x=1.15) y emoción scared desde t=2.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (motion.py) | ciclos procedurales | ✅ motor propio del estudio |
| Blender (scene3d.py) | las mismas acciones en 3D | ✅ instalado y probado |
| Spine / DragonBones | rig 2D por huesos para juegos | 💻 programa externo recomendado |
| Mixamo | animaciones 3D humanoides | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Pies apoyados en el suelo en el contacto (sin patinar).
- [ ] Cambio de acción sin saltos visibles.
- [ ] La emoción se lee en la cara.

## Errores comunes y cómo evitarlos

- Velocidad de desplazamiento incoherente con el ciclo → patinaje: para caminar ≈0.3 del ancho por 2.5 s.
- Olvidar `facing`: se calcula solo para walk/run; para otras acciones fíjalo (1 derecha, -1 izquierda).

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
