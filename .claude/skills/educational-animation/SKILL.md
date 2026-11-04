---
name: educational-animation
description: Videos educativos claros: presentador animado, pizarra/aula, explicación paso a paso, ejemplos visuales, infografías, subtítulos, repaso final y ritmo adaptado a la edad. Úsala para 'educativo', 'explica', 'clase', 'lección', 'tutorial animado', 'para enseñar'.
---

# Animación educativa

**Categoría:** Estilos especiales · **Skills relacionadas:** `infographic-animation`, `kinetic-typography`, `animation-scripting`

El planificador reconoce 'clase/aula/explica' → escenario `classroom` (pizarra), personaje presentador que `talk`, subtítulos y música `calm`. Las infografías (`infographic`) y textos animados (`text`) ilustran datos y conceptos.

## Cuándo usar esta Skill

- Lecciones, divulgación, onboarding, formación.

## Principios profesionales

- Un concepto por escena; máximo 3 conceptos por video corto.
- Ejemplo concreto después de cada idea.
- Repetición final (resumen).
- Lenguaje y ritmo según la edad (niños: frases ≤ 8 palabras).

## Procedimiento paso a paso

1. Define objetivo de aprendizaje.
2. Guion: gancho (pregunta) → explicación → ejemplo → resumen.
3. Escenas en `classroom` con `talk`; inserta infografías.
4. Une con `concat` y añade SRT.

## Comandos del estudio

```bash
python -m studio make "Clase educativa: un robot explica en el aula por qué llueve" --style minimalist
python -m studio infographic "Mercurio=0.38,Tierra=1,Júpiter=11.2" --title "Tamaño de los planetas (Tierra=1)"
```

## Ejemplo completo

Lección de 40 s sobre el ciclo del agua: robot en el aula (talk) → escena con lluvia → infografía de etapas → resumen y 'Fin'.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (classroom + talk) | presentador | ✅ motor propio del estudio |
| infographic/kinetic text | datos y conceptos | ✅ motor propio del estudio |
| Claude (opcional) | guion didáctico | 🔑 requiere clave API |

## Control de calidad

- [ ] Información correcta (revisar datos).
- [ ] Subtítulos completos.
- [ ] Ritmo que permite leer.

## Errores comunes y cómo evitarlos

- Datos inventados: verifica cifras antes de animarlas.
- Pizarra con texto fijo irrelevante: personaliza si es necesario.

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
