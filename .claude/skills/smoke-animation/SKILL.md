---
name: smoke-animation
description: Humo, vapor, polvo y nubes de impacto: partículas grandes que ascienden, se expanden y se desvanecen con deriva lateral. Úsala para 'humo', 'vapor', 'polvo', 'nube de polvo', 'chimenea', 'niebla densa'.
---

# Animación de humo y vapor

**Categoría:** Efectos visuales · **Skills relacionadas:** `fire-animation`, `explosions`, `horror-animation`

`smoke` usa 26 partículas grises de vida 2–3.5 s que suben 200–340 px expandiéndose de 20 a 100 px de radio y perdiendo alfa; `fog` crea bandas difuminadas horizontales para ambiente. La explosión encadena humo automáticamente tras 0.4 s.

## Cuándo usar esta Skill

- Chimeneas, tazas calientes, incendios, aterrizajes, explosiones, ambientes misteriosos.

## Principios profesionales

- Movimiento lento y orgánico.
- Mayor tamaño y transparencia con la edad.
- Color según fuente: gris (fuego), blanco (vapor), marrón (polvo).

## Procedimiento paso a paso

1. Elige `smoke` (columna) o `fog` (ambiente).
2. Coloca la fuente; usa `intensity` 0.5–1.5.
3. En terror combina `fog` + `horror`.

## Comandos del estudio

```bash
python -m studio make "Un fantasma aparece entre la niebla en el bosque embrujado" --style horror
```

## Fragmento de proyecto (project.json)

```json
{"effects": [{"type": "smoke", "x": 0.3, "y": 0.8, "intensity": 0.8}, {"type": "fog", "intensity": 1.2}]}
```

## Ejemplo completo

Aterrizaje con polvo: `smoke` con `start` en el momento del contacto, `x` en los pies, intensidad 0.6, `end` a +1.5 s.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py smoke/fog | humo 2D | ✅ motor propio del estudio |
| Blender Mantaflow (smoke) | humo 3D | ✅ instalado y probado |

## Control de calidad

- [ ] El humo no oscurece al protagonista.
- [ ] Movimiento continuo sin reinicios visibles.

## Errores comunes y cómo evitarlos

- Humo opaco = mancha gris: mantener alfa bajo.
- Niebla intensa en 9:16 cubre todo.

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
