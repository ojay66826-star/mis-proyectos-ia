# Skills de terceros (procedencia)

Instaladas el 2026-11-04 a partir de un carrusel de imágenes guardado en Google Drive (TikTok @steven_aristizabal).
Cada una se revisó (SKILL.md, referencias y scripts) antes de copiarla. Se conserva la licencia original en cada carpeta.
No las regenera `scripts/skills/build.py`; para actualizarlas, vuelve a copiar desde el repositorio de origen y revisa el diff.

| Skill | Imagen de origen | Repositorio | Commit | Licencia | Cambios locales |
|---|---|---|---|---|---|
| hyperframes | "CSS Animations (HyperFrames)" | github.com/heygen-com/hyperframes (`skills/hyperframes`) — oficial de HeyGen; la antigua skill `css-animations` está fusionada aquí | af0c815 | Apache-2.0 | se quitaron `*.test.mjs` |
| hyperframes-cli | (dependencia de la anterior) | heygen-com/hyperframes (`skills/hyperframes-cli`) | af0c815 | Apache-2.0 | ninguno |
| hyperframes-registry | (dependencia de la anterior) | heygen-com/hyperframes (`skills/hyperframes-registry`) | af0c815 | Apache-2.0 | ninguno |
| threejs-animation-api | "Three.js 3D Animation" | github.com/cloudai-x/threejs-skills (`skills/threejs-animation`) | 0e18186 | MIT | renombrada (antes `threejs-animation`) para no chocar con la Skill propia del estudio |
| ui-animation | "UI-Animation" | github.com/travisjneuman/.claude (`skills/ui-animation`) | ae7c24d | MIT | ninguno |
| flutter-animations | "Flutter Animations" | github.com/MADTeacher/mad-agents-skills (`flutter-animations`) — el repo oficial `flutter/skills` ya no incluye skill de animación | 2fb67e3 | MIT | ninguno |

Requisitos de HyperFrames: Node.js ≥ 22, FFmpeg y Chrome/Chromium; usa `npx hyperframes …` (paquete npm `hyperframes`).
Recomendado: `HYPERFRAMES_NO_TELEMETRY=1`. El render en la nube y los avatares usan cuenta/créditos de HeyGen (de pago): no son necesarios para render local.

No instalada: "Aura.js Web Motion Toolkit" — no existe ninguna Skill ni librería con ese nombre en fuentes verificables.

## Verificación de HyperFrames (2026-11-04)

Render local de prueba correcto con `hyperframes@0.9.13` (5 s, 1920×1080, 30 fps, H.264, 8,5 s de render),
`check` sin errores. Nota para este entorno: el Chromium del renderizador no usa el proxy de salida, así que
los `<script>` desde CDN fallan (`sub_timeline_script_failure`). Solución: guardar GSAP en el proyecto
(`npm pack gsap@<versión>` → `assets/vendor/gsap.min.js`) y referenciarlo como `assets/vendor/gsap.min.js`.
Exporta `HYPERFRAMES_NO_TELEMETRY=1` antes de usar la CLI.

## Ampliación "peleas de anime" (2026-11-05)

Búsqueda en GitHub por categorías (animación, combate, 3D, audio, IA, Unreal, mocap). Criterios: repositorio oficial
o con reputación (estrellas, licencia clara, actividad reciente), contenido revisado (SKILL.md, referencias y scripts:
sin descargas encubiertas, ejecución remota, manejo de credenciales ni instrucciones ocultas) y sin duplicar Skills ya
instaladas. Se copiaron tal cual, con su licencia; los cambios locales se indican abajo.

| Repositorio (commit) | Licencia | Skills instaladas | Cambios locales | Requisitos |
|---|---|---|---|---|
| anthropics/skills — oficial (ca45fc4) | Apache-2.0 (LICENSE.txt en cada Skill) | algorithmic-art, canvas-design, slack-gif-creator | ninguno | — |
| EpicGames/unreal-engine-skills-for-claude-code-plugin — oficial (0e27bde) | MIT | unreal-mcp, create-toolset, unreal-skill | ninguno | Unreal Engine 5 + plugin MCP de Epic en tu PC |
| remotion-dev/skills — oficial (a2824c6) | sin archivo LICENSE en el repo (distribución oficial de Remotion para agentes) | remotion-best-practices (incluye dentro todas sus sub-Skills) | ninguno | licencia Remotion para empresas grandes |
| elevenlabs/skills — oficial (9763c39) | MIT | sound-effects, music, text-to-speech, speech-to-text, voice-changer, voice-isolator, setup-api-key | ninguno | `ELEVENLABS_API_KEY` + red a api.elevenlabs.io (créditos) |
| black-forest-labs/skills — oficial (8907d51) | MIT | bfl-api, flux-image-best-practices, flux-3-video, flux-3-generate, flux-3-cinematic-inserts, flux-3-keyframes-continuation, flux-3-audio-dialogue, flux-3-prompt-doctor, flux-3-archival-formats, flux-3-product-ads | ninguno | `BFL_API_KEY` (de pago) |
| EL4CTEO/blender-skills (fb92cfb, 725★) | MIT | blender-core, blender-animation-api, blender-character-rigging, blender-facial-shapekeys, blender-simulation, blender-stylized-npr, blender-lighting-lookdev, blender-rendering, blender-pbr-materials, blender-texturing, blender-sculpting, blender-hair-grooming, blender-clothing, blender-video-editing, blender-weather-fx, blender-geometry-nodes, blender-scene-setup, blender-pipeline-automation, blender-workflow-recipes, blender-asset-qa, blender-retopology-uv, blender-time-of-day, blender-environment-kits, blender-texture-baking, blender-export-pipelines, blender-hardsurface-modeling | `blender-animation` renombrada a `blender-animation-api` (choca con la Skill del estudio) y sus referencias internas actualizadas | Blender 5.2: `BLENDER_EXE=/usr/local/bin/blender5` |
| arjun988/blender-skills (8f778d2, 1,9k★) | MIT | genre-action-combat, anime-style, manga-style, character-artist, physics-sim, compositing, camera-cinematography, realistic-style | `character-artist`: copiado `references/asset-pipeline.md` (antes compartido) y ruta ajustada | Blender; algunas mencionan su servidor MCP (opcional) |
| majidmanzarpour/blender-game-skills (f0ef293) | MIT | blender-image-to-3d | ninguno | Blender 5.x |
| gamedev-skills/awesome-gamedev-agent-skills (19d93f9, 6,9k★) | Apache-2.0 | game-feel, camera-systems, audio-design, physics-tuning, shader-programming, unreal-niagara | ninguno | — (unreal-niagara: Unreal) |
| calesthio/OpenMontage (d21f5d4, 77k★) | AGPL-3.0 | pose-library-design, character-rigging, canvas-procedural-animation, character-animation-qa, ffmpeg | ninguno | — |
| wuwangzhang1216/DirectorSKILL (c65ae0d) | MIT | cinematic-director | solo SKILL.md, assets, references y LICENSE (sin historial git) | — |
| cloudai-x/threejs-skills (0e18186) | MIT | threejs-fundamentals, threejs-geometry, threejs-materials, threejs-lighting, threejs-textures, threejs-loaders, threejs-shaders, threejs-postprocessing, threejs-interaction, threejs-performance, threejs-asset-pipeline, threejs-react-three-fiber | ninguno | `npm ci` (three) |

Skill propia añadida: **anime-fight-production** (orquestador de peleas; no procede de GitHub).

### Revisados y no instalados

| Repositorio | Motivo |
|---|---|
| arjun988: animation, rigging, rendering, lighting, materials… | duplican Skills de EL4CTEO o del estudio |
| remotion-dev: sub-Skills sueltas | ya incluidas dentro de `remotion-best-practices` |
| anthropics: skill-creator, pdf, docx, pptx, xlsx | ya disponibles como plugin `anthropic-skills` |
| Comfy-Org/comfy-skills | formato OpenClaw + Comfy Cloud de pago; artokun/comfyui-mcp necesita ComfyUI con GPU local |
| viettranx/3dviz-pro-max (159 MB), mromidev/claude-animated-shorts | enfocados a divulgación/cortos cartoon, no a combate |
| Rylaispirit/cinematic-video-prompt-skill | contenido en vietnamita; cubierto por cinematic-director |
| Repos de efectos de sonido con <15★ (sfx, genny, Game-Sound-Effect…) | reputación insuficiente para instalar sin más revisión |
| Skills de "anime fight"/"combat animation" específicas | no existe ninguna con reputación verificable (solo repos de 0–1★) |
| Unreal Engine, ComfyUI, Real-ESRGAN | requieren aplicación/GPU en tu equipo; no instalables en este contenedor |

### Herramientas instaladas en el sistema (verificadas)

| Herramienta | Origen | Prueba |
|---|---|---|
| Blender 4.0.2 | apt (Ubuntu) | `python -m studio character3d persona --action punch --engine eevee` → MP4 + GLB |
| Blender 5.2.3 LTS (`bpy`) + envoltorio `scripts/blender5` | PyPI `bpy==5.2.3` en `/opt/blender5-py` | runner de `blender-core`, `toon_setup.py`, render EEVEE |
| espeak-ng, sox, python3-numpy, librerías EGL/Mesa | apt | `python -m studio doctor` |
| three, gsap, lottie-web, Remotion | `npm ci` (lockfiles del repo) | `python -m studio remotion "…"` → MP4 |
| MediaPipe 1.2.2 + modelo pose_landmarker_full | PyPI en `/opt/mocap-py` + storage.googleapis.com | `scripts/mocap/video_pose.py` |
| Rhubarb Lip Sync 1.14.0 | GitHub Releases (DanielSWolf), sha256 a9a90748…8667 | `rhubarb -f json -r phonetic` |
