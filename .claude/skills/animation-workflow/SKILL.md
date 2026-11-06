---
name: animation-workflow
description: Orquesta TODO el estudio: interpreta cualquier petición de animación o video, decide qué Skills combinar y en qué orden (guion, personajes, escenarios, imágenes, video, movimiento, expresiones, 2D/3D, audio, edición, render, QC, exportación) y ejecuta el pipeline de punta a punta. Úsala SIEMPRE que el usuario pida crear una animación o video, o cuando no esté claro qué Skill usar.
---

# Flujo de trabajo del estudio (orquestador)

**Categoría:** Producción profesional · **Skills relacionadas:** `animation-scripting`, `animation-storyboarding`, `2d-animation`, `3d-animation`, `animation-quality-control`

Esta es la Skill directora. Recibe instrucciones en lenguaje natural («Crea una caricatura animada», «Haz que un personaje baile», «Convierte esta imagen en video»…) y produce el resultado completo combinando Skills especializadas sobre un único `project.json`.

### Tabla de enrutado

| Petición del usuario | Skills que se combinan | Comando base |
|---|---|---|
| «Crea una caricatura animada» | cartoon-animation → character-design → 2d-animation → animation-sound-design | `make "<idea>" --style cartoon` |
| «Haz una animación estilo anime» | anime-animation → character-expressions → magic/energy-effects | `make "<idea>" --style anime` |
| «Crea un personaje 3D» | character-design → 3d-modeling → 3d-character-animation → blender-animation | `character3d <especie>` o `make "<idea>" --3d` |
| «Historia con frutas animadas» | animation-scripting → story-animation → character-dialogue → character-lip-sync | `make "Haz una historia con frutas…"` |
| «Animación cinematográfica» | cinematic-video → cinematic-effects → 3d-camera-animation → animation-lighting | `make "<idea>" --style cinematic --transition dip` |
| «Convierte esta imagen en video» | ai-video-generation (local o Replicate) → video-editing | `img2video foto.jpg --move parallax` |
| «Para YouTube Shorts / TikTok» | tiktok-animation / youtube-animation → short-video-animation → animation-optimization | `make "<idea>" --format 9:16` + `export --preset tiktok` |
| «Que camine / baile / hable / se emocione» | character-animation → character-movement / character-dancing / character-lip-sync / character-emotions | `make "<personaje> <acción>"` |
| «Para editar en CapCut» | animation-optimization | `export projects/<…>/final.mp4 --preset capcut` (+ enviar el zip al usuario como archivo) |
| «Corto / historia / animación de calidad / 3D tipo película / menos básico» | **corto-3d-ia** (preferido por el usuario) | hoja de personajes → storyboard → Kling 3 Pro → `assemble` (ver `.claude/skills/corto-3d-ia/SKILL.md` y `biblioteca/`) |
| «Ilustrado 2D con arte IA (sin video IA)» | animation-workflow (modo híbrido) | `sprite cutout`/`sprite patch` → `render` (ver `docs/HIBRIDO.md`) |
| «Logo / texto / infografía animada» | animated-logos / kinetic-typography / infographic-animation | `logo`, `text`, `infographic` |
| «Animación para web / Lottie / GSAP / Three.js» | svg/css/gsap/lottie/threejs/interactive-animation | `web <plantilla>`, `lottie` |

## Cuándo usar esta Skill

- Cualquier petición de producción audiovisual animada.
- Peticiones compuestas que requieren varias Skills.
- Cuando hay que decidir entre 2D, 3D, web o IA externa.

## Principios profesionales

- Un proyecto, una fuente de verdad (`project.json`); todas las Skills leen y escriben ahí.
- Iterar barato: plan → storyboard → borrador (`preview`) → final.
- Local primero; IA de pago solo si aporta y el usuario lo acepta.
- Verificar cada entrega con QC y mirando frames reales.
- Comunicar al final qué se hizo, dónde están los archivos y qué requiere claves.

## Procedimiento paso a paso

1. **Diagnóstico**: `python -m studio doctor` (herramientas/claves disponibles).
2. **Interpretar** la petición: formato, estilo, personajes, acciones, emociones, escenario, efectos, duración, destino (YouTube/TikTok…), 2D/3D.
3. **Guion** (`animation-scripting`): `python -m studio plan "<petición>" -o projects/<nombre>.json` (con `--ai` si hay ANTHROPIC_API_KEY).
4. **Personajes** (`character-design`): revisar/ajustar fichas; hoja de modelo para consistencia.
5. **Storyboard** (`animation-storyboarding`): `python -m studio make … --storyboard-only` y revisar `storyboard.jpg`.
6. **Animación** 2D (`2d-animation`) o 3D (`3d-animation`), con estilos, movimiento, expresiones y efectos de las Skills correspondientes.
7. **Audio** (`animation-sound-design`): voces + lip-sync + música + SFX (automático en el render).
8. **Render** (`animation-rendering`): `python -m studio render <json> --quality hd|fullhd`.
9. **Edición/exportación** (`video-editing`, `animation-optimization`): concat, logos, presets de plataforma.
10. **QC** (`animation-quality-control`): `python -m studio qc final.mp4` + inspección visual de 2–3 frames.
11. **Entrega**: rutas de `final.mp4`, `storyboard.jpg`, `vista_previa.gif`, `subtitulos.srt`, ZIP; lista de lo que necesitaría claves externas.

## Comandos del estudio

```bash
python -m studio doctor
python -m studio make "Haz una historia con frutas animadas" --quality preview     # borrador rápido
python -m studio render projects/<carpeta>/project.json --quality hd               # final
python -m studio qc projects/<carpeta>/final.mp4
python -m studio export projects/<carpeta>/final.mp4 --preset tiktok
python -m studio serve                                                             # interfaz gráfica
```

## Fragmento de proyecto (project.json)

```json
{
  "title": "…", "style": "cartoon", "format": "16:9", "fps": 24, "mood": "happy", "engine": "2d",
  "music": true, "voices": true, "subtitles": true, "transition": "fade",
  "characters": [ {"id": "…", "species": "…", "color": "#…", "accessory": "none"} ],
  "scenes": [ {"background": "…", "time_of_day": "day", "duration": 4, "camera": {"type": "pan"},
               "actors": [ … ], "dialogue": [ … ], "effects": [ … ], "caption": "…"} ]
}
```

## Ejemplo completo

**«Crea una animación para YouTube Shorts de un gato y un perro que bailan en la playa al atardecer, estilo tierno»**

1. `doctor` → todo local disponible.  2. `plan "… " --style cute --format 9:16 -o projects/baile.json` → 3 escenas en `beach` (sunset), dance/jump/celebrate, música dance.
3. Ajustar: añadir `hearts` en la escena final.  4. `render projects/baile.json --quality preview` → revisar storyboard y GIF.
5. `render … --quality fullhd` → `qc` aprobado.  6. `export … --preset youtube_shorts`.  7. Entregar rutas y mencionar que voces realistas requerirían ELEVENLABS_API_KEY (opcional).

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| CLI `python -m studio` | pipeline completo | ✅ motor propio del estudio |
| Interfaz web (FastAPI) | uso sin programar | ✅ motor propio del estudio |
| Blender, FFmpeg, espeak-ng, Chromium, Remotion | motores | ✅ instalado y probado |
| Claude API / Replicate / ElevenLabs / OpenAI / Stability / HF | capacidades IA opcionales | 🔑 requiere clave API |

## Control de calidad

- [ ] Se usaron las Skills adecuadas para cada parte de la petición.
- [ ] El resultado coincide con formato, estilo y duración pedidos.
- [ ] QC aprobado y frames revisados.
- [ ] Informe final honesto (qué funcionó, qué necesita claves).

## Errores comunes y cómo evitarlos

- Saltarse el borrador y renderizar en fullhd a la primera (tiempo perdido).
- Mezclar estilos sin intención.
- Decir que algo funcionó sin abrir el archivo.

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
