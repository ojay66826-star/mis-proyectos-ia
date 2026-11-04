---
name: clay-animation
description: Look de plastilina: sombreado suave, textura de arcilla con huellas, colores mate, 12 fps con temblor y viñeta; en 3D con materiales mate y subsurface. Úsala para 'plastilina', 'arcilla', 'claymation', 'estilo Aardman', 'muñecos de plasti'.
---

# Animación de plastilina (claymation)

**Categoría:** Estilos especiales · **Skills relacionadas:** `stop-motion`, `cute-animation`, `3d-animation`

`style: clay` usa sombreado degradado (no cel), sin contorno, textura de ruido multiplicada (huellas) y la cadencia stop-motion. En 3D, materiales con roughness 0.6–0.8 y subsurface ligero dan aspecto de arcilla.

## Cuándo usar esta Skill

- Estética artesanal infantil, publicidad cálida.

## Principios profesionales

- Formas redondeadas y gruesas.
- Colores mate saturados, sin brillos especulares fuertes.
- Movimiento a 12 fps con imperfección.
- Iluminación suave de estudio.

## Procedimiento paso a paso

1. `make … --style clay`.
2. Para 3D: `--3d` y ajustar roughness en scene3d (`mat(…, rough=0.7, sss=0.1)`).
3. Escenarios simples (kitchen, studio, park).

## Comandos del estudio

```bash
python -m studio make "Un oso y un conejo de plastilina hacen un pastel en la cocina" --style clay
```

## Ejemplo completo

Anuncio cálido: mascota de plastilina en la cocina, música `cute`, 12 fps, textura visible en primer plano.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| style clay | claymation digital | ✅ motor propio del estudio |
| Blender (materiales mate + displacement) | clay 3D realista | ✅ instalado y probado |

## Control de calidad

- [ ] Textura visible pero no ruidosa.
- [ ] Sin contornos de cartoon.
- [ ] Movimiento con cadencia de 12 fps.

## Errores comunes y cómo evitarlos

- Brillos especulares fuertes delatan lo digital.
- Escenas muy largas en clay cansan: cortas y expresivas.

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
