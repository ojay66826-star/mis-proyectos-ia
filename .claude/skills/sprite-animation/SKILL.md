---
name: sprite-animation
description: Genera sprites y spritesheets animados (idle, walk, run, jump, attack) para videojuegos web o motores (Godot, Unity, Phaser), con fondo transparente y metadatos de frames. Úsala para 'sprite', 'spritesheet', 'personaje para mi juego', 'animación de juego 2D'.
---

# Animación de sprites (hojas de sprites para juegos)

**Categoría:** Animación 2D · **Skills relacionadas:** `pixel-art-animation`, `character-animation`, `interactive-animation`

El renderizador de personajes devuelve imágenes RGBA con ancla en los pies, perfectas para sprites. Esta Skill crea spritesheets (rejilla de frames) por acción con transparencia y un JSON de metadatos compatible con Phaser/Godot.

## Cuándo usar esta Skill

- El usuario quiere usar el personaje en un juego.
- Necesita GIF/PNG transparentes por acción.

## Principios profesionales

- Todos los frames con el mismo tamaño y el mismo punto de ancla (pies).
- Ciclos de 8–12 frames que cierran en bucle perfecto.
- Fondo transparente y márgenes mínimos.
- Nombres consistentes: <personaje>_<acción>.png + .json.

## Procedimiento paso a paso

1. Elige personaje y acciones (idle, walk, run, jump, punch, celebrate).
2. Ejecuta el script de abajo para generar la hoja por acción.
3. Importa en el motor: Phaser `this.load.spritesheet(key, png, {frameWidth, frameHeight})`; Godot `AnimatedSprite2D` + SpriteFrames.
4. Para pixel art, reescala con `Image.NEAREST`.

## Comandos del estudio

```bash
python - <<'PY'
from studio.characters import make_character, render_character
from studio.motion import pose_for
from PIL import Image
import json
spec = make_character("zorro", "Foxy")
for action, n, period in [("idle", 8, 2.5), ("walk", 10, 1/1.6), ("run", 8, 1/2.6), ("jump", 12, 1.2)]:
    frames = [render_character(spec, pose_for(action, i * period / n), 200, "cartoon")[0] for i in range(n)]
    w = max(f.width for f in frames); h = max(f.height for f in frames)
    sheet = Image.new("RGBA", (w * n, h))
    for i, f in enumerate(frames): sheet.paste(f, (i * w + (w - f.width) // 2, h - f.height))
    sheet.save(f"foxy_{action}.png")
    json.dump({"frameWidth": w, "frameHeight": h, "frames": n, "fps": round(n / period)}, open(f"foxy_{action}.json", "w"))
PY
```

## Ejemplo completo

«Hazme el personaje de mi juego de plataformas»: generar idle/walk/run/jump del `zorro`, entregar PNG + JSON, y un GIF de muestra por acción con `ffmpeg -i foxy_walk.png …` o directamente en el visor del motor.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor de personajes (render_character) | frames RGBA | ✅ motor propio del estudio |
| Aseprite | edición de sprites | 💻 programa externo recomendado |
| TexturePacker / free-tex-packer | atlas optimizados | 💻 programa externo recomendado |
| Godot / Phaser | motores de juego destino | 💻 programa externo recomendado |

## Control de calidad

- [ ] Ancla estable (los pies no saltan entre frames).
- [ ] El último frame enlaza con el primero.
- [ ] Transparencia correcta (sin halo).

## Errores comunes y cómo evitarlos

- Recortar cada frame a su caja individual cambia el ancla: usa tamaño común.
- Premultiplicar alfa en el motor si se ven bordes oscuros.

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
