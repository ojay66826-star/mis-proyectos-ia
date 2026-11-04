---
name: tiktok-animation
description: Animaciones verticales 9:16 para TikTok, Instagram Reels y Facebook: gancho inmediato, tendencias de baile, subtítulos grandes en zona segura, ritmo con la música y bucle. Úsala para 'para TikTok', 'Reels', 'video vertical', 'trend', 'baile de TikTok'.
---

# Animación para TikTok / Reels

**Categoría:** Videos y contenido · **Skills relacionadas:** `short-video-animation`, `character-dancing`, `kinetic-typography`

El planificador cambia a 9:16 con palabras como tiktok/reels/shorts, usa subtítulos grandes centrados en la zona media-baja (y≈70 %), personajes al 42 % del ancho y música con tempo marcado.

## Cuándo usar esta Skill

- El destino es TikTok, Reels o Stories.

## Principios profesionales

- 0.5 s de gancho; nada de logos al inicio.
- Ritmo sincronizado al beat (cortes y saltos en el pulso).
- Zona segura: margen superior 10 %, inferior 20 %, derecho 15 %.
- Duración 7–20 s para máxima retención.

## Procedimiento paso a paso

1. `make "… para TikTok …"` o `--format 9:16`.
2. Revisa el storyboard vertical.
3. Exporta `--preset tiktok` (1080×1920).
4. Opcional: `loop` para enganchar.

## Comandos del estudio

```bash
python -m studio make "Crea una animación para TikTok de un plátano que baila"
python -m studio export projects/<…>/final.mp4 --preset tiktok
python -m studio text "¿Sabías esto? Las fresas no son bayas" --format 9:16 --mode pop     # texto viral
```

## Ejemplo completo

Trend de baile: plátano y fresa bailan en escenario (dance + confeti), 12 s, subtítulos amarillos, preset tiktok y GIF para previsualizar.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D 9:16 | render vertical | ✅ motor propio del estudio |
| kinetic_typography | textos virales | ✅ motor propio del estudio |
| Preset tiktok | 1080×1920 CRF 20 | ✅ motor propio del estudio |

## Control de calidad

- [ ] Nada importante en la franja inferior 20 %.
- [ ] Primer frame atractivo (es la portada).
- [ ] Audio no satura en móvil.

## Errores comunes y cómo evitarlos

- Usar 16:9 con barras negras: penaliza alcance.
- Subtítulos pequeños ilegibles en móvil.

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
