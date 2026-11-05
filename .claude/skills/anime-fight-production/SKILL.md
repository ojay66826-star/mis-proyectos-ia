---
name: anime-fight-production
description: Dirige la producción completa de escenas de combate de anime (artes marciales, boxeo, MMA, peleas 3DCG con cel-shading y luchadores musculosos): coreografía, guion de pelea, storyboard, personajes, animación 2D o 3D (Blender 4/5.2, Three.js, Unreal), captura de movimiento desde video, impactos, hit-stop, cámara lenta, destrucción, iluminación dramática, sonido sincronizado y montaje. Úsala para 'pelea', 'combate', 'escena de lucha anime', 'artes marciales', 'puñetazo/patada', 'estilo anime de peleas 3D', o cuando una petición de combate necesite combinar varias Skills.
---

# Producción de peleas de anime (orquestador)

Skill propia del estudio (no procede de GitHub). Coordina las Skills del estudio y las de terceros instaladas en
`.claude/skills/` (ver `THIRD_PARTY_SKILLS.md`) para producir combates con dinamismo de anime 3DCG: golpes con peso,
cámara agresiva, impactos legibles y sonido clavado al fotograma.

**Referencias de estilo.** Se puede tomar como referencia la *calidad* y el *ritmo* de series de peleas 3DCG, pero los
personajes, diseños, nombres, técnicas con nombre propio y planos concretos deben ser **originales**: no recrees
personajes ni escenas de obras protegidas (regla del estudio).

## 1. Elegir la ruta de producción

| Ruta | Cuándo | Herramientas (verificadas en este entorno) |
|---|---|---|
| **Animatic 2D rápido** | previs, ritmo, pruebas de coreografía en minutos | `python -m studio make/render` (acciones `punch`, `kick`, `spin`, `scared_shake`; efectos `speedlines`, `energy`, `explosion`, `lightning`, `smoke`; cámara `shake`, `zoom_in`, `dolly_in`) |
| **3D del estudio** | personaje 3D procedural + GLB en un comando | `python -m studio character3d persona --action punch --engine eevee` (Blender 4.0.2) |
| **Escena 3D de pelea completa** (recomendada) | combate coreografiado con cel-shading, planos, cámara lenta, hit-stop, rótulos y sonido | `scripts/fight3d/` (coreografía JSON → Blender 5.2 → post): ver «Motor fight3d» abajo |
| **3D profesional (Blender 5.2)** | personajes musculosos, rig, mocap, cel-shading, destrucción, render final | Skills `blender-*` con `BLENDER_EXE=/usr/local/bin/blender5` (módulo oficial bpy 5.2.3) |
| **Web / tiempo real** | escenas interactivas, previs en navegador, captura a MP4 | Skills `threejs-*`, `python -m studio web`, `scripts/capture.mjs` |
| **Títulos y montaje por código** | rótulos de ronda, nombres de técnica, créditos | `remotion-best-practices`, `python -m studio remotion`, HyperFrames (`hyperframes`) |
| **IA generativa** | fondos, concept art, planos foto-realistas | `flux-*`/`bfl-api` (clave BFL), conector ElevenLabs (créditos), `python -m studio image/img2video` |
| **Unreal Engine** | cinemáticas en tiempo real con Niagara/Sequencer | `unreal-mcp`, `unreal-niagara`, `create-toolset` (requieren Unreal Editor en tu PC) |

## 2. Preproducción

1. **Guion de pelea** (`animation-scripting`, `cinematic-director`): premisa, motivación de cada luchador, 3 actos
   (tanteo → dominio del rival → giro y remate). Una frase por intercambio.
2. **Coreografía por "beats"** — cada intercambio se escribe como: *lectura/guardia → finta → ataque → respuesta
   (bloqueo, esquiva, parada, contra) → impacto → reacción → respiro*. Varía distancia (larga: patadas; media:
   puñetazos; corta: codos, rodillas, clinch, derribos). Escala la intensidad; el golpe más fuerte va al final.
3. **Shot list y storyboard** (`cinematic-director`, `animation-storyboarding`): plano general para establecer
   distancia, medio para el intercambio, primer plano para la reacción, inserto para el impacto.
   `python -m studio make "<idea>" --storyboard-only` (o `render proyecto.json --quality preview`) para validar antes
   de animar; corrige el `project.json` (fondo `dojo`, especie `persona`, acciones) si el planificador lo interpreta mal.
4. **Personajes** (`character-design`; en 3D `character-artist`, `blender-sculpting`): proporción heroica de 7,5–8
   cabezas, trapecios, dorsales y antebrazos exagerados, cintura estrecha, silueta distinta para cada luchador
   (uno ancho y pesado, otro alto y fibroso). Ficha JSON para mantener la consistencia.

## 3. Animación de golpes con peso (reglas de oro)

| Fase | Fotogramas a 24 fps | Notas |
|---|---|---|
| Anticipación | 4–8 | carga de cadera y hombro hacia atrás; el pie de apoyo pivota |
| Golpe | 2–4 | la cadera arrastra al hombro y este al puño; *smear* o desenfoque en 1–2 fotogramas |
| **Hit-stop** | 3–6 congelados | ambos personajes se detienen en el contacto (`game-feel`) |
| Fotograma de impacto | 1–2 | destello, colores invertidos o fondo plano de líneas; onda de choque |
| Reacción | 6–12 | cabeza/torso del receptor siguen la dirección del golpe; *overshoot* y recuperación |
| Mantenimiento | 6–12 | deja leer la pose antes del siguiente beat |

- **Cámara lenta selectiva:** rampa de velocidad 100 % → 20–30 % justo antes del contacto → 150 % en la recuperación.
- **Temblor de cámara** de 0,2–0,4 s con caída exponencial; más fuerte cuanto más pesado el golpe (`camera-systems`).
- **Bloqueos y esquivas:** el bloqueo absorbe con retroceso de 1–2 pasos; la esquiva usa el torso, no solo la cabeza.
- **Física corporal:** el centro de masa siempre sobre la base; tras un golpe fallido, el atacante pierde equilibrio.
- **Expresiones** (`character-expressions`, `blender-facial-shapekeys`): dientes apretados en la carga, ojos muy
  abiertos al recibir, rostro deformado 1–2 fotogramas en el impacto.
- **Mocap de referencia:** grábate haciendo el movimiento y extrae la pose:
  `/opt/mocap-py/bin/python scripts/mocap/video_pose.py golpe.mp4 -o projects/mocap/golpe` → `pose.json` (33 puntos por
  fotograma, 2 personas) + `control.mp4`. Úsalo para timing y poses clave; para retargeting a un rig usa BVH/FBX de mocap
  con `blender-animation-api` (`retarget.py`).

## Motor fight3d (escena 3D de pelea por coreografía)

Ejemplo de referencia: `projects/pelea-3d-anime/coreografia.json`. La coreografía define dos luchadores (medidas,
musculatura, colores, pelo, pantalón), claves de pose por tiempo (`root`, `pelvis_h`, `lean`, `twist`, `handL/R`,
`footL/R` en coordenadas locales [delante, derecha, arriba] o apuntando al rival con `{"ref": "@B.head", "off": [...]}`),
rampas de cámara lenta (`speed`), impactos (`block`, `hit`, `big`, `land`, `whiff`), barridos, campanas, rótulos y
planos de cámara (órbita o travelling, con mirada a puntos de los luchadores). Pasos:

```bash
export BLENDER_EXE=/usr/local/bin/blender5; R="python3 .claude/skills/blender-core/scripts/run_in_blender.py"; P=projects/<escena>
$R scripts/fight3d/fight3d.py -- $P/coreografia.json $P/escena.blend $P/eventos.json          # construir y animar
ALL=$(python3 -c "import json;e=json.load(open('$P/eventos.json'));print(' '.join(e['fighter_meshes']+e['arena_meshes']))")
$R --blend $P/escena.blend .claude/skills/blender-stylized-npr/scripts/toon_setup.py -- --objects $ALL --lighting scene \
   --bands 2 --rim 0.45 --outline 0.006 --save $P/escena_toon.blend                        # UNA sola pasada de toon
$R --blend $P/escena_toon.blend scripts/fight3d/strip_outline.py -- A_ B_                   # contorno solo en luchadores
for o in 0 1 2; do blender5 -b $P/escena_toon.blend -P scripts/fight3d/render.py -- $P/frames 1-<N> 75 8 3 $o & done; wait
python3 scripts/fight3d/post.py $P/frames $P/eventos.json $P                                # hit-stop, FX, rótulos, sonido → final.mp4
```

Avisos: no ejecutes `toon_setup.py` dos veces sobre el mismo archivo (reconstruye su grupo de nodos y deja a cero
los materiales de la pasada anterior). En CPU, ≈11 s por fotograma a 960×540 con 3 procesos; el contorno casi
duplica el coste. Prueba primero 6–8 fotogramas clave a media resolución (`render.py … 15,46,77 50 8`).

## 4. Pipeline 3D profesional (Blender 5.2)

```bash
export BLENDER_EXE=/usr/local/bin/blender5          # Blender 5.2.3 (módulo bpy); `blender` = 4.0.2 del estudio
R=.claude/skills/blender-core/scripts/run_in_blender.py
python3 $R --expr "import bpy; print(bpy.app.version_string)"
```

1. `blender-core` → reglas de bpy 5.x y verificación.
2. Modelado: `character-artist` (anatomía), `blender-sculpting`, `blender-retopology-uv`, `blender-image-to-3d`
   (desde concept art), `blender-clothing`, `blender-hair-grooming`.
3. Rig: `blender-character-rigging` (Rigify, IK/FK, `rigify_build.py`, `stress_poses.py`), `blender-facial-shapekeys`.
4. Animación: `blender-animation-api` (keyframes, NLA, mocap BVH/Mixamo, `bake_action.py`).
5. Física y destrucción: `blender-simulation`, `physics-sim` (fractura de celdas, escombros), `blender-weather-fx`.
6. Look anime: `blender-stylized-npr` (`toon_setup.py --bands 2 --rim 0.5 --outline 0.012`), `anime-style`,
   `manga-style`; look realista: `realistic-style`, `blender-pbr-materials`, `blender-texturing`.
7. Luz y cámara: `blender-lighting-lookdev`, `camera-cinematography`, `blender-time-of-day`, `animation-lighting`
   (clave dura cenital para marcar músculo, contraluz de color, humo volumétrico en la arena).
8. Render y post: `blender-rendering` (EEVEE/Cycles en CPU), `compositing` (glare, grading), `blender-video-editing`.
9. Exportar a Unreal/Unity/web: `blender-export-pipelines`.
10. Control: `blender-asset-qa`, `animation-quality-control`, `character-animation-qa`.

Ejemplo verificado: cel-shading sobre un GLB del estudio y render EEVEE en Blender 5.2 (≈30 s por imagen a 720 px en CPU).

## 5. Sonido sincronizado

| Capa | Fuente local (gratis) | Fuente IA (opcional) |
|---|---|---|
| Golpe (thud grave + chasquido) | `synth_sfx("punch")` del estudio | `sound-effects` (ElevenLabs API) o conector ElevenLabs |
| Barrido de aire / ropa | `synth_sfx("whoosh")` | ídem, "cloth whoosh, fast punch swish" |
| Explosión / destrucción | `synth_sfx("explosion")`, `thunder` | ídem |
| Pasos y arrastre | `synth_sfx("footstep")` | ídem |
| Música de tensión | `synth_music("action"/"epic")` | `music` (ElevenLabs API) |
| Voces y gritos | `espeak-ng` + `rhubarb` (boca por fonemas) | `text-to-speech`, conector ElevenLabs |

Reglas (`audio-design`, `animation-sound-design`): el ataque del SFX cae **en el fotograma de impacto exacto**
(no en la anticipación); silencio breve antes del golpe decisivo; *ducking* de la música 6–10 dB en cada impacto;
varía tono y volumen entre golpes repetidos; ambiente de arena (público, eco) por debajo de todo.
`rhubarb -f json -r phonetic grito.wav` devuelve las posiciones de boca A–X para el lip-sync.

## 6. Montaje, calidad y entrega

- Montaje: `video-editing`, `video-transitions`, `ffmpeg`, `blender-video-editing`; rótulos de ronda/técnica con
  `kinetic-typography` o `remotion-best-practices`.
- Corrección de color y look: `cinematic-effects`, `compositing`, `threejs-postprocessing` (bloom, DOF).
- Optimización y formatos: `animation-optimization` → `python -m studio export final.mp4 --preset youtube|tiktok`.
- QC obligatorio: `python -m studio qc final.mp4` y mirar 2–3 fotogramas de impacto antes de entregar.

## 7. Qué requiere servicios externos

| Herramienta | Requisito | Coste |
|---|---|---|
| Skills `sound-effects`, `music`, `text-to-speech`, `speech-to-text`, `voice-changer`, `voice-isolator` | `ELEVENLABS_API_KEY` y acceso de red a `api.elevenlabs.io` | créditos ElevenLabs |
| Conector ElevenLabs de Claude (voz, imagen, video) | ya conectado | créditos; las descargas a `elevenlabsusercontent.com` están bloqueadas por la red del entorno: sube los archivos al Drive |
| `flux-*`, `bfl-api` | `BFL_API_KEY` (Black Forest Labs) | de pago por imagen/video |
| `unreal-mcp`, `create-toolset`, `unreal-skill`, `unreal-niagara` | Unreal Engine 5 + plugin de Epic en tu PC | Unreal es gratis (regalías según ingresos) |
| `remotion-best-practices` | licencia de Remotion para empresas grandes | gratis para particulares |
| `python -m studio img2video --provider replicate` | `REPLICATE_API_TOKEN` | de pago |
| Real-ESRGAN (`upscale`) | GPU con Vulkan | no disponible en este contenedor; usar upscale Lanczos |

## Errores comunes

- Golpes sin anticipación ni hit-stop: se ven flotantes. Siempre carga → contacto congelado → reacción.
- Sonido desplazado 2–3 fotogramas: el golpe "no pesa". Alinea el SFX al fotograma de impacto.
- Cámara quieta en una pelea: usa al menos un cambio de plano o un temblor por intercambio.
- Personajes iguales en silueta: el espectador pierde quién golpea a quién.
- Copiar diseños de una serie concreta: usa referencias de calidad, nunca personajes o planos protegidos.
