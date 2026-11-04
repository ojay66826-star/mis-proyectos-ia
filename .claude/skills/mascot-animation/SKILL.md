---
name: mascot-animation
description: Crea y anima mascotas para marcas, canales o negocios: diseño memorable, saludo, logo animado, intro/outro, stickers Lottie y versión 3D. Úsala para 'mascota', 'personaje para mi marca', 'intro de canal con mascota', 'stickers animados'.
---

# Animación de mascotas de marca

**Categoría:** Personajes · **Skills relacionadas:** `character-design`, `animated-logos`, `lottie-animation`, `youtube-animation`

Combina `character-design` (ficha con colores de marca), `animated-logos`, `lottie-animation` (stickers) y `3d-modeling`. Entregable típico: hoja de personaje, intro de 4–6 s (saludo + logo), outro (celebrate + 'suscríbete'), Lottie JSON y GLB.

## Cuándo usar esta Skill

- Branding con personaje.
- Intro/outro de YouTube o Twitch.
- Stickers para WhatsApp/Telegram.

## Principios profesionales

- Colores de marca en la ficha (HEX exacto).
- Pose firma (wave o celebrate) siempre igual.
- Duración de intro ≤ 5 s.
- Versiones: horizontal, vertical, cuadrada y transparente.

## Procedimiento paso a paso

1. Ficha: `python -m studio character mascota --name <Marca> --color <HEX> --accessory cap`.
2. Intro: `plan "una mascota saluda feliz" --background studio --duration 5 -o intro.json`, sustituye la ficha del reparto por la de tu mascota (mismo `id` en actores) y `render intro.json`.
3. Logo: `python -m studio logo "<Marca>" --color <HEX> --tagline …`.
4. Sticker Lottie: `python -m studio lottie --color <HEX>`.
5. 3D: `python -m studio character3d mascota --color <HEX>`.

## Comandos del estudio

```bash
python -m studio character mascota --name "Pixi" --color "#00b4d8" --accessory cap --style cute
python -m studio plan "una mascota saluda feliz y celebra" --background studio --duration 5 --style cute -o intro.json
# editar intro.json: characters[0] = ficha de Pixi (pixi_hoja.json)
python -m studio render intro.json
python -m studio logo "Pixi Studio" --color "#00b4d8" --tagline "Animación con IA"
python -m studio lottie --color "#00b4d8" -o pixi_sticker.json
```

## Ejemplo completo

Kit de mascota completo en una carpeta: hoja PNG/JSON, intro MP4, logo MP4, sticker Lottie y GLB 3D.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D/3D | mascota | ✅ motor propio del estudio |
| Lottie generator | stickers vectoriales | ✅ motor propio del estudio |
| LottieFiles | previsualizar/publicar Lottie | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Colores exactos de marca.
- [ ] Lottie abre en lottie-web.
- [ ] Intro ≤ 5 s y con sonido corto.

## Errores comunes y cómo evitarlos

- Mascotas con demasiados detalles no escalan a sticker.
- Usar personajes o marcas registradas de terceros (prohibido): crea diseños originales.

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
