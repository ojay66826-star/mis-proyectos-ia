# Arquitectura del estudio

## Pipeline

```
 instrucción ──► planner.plan() ──► project.json ──► render.prepare()
   (texto)        reglas / Claude      (fuente de        │  hojas de personaje (characters.py)
                                        verdad)          │  voces TTS + lip-sync (audio.py)
                                                         │  línea de tiempo + transiciones
                                                         ▼
                         ┌──────────── engine "2d" ─────────────┐   engine "3d"
                         │ SceneRenderer (multiproceso)         │   blender_bridge → scene3d.py (bpy)
                         │  backgrounds (paralaje, hora del día)│   personajes 3D, luces, cámara,
                         │  characters (rig 2D) + motion (poses)│   EEVEE/Cycles → PNG → FFmpeg
                         │  effects (partículas deterministas)  │   + GLB para Three.js
                         │  styles (post-procesado numpy)       │
                         │  overlays (título, rótulos, subs)    │
                         └──────────────► FFmpeg (x264) ◄───────┘
                                              │
                          audio.build: voces + SFX + música (ducking) ─► mux AAC
                                              │
                         miniatura · GIF · storyboard · SRT · QC (qc.py) · project.json
```

Rutas alternativas que comparten el mismo audio, estilos y exportación:

- `image2video.py` — imagen → video (Ken Burns subpíxel, paralaje 2.5D, efectos, grading) o Replicate.
- `motiongraphics.py` — tipografía cinética, logos, infografías, fondos en bucle.
- `lottie.py` — animaciones Lottie JSON.
- `templates/web/*.html` + `scripts/capture.mjs` — GSAP/CSS/SVG/Lottie/Three.js capturados frame a frame.
- `remotion_bridge.py` + `remotion/` — composición React a partir del proyecto.
- `exporter.py` — presets de plataforma, WebM, GIF, upscale, interpolación, bucles, concat con xfade, ZIP.

## project.json (esquema)

```jsonc
{
  "title": "Mi animación", "prompt": "…",
  "style": "cartoon",            // cartoon anime pixel minimalist cute cinematic horror fantasy paper clay stopmotion realistic comic retro
  "format": "16:9",              // 16:9 9:16 1:1 4:5
  "fps": 24, "quality": "hd",    // preview hd fullhd
  "engine": "2d",                // "3d" = Blender
  "render_engine": "eevee",      // 3D: rapido eevee cycles
  "mood": "happy",               // happy cute sad epic spooky dance action calm fantasy
  "music": true, "voices": true, "subtitles": true,   // subtitles: true | "big" | false
  "transition": "fade",          // fade dip wipe slide circle cut
  "show_title": true, "letterbox": null, "tts_provider": "auto",
  "characters": [{
    "id": "manzana", "name": "Manzana", "species": "manzana", "kind": "fruit", "shape": "apple",
    "color": "#e53935", "eyes": "round", "accessory": "none", "hair": "short", "hair_color": "#4e342e",
    "skin": "#f1c27d", "height": 1.0, "personality": ""
  }],
  "scenes": [{
    "id": "escena_1", "background": "park", "time_of_day": "day", "duration": 4,
    "camera": {"type": "pan", "focus": [0.5, 0.55]},        // static pan pan_left zoom_in zoom_out dolly_in shake (3D: orbit)
    "caption": "Había una vez…", "transition": "circle",
    "actors": [{
      "character": "manzana", "action": "walk", "emotion": "happy",
      "from": [0.1, 0.82], "to": [0.5, 0.82], "move_start": 0, "move_end": 3,
      "facing": 1, "scale": 1.0,
      "actions":  [{"t": 3, "action": "wave"}],
      "emotions": [{"t": 3, "emotion": "joy"}],
      "transform_to": "estrella", "transform_at": 3.5
    }],
    "dialogue": [{"character": "manzana", "text": "¡Hola!", "start": 0.5, "audio_file": "opcional.mp3"}],
    "effects": [{"type": "sparkles", "x": 0.5, "y": 0.5, "on": "manzana", "start": 1, "end": 3, "intensity": 1, "scale": 1, "color": [255, 215, 64]}]
  }]
}
```

`planner.normalize()` valida y completa cualquier proyecto (también los editados a mano o generados por Claude).

## Cómo trabajan juntas las Skills

Las 80 Skills son instrucciones para Claude. Todas apuntan al mismo motor y al mismo `project.json`, de modo que cada
Skill solo modifica la parte que le corresponde:

| Fase | Skills | Qué tocan |
|---|---|---|
| Idea y guion | animation-scripting, animated-storytelling, story-animation | `title`, `scenes[].dialogue`, estructura |
| Personajes | character-design, character-expressions, mascot-animation | `characters[]`, `emotion(s)` |
| Storyboard y composición | animation-storyboarding, scene-composition | `from/to`, `scale`, `camera` |
| Animación | 2d-animation, 3d-animation, character-* | `action(s)`, `engine` |
| Estilo | cartoon/anime/pixel/…/realistic | `style`, `letterbox` |
| Efectos | visual-effects y efectos específicos | `scenes[].effects` |
| Audio | animation-sound-design, character-lip-sync | `mood`, `voices`, `audio_file` |
| Render y post | animation-rendering, video-editing, video-transitions | `quality`, `transition`, exportación |
| Entrega | animation-quality-control, animation-optimization, animation-upscaling | QC, presets |

El orquestador `animation-workflow` contiene la tabla de enrutado petición → Skills → comando.

## Rendimiento medido (contenedor de 4 núcleos, sin GPU)

| Tarea | Tiempo |
|---|---|
| Historia 2D de 15 s, 720p | ~80 s |
| Borrador 2D (preview) de 8 s | ~15–20 s |
| Personaje 3D EEVEE (software) 640×360 | ~3–6 s por frame |
| Captura web 2 s a 12 fps | ~3 s |
| Remotion 8 s 720p | ~21 s |

Con GPU (Blender oficial) el 3D es 10–50× más rápido.
