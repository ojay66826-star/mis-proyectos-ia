---
name: typography-animation
description: Anima textos con criterio tipográfico: jerarquía, tracking, entrada/salida por letra, palabra o línea, máscaras, máquina de escribir, subtítulos estilizados y rótulos. Úsala para 'texto animado', 'título animado', 'subtítulos bonitos', 'rótulo', 'efecto máquina de escribir'.
---

# Animación tipográfica

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `kinetic-typography`, `motion-graphics`, `video-editing`

Modos de `kinetic_typography`: `pop` (escala con rebote), `slide` (entrada lateral alternada), `wave` (ondulación), `typewriter` (letra a letra). Subtítulos del motor 2D: estándar (caja negra) o `big` (amarillos con contorno, centrados). Rótulos de escena con `caption`.

## Cuándo usar esta Skill

- Títulos, citas, subtítulos estilizados, rótulos de capítulo.

## Principios profesionales

- Legibilidad primero: contraste ≥ 4.5:1, contorno en fondos complejos.
- Tiempo de lectura: ~3 palabras/segundo.
- Una familia tipográfica, 2 pesos.
- Animar con sentido de lectura (izquierda→derecha).

## Procedimiento paso a paso

1. Elige modo según tono (pop alegre, slide dinámico, typewriter narrativo).
2. Ajusta paleta y formato.
3. Para subtítulos grandes en el motor: `"subtitles": "big"`.

## Comandos del estudio

```bash
python -m studio text "Había una vez un pequeño robot" --mode typewriter --format 16:9 --palette oscuro --music calm
python -m studio make "Un robot cuenta un secreto" --format 9:16     # subtítulos grandes automáticos
```

## Ejemplo completo

Cita inspiradora para redes: `text "El mejor momento para empezar es ahora" --mode pop --palette pastel --format 1:1`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| kinetic_typography | texto animado | ✅ motor propio del estudio |
| kinetic-type.html (GSAP) | texto web | ✅ instalado y probado |
| Remotion TituloCinetico | texto con springs | ✅ instalado y probado |

## Control de calidad

- [ ] Cada palabra visible el tiempo suficiente.
- [ ] Sin cortes de palabras por ancho.
- [ ] Acentos y ñ correctos (fuente DejaVu).

## Errores comunes y cómo evitarlos

- Textos largos en modo pop (una pantalla por 3 palabras) se alargan mucho.
- Fuentes sin soporte de acentos.

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
