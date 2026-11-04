---
name: cartoon-animation
description: Produce caricaturas animadas clásicas: contornos gruesos, colores saturados, brazos de 'manguera' con guantes blancos, squash & stretch exagerado y gags. Úsala para 'caricatura', 'dibujo animado', 'cartoon', 'estilo Cartoon Network/rubber hose'.
---

# Animación de caricaturas (cartoon)

**Categoría:** Animación 2D · **Skills relacionadas:** `2d-animation`, `character-expressions`, `cute-animation`, `animation-sound-design`

Estilo cartoon del estudio (`style: cartoon`): silueta con contorno oscuro automático, sombreado cel de una sola banda, brillo especular, extremidades tipo rubber-hose con guantes y zapatos, y física exagerada en saltos y celebraciones.

## Cuándo usar esta Skill

- El usuario pide 'caricatura', 'cartoon', 'dibujo animado' o un tono humorístico infantil.
- Contenido para niños, mascotas de marca, sketches cómicos.

## Principios profesionales

- Exageración: anticipación marcada antes de cada salto (squash 25 %), stretch en el aire.
- Poses claras y legibles en silueta; una idea por pose.
- Timing cómico: pausa (hold) de 0.3 s antes del remate del gag.
- Paleta saturada con fondo más claro y menos contrastado que los personajes.
- Sonido cartoon: boing en celebraciones, pops y whoosh en transiciones (automático).

## Procedimiento paso a paso

1. Define el gag o la historia en 3 golpes: presentación → problema → remate.
2. Elige personajes con siluetas distintas (p. ej. manzana redonda + plátano alargado).
3. Planifica con `--style cartoon` y revisa que cada escena tenga una acción exagerada (jump, celebrate, scared_shake).
4. Añade efectos de apoyo: `confetti`, `sparkles`, `speedlines` para gags rápidos.
5. Renderiza y revisa el timing en `vista_previa.gif`; ajusta duraciones de escena.

## Comandos del estudio

```bash
python -m studio make "Una fresa intenta saltar un charco y cae, luego celebra" --style cartoon
python -m studio character fresa --style cartoon --name Fresita     # hoja de personaje
python -m studio export projects/<…>/final.mp4 --preset youtube
```

## Ejemplo completo

**Petición:** «Haz una caricatura de un perro y un gato que se asustan con un rayo».
`python -m studio make "Un perro y un gato en el parque se asustan con un rayo" --style cartoon` → el planificador crea
presentación (wave), problema (scared_shake + lightning + truenos) y resolución (celebrate + confetti).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D `studio` (style cartoon) | render completo | ✅ motor propio del estudio |
| Blender Grease Pencil | cartoon dibujado a mano 2D/3D | ✅ instalado y probado |
| OpenToonz | producción cartoon tradicional | 💻 programa externo recomendado |
| Freesound.org | efectos cartoon reales (CC) | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Contornos continuos sin huecos.
- [ ] Cada salto tiene anticipación y aterrizaje con squash.
- [ ] El gag se entiende sin audio.

## Errores comunes y cómo evitarlos

- Gags sin pausa previa pierden gracia: deja 0.3–0.5 s de hold.
- Demasiados efectos a la vez tapan la acción.

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
