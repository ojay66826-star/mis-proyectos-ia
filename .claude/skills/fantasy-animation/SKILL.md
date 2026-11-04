---
name: fantasy-animation
description: Mundos de fantasía: castillos, bosques encantados, magos, hadas, criaturas, luces mágicas, gradación violeta-dorada y bloom, música orquestal de fantasía. Úsala para 'fantasía', 'mágico', 'reino', 'hadas', 'dragones', 'cuento de hadas'.
---

# Animación de fantasía

**Categoría:** Estilos especiales · **Skills relacionadas:** `magic-effects`, `character-transformations`, `anime-animation`

`style: fantasy` aplica tinte violeta-dorado, bloom fuerte en altas luces y viñeta; el planificador elige `castle`, magia, luciérnagas y música `fantasy` (Eb mayor, campanas). Especies útiles: mago, estrella, monstruo, conejo, zorro.

## Cuándo usar esta Skill

- Cuentos de hadas, aventuras mágicas, videojuegos de fantasía.

## Principios profesionales

- Luz como magia: fuentes cálidas en entornos fríos.
- Escala: castillos grandes, personajes pequeños.
- Criaturas con siluetas originales.
- Música con campanas y cuerdas.

## Procedimiento paso a paso

1. `make … --style fantasy`.
2. Añade `magic`, `fireflies`, `sparkles`.
3. Usa transformaciones para momentos mágicos.
4. Cierra con `zoom_out` al castillo.

## Comandos del estudio

```bash
python -m studio make "Un mago y un conejo buscan una estrella mágica en el castillo" --style fantasy
```

## Ejemplo completo

Aventura mágica de 20 s: llegada al castillo (pan), hechizo (magic + transform), celebración con sparkles, música fantasy.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| style fantasy + efectos mágicos | look de fantasía | ✅ motor propio del estudio |
| Blender EEVEE (bloom) | fantasía 3D | ✅ instalado y probado |
| FLUX/SDXL (IA) | fondos pintados | 🔑 requiere clave API |

## Control de calidad

- [ ] Bloom sin quemar caras.
- [ ] Paleta coherente violeta/dorado.
- [ ] Música acorde.

## Errores comunes y cómo evitarlos

- Abusar del bloom → imagen lechosa.
- Criaturas de franquicias existentes: diseña originales.

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
