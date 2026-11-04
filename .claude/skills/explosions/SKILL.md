---
name: explosions
description: Explosiones estilizadas: flash, bola de fuego expansiva, onda de choque, escombros con gravedad y humo posterior, con sonido de boom y temblor. Úsala para 'explosión', 'explota', 'boom', 'bomba', 'impacto', 'estallido'.
---

# Explosiones

**Categoría:** Efectos visuales · **Skills relacionadas:** `fire-animation`, `smoke-animation`, `character-fighting`

`explosion` dura `length` (1.6 s): flash de 0.08 s, 26 bolas de fuego que se expanden con easing cúbico y cambian de amarillo a naranja-rojo, anillo de onda de choque elíptico, 30 escombros parabólicos y humo encadenado. Audio: ruido filtrado + boom grave.

## Cuándo usar esta Skill

- Finales de pelea, gags cartoon, acción, reveal de título.

## Principios profesionales

- Anticipación (silencio o zoom) antes del boom.
- Temblor de cámara en el impacto.
- Humo residual para que no desaparezca de golpe.
- Apto para todo público: sin daño visible a personajes.

## Procedimiento paso a paso

1. Añade `explosion` con `x`,`y` y `start`.
2. Escena con `camera: shake` o `zoom_in`.
3. Reacción de personajes (`scared_shake` o `surprised`).

## Comandos del estudio

```bash
python -m studio make "Un perro y un gato pelean en el dojo con explosiones" --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"camera": {"type": "shake"}, "effects": [{"type": "explosion", "x": 0.5, "y": 0.6, "start": 0.4, "scale": 1.2}]}
```

## Ejemplo completo

Explosión cartoon de confeti: `explosion` con `intensity:0.6` + `confetti` con `start` 0.3 s después.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py explosion | explosión 2D | ✅ motor propio del estudio |
| Blender Mantaflow | explosión 3D | ✅ instalado y probado |
| JangaFX EmberGen | VFX en tiempo real | 💻 programa externo recomendado |

## Control de calidad

- [ ] Flash no supera 2 frames.
- [ ] Boom sincronizado.
- [ ] Humo posterior visible.

## Errores comunes y cómo evitarlos

- Explosión pegada al personaje sin reacción parece error.
- Varias explosiones simultáneas saturan.

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
