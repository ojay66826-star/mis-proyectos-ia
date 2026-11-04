---
name: 3d-walk-cycles
description: Crea ciclos de caminar y correr 3D en bucle: contacto, bajada, paso y subida, contrabalanceo de brazos, bote y rumbo. Úsala para 'ciclo de caminar', 'walk cycle', 'que camine en 3D', 'run cycle'.
---

# Ciclos de caminar 3D

**Categoría:** Animación 3D · **Skills relacionadas:** `3d-character-animation`, `character-movement`, `seamless-loop-animation`

La acción `walk` usa frecuencia 1.6 Hz (paso cada 0.31 s): piernas ±0.55 rad, brazos opuestos, bote |cos| de 3 cm e inclinación 0.05 rad. `run` sube a 2.6 Hz con mayor amplitud e inclinación. El desplazamiento del root está sincronizado con la duración.

## Cuándo usar esta Skill

- Personaje 3D que se desplaza.
- Ciclos en bucle para juegos o fondos.

## Principios profesionales

- Las 4 poses clave: contacto, bajada (peso), paso (pierna cruzando), subida.
- Velocidad de traslación = longitud de zancada × frecuencia (evita patinaje).
- Cadera y hombros giran en oposición.
- Para bucle: duración múltiplo del periodo (0.625 s caminando).

## Procedimiento paso a paso

1. Define `from`/`to` distintos y acción `walk` o `run`.
2. Ajusta la duración para que la distancia cuadre con la zancada (~0.5 unidades/s caminando).
3. Render `--3d --quality preview` y revisa pies.
4. Para ciclo en el sitio (juegos) deja `from == to` y exporta GLB.

## Comandos del estudio

```bash
python -m studio make "Un pingüino camina en la nieve" --3d --quality preview
python -m studio character3d pinguino --action walk --duration 1.25   # 2 ciclos exactos
```

## Ejemplo completo

Ciclo de caminar en bucle para web: `character3d robot --action walk --duration 1.25` y cargar el GLB en `three-scene.html?glb=…`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender keyframes | ciclo procedural | ✅ instalado y probado |
| Graph Editor (Cycles modifier) | bucles manuales | ✅ instalado y probado |
| Mixamo walk | mocap | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Pies sin deslizar.
- [ ] Bucle sin salto al reiniciar.
- [ ] Ritmo de pasos coincide con el audio (footsteps).

## Errores comunes y cómo evitarlos

- Duración no múltiplo del periodo → salto en el bucle.
- Inclinación excesiva parece que cae.

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
