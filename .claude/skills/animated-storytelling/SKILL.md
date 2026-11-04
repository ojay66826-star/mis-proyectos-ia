---
name: animated-storytelling
description: Aplica técnicas narrativas a videos animados: estructura en actos, viaje del héroe, ganchos, ritmo, subtexto, payoff y moraleja; adapta la historia al formato y duración. Úsala para 'cuenta una historia', 'narrativa', 'guion con moraleja', 'storytelling para mi marca'.
---

# Narrativa animada (storytelling)

**Categoría:** Videos y contenido · **Skills relacionadas:** `story-animation`, `animation-scripting`, `animation-storyboarding`, `character-emotions`

Capa de dirección narrativa por encima de `story-animation` y `animation-scripting`: decide qué contar, en qué orden y con qué emoción, y lo traduce a escenas del proyecto (duración, cámara, música, efectos).

## Cuándo usar esta Skill

- Historias con propósito (educativo, marca, emocional).
- Adaptar un texto/cuento a video.

## Principios profesionales

- Personaje con deseo + obstáculo + cambio = historia.
- Setup/payoff: lo que se presenta en la escena 1 se paga al final.
- Mostrar en vez de narrar; voz en off solo si aporta.
- Duración: 15 s = 3 beats, 60 s = 6–8 beats.

## Procedimiento paso a paso

1. Resume en logline.
2. Divide en beats (escenas) con emoción objetivo.
3. Asigna recursos visuales (cámara, música, efectos) a cada beat.
4. Genera con `plan` (o `--ai`), edita y renderiza.
5. Valida: ¿se entiende sin sonido? ¿el final paga el inicio?

## Comandos del estudio

```bash
python -m studio plan "Una naranja tímida quiere cantar en el escenario pero tiene miedo; sus amigos la animan y triunfa" --ai -o historia.json
python -m studio render historia.json
```

## Ejemplo completo

Storytelling de marca (panadería): mascota estrella busca el pan perfecto (park) → se le quema (fire + smoke) → aprende con un amigo (idea) → celebra con clientes (confetti) → logo final.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Planificador + Claude (opcional) | estructura y diálogos | 🔑 requiere clave API |
| Motor 2D/3D | escenificación | ✅ motor propio del estudio |

## Control de calidad

- [ ] Logline clara.
- [ ] Cada escena avanza la historia.
- [ ] Final emocional o con moraleja.

## Errores comunes y cómo evitarlos

- Demasiados personajes para la duración.
- Final abrupto sin cierre.

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
