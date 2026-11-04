---
name: horror-animation
description: Terror y suspenso: desaturación, viñeta fuerte, parpadeo de luz, grano, niebla, rayos, fantasmas, sustos con cámara y drones sonoros disonantes. Úsala para 'terror', 'miedo', 'Halloween', 'suspenso', 'casa embrujada', 'fantasma'.
---

# Animación de terror (apta para todo público o suave)

**Categoría:** Estilos especiales · **Skills relacionadas:** `smoke-animation`, `lightning-effects`, `animation-sound-design`

`style: horror` desatura al 35 %, tiñe hacia rojo-verdoso, aplica viñeta intensa, parpadeo irregular de luz y grano fuerte. El planificador usa `haunted` (bosque muerto + niebla + luna), música `spooky` (drone + viento + campanas disonantes), personajes niño + fantasma.

## Cuándo usar esta Skill

- Halloween, historias de miedo, suspenso.

## Principios profesionales

- El miedo está en lo que no se ve: oscuridad y sonido.
- Construir tensión (lento) → susto (rápido + sonido) → alivio.
- Planos cerrados y cámara inestable.
- Mantener un nivel apto para el público objetivo.

## Procedimiento paso a paso

1. `make … --style horror` (o palabras terror/miedo/embrujado).
2. Escena 1 tensión (walk scared + fog), 2 susto (lightning + shake + fantasma), 3 huida (run).
3. Revisa que el susto no sea excesivo si es para niños.

## Comandos del estudio

```bash
python -m studio make "Un fantasma asusta a un niño en un bosque embrujado" --style horror
```

## Ejemplo completo

Corto de Halloween de 11 s con 3 escenas, truenos, niebla, 'Continuará…' y música spooky.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| style horror | look de terror | ✅ motor propio del estudio |
| effects fog/lightning/smoke | atmósfera | ✅ motor propio del estudio |
| sox | efectos de audio extra (reverb, pitch) | ✅ instalado y probado |

## Control de calidad

- [ ] Imagen oscura pero legible.
- [ ] Flashes con periodo ≥ 1.5 s (fotosensibilidad).
- [ ] Apto para la edad indicada.

## Errores comunes y cómo evitarlos

- Todo negro = no se ve nada: subir ligeramente la luz de personajes.
- Sustos constantes dejan de asustar.

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
