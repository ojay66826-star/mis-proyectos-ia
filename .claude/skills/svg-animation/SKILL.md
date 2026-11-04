---
name: svg-animation
description: Animaciones vectoriales SVG para web: dibujado de trazos (stroke-dashoffset), morphing, transformaciones con transform-origin, CSS keyframes, SMIL o GSAP, y captura a video. Úsala para 'SVG animado', 'icono animado', 'ilustración vectorial animada', 'animación ligera para web'.
---

# Animación SVG

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `css-animation`, `gsap-animation`, `lottie-animation`

`templates/web/svg-css-character.html` muestra un personaje SVG (manzana) animado solo con CSS: rebote con squash & stretch, parpadeo con `steps`, brazos con `transform-origin`, sombra sincronizada y nube a la deriva. `gsap-logo.html` dibuja un anillo con `stroke-dashoffset`. Ambos se capturan determinísticamente vía Web Animations API.

## Cuándo usar esta Skill

- Animaciones web ligeras, iconos, ilustraciones, landing pages.

## Principios profesionales

- `transform-box: fill-box` y `transform-origin` correctos para rotar piezas.
- Usar `pathLength=1` para animar trazos fácilmente.
- Preferir transform/opacity (GPU) frente a propiedades de layout.
- Accesibilidad: respetar `prefers-reduced-motion`.

## Procedimiento paso a paso

1. Parte de la plantilla y reemplaza los paths por tu ilustración (exportada de Inkscape/Figma).
2. Anima con CSS keyframes o GSAP.
3. Previsualiza: `python -m studio serve` → 3D y Web → svg-css-character → Ver en vivo.
4. Captura: `python -m studio web svg-css-character --duration 4 --query color=%2343a047`.

## Comandos del estudio

```bash
python -m studio web svg-css-character --duration 4 --query "color=%23fb8c00" -o naranja_svg.mp4
```

## Ejemplo completo

Icono de 'me gusta' animado para una web: SVG del corazón con `stroke-dashoffset` + `scale` con rebote en hover, y versión MP4 para redes.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| svg-css-character.html | plantilla SVG+CSS | ✅ instalado y probado |
| GSAP DrawSVG/MorphSVG | SVG avanzado (plugins incluidos en gsap, sin probar) | 📦 incluido, sin probar |
| Inkscape (gratis) | edición SVG | 💻 programa externo recomendado |

## Control de calidad

- [ ] Pivotes correctos (sin piezas que 'vuelan').
- [ ] Funciona en Chrome, Firefox y Safari.
- [ ] Peso < 50 KB.

## Errores comunes y cómo evitarlos

- transform-origin en SVG sin fill-box rota respecto al lienzo.
- Animar `d` sin el mismo número de puntos (morph) falla sin plugin.

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
