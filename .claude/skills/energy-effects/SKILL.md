---
name: energy-effects
description: Auras de poder pulsantes, chispas ascendentes, arcos eléctricos alrededor del personaje y rayos de energía (beams) estilo anime. Úsala para 'aura', 'poder', 'energía', 'super saiyajin', 'rayo de energía', 'kamehameha', 'superpoder'.
---

# Efectos de energía y poder

**Categoría:** Efectos visuales · **Skills relacionadas:** `character-fighting`, `anime-animation`, `lightning-effects`

`energy` (aura de 3 capas pulsando a 10 rad/s + chispas que suben + 2 arcos eléctricos por frame) y `energy_beam` (rayo horizontal que se extiende en 0.3 s con núcleo blanco y glow de color, dirección `dir`). Anclar con `on`.

## Cuándo usar esta Skill

- Superhéroes, peleas anime, power-ups, momentos de transformación.

## Principios profesionales

- Carga → disparo → impacto.
- Núcleo blanco + borde de color = sensación de intensidad.
- Aura sincronizada con la respiración/tensión del personaje.
- Sonido zumbido (energy) + whoosh.

## Procedimiento paso a paso

1. Carga: `energy` con `on: héroe` durante 1–2 s.
2. Disparo: `energy_beam` con `start` y `dir` (1 derecha, -1 izquierda).
3. Impacto: `explosion` en el rival.

## Comandos del estudio

```bash
python -m studio make "Un robot carga energía y dispara un rayo contra un monstruo" --style anime
```

## Fragmento de proyecto (project.json)

```json
{"effects": [{"type": "energy", "on": "robot", "end": 1.8, "color": [79, 195, 247]},
  {"type": "energy_beam", "on": "robot", "start": 1.8, "dir": 1}, {"type": "explosion", "x": 0.8, "y": 0.62, "start": 2.1}]}
```

## Ejemplo completo

Power-up de la fresa: aura rosa (`color:[255,64,129]`) + `sparkles` + cambio de emoción a `excited`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py energy/energy_beam | poderes 2D | ✅ motor propio del estudio |
| Blender (emisión + bloom EEVEE) | auras 3D | ✅ instalado y probado |

## Control de calidad

- [ ] El beam sale del personaje y en la dirección correcta.
- [ ] Aura no oculta la cara.

## Errores comunes y cómo evitarlos

- `dir` incorrecto dispara hacia atrás.
- Beam permanente: limita con `end`.

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
