---
name: 3d-environment-animation
description: Crea y anima entornos 3D: suelo, cielo (world), árboles, edificios, escenario con focos, mar, planetas; niebla y luz por hora del día. Úsala para 'escenario 3D', 'mundo 3D', 'fondo 3D', 'ambiente 3D'.
---

# Escenarios 3D animados

**Categoría:** Animación 3D · **Skills relacionadas:** `animation-lighting`, `3d-animation`, `animated-backgrounds`

`build_set()` genera 15 escenarios 3D coherentes con los 2D (park, forest, city, beach, space, stage con focos RGB, kitchen, classroom, dojo, studio…) y `lights()` adapta energía y color al momento del día (day/sunset/night).

## Cuándo usar esta Skill

- Escenas 3D con contexto.
- Fondos 3D para personajes o productos.

## Principios profesionales

- Profundidad: elementos en primer plano, medio y fondo.
- El fondo menos saturado y con más niebla.
- Color de la luz cuenta la hora: día neutro, atardecer naranja, noche azul.
- Variedad controlada (semilla fija por escenario).

## Procedimiento paso a paso

1. Elige `background` y `time_of_day` por escena.
2. Para entornos a medida, añade props en `build_set` (obj_add con materiales).
3. Para HDRI realistas: descarga de Poly Haven (CC0) y asígnalo al World.
4. Render y revisa la exposición.

## Comandos del estudio

```bash
python -m studio make "Un astronauta rana explora el espacio" --3d --quality preview
```

## Ejemplo completo

«Escena 3D en la playa al atardecer»: `background: beach`, `time_of_day: sunset` → luz key naranja, mar y arena.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender | props procedurales | ✅ instalado y probado |
| Poly Haven | HDRI, texturas y modelos CC0 | 🌐 gratis, requiere internet |
| Geometry Nodes | dispersión de vegetación | ✅ instalado y probado |

## Control de calidad

- [ ] Horizonte sin cortes del plano de suelo.
- [ ] Exposición correcta de cielo y suelo.
- [ ] Escala coherente de props.

## Errores comunes y cómo evitarlos

- Plano de suelo pequeño se ve el borde en órbitas: usa 40×40 m.
- Demasiados objetos ralentizan EEVEE por software.

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
