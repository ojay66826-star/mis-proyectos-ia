---
name: scene-composition
description: Compone planos legibles y atractivos: regla de tercios, profundidad, aire en la mirada, jerarquía visual, escala, contraste figura-fondo, posiciones de personajes y encuadre por formato (16:9, 9:16, 1:1). Úsala para 'composición', 'encuadre', 'dónde poner a los personajes', 'que se vea mejor la escena'.
---

# Composición de escena

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-storyboarding`, `3d-camera-animation`, `character-movement`

Coordenadas normalizadas del estudio: x 0–1, y del suelo 0.82 (`GROUND_Y`). Personajes a 46 % de la altura (1–2 personajes) o 38 % (3+); en vertical, 42 % del ancho. El orden de dibujo por y simula profundidad. La cámara `focus` define el centro de zoom.

## Cuándo usar esta Skill

- Ajustar posiciones y cámaras.
- Adaptar una escena de 16:9 a 9:16.

## Principios profesionales

- Tercios: protagonistas en x≈0.33/0.66.
- Aire delante de la mirada.
- Primer plano más oscuro/grande, fondo más claro/pequeño.
- En 9:16 apilar verticalmente o usar 1–2 personajes.

## Procedimiento paso a paso

1. Revisa el storyboard.
2. Ajusta `from/to`, `scale`, `facing` y `camera.focus`.
3. Para profundidad, distintos `y` (0.78–0.88) y `scale` (0.8–1.1).
4. Re-renderiza en preview.

## Comandos del estudio

```bash
python -m studio render projects/<…>/project.json --quality preview
```

## Fragmento de proyecto (project.json)

```json
{"camera": {"type": "zoom_in", "focus": [0.33, 0.6]},
 "actors": [{"character": "heroe", "from": [0.33, 0.85], "scale": 1.1, "facing": 1},
            {"character": "amigo", "from": [0.7, 0.79], "scale": 0.85, "facing": -1}]}
```

## Ejemplo completo

Diálogo en 9:16: dos personajes a x 0.3 y 0.7, cámara static, subtítulos grandes a y≈70 % — sin superponer caras.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (coordenadas normalizadas) | composición | ✅ motor propio del estudio |
| Blender camera | composición 3D (guías de tercios) | ✅ instalado y probado |

## Control de calidad

- [ ] Protagonista identificable en 1 s.
- [ ] Nada importante en los bordes.
- [ ] Subtítulos sin tapar caras.

## Errores comunes y cómo evitarlos

- Centrar todo siempre: estático y aburrido.
- Personajes cortados por los bordes en 9:16.

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
