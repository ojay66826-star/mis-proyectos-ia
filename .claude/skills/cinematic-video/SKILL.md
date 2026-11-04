---
name: cinematic-video
description: Dirige videos con lenguaje de cine: planos (general, medio, primer plano), movimientos de cámara, ritmo de montaje, grading, música épica y títulos. Úsala para 'video cinematográfico', 'tráiler', 'corto de cine', 'que parezca una película'.
---

# Video cinematográfico

**Categoría:** Videos y contenido · **Skills relacionadas:** `cinematic-effects`, `3d-camera-animation`, `video-editing`

Une `cinematic-effects` (look) con dirección: cada escena es un plano con intención; la duración y la cámara siguen la tensión dramática; la música `epic` crece; transiciones `dip` a negro en cambios de acto.

## Cuándo usar esta Skill

- Tráileres, presentaciones dramáticas, cortos narrativos.

## Principios profesionales

- Planos: establecimiento (general) → acción (medio) → emoción (primer plano/dolly_in).
- Ritmo: planos largos al principio, cortos en el clímax.
- Regla de tercios y aire en la dirección de mirada.
- Un clímax visual y sonoro claro.

## Procedimiento paso a paso

1. Escribe un beat sheet de 4–6 planos.
2. Plan con `--style cinematic --transition dip`.
3. Asigna cámara por plano (pan, dolly_in, shake, zoom_out final).
4. Render `fullhd` y exporta preset `youtube`.

## Comandos del estudio

```bash
python -m studio make "Crea una animación cinematográfica de un robot en la ciudad de noche" --style cinematic --transition dip
python -m studio export projects/<…>/final.mp4 --preset youtube
```

## Ejemplo completo

Tráiler: plano general de ciudad (pan, 4 s) → robot camina (dolly_in) → amenaza (lightning + shake) → clímax (explosion) → título final con logo animado.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D/3D + style cinematic | look de cine | ✅ motor propio del estudio |
| Blender EEVEE/Cycles | planos 3D | ✅ instalado y probado |
| DaVinci Resolve | montaje/grading profesional | 💻 programa externo recomendado |

## Control de calidad

- [ ] Cada plano tiene propósito.
- [ ] Audio con dinámica (silencio antes del clímax).
- [ ] Letterbox y grading consistentes.

## Errores comunes y cómo evitarlos

- Todos los planos iguales en duración = monótono.
- Música a todo volumen tapando efectos.

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
