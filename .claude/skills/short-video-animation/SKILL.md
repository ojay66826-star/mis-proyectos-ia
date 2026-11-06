---
name: short-video-animation
description: Videos animados de 5–60 s optimizados para retención: gancho en el primer segundo, ritmo rápido, subtítulos grandes, bucle y formatos verticales/cuadrados. Úsala para 'video corto', 'clip para redes', 'reel', 'short', 'video viral'.
---

# Animaciones cortas para redes

**Categoría:** Videos y contenido · **Skills relacionadas:** `tiktok-animation`, `youtube-animation`, `seamless-loop-animation`

El planificador detecta 'short/reel/vertical' → formato 9:16 y subtítulos grandes amarillos con contorno. Esta Skill añade reglas de retención y exportación multi-plataforma.

## Cuándo usar esta Skill

- Contenido para redes sociales en general (ver también youtube/tiktok).

## Principios profesionales

- Gancho visual en 0–1 s (acción, no título lento).
- Cambio visual cada 1.5–3 s.
- Subtítulos siempre (80 % se ve sin sonido).
- Final que enlaza con el inicio (loop).

## Procedimiento paso a paso

1. Plan con `--format 9:16 --duration 15`.
2. Desactiva el título inicial si roba el gancho (`show_title: false`).
3. Render, luego `loop` si aplica.
4. Exporta: `--preset tiktok`, `youtube_shorts`, `instagram`.

## Comandos del estudio

```bash
python -m studio make "Un plátano baila y hace un truco increíble" --format 9:16 --duration 15
python -m studio export projects/<…>/final.mp4 --preset youtube_shorts
```

## Fragmento de proyecto (project.json)

```json
{"format": "9:16", "subtitles": "big", "show_title": false, "transition": "cut"}
```

## Ejemplo completo

Reel de 12 s: gancho con salto (jump) en el segundo 0, baile con confeti, remate con celebrate; corte seco entre escenas; loop.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (9:16) | render vertical | ✅ motor propio del estudio |
| exporter presets | tiktok/shorts/instagram | ✅ motor propio del estudio |
| CapCut | ajustes finales manuales (`export --preset capcut` prepara las capas) | 💻 programa externo recomendado |

## Control de calidad

- [ ] Gancho en el primer segundo.
- [ ] Texto dentro de zonas seguras (no bajo la UI de la app).
- [ ] Duración ≤ 60 s.

## Errores comunes y cómo evitarlos

- Texto en el 15 % inferior queda tapado por la interfaz de TikTok/Reels.
- Intros largas matan la retención.

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
