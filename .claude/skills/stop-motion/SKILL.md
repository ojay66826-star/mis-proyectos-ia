---
name: stop-motion
description: Simula stop-motion: 12 fps con poses mantenidas (on twos), micro-temblor de posición y rotación entre fotogramas, textura y viñeta; también guía para stop-motion real con cámara. Úsala para 'stop motion', 'cuadro a cuadro con objetos', 'animación con juguetes'.
---

# Stop-motion

**Categoría:** Estilos especiales · **Skills relacionadas:** `clay-animation`, `paper-animation`, `frame-by-frame-animation`

`style: stopmotion` cuantiza el tiempo a 1/12 s (las poses se mantienen 2 frames a 24 fps) y aplica un jitter determinista por pose (±1.5 px, ±0.6°) que imita la manipulación manual, más textura y viñeta suave. Para stop-motion real: fotos numeradas → FFmpeg.

## Cuándo usar esta Skill

- Look artesanal, juguetes, objetos animados.
- Ensamblar fotos de stop-motion reales del usuario.

## Principios profesionales

- 12 fps (o 8 para más carácter).
- El temblor es parte del encanto, pero sutil.
- Iluminación constante (evitar parpadeo de luz en fotos reales).
- Movimientos con easing marcados en poses clave.

## Procedimiento paso a paso

1. Digital: `make … --style stopmotion`.
2. Real: fotos con trípode y exposición manual → `foto_0001.jpg…`.
3. Ensamblar: `ffmpeg -framerate 12 -i foto_%04d.jpg -vf scale=1920:-2 -r 24 -pix_fmt yuv420p stop.mp4`.
4. Deflicker si hay parpadeo: `-vf deflicker`.

## Comandos del estudio

```bash
python -m studio make "Unos juguetes robot bailan en la mesa" --style stopmotion
ffmpeg -framerate 12 -i fotos/foto_%04d.jpg -vf "scale=1920:-2,deflicker" -r 24 -pix_fmt yuv420p stopmotion_real.mp4
```

## Ejemplo completo

Stop-motion real del usuario con 96 fotos → 8 s a 12 fps, deflicker, música `cute` del estudio con `add_audio`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| style stopmotion | simulación | ✅ motor propio del estudio |
| FFmpeg (deflicker) | ensamblado real | ✅ instalado y probado |
| Stop Motion Studio / qStopMotion | captura con papel cebolla | 💻 programa externo recomendado |

## Control de calidad

- [ ] Ritmo 12 fps estable.
- [ ] Sin parpadeo de exposición.
- [ ] Jitter apreciable pero no mareante.

## Errores comunes y cómo evitarlos

- Exposición automática de la cámara provoca parpadeo.
- Mezclar 24 fps fluido con stop-motion rompe el estilo.

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
