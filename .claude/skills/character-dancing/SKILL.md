---
name: character-dancing
description: Coreografías de baile sincronizadas con el tempo de la música: rebote en el pulso, brazos alternos, balanceo, saltos, confeti y focos. Úsala para 'que baile', 'baile', 'fiesta', 'coreografía', 'TikTok dance'.
---

# Personajes que bailan

**Categoría:** Personajes · **Skills relacionadas:** `music-video-animation`, `tiktok-animation`, `character-animation`

La acción `dance` sincroniza el rebote con el BPM de la música del proyecto (dance = 124 BPM): el cuerpo cae en cada pulso con squash, los brazos alternan arriba/abajo cada compás y la mirada sigue el movimiento. El planificador crea escenas en `stage` con confeti y música `dance`.

## Cuándo usar esta Skill

- Baile, fiesta, celebración musical.
- Contenido para TikTok/Reels.

## Principios profesionales

- El impacto del movimiento cae en el beat.
- Variación cada 2–4 compases (dance → jump → celebrate).
- Formación: grupo en línea con el protagonista al centro.
- Luces de colores y confeti refuerzan la energía.

## Procedimiento paso a paso

1. Pide baile: `make "… baila …"`.
2. Ajusta `mood` (dance, happy, cute) o `bpm` en el JSON de música.
3. Alterna acciones por personaje para que no bailen idéntico.
4. Exporta vertical para redes.

## Comandos del estudio

```bash
python -m studio make "Crea una animación para TikTok de un plátano que baila" --format 9:16
python -m studio make "Las frutas hacen una fiesta de baile" --mood dance
```

## Ejemplo completo

TikTok de plátano bailando: 9:16, 3 escenas en escenario (dance+confeti, dance/jump, celebrate), subtítulos grandes amarillos y música dance 124 BPM.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (dance sincronizado) | baile procedural | ✅ motor propio del estudio |
| Blender (dance 3D) | baile 3D | ✅ instalado y probado |
| Mixamo dances | mocap de baile para humanoides | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Los rebotes coinciden con el bombo.
- [ ] Nadie se sale de cuadro en 9:16.
- [ ] Confeti no tapa caras.

## Errores comunes y cómo evitarlos

- Cambiar el mood sin cambiar bpm descoordina: el baile toma el BPM del mood.
- Muchos bailarines en 9:16: máximo 3.

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
