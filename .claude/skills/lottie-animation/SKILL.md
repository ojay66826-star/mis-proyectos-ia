---
name: lottie-animation
description: Genera animaciones Lottie (JSON Bodymovin v5) sin After Effects: capas de forma, keyframes con easing, squash & stretch, parpadeo y sombra; reproducción con lottie-web y captura a MP4/GIF; stickers para apps. Úsala para 'Lottie', 'animación JSON', 'sticker animado', 'animación para app'.
---

# Animación Lottie

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `svg-animation`, `mascot-animation`, `seamless-loop-animation`

`studio/lottie.py` escribe JSON Lottie válido (probado con lottie-web 5.12): personaje con cuerpo, hoja, brillo, ojos con parpadeo, pupilas, mejillas y boca, rebote con squash & stretch y sombra que escala. `lottie-player.html` lo reproduce y `__seek` permite capturarlo. Recuerda: en Lottie el primer elemento de la lista se dibuja encima.

## Cuándo usar esta Skill

- Animaciones para apps (Android/iOS/Flutter/React Native), webs y stickers.

## Principios profesionales

- Vectores = nitidez a cualquier tamaño y archivos pequeños.
- Keyframes con easing (`i`/`o` bezier).
- Loops cerrados (primer y último keyframe iguales).
- Evitar efectos no soportados por lottie-web (blur, expresiones).

## Procedimiento paso a paso

1. `python -m studio lottie --color "#e53935" -o personaje.json`.
2. Previsualiza: `templates/web/lottie-player.html?src=lottie/personaje.json`.
3. Captura a video: `python -m studio web lottie-player --query "src=lottie/personaje.json&loops=3"`.
4. Publica en LottieFiles o integra con lottie-web/lottie-android.

## Comandos del estudio

```bash
python -m studio lottie --color "#7e57c2" -o templates/web/lottie/uva.json
python -m studio web lottie-player --query "src=lottie/uva.json&loops=3&bg=%23ffffff" --width 512 --height 512 -o uva.mp4
```

## Ejemplo completo

Sticker de mascota para Telegram: generar Lottie, convertir a `.tgs` (gzip del JSON a 512×512, 60 fps, ≤3 s) con herramientas de Telegram.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| studio/lottie.py | generador Lottie | ✅ motor propio del estudio |
| lottie-web 5.12 | reproducción y captura | ✅ instalado y probado |
| LottieFiles | editor/preview online | 🌐 gratis, requiere internet |
| After Effects + Bodymovin | Lottie complejo | 💻 programa externo recomendado |

## Control de calidad

- [ ] Abre sin errores en lottie-web.
- [ ] Bucle limpio.
- [ ] Tamaño < 100 KB.

## Errores comunes y cómo evitarlos

- Orden de capas invertido (pupilas tapadas): el estudio ya invierte el orden.
- Keyframes con distinta dimensión (2D vs 3D) rompen la animación.

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
