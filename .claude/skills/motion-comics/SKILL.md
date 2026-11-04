---
name: motion-comics
description: Convierte historias en cómic animado: viñetas, tramas de semitono, globos/rótulos, paneos sobre ilustraciones y animación limitada. Úsala para 'motion comic', 'cómic animado', 'historieta animada', 'manga animado'.
---

# Motion comics (cómic animado)

**Categoría:** Animación 2D · **Skills relacionadas:** `animated-storytelling`, `typography-animation`, `video-editing`

El estilo `comic` aplica trama de puntos (halftone) dependiente de la luminancia, contornos marcados y 12 fps. Se combina con rótulos (`caption`), subtítulos y movimientos de cámara (pan/zoom) para recorrer la 'viñeta'. Para ilustraciones propias usa `img2video` con `--move pan_*`.

## Cuándo usar esta Skill

- Narrativas con texto, cómics existentes o ilustraciones fijas que hay que animar.
- Trailers estilo novela gráfica.

## Principios profesionales

- Cada viñeta = un plano; la cámara guía la lectura (izquierda→derecha, arriba→abajo).
- Animación limitada: solo se mueve lo esencial (ojos, boca, partículas).
- Rótulos breves con tipografía bold y contorno.
- Ritmo: 2.5–4 s por viñeta.

## Procedimiento paso a paso

1. Divide la historia en viñetas (escenas) con un `caption` cada una.
2. Renderiza con `--style comic`.
3. Para páginas de cómic reales: corta cada viñeta como imagen y usa `python -m studio img2video viñeta.png --move pan_right --style none`.
4. Une los clips con `exporter.concat` (xfade) o la Skill `video-editing`.

## Comandos del estudio

```bash
python -m studio make "Un superhéroe robot salva la ciudad" --style comic
python -m studio img2video vineta1.png --move pan_right --style none --duration 4 -o v1.mp4
```

## Ejemplo completo

«Anima mi cómic de 4 viñetas»: un `img2video` por viñeta (pan/zoom alternados) + `concat` con transición `fade` + música `epic`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (style comic) | halftone + contornos | ✅ motor propio del estudio |
| img2video | paneos sobre viñetas | ✅ motor propio del estudio |
| Remotion | rótulos/globos programáticos | ✅ instalado y probado |

## Control de calidad

- [ ] La trama no oculta las caras.
- [ ] Rótulos legibles en móvil.
- [ ] Orden de lectura correcto.

## Errores comunes y cómo evitarlos

- Trama demasiado densa en 9:16 pequeño.
- Paneos rápidos impiden leer.

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
