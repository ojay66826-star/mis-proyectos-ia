---
name: pixel-art-animation
description: Animaciones retro en pixel art: baja resolución, paleta limitada, escalado sin suavizado (nearest neighbor), 8–12 fps y ciclos cortos. Úsala para 'pixel art', '8 bits', '16 bits', 'estilo videojuego retro'.
---

# Animación pixel art

**Categoría:** Animación 2D · **Skills relacionadas:** `sprite-animation`, `minimalist-animation`, `animation-optimization`

El estilo `pixel` renderiza la escena normal, la reduce a ~240 px de ancho, cuantiza a 40 colores (median cut) y la reescala con vecino más cercano: píxeles nítidos y paleta coherente. Ideal para intros de juegos, streams y redes.

## Cuándo usar esta Skill

- 'Pixel art', '8-bit', 'retro gaming', 'sprite', 'arcade'.
- Contenido gamer o nostálgico.

## Principios profesionales

- Resolución base baja y fija; nunca escalar por factores no enteros en el resultado final.
- Paleta limitada (16–40 colores) con rampas de sombreado.
- Animación a 8–12 fps con ciclos de 4–8 frames.
- Evitar antialiasing y degradados suaves.

## Procedimiento paso a paso

1. Planifica con `--style pixel` (fps 12 automático).
2. Prefiere escenarios simples (park, space, desert) y personajes con siluetas fuertes.
3. Exporta GIF para redes: `python -m studio export final.mp4 --preset gif`.
4. Para sprites de juego, ver Skill `sprite-animation`.

## Comandos del estudio

```bash
python -m studio make "Un robot salta en el espacio" --style pixel
python -m studio export projects/<…>/final.mp4 --preset gif
```

## Ejemplo completo

«Intro pixel para mi canal de juegos»: `python -m studio make "Un zorro corre por el bosque y salta" --style pixel --format 16:9 --mood action`, luego logo con `python -m studio logo "MiCanal"`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (style pixel) | pixelado + paleta | ✅ motor propio del estudio |
| Aseprite / LibreSprite | pixel art manual | 💻 programa externo recomendado |
| FFmpeg palettegen | GIF de alta calidad | ✅ instalado y probado |

## Control de calidad

- [ ] Píxeles cuadrados y nítidos (sin blur).
- [ ] Paleta consistente entre escenas.
- [ ] GIF < 8 MB para redes.

## Errores comunes y cómo evitarlos

- Re-escalar el MP4 con bicúbico arruina los píxeles: usa `flags=neighbor`.
- Texto pequeño ilegible tras pixelar.

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
