---
name: kinetic-typography
description: Tipografía cinética sincronizada con música o voz: palabras en el beat, escalas y rotaciones expresivas, cambios de color, fondo dinámico y barra de progreso; estilo lyric video y reels virales. Úsala para 'tipografía cinética', 'kinetic typography', 'lyric video', 'texto al ritmo'.
---

# Tipografía cinética

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `typography-animation`, `music-video-animation`, `tiktok-animation`

`kinetic_typography` coloca una palabra por pulso según el BPM del mood (dance=124), agrupa en pantallas de hasta 3 palabras y añade pop/whoosh por palabra; `kinetic-type.html` (GSAP) alterna 4 efectos (escala+rotación, subida, entrada lateral con skew, elástico vertical) sobre un degradado animado con barra de progreso.

## Cuándo usar esta Skill

- Reels de texto, letras de canciones, frases motivacionales, anuncios.

## Principios profesionales

- Sincronía exacta con el pulso.
- Énfasis en palabras clave (tamaño/color).
- Variedad de movimientos con coherencia.
- Contraste fuerte con el fondo.

## Procedimiento paso a paso

1. Escribe el texto en frases cortas.
2. Python: `python -m studio text "…" --music dance`.
3. Web/GSAP: `python -m studio web kinetic-type --query "text=…&bpm=120"`.
4. Exporta vertical para redes.

## Comandos del estudio

```bash
python -m studio text "Crea animaciones increíbles con inteligencia artificial" --mode pop --format 9:16
python -m studio web kinetic-type --query "text=Tu historia merece moverse&bpm=110" --width 1080 --height 1920
```

## Ejemplo completo

Lyric video: dividir la letra por compases; `text` por frase con el mismo `music` y BPM de la canción; unir y añadir la canción con `add_audio`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| kinetic_typography (Python) | rápido, sin navegador | ✅ motor propio del estudio |
| kinetic-type.html (GSAP) | efectos web | ✅ instalado y probado |
| Remotion | kinetic con springs | ✅ instalado y probado |

## Control de calidad

- [ ] Palabras en el beat.
- [ ] Texto completo y sin erratas.
- [ ] Legible en móvil.

## Errores comunes y cómo evitarlos

- BPM de la plantilla distinto al de la canción.
- Palabras muy largas reducen el tamaño: el motor ajusta pero conviene partirlas.

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
