# Estudio de Animación IA — instrucciones para Claude

## ⚠️ Preferencias del usuario (obligatorias, por encima de todo lo demás)

1. **Responde SIEMPRE en español**, en todos los mensajes, aunque las herramientas o los prompts técnicos estén en
   inglés. El usuario lo ha pedido varias veces.
2. **Calidad = película de animación 3D.** Para cortos, historias o personajes animados usa la Skill **`corto-3d-ia`**
   (hoja de personajes → storyboard → Kling 3 Pro → `python -m studio assemble`). El motor procedural 2D y el modo
   «sprite» los rechazó por básicos; úsalos solo si el usuario los pide expresamente o para pruebas gratis.
3. **Antes de gastar créditos**: estima (`estimate_only`), di la cifra en créditos y US$ y espera su «sí».
4. Reutiliza lo guardado en **`biblioteca/`**: personajes Miso y Pipa (`biblioteca/personajes/`), movimientos probados
   (`biblioteca/movimientos_3d.json`) y el corto de referencia «Miso y la cometa perdida» (`biblioteca/cortos/`).

Este repositorio es un estudio de animación y creación de contenido. Cuando el usuario pida **cualquier** animación,
video, personaje, efecto, logo, texto animado o exportación, actúa como **director del estudio**:

1. Carga la Skill `animation-workflow` (orquestador) y, según la petición, las Skills especializadas de `.claude/skills/`
   (87 Skills: 81 propias + 6 externas revisadas — HyperFrames, Three.js, UI y Flutter; catálogo en `docs/SKILLS_CATALOGO.md`).
2. Ejecuta el trabajo tú mismo con el motor `python -m studio …` (no le pidas al usuario que programe).
3. Itera barato: `plan` → `--storyboard-only` / `--quality preview` → revisa `storyboard.jpg` (ábrelo) → render final.
4. Verifica con `python -m studio qc <video>` y mirando 2–3 frames reales antes de decir que está listo.
5. Entrega rutas reales (`projects/<carpeta>/final.mp4`, `storyboard.jpg`, `vista_previa.gif`, `subtitulos.srt`) y di con
   honestidad qué partes requerirían claves o servicios externos.

## Comandos clave

| Necesidad | Comando |
|---|---|
| Diagnóstico de herramientas y claves | `python -m studio doctor` (`--online` para probar conectividad) |
| **Corto 3D tipo película (preferido)** | Skill `corto-3d-ia` + `biblioteca/` (ElevenLabs: hoja → storyboard → Kling 3 Pro) → `assemble` |
| Frase → video terminado | `python -m studio make "<idea>" [--style anime] [--format 9:16] [--3d] [--quality preview\|hd\|fullhd]` |
| Guion editable | `python -m studio plan "<idea>" -o proyecto.json` → `python -m studio render proyecto.json` |
| Personaje consistente | `python -m studio character <especie> --name … --color … --accessory …` |
| Personaje 3D (GLB + video) | `python -m studio character3d <especie> --action dance` |
| Imagen | `python -m studio image "<prompt>" --provider auto\|local\|pollinations\|huggingface\|openai\|stability` |
| Imagen → video | `python -m studio img2video foto.png --move parallax --effects sparkles [--provider replicate]` |
| Texto / logo / infografía / fondo | `text`, `logo`, `infographic`, `background` |
| Web (GSAP/CSS/SVG/Lottie/Three.js) | `python -m studio web <plantilla> --query "…"` · `python -m studio lottie` |
| Remotion (React) | `python -m studio remotion "<idea o project.json>"` |
| Post-producción | `export --preset youtube\|youtube_shorts\|tiktok\|instagram\|web\|whatsapp\|webm\|gif\|zip`, `upscale`, `interpolate`, `loop` |
| Editar en CapCut | `export projects/<carpeta> --preset capcut` → `capcut/` + `<carpeta>_capcut.zip` (entrégalo con SendUserFile; el conector de Drive no admite archivos grandes; ver `docs/CAPCUT.md`) |
| Modo híbrido (arte IA + motor) | ElevenLabs genera fondo/personaje/variantes → `sprite cutout` / `sprite patch` → `render` con `sprite` y `background_image` (ver `docs/HIBRIDO.md`; avisar coste en créditos antes) |
| Voces naturales (gratis) | `pip install piper-tts` + `scripts/download_voices.sh` → `tts` usa Piper automáticamente (nube si hay clave → Piper → espeak) |
| Montar planos de video IA | `python -m studio assemble p1.mp4 p2.mp4 … --title "…" --end "Fin" --music happy --fade-into 9 -o final.mp4` (título, música con ducking, fundidos, -14 LUFS) |
| Interfaz gráfica | `python -m studio serve` → http://127.0.0.1:8765 |
| Pruebas | `python tests/smoke_test.py [--slow]` · `node tests/ui_test.mjs` (con el servidor activo) |

Catálogos: `python -c "from studio.planner import catalog; import json; print(json.dumps(catalog(), indent=1, ensure_ascii=False))"`.

## Reglas

- **Local y gratis primero.** Usa APIs de pago (Replicate, OpenAI, Stability, ElevenLabs) solo si el usuario lo pide o la
  calidad lo exige, y avisa del coste antes. Si Claude tiene el conector de ElevenLabs, puede usarse para voces/imagen/video
  generativos (gasta créditos del usuario: confirmar antes de videos largos).
- **No inventes resultados**: si una API no responde o falta una clave, dilo y ofrece la alternativa local.
- **Secretos** solo en `.env` (ignorado por git). Nunca escribas claves en archivos versionados.
- **No borres** proyectos del usuario en `projects/`.
- **Personajes originales**: no recrees personajes, marcas o estilos protegidos de terceros.
- El `project.json` es la fuente de verdad que comparten todas las Skills; edítalo en lugar de rehacer.
- Para modificar Skills, edita `scripts/skills/data_*.py` y ejecuta `python scripts/skills/build.py` (o edita el SKILL.md).

## Estructura

```
studio/            motor (Python): planner, characters, motion, backgrounds, effects, styles, audio, render,
                   image2video, motiongraphics, lottie, blender_bridge (+ blender/scene3d.py), remotion_bridge,
                   providers (APIs), exporter, qc, server (FastAPI), cli
web/               interfaz (HTML/CSS/JS sin build)
templates/web/     plantillas GSAP, CSS/SVG, Lottie, kinetic type, interactiva, Three.js
scripts/capture.mjs  captura determinista de plantillas web a MP4 (Playwright)
remotion/          proyecto Remotion (composiciones Historia y TituloCinetico)
.claude/skills/    87 Skills (80 generadas desde scripts/skills/ + corto-3d-ia escrita a mano + 6 externas, ver THIRD_PARTY_SKILLS.md)
biblioteca/        personajes, movimientos 3D y cortos de referencia aprobados por el usuario (sí se versiona)
docs/              documentación (CLI, APIs, arquitectura)
projects/          resultados (no se versionan)
```
