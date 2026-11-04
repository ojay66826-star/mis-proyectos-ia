---
name: css-animation
description: Animaciones con CSS puro: @keyframes, transiciones, timing functions (cubic-bezier, steps), transform/opacity, animación de variables y control con Web Animations API; ideal para UI y webs ligeras. Úsala para 'animación CSS', 'keyframes', 'animar un botón', 'loader', 'microinteracciones'.
---

# Animación CSS

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `svg-animation`, `gsap-animation`, `interactive-animation`

La plantilla SVG+CSS demuestra squash & stretch, parpadeo con `steps(1)` y deriva infinita, todo en CSS. Para capturar, `window.__seek(t)` pausa cada animación (`document.getAnimations()`) y fija `currentTime` — técnica válida para cualquier página con CSS animations.

## Cuándo usar esta Skill

- Microinteracciones, loaders, banners web, animaciones de UI.

## Principios profesionales

- Animar solo `transform` y `opacity` para 60 fps.
- Duraciones de UI 150–400 ms; ilustraciones 0.6–3 s.
- `cubic-bezier(.34,1.56,.64,1)` para overshoot.
- `@media (prefers-reduced-motion)` para accesibilidad.

## Procedimiento paso a paso

1. Escribe @keyframes y aplica `animation`.
2. Ajusta timing con cubic-bezier.
3. Para video: añade el `__seek` de la plantilla y captura con `python -m studio web <archivo.html>`.

## Comandos del estudio

```bash
python -m studio web svg-css-character --duration 3
python -m studio web ruta/a/mi_animacion.html --duration 5 --width 1080 --height 1080
```

## Ejemplo completo

Loader de marca: tres frutas que botan con `animation-delay` escalonado (0, .15s, .3s), `ease-in-out infinite`; capturado a GIF para redes.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| CSS + Web Animations API | animación nativa | ✅ instalado y probado |
| capture.mjs | CSS → MP4 | ✅ instalado y probado |
| Animista / cubic-bezier.com | generadores de keyframes y curvas | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Fluido a 60 fps (DevTools Performance).
- [ ] Respeta reduced-motion.
- [ ] Sin saltos de layout.

## Errores comunes y cómo evitarlos

- Animar `top/left/width` provoca reflow.
- `transform` sobrescribe otros transforms del mismo elemento: anida elementos.

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
