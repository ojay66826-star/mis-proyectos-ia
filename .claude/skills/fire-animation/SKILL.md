---
name: fire-animation
description: Fuego animado: llamas ascendentes con color por temperatura (amarillo→naranja→rojo), parpadeo, brillo y crepitar sonoro; hogueras, antorchas, volcanes, personajes en llamas. Úsala para 'fuego', 'llamas', 'hoguera', 'incendio', 'antorcha'.
---

# Animación de fuego

**Categoría:** Efectos visuales · **Skills relacionadas:** `smoke-animation`, `particle-effects`, `animation-lighting`

El efecto `fire` emite 70 partículas por intensidad desde una base de ancho `width` (60 px por defecto a 720p), que suben 120–220 px, se estrechan, cambian de color por edad y llevan glow. El audio añade crepitar en bucle.

## Cuándo usar esta Skill

- Fuego en escena, poderes de fuego, ambiente cálido nocturno.

## Principios profesionales

- Forma de lágrima: base ancha, punta estrecha.
- Movimiento turbulento (oscilación lateral) y rápido (vida 0.5–1 s).
- Ilumina el entorno: escena nocturna o atardecer.
- Humo encima para realismo (`smoke` desplazado arriba).

## Procedimiento paso a paso

1. Coloca la base con `x`,`y` (suelo ≈ 0.82).
2. Ajusta `intensity` (altura) y `width`.
3. Combina con `smoke` (y más alto) y escena `night`.
4. Render y revisa el bloom.

## Comandos del estudio

```bash
python -m studio make "Unos amigos cuentan historias junto al fuego en el bosque de noche" --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"time_of_day": "night", "effects": [{"type": "fire", "x": 0.5, "y": 0.84, "intensity": 1.2, "width": 50},
  {"type": "smoke", "x": 0.5, "y": 0.62, "intensity": 0.5}, {"type": "fireflies"}]}
```

## Ejemplo completo

Personaje con poder de fuego: `{"type":"fire","on":"dragon","intensity":0.8}` sigue al personaje.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py fire | fuego 2D | ✅ motor propio del estudio |
| Blender Mantaflow | fuego volumétrico 3D | ✅ instalado y probado |
| EmberGen | simulación en tiempo real | 💻 programa externo recomendado |

## Control de calidad

- [ ] Colores cálidos sin saturar a blanco.
- [ ] Crepitar audible y no molesto.
- [ ] Base del fuego apoyada.

## Errores comunes y cómo evitarlos

- Fuego de día pierde impacto.
- Intensidad > 2 cubre la escena.

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
