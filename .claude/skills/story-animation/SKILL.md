---
name: story-animation
description: Construye historias animadas completas con estructura narrativa (inicio, conflicto, clímax, resolución), varios personajes, diálogos y música. Úsala para 'haz una historia', 'cuento animado', 'episodio', 'fábula', 'historia con frutas/animales'.
---

# Animación de historias

**Categoría:** Animación 2D · **Skills relacionadas:** `animated-storytelling`, `animation-scripting`, `character-dialogue`, `animation-storyboarding`

Combina `animation-scripting` (guion) con el motor 2D. El planificador detecta 'historia/cuento' y crea 4 escenas: presentación (walk + saludo), problema (efecto climático o peligro, miedo), solución (idea + celebración con confeti) y despedida al atardecer con 'Fin'.

## Cuándo usar esta Skill

- 'Historia', 'cuento', 'episodio', 'fábula', 'aventura'.
- Contenido educativo o infantil con moraleja.

## Principios profesionales

- Estructura en 3 actos aunque dure 20 s.
- Un deseo claro del protagonista y un obstáculo visible.
- El clímax tiene la mayor energía visual (efectos, cámara, música).
- Cierre emocional (atardecer, despedida, 'Fin').

## Procedimiento paso a paso

1. Escribe la premisa en una frase: «<personaje> quiere <deseo> pero <obstáculo>».
2. Genera el plan (`--ai` si hay ANTHROPIC_API_KEY para diálogos más creativos).
3. Edita diálogos en la interfaz (pestaña Crear → Ver guion) o en el JSON.
4. Renderiza en borrador, ajusta duraciones, render final.

## Comandos del estudio

```bash
python -m studio make "Haz una historia con frutas animadas en la cocina"
python -m studio plan "Una fábula de un conejo y un zorro que aprenden a compartir" --ai -o fabula.json   # con Claude
python -m studio render fabula.json
```

## Ejemplo completo

«Historia con frutas animadas»: reparto Manzana, Plátano, Fresa y Naranja en la cocina; escena 2 con lluvia y miedo, escena 3 con
idea y celebración, escena 4 despedida. Video ~15 s con voces distintas por personaje y SRT.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Planificador local | estructura y diálogos por plantillas | ✅ motor propio del estudio |
| Claude API (opcional) | guiones creativos estructurados | 🔑 requiere clave API |
| Motor 2D/3D | render | ✅ motor propio del estudio |

## Control de calidad

- [ ] Se entiende la historia sin sonido (acciones claras).
- [ ] Cada personaje tiene al menos una línea o acción propia.
- [ ] Final claro.

## Errores comunes y cómo evitarlos

- Historias de más de 6 escenas sin subtramas se vuelven monótonas.
- Diálogos que explican lo que ya se ve.

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
