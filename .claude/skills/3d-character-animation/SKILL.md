---
name: 3d-character-animation
description: Anima personajes 3D (caminar, correr, bailar, saltar, saludar, golpear, flotar) con jerarquías de pivotes, squash & stretch volumétrico, parpadeo y boca sincronizada. Úsala para 'personaje 3D que camina/baila/habla'.
---

# Animación de personajes 3D

**Categoría:** Animación 3D · **Skills relacionadas:** `3d-rigging`, `3d-walk-cycles`, `3d-facial-animation`, `character-animation`

Cada personaje 3D tiene un empty raíz (posición/rumbo), un empty de cuerpo (bote, squash, inclinación) y pivotes de hombro/cadera para las extremidades. `animate()` en scene3d.py escribe keyframes por frame para que el resultado sea idéntico al motor 2D.

## Cuándo usar esta Skill

- Acciones de personaje en 3D.
- Exportar personaje animado a GLB para web/juegos.

## Principios profesionales

- Conservar volumen en el squash: escala XY = √s y Z = 1/s.
- Rumbo hacia la dirección de marcha (root rotación Z).
- Contrapeso: inclinación del cuerpo hacia delante al correr (≈10°).
- Parpadeo cada ~3 s y movimiento de boca por visemas.

## Procedimiento paso a paso

1. Define acciones en el JSON (mismas que en 2D).
2. Para un personaje aislado: `python -m studio character3d <especie> --action dance`.
3. Revisa el turntable y el GLB (`templates/web/three-scene.html?glb=/projects/.../x.glb`).
4. Para rigs humanoides reales, importa el GLB en Blender, añade Rigify o sube a Mixamo.

## Comandos del estudio

```bash
python -m studio character3d gato --action dance --duration 4 --engine eevee
python -m studio character3d robot --action walk --engine rapido -o projects/robot3d
```

## Ejemplo completo

«Haz un perro 3D que salude»: `python -m studio character3d perro --action wave --duration 3` → `perro_3d.mp4` (órbita de cámara) + `perro.glb` con la animación embebida.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender bpy | keyframes procedurales | ✅ instalado y probado |
| glTF 2.0 exporter | GLB animado | ✅ instalado y probado |
| Rigify | rig humanoide avanzado | ✅ instalado y probado |
| Mixamo | auto-rig + mocap | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Sin deslizamiento de pies al caminar.
- [ ] Brazos no atraviesan el cuerpo.
- [ ] La animación del GLB se reproduce en Three.js.

## Errores comunes y cómo evitarlos

- Rotaciones Euler grandes en Y pueden voltear brazos: limitar a ±2.8 rad.
- Escalar el cuerpo con squash afecta a hijos (ojos): es intencional.

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
