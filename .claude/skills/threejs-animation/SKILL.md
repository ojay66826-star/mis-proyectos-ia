---
name: threejs-animation
description: Crea escenas 3D interactivas en el navegador con Three.js (WebGL): personajes procedurales o GLB de Blender, luces, sombras, OrbitControls, y captura determinista a MP4. Úsala para 'Three.js', 'WebGL', '3D en la web', 'visor 3D', 'escena 3D interactiva'.
---

# Animación 3D web con Three.js

**Categoría:** Animación 3D · **Skills relacionadas:** `interactive-animation`, `3d-modeling`, `gsap-animation`

`templates/web/three-scene.html` (Three.js 0.170 local, sin CDN) crea una escena con iluminación de tres puntos, sombras suaves, árboles low-poly y un personaje animado (dance/walk/jump) o carga un GLB exportado por Blender con su animación. `window.__seek(t)` permite capturar frames exactos con `scripts/capture.mjs` (Chromium + SwiftShader).

## Cuándo usar esta Skill

- 3D en páginas web o visor de modelos.
- Video 3D rápido sin Blender.

## Principios profesionales

- Render determinista: separar estado de animación (`pose(t)`) del bucle de render.
- Tone mapping ACES + sombras PCFSoft para look profesional.
- Pixel ratio 1 en captura; `preserveDrawingBuffer` para screenshots.
- Cargar dependencias locales (importmap a node_modules).

## Procedimiento paso a paso

1. Abre en vivo: `python -m studio serve` → pestaña 3D y Web → three-scene → Ver en vivo.
2. Parámetros por URL: `color`, `action` (dance/walk/jump), `sky`, `ground`, `glb`, `duration`.
3. Captura: `python -m studio web three-scene --duration 4 --query "action=walk&color=%23fb8c00"`.
4. Para un GLB: `--query "glb=/projects/<…>/personaje.glb"` (servido por el estudio).

## Comandos del estudio

```bash
python -m studio web three-scene --duration 4 --query "action=dance&color=%23e53935"
python -m studio web three-scene --query "glb=/projects/<carpeta>/manzana.glb" -o manzana_web.mp4
```

## Ejemplo completo

«Quiero un visor 3D de mi personaje para mi web»: `character3d manzana` → copiar `three-scene.html` + GLB a la web y abrir `three-scene.html?glb=manzana.glb`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Three.js 0.170 | WebGL | ✅ instalado y probado |
| Playwright + Chromium (SwiftShader) | captura a video | ✅ instalado y probado |
| React Three Fiber | Three.js en React | 💻 programa externo recomendado |

## Control de calidad

- [ ] Sin errores en consola.
- [ ] Frames idénticos entre capturas (determinismo).
- [ ] GLB con animación reproduciéndose.

## Errores comunes y cómo evitarlos

- Abrir el HTML con file:// bloquea módulos ES: usar el servidor del estudio.
- WebGL sin GPU es lento a 1080p: capturar a 720p.

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
