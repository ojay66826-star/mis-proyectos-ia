---
name: water-animation
description: Agua animada: lluvia con salpicaduras, olas con espuma, salpicaduras parabólicas con ondas, burbujas submarinas y rayos de luz bajo el agua. Úsala para 'agua', 'lluvia', 'mar', 'olas', 'chapuzón', 'bajo el agua', 'burbujas'.
---

# Animación de agua

**Categoría:** Efectos visuales · **Skills relacionadas:** `particle-effects`, `visual-effects`, `3d-environment-animation`

Efectos: `rain` (220 gotas inclinadas + salpicaduras en el suelo), `waves` (4 capas de olas sinusoidales con espuma), `water_splash` (gotas parabólicas con gravedad + anillo de onda), `bubbles` (burbujas con brillo). Escenario `underwater` y `beach` complementan.

## Cuándo usar esta Skill

- Clima lluvioso, playa, piscina, océano, peces/submarinos.

## Principios profesionales

- Gravedad real en salpicaduras (parábola).
- Paralaje en olas (capas a distinta velocidad).
- Lluvia inclinada indica viento; gotas rápidas y finas.
- Sonido continuo (rain/splash).

## Procedimiento paso a paso

1. Ambiente: `rain` o `waves`; acción: `water_splash` anclado.
2. Bajo el agua: `background: underwater` + `bubbles`.
3. Ajusta intensidad y periodo del splash (`period`).

## Comandos del estudio

```bash
python -m studio make "Una rana salta al agua en el fondo del mar con burbujas" --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"background": "beach", "effects": [{"type": "waves"}, {"type": "water_splash", "x": 0.6, "y": 0.86, "period": 1.6}]}
```

## Ejemplo completo

Día de lluvia triste: `rain` intensidad 1.0, `time_of_day: sunset`, personaje `sad`; música `sad`; sonido de lluvia automático.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| effects.py rain/waves/water_splash/bubbles | agua 2D | ✅ motor propio del estudio |
| Blender Ocean modifier / FLIP fluids | agua 3D | ✅ instalado y probado |

## Control de calidad

- [ ] Salpicaduras nacen del punto correcto.
- [ ] Olas no cubren a los personajes.
- [ ] Audio de lluvia sin clipping.

## Errores comunes y cómo evitarlos

- Lluvia muy densa reduce legibilidad.
- Olas en escenario no costero.

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
