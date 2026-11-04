---
name: seamless-loop-animation
description: Crea loops perfectos sin salto visible: periodos que dividen la duración, partículas cíclicas, fondos periódicos y crossfade final; para GIFs, fondos de stream y redes. Úsala para 'bucle', 'loop infinito', 'GIF en bucle', 'fondo que se repite'.
---

# Animaciones en bucle perfecto

**Categoría:** Videos y contenido · **Skills relacionadas:** `animated-backgrounds`, `lottie-animation`, `animation-optimization`

Tres técnicas: (1) **matemática**: todo movimiento con periodo que divide la duración (fondos de `motiongraphics.animated_background` son periódicos por diseño); (2) **ciclos** de acción (walk 0.625 s, dance según BPM, jump 1.2 s); (3) **crossfade** final con `exporter.make_loop` (xfade del final con el inicio).

## Cuándo usar esta Skill

- GIFs, fondos animados, stickers, pantallas de espera, clips de redes en loop.

## Principios profesionales

- Duración = múltiplo común de los periodos usados.
- Cámara estática o periódica.
- Sin elementos que aparecen una sola vez.
- Verificar el punto de unión frame a frame.

## Procedimiento paso a paso

1. Para fondos: `python -m studio background blobs --duration 6`.
2. Para personajes: acción cíclica, `from == to`, duración múltiplo del ciclo.
3. Para cualquier video: `python -m studio loop video.mp4 --crossfade 0.5`.
4. Exporta GIF: `python -m studio export loop.mp4 --preset gif`.

## Comandos del estudio

```bash
python -m studio background particles --duration 8 --palette neon -o fondo_loop.mp4
python -m studio loop projects/<…>/final.mp4 --crossfade 0.6
python -m studio export fondo_loop.mp4 --preset gif
```

## Ejemplo completo

Sticker de fruta saltando en bucle: `lottie` (ya es cíclico) o `character3d manzana --action jump --duration 2.4` (2 saltos exactos).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| animated_background | fondos periódicos | ✅ motor propio del estudio |
| exporter.make_loop | crossfade de cierre | ✅ motor propio del estudio |
| FFmpeg palettegen | GIF | ✅ instalado y probado |

## Control de calidad

- [ ] El último frame enlaza con el primero.
- [ ] Sin parpadeo en la unión.
- [ ] Tamaño de GIF razonable.

## Errores comunes y cómo evitarlos

- Música en loop corta: quítala o usa audio en bucle.
- Partículas con vidas aleatorias que no cierran: usa la versión determinista del estudio.

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
