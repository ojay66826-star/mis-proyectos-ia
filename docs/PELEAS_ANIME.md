# Peleas de anime — Skills, herramientas y cómo usarlas

Informe de la especialización del estudio en escenas de combate de anime (2026-11-05). Todo lo que figura como
**verificado** se ejecutó en este entorno y se revisó su salida (video, imagen o JSON).

## 1. Cómo pedírselo a Claude

Pide la escena en lenguaje natural; Claude carga `anime-fight-production` (orquestador) y las Skills necesarias:

- «Haz un animatic 2D de 15 s: dos luchadores en un ring subterráneo, finta, puñetazo bloqueado, contra con patada alta, cámara lenta en el impacto.»
- «Crea un luchador 3D musculoso con rig Rigify, aplícale cel-shading anime y renderiza un puñetazo con cámara contrapicada.»
- «Escribe el guion y la coreografía beat a beat de una pelea de 3 rondas y saca el shot list.»
- «Extrae el movimiento de este video mío lanzando una patada y úsalo como referencia de timing.»
- «Añade sonidos de golpes, ropa, huesos y una música de tensión sincronizados con cada impacto.»

## 2. Herramientas instaladas y verificadas

| Herramienta | Para qué | Cómo se usa | Estado |
|---|---|---|---|
| Motor 2D del estudio | animatics de pelea rápidos (acciones `punch`, `kick`, efectos `speedlines`, `energy`, `explosion`, cámara `shake`) | `python -m studio make "<idea>" --style anime` · `render project.json` | verificado: escena de dojo con 2 luchadores, QC aprobado |
| Blender 4.0.2 (apt) | pipeline 3D del estudio, GLB | `python -m studio character3d persona --action punch --engine eevee` | verificado: MP4 960×960 + GLB |
| Blender 5.2.3 LTS (módulo `bpy` de PyPI) + `scripts/blender5` | Skills `blender-*` (Rigify, mocap, cel-shading, simulación, Cycles/EEVEE) | `BLENDER_EXE=/usr/local/bin/blender5 python3 .claude/skills/blender-core/scripts/run_in_blender.py <script.py> -- …` | verificado: importar GLB, `toon_setup.py`, render EEVEE |
| MediaPipe 1.2.2 + modelo de pose | captura de movimiento desde video (33 puntos, 2 personas) | `/opt/mocap-py/bin/python scripts/mocap/video_pose.py video.mp4 -o projects/mocap/x` | verificado de punta a punta (falta probar con un video tuyo) |
| Rhubarb Lip Sync 1.14.0 | boca sincronizada por fonemas para gritos y diálogos | `rhubarb -f json -r phonetic voz.wav` | verificado |
| espeak-ng + sox | voz local gratuita y procesado de audio | automático en el estudio | verificado (`doctor`) |
| Three.js, GSAP, Lottie (npm) | escenas web/tiempo real y captura a MP4 | `python -m studio web …` | instalado (`doctor` ✔) |
| Remotion (npm) | rótulos de ronda, montaje por código | `python -m studio remotion "<idea>"` | verificado: título cinético a MP4 |
| HyperFrames (instalado antes) | composiciones HTML→video con audio | Skill `hyperframes` | verificado en videos anteriores |

No instalables aquí: **Unreal Engine** (aplicación de escritorio con GPU), **ComfyUI** local (GPU), **Real-ESRGAN**
(Vulkan/GPU). `blender.org` está bloqueado por la red del entorno; por eso Blender 5.2 se usa como módulo `bpy`.

## 3. Skills por categoría pedida

### Animación y movimientos
- `anime-fight-production` (propia): coreografía por beats, reglas de golpes con peso, hit-stop, cámara lenta, rutas 2D/3D/web/Unreal.
- `character-fighting`, `character-animation`, `character-movement`, `3d-character-animation` (estudio): acciones y trayectorias.
- `blender-animation-api`: keyframes, NLA, **retargeting de mocap BVH/Mixamo**, bake, root motion.
- `pose-library-design`, `character-rigging`, `canvas-procedural-animation`: poses clave y rigs 2D por datos.
- `game-feel`: hit-stop, temblor, squash & stretch, knockback. `physics-tuning`: física estable y con peso.
- `camera-systems`, `camera-cinematography`, `3d-camera-animation`: cámara que sigue, encuadra y tiembla.
- `character-expressions`, `blender-facial-shapekeys`, `character-lip-sync`: caras y sincronía.

### Animación de anime
- `anime-style`, `manga-style`, `blender-stylized-npr` (cel-shading, contornos, Line Art), `anime-animation`.
- `character-artist` (anatomía humana), `blender-sculpting`, `blender-character-rigging` (Rigify), `blender-clothing`, `blender-hair-grooming`.
- `cinematic-director`, `cinematic-video`, `cinematic-effects`: planos, shot list y look de cine.
- `physics-sim`, `blender-simulation`: destrucción por fractura, escombros, tela. `explosions`, `energy-effects`, `smoke-animation`.
- `blender-lighting-lookdev`, `animation-lighting`, `blender-time-of-day`: iluminación dramática.
- `realistic-style`, `blender-pbr-materials`, `blender-texturing`, `blender-texture-baking`: sombras y texturas realistas.

### Sonidos y audio
- `animation-sound-design` (estudio): SFX procedurales locales (`punch`, `whoosh`, `explosion`, `thunder`, `footstep`), música por estado de ánimo (`action`, `epic`…), ducking.
- `audio-design`: buses, ducking, variación de SFX, sincronía con el beat.
- `sound-effects`, `music`, `text-to-speech`, `speech-to-text`, `voice-changer`, `voice-isolator` (ElevenLabs oficiales; requieren clave).
- `flux-3-audio-dialogue`: dirección de audio para video IA. Rhubarb + espeak-ng para voces locales.

### Calidad visual
- `blender-rendering` (Cycles/EEVEE, AgX/ACES), `compositing` (glare, grading, passes), `threejs-postprocessing` (bloom, DOF).
- `blender-asset-qa`, `animation-quality-control`, `character-animation-qa`: control de calidad.
- `animation-upscaling`, `animation-optimization`, `ffmpeg`: resolución, fluidez y formatos.

### Herramientas profesionales
- Blender: 27 Skills `blender-*` + `character-artist`, `physics-sim`, `compositing`, `camera-cinematography`, `blender-image-to-3d`.
- Unreal Engine: `unreal-mcp`, `create-toolset`, `unreal-skill` (oficiales de Epic), `unreal-niagara`.
- Three.js: 14 Skills `threejs-*`. Remotion: `remotion-best-practices`. Edición: `video-editing`, `blender-video-editing`, `ffmpeg`.
- IA generativa: `bfl-api`, `flux-image-best-practices`, `flux-3-*` (Black Forest Labs), `ai-video-generation`, conector ElevenLabs.

### Producción automática
- `animation-workflow` (orquestador general) + `anime-fight-production` (orquestador de peleas).
- Guion y storyboard: `animation-scripting`, `animation-storyboarding`, `cinematic-director`.
- Escenarios: `3d-environment-animation`, `blender-environment-kits`, `genre-action-combat` (arenas legibles para combate).
- Montaje y sincronía: `video-editing`, `video-transitions`, `blender-workflow-recipes`, `blender-pipeline-automation`.

Lista completa y por categorías: `docs/SKILLS_CATALOGO.md`. Procedencia, licencias y versiones: `.claude/skills/THIRD_PARTY_SKILLS.md`.

## 4. Qué requiere servicios externos

| Necesidad | Qué hace falta | Coste |
|---|---|---|
| Skills de ElevenLabs (SFX, música, voz) | `ELEVENLABS_API_KEY` + permitir `api.elevenlabs.io` | créditos |
| Conector ElevenLabs de Claude | ya conectado; descargar resultados vía Drive (dominio de descargas bloqueado) | créditos |
| FLUX (imágenes/video IA) | `BFL_API_KEY` | de pago |
| Video IA vía estudio (`img2video --provider replicate`) | `REPLICATE_API_TOKEN` | de pago |
| Unreal Engine + MCP de Epic | Unreal Engine 5 en tu PC con GPU | gratis (regalías según ingresos) |
| Remotion | licencia solo para empresas grandes | gratis para particulares |
| Modelos 3D base musculosos con rig | crear con `character-artist`/`blender-sculpting` o importar (Mixamo requiere cuenta Adobe) | variable |

## 5. Límites honestos

- El motor 2D procedural y el personaje 3D del estudio son **previsualización**: sirven para coreografía, ritmo,
  cámara y sonido, pero no alcanzan por sí solos la calidad de un anime 3DCG profesional.
- Para esa calidad hacen falta **modelos 3D detallados** (esculpidos o importados), **mocap real** de los golpes y
  **render con GPU**. Este contenedor solo tiene CPU (EEVEE ≈30 s por imagen a 720 px).
- No existe en GitHub ninguna Skill específica de "anime de peleas" con reputación verificable; la especialización
  se cubre combinando Skills fiables y el orquestador propio `anime-fight-production`.

## 6. Reinstalar en una sesión nueva

Las Skills y los scripts están en el repositorio, pero las herramientas del sistema (Blender, bpy 5.2, MediaPipe,
Rhubarb, paquetes npm) viven en el contenedor y se pierden al cerrarlo. En una sesión nueva, ejecuta (o pide a Claude
que ejecute):

```bash
bash scripts/instalar_herramientas.sh    # apt + bpy 5.2 + MediaPipe + modelo de pose + Rhubarb (sha256) + npm ci
python -m studio doctor                  # comprobar
```

También se puede guardar como script de configuración del entorno en la nube para que se ejecute solo en cada sesión.
