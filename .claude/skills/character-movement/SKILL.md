---
name: character-movement
description: Planifica trayectorias y desplazamientos: entrar/salir de cuadro, cruzarse, perseguir, posiciones en profundidad, dirección (facing) y velocidad sin patinaje. Úsala para 'que entre por la izquierda', 'que corra hacia…', 'persecución', 'que se mueva por la escena'.
---

# Movimiento y desplazamiento de personajes

**Categoría:** Personajes · **Skills relacionadas:** `character-animation`, `scene-composition`, `3d-walk-cycles`

Cada actor tiene `from`/`to` normalizados (x 0–1, y 0.82 = suelo), `move_start`/`move_end` para el tramo de movimiento, y `facing`. El orden de dibujo se calcula por la y (más abajo = delante) para simular profundidad.

## Cuándo usar esta Skill

- Composición dinámica con desplazamientos.
- Persecuciones, entradas y salidas.

## Principios profesionales

- Velocidad coherente con el ciclo: caminar ~0.12 ancho/s, correr ~0.25 ancho/s.
- Entrar desde fuera del cuadro (x<0 o x>1).
- Dejar 'aire' delante del personaje en la dirección de mirada.
- Cruces en distintas profundidades (y 0.78 vs 0.86).

## Procedimiento paso a paso

1. Dibuja en papel el recorrido de cada actor por escena.
2. Asigna from/to y el tramo de movimiento.
3. Ajusta `facing` en acciones estáticas.
4. Revisa el storyboard (2 fotogramas por escena muestran posición inicial y media).

## Comandos del estudio

```bash
python -m studio make "Un perro persigue a un gato por la ciudad" --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"actors": [
  {"character": "gato", "action": "run", "emotion": "scared", "from": [0.35, 0.84], "to": [1.15, 0.84]},
  {"character": "perro", "action": "run", "emotion": "excited", "from": [-0.15, 0.80], "to": [0.85, 0.80]}]}
```

## Ejemplo completo

Persecución: gato delante (y=0.84) huyendo, perro detrás (y=0.80) con 0.5 de desfase; cámara `pan`; música `action`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (actor_position) | trayectorias con easing | ✅ motor propio del estudio |
| Blender | mismas trayectorias en 3D (x×3.2 m) | ✅ instalado y probado |

## Control de calidad

- [ ] Sin patinaje de pies.
- [ ] Entradas/salidas completas.
- [ ] Orden de profundidad correcto.

## Errores comunes y cómo evitarlos

- y muy distintas cambian el tamaño aparente solo por orden, no por escala: usa `scale` para profundidad real.
- Personajes solapados en la misma x y y.

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
