---
name: 3d-animation
description: Produce animaciones 3D completas con Blender en modo headless: personajes procedurales, escenario, iluminación de tres puntos, cámara animada, lip-sync, render EEVEE/Cycles y montaje con audio. Úsala para 'animación 3D', 'en 3D', 'tridimensional', 'render 3D'.
---

# Animación 3D

**Categoría:** Animación 3D · **Skills relacionadas:** `blender-animation`, `3d-character-animation`, `3d-camera-animation`, `animation-lighting`, `animation-rendering`

El estudio traduce el mismo `project.json` del 2D a una escena de Blender (`studio/blender/scene3d.py`): construye personajes con primitivas suavizadas y materiales PBR, anima con keyframes por frame, coloca luces key/fill/rim y cámara con Track-To, renderiza PNG por escena y los monta con FFmpeg + audio del estudio. Blender 4.0.2 (headless) con EEVEE por software; Cycles sin denoiser en la build de Ubuntu.

## Cuándo usar esta Skill

- La petición menciona 3D, Blender, render 3D o 'personaje 3D'.
- Se necesita un modelo reutilizable (GLB) además del video.

## Principios profesionales

- Iluminación de tres puntos: key cálida, fill suave opuesta, rim fría para separar del fondo.
- Cámara a altura de ojos del personaje (0.8–1.1 m) con lente 35 mm para cercanía.
- Materiales con roughness 0.3–0.5 para look 'juguete'/estilizado.
- Mantener polígonos bajos y subdivisión suave para renders rápidos.

## Procedimiento paso a paso

1. Planifica igual que en 2D (`plan`) y añade `"engine": "3d"` o usa `--3d`.
2. Elige motor: `rapido` (Workbench, previsualizar), `eevee` (calidad, por defecto), `cycles` (fotorrealista, lento).
3. Haz primero `--quality preview` (640×360) para validar cámara y acciones.
4. Render final en `hd`. Se generan `final.mp4`, `personaje.glb` y `escena_N.blend` editable.
5. Abre el `.blend` en Blender de escritorio para retoques manuales si el usuario lo desea.

## Comandos del estudio

```bash
python -m studio make "Crea un personaje 3D: un gato que baila en el escenario" --3d --quality preview
python -m studio make "Un robot camina por la ciudad" --3d --engine eevee --quality hd
blender projects/<…>/frames3d/escena_1.blend          # abrir para edición manual
```

## Fragmento de proyecto (project.json)

```json
{"engine": "3d", "render_engine": "eevee", "samples": 8, "save_blend": true,
 "scenes": [{"background": "stage", "time_of_day": "night", "duration": 5, "camera": {"type": "orbit"},
   "actors": [{"character": "gato", "action": "dance", "emotion": "joy", "from": [0.5, 0.82]}]}]}
```

## Ejemplo completo

«Crea un personaje 3D que baile»: `python -m studio make "Un gato baila en el escenario" --3d` →
render EEVEE con focos de colores, cámara orbital, música dance, GLB exportado y QC aprobado (~4 min en CPU para 6 s a 640×360).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender 4.0 (bpy) | modelado/rig/render | ✅ instalado y probado |
| EEVEE | render rápido de calidad | ✅ instalado y probado |
| Cycles | path tracing | ✅ instalado y probado |
| FFmpeg | montaje | ✅ instalado y probado |
| Mixamo | animaciones humanoides para personajes riggeados | 🌐 gratis, requiere internet |

## Control de calidad

- [ ] Personaje apoyado en el suelo, sin intersecciones con el piso.
- [ ] Sin frames negros (EGL/GPU).
- [ ] Iluminación sin quemados (AgX).
- [ ] GLB abre en el visor Three.js.

## Errores comunes y cómo evitarlos

- En servidores sin GPU EEVEE usa software (lento): usa `preview` para iterar.
- Cycles sin denoiser produce ruido: sube `samples` a 128+ o instala Blender oficial con OIDN.
- Blender usa su propio Python: numpy debe estar instalado para el exportador glTF (python3-numpy).

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
