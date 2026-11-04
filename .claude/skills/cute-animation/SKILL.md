---
name: cute-animation
description: Animación kawaii/tierna: proporciones chibi, ojos grandes, mejillas sonrosadas, paleta pastel, movimientos rebotones, corazones y destellos, música de caja de música. Úsala para 'tierno', 'kawaii', 'cute', 'adorable', 'para niños pequeños'.
---

# Animación tierna (kawaii)

**Categoría:** Estilos especiales · **Skills relacionadas:** `cartoon-animation`, `mascot-animation`, `character-expressions`

`style: cute` agranda los ojos 12 %, añade rubor permanente, aclara la paleta (pastel) y usa contorno fino; música `cute` (F mayor, campanas). Efectos recomendados: hearts, sparkles, bubbles.

## Cuándo usar esta Skill

- Contenido infantil, stickers, saludos, mascotas tiernas.

## Principios profesionales

- Formas redondas, sin esquinas.
- Rebote suave en todo (squash ligero).
- Paleta pastel con alto valor.
- Expresiones felices y sorpresas suaves.

## Procedimiento paso a paso

1. `make … --style cute`.
2. Elige conejo, gato, panda, fresa, estrella.
3. Añade `hearts` o `sparkles`.
4. Exporta GIF/Lottie para stickers.

## Comandos del estudio

```bash
python -m studio make "Un conejo tierno camina en la nieve" --style cute
python -m studio lottie --color "#f8bbd0" -o sticker_kawaii.json
```

## Ejemplo completo

Tarjeta de cumpleaños: panda y fresa kawaii celebran con confeti y corazones, 8 s, cuadrado 1:1.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| style cute | kawaii | ✅ motor propio del estudio |
| Lottie generator | stickers | ✅ motor propio del estudio |

## Control de calidad

- [ ] Colores pastel sin perder contraste del personaje.
- [ ] Ritmo alegre.
- [ ] Sin expresiones agresivas.

## Errores comunes y cómo evitarlos

- Fondos pastel + personaje pastel = sin contraste: usa contorno o fondo más saturado.
- Música demasiado rápida para lo tierno.

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
