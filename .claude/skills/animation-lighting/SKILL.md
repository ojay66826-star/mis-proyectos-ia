---
name: animation-lighting
description: Diseña la iluminación: tres puntos (key, fill, rim), hora del día (día, atardecer, noche), color de la luz con intención emocional, focos de escenario, exposición y tone mapping (AgX/Filmic/ACES) en 2D, Blender y Three.js. Úsala para 'iluminación', 'luces', 'que se vea más bonito', 'ambiente nocturno', 'luz dramática'.
---

# Iluminación para animación

**Categoría:** Producción profesional · **Skills relacionadas:** `cinematic-effects`, `3d-environment-animation`, `animation-rendering`

2D: `time_of_day` cambia paleta (sunset tinta naranja, night oscurece al 45 %), sol con halo, luna y estrellas; los estilos añaden grading/bloom. 3D: `lights()` crea sun key + area fill + area rim con energía por hora, focos RGB en `stage`, transform AgX. Three.js: hemisferio + key con sombras + rim y ACES.

## Cuándo usar esta Skill

- Ajustar ambiente y emoción.
- Escenas 3D que se ven planas o quemadas.

## Principios profesionales

- Key define la forma; fill controla el contraste; rim separa del fondo.
- Ratio key:fill 2:1 (amable) a 8:1 (dramático).
- Temperatura con significado: cálido = seguridad, frío = misterio.
- Exposición sin quemar blancos (tone mapping).

## Procedimiento paso a paso

1. Elige hora del día por escena.
2. En 3D ajusta energías en `lights()` o en el `.blend`.
3. Revisa histograma/frame y corrige.
4. Aplica estilo (cinematic/fantasy) para grading final.

## Comandos del estudio

```bash
python -m studio make "Un oso acampa en el bosque al atardecer" --quality preview
python -m studio make "Un gato baila en el escenario" --3d --quality preview     # focos de colores
```

## Ejemplo completo

Escena de terror más legible: mantener `night` pero añadir `fireflies`/`fire` como fuentes de luz motivadas cerca del personaje.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| backgrounds (time_of_day) | luz 2D | ✅ motor propio del estudio |
| Blender lights + AgX | luz 3D | ✅ instalado y probado |
| Three.js lights + ACES | luz web | ✅ instalado y probado |
| Poly Haven HDRI | iluminación realista | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Personajes bien iluminados (cara legible).
- [ ] Sin zonas quemadas.
- [ ] Coherencia de dirección de luz entre planos.

## Errores comunes y cómo evitarlos

- Energías de luz en Blender demasiado altas (colores lavados).
- Noche totalmente negra.

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
