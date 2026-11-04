---
name: cutout-animation
description: Animación por piezas articuladas (marioneta digital): cabeza, torso, brazos y piernas como piezas que rotan sobre pivotes. Úsala para 'cutout', 'recortes', 'marioneta', 'estilo South Park', 'rig 2D por piezas'.
---

# Animación cutout (recortes / marionetas)

**Categoría:** Animación 2D · **Skills relacionadas:** `paper-animation`, `2d-animation`, `character-animation`

Los personajes del estudio ya son marionetas cutout: cada extremidad es una pieza con pivote (hombro, codo, cadera, rodilla) y el cuerpo es una pieza con squash. Con `style: paper` se obtiene el look de papel recortado con textura y animación a 12 fps.

## Cuándo usar esta Skill

- Estilo de papel recortado, marionetas, collage.
- Producción rápida de muchos episodios con el mismo rig.

## Principios profesionales

- Pivotes bien colocados (hombros dentro del cuerpo) evitan huecos al rotar.
- Pocas piezas y bien diseñadas > muchas piezas.
- Movimiento a 12 fps con ligeros saltos refuerza el estilo.
- Sombra proyectada corta para separar capas.

## Procedimiento paso a paso

1. Elige `style: paper` (o `cartoon` para cutout limpio).
2. Planifica escenas cortas con acciones claras (talk, wave, walk).
3. Si el usuario trae piezas propias (PNG), crea un rig en Blender (planos con pivotes) o en OpenToonz/Moho.
4. Renderiza y comprueba que no haya huecos en articulaciones.

## Comandos del estudio

```bash
python -m studio make "Dos amigos conversan en el parque" --style paper
python -m studio character persona --style paper
```

## Ejemplo completo

«Haz un episodio corto estilo recortes de papel»: `python -m studio make "Un niño y su perro buscan un tesoro en la playa" --style paper --duration 20`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (style paper) | cutout con textura de papel | ✅ motor propio del estudio |
| Moho / Cartoon Animator | cutout profesional | 💻 programa externo recomendado |
| Blender (planos + huesos) | cutout con piezas propias | ✅ instalado y probado |

## Control de calidad

- [ ] Sin huecos en las articulaciones.
- [ ] Textura de papel visible pero sutil.
- [ ] Ritmo a 12 fps intencional.

## Errores comunes y cómo evitarlos

- Rotaciones extremas (>150°) delatan la pieza: limita ángulos.
- Sombras largas ensucian el plano.

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
