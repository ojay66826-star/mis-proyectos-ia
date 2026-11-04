---
name: 3d-camera-animation
description: Diseña movimientos de cámara 3D cinematográficos: órbita, dolly in/out, paneo, travelling, temblor, con Track-To y easing. Úsala para 'cámara que gira', 'plano cinematográfico 3D', 'órbita', 'dolly', 'travelling'.
---

# Animación de cámara 3D

**Categoría:** Animación 3D · **Skills relacionadas:** `cinematic-video`, `scene-composition`, `3d-environment-animation`

`camera()` en scene3d.py crea una cámara con restricción Track-To a un objetivo a la altura del personaje y keyframes por frame con easing smoothstep. Tipos: `static`, `orbit`, `pan`, `zoom_in`/`dolly_in`, `zoom_out`, `shake`. La distancia se adapta al número de personajes.

## Cuándo usar esta Skill

- Planos 3D dinámicos.
- Turntables de producto/personaje.

## Principios profesionales

- Mover la cámara con motivación (revelar, seguir, enfatizar).
- Easing in/out siempre; nunca velocidad constante salvo travelling.
- Regla de 180° entre personajes que dialogan.
- Lentes: 24–35 mm acción, 50–85 mm retratos.

## Procedimiento paso a paso

1. Elige `camera.type` por escena en el JSON.
2. Orbit para presentar personajes; dolly_in para momentos emotivos; shake para impactos.
3. Previsualiza con `--engine rapido`.
4. Ajusta en el `.blend` si se requiere un movimiento a medida (Graph Editor).

## Comandos del estudio

```bash
python -m studio make "Una fresa 3D presenta su nuevo baile" --3d --engine rapido --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"scenes": [{"camera": {"type": "orbit"}}, {"camera": {"type": "dolly_in"}}, {"camera": {"type": "shake"}}]}
```

## Ejemplo completo

Turntable de personaje: `character3d estrella --action idle --duration 6` usa órbita completa suave alrededor del personaje.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Blender camera + Track To | movimientos procedurales | ✅ instalado y probado |
| Camera Shakify (addon) | temblor realista | 💻 programa externo recomendado |
| Three.js OrbitControls | cámara interactiva web | ✅ instalado y probado |

## Control de calidad

- [ ] El sujeto nunca sale de cuadro.
- [ ] Sin cambios bruscos de velocidad.
- [ ] Horizonte nivelado salvo intención.

## Errores comunes y cómo evitarlos

- Órbitas rápidas marean: ≤ 70° en 5 s.
- Cámara dentro de objetos del escenario.

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
