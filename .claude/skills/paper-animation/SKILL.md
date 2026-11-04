---
name: paper-animation
description: Estética de papel: textura de papel con fibras, tonos cálidos, sin contornos, sombras proyectadas, capas recortadas y movimiento a saltos (12 fps). Úsala para 'papel', 'papercraft', 'origami', 'recortes de papel', 'collage'.
---

# Animación de papel (papercraft)

**Categoría:** Estilos especiales · **Skills relacionadas:** `cutout-animation`, `stop-motion`, `educational-animation`

`style: paper` añade textura de papel (ruido de fibras) con tinte cálido, quita contornos y cel shading, y aplica cadencia de 12 fps con jitter de recorte. Complementa con escenarios de capas (paralaje) que simulan teatro de papel.

## Cuándo usar esta Skill

- Cuentos, educación, explicativos artesanales.

## Principios profesionales

- Capas planas a distintas profundidades.
- Sombra corta bajo cada capa.
- Paleta limitada de cartulinas.
- Imperfecciones intencionales.

## Procedimiento paso a paso

1. `make … --style paper`.
2. Prefiere cámara `pan` para lucir el paralaje.
3. Música `calm` o `cute`.

## Comandos del estudio

```bash
python -m studio make "Un zorro y una rana cuentan un cuento en el bosque" --style paper
```

## Ejemplo completo

Cuento de papel de 30 s: 4 escenas en forest/park con paneos, narración por personajes y subtítulos.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| style paper | papel digital | ✅ motor propio del estudio |
| Blender (planos con grosor + textura) | papercraft 3D | ✅ instalado y probado |

## Control de calidad

- [ ] Textura de papel visible en zonas planas.
- [ ] Sin contornos negros.
- [ ] Paralaje perceptible.

## Errores comunes y cómo evitarlos

- Combinar papel con efectos de partículas brillantes rompe el estilo (usa leaves, confetti).
- Fondos con degradados fuertes no parecen papel.

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
