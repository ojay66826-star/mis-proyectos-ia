---
name: visual-effects
description: Selecciona, combina y ajusta efectos visuales para animaciones: partículas, clima, magia, energía, explosiones, niebla, bloom y grading. Úsala cuando la petición pida 'efectos', 'VFX', 'que se vea espectacular', o no esté claro qué efecto concreto usar.
---

# Efectos visuales (VFX) — visión general

**Categoría:** Efectos visuales · **Skills relacionadas:** `particle-effects`, `cinematic-effects`, `magic-effects`, `animation-sound-design`

El sistema de efectos (`studio/effects.py`) dibuja partículas **deterministas**: cada partícula se calcula analíticamente por su semilla y edad, por lo que cualquier frame se puede renderizar aislado (render paralelo, bucles perfectos). Hay 19 efectos con capa de brillo (bloom) automática. Campos comunes de un efecto: `type`, `x`/`y` (0–1) o `on: <id_personaje>`, `start`, `end`, `intensity`, `scale`, `color` [r,g,b], `seed`.

## Cuándo usar esta Skill

- Dar espectacularidad a una escena.
- Elegir combinación de efectos coherente con el estilo y la historia.

## Principios profesionales

- Los efectos sirven a la historia: cada uno debe tener motivo (clima, poder, emoción).
- Jerarquía: un efecto protagonista + uno ambiental como máximo.
- Coherencia de luz: efectos brillantes en escenas oscuras lucen más.
- Sonido para cada efecto (automático en el estudio).

## Procedimiento paso a paso

1. Identifica la intención: ambiente (rain, snow, fog, fireflies, leaves, bubbles), poder (magic, energy, energy_beam, lightning), impacto (explosion, water_splash, speedlines), celebración (confetti, sparkles, hearts).
2. Añade los efectos en `effects` de la escena (o en la interfaz, paso 5).
3. Ancla al personaje con `on` cuando el efecto sale de él.
4. Controla tiempos con `start`/`end` e intensidad con `intensity` (0.5–1.5).
5. Revisa frames clave y el sonido.

## Comandos del estudio

```bash
python -m studio make "Un mago lanza magia bajo la lluvia con rayos" --style fantasy
python -c "from studio.effects import EFFECTS; print(EFFECTS)"
```

## Fragmento de proyecto (project.json)

```json
{"effects": [{"type": "rain", "intensity": 0.8}, {"type": "lightning", "period": 2.2},
  {"type": "magic", "on": "mago", "start": 1.0, "color": [186, 104, 255]}]}
```

## Ejemplo completo

Escena épica: `fog` (ambiente) + `energy` en el héroe (protagonista) + `lightning` cada 2 s; estilo `cinematic` añade grading y viñeta.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py | 19 efectos con bloom | ✅ motor propio del estudio |
| Blender (partículas, Mantaflow) | fuego/humo/agua simulados 3D | ✅ instalado y probado |
| ActionVFX / ProductionCrate | stock VFX (licencias) | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Ningún efecto tapa la cara del protagonista.
- [ ] Efectos sincronizados con su sonido.
- [ ] Rendimiento: ≤ 3 efectos por escena.

## Errores comunes y cómo evitarlos

- Lluvia + nieve + niebla + confeti = ruido visual.
- Efectos con `on` a un personaje que no está en la escena se descartan (normalize).

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
