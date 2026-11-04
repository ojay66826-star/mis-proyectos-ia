---
name: particle-effects
description: Diseña sistemas de partículas personalizados (emisión, vida, velocidad, gravedad, color por edad, tamaño, alfa, rotación, bloom) en 2D determinista, en Three.js o en Blender. Úsala para 'partículas', 'chispas', 'polvo', 'confeti', 'brillitos', 'crear un efecto nuevo'.
---

# Sistemas de partículas

**Categoría:** Efectos visuales · **Skills relacionadas:** `visual-effects`, `fire-animation`, `magic-effects`

Patrón del estudio: para la partícula i, `r = rng(seed+i)`; `life = r.uniform(a,b)`; `age = (t + r.uniform(0,life)) % life`; `k = age/life`. Posición, tamaño, color y alfa son funciones de k → sin estado, reproducible y en bucle. Para crear un efecto nuevo añade una rama `elif kind == ...` en `draw_effect`.

## Cuándo usar esta Skill

- Crear un efecto que no existe.
- Ajustar densidad, color o física de uno existente.

## Principios profesionales

- Variación aleatoria acotada (tamaño ±40 %, vida ±30 %).
- Color por edad (caliente→frío, opaco→transparente).
- Más partículas pequeñas > pocas grandes.
- Bloom solo en partículas emisivas.

## Procedimiento paso a paso

1. Copia la rama de un efecto similar en `studio/effects.py`.
2. Define emisor (punto, línea, área, personaje).
3. Define trayectoria analítica (lineal, parabólica con gravedad, espiral).
4. Registra el nombre en `EFFECTS` (y en `GLOWY` si brilla) y su sonido en `audio.EFFECT_SFX`.
5. Prueba con un render corto en preview.

## Comandos del estudio

```bash
python - <<'PY'
from PIL import Image
from studio.effects import render_effects
im = Image.new('RGBA', (640, 360), (20, 20, 40, 255))
im.alpha_composite(render_effects((640, 360), [{"type": "fireflies"}, {"type": "sparkles", "x": 0.5, "y": 0.6}], t=1.0))
im.save('particulas.png')
PY
```

## Ejemplo completo

Efecto 'polvo mágico dorado': partir de `sparkles`, cambiar trayectoria a espiral (`ang += lt*3`), color base (255,215,64), registrar como `golden_dust`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py | partículas deterministas | ✅ motor propio del estudio |
| Three.js Points | partículas web | ✅ instalado y probado |
| Blender Particle System | partículas 3D | ✅ instalado y probado |

## Control de calidad

- [ ] El efecto se ve igual en render paralelo.
- [ ] Bucle sin saltos (usa periodos que dividan la duración).
- [ ] Sin partículas congeladas.

## Errores comunes y cómo evitarlos

- Usar `random` sin semilla rompe el determinismo.
- Demasiadas partículas con blur grande ralentizan.

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
