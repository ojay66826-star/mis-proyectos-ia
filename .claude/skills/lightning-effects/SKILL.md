---
name: lightning-effects
description: Rayos procedurales con desplazamiento de punto medio, ramificación, parpadeo, flash de pantalla y truenos sincronizados; también arcos eléctricos. Úsala para 'rayo', 'relámpago', 'tormenta eléctrica', 'electricidad', 'trueno'.
---

# Rayos y relámpagos

**Categoría:** Efectos visuales · **Skills relacionadas:** `energy-effects`, `horror-animation`, `cinematic-effects`

`lightning` genera un rayo nuevo cada `period` s con el algoritmo de desplazamiento de punto medio (6 niveles), lo dibuja nítido + glow azulado, parpadea a 30 Hz durante 0.35 s y hace un flash blanco de 0.08 s. El audio pone un trueno en cada descarga.

## Cuándo usar esta Skill

- Tormentas, terror, superpoderes eléctricos, momentos dramáticos.

## Principios profesionales

- Flash corto y fuerte, luego oscuridad.
- Trueno con ligero retraso respecto al flash (realismo).
- Escena nocturna u oscura.
- Combinar con lluvia y temblor de cámara.

## Procedimiento paso a paso

1. Añade `lightning` con `period` 1.8–3 s.
2. Usa `on` para que el rayo caiga sobre un personaje.
3. Cámara `shake` y estilo `horror` o `cinematic`.

## Comandos del estudio

```bash
python -m studio make "Un fantasma asusta a un niño en un bosque embrujado" --style horror
```

## Fragmento de proyecto (project.json)

```json
{"time_of_day": "night", "camera": {"type": "shake"}, "effects": [{"type": "rain"}, {"type": "lightning", "period": 2.0}]}
```

## Ejemplo completo

Poder eléctrico del robot: `energy` en el robot (`color:[120,200,255]`) + `lightning` con `on: robot`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py lightning | rayos procedurales | ✅ motor propio del estudio |
| Blender (curvas + emisión) | rayos 3D | ✅ instalado y probado |

## Control de calidad

- [ ] No más de 3 flashes por segundo (seguridad para fotosensibles).
- [ ] Trueno audible tras cada rayo.

## Errores comunes y cómo evitarlos

- Flashes muy frecuentes pueden afectar a personas fotosensibles: periodo ≥ 1.5 s.
- Rayos de día pierden contraste.

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
