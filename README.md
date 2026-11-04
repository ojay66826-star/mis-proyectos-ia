# mis-proyectos-ia

## 🎬 Estudio de Animación con Inteligencia Artificial

Un estudio completo de creación de contenido animado que **recibe instrucciones en español** y produce el video
terminado: guion, personajes consistentes, escenarios, animación 2D y 3D, expresiones, lip-sync, efectos visuales,
voces, música, efectos de sonido, edición, render, control de calidad y exportación para cada red social.

> «Crea una caricatura animada» · «Haz una animación estilo anime» · «Crea un personaje 3D» ·
> «Haz una historia con frutas animadas» · «Crea una animación cinematográfica» · «Convierte esta imagen en un video» ·
> «Crea una animación para YouTube Shorts o TikTok» · «Haz que un personaje camine, baile, hable o exprese emociones»

**Funciona 100 % gratis y sin conexión** con motores locales. Las APIs de IA (imágenes/video/voces realistas) son opcionales.

---

## 🚀 Cómo usarlo (sin programar)

### Opción A — Pídeselo a Claude
Abre este repositorio en Claude Code y escribe lo que quieras, por ejemplo:
*«Haz una historia con frutas animadas para TikTok»*. Claude usa las 80 Skills del estudio (`.claude/skills/`),
ejecuta el motor, revisa el resultado y te entrega el video.

### Opción B — La interfaz gráfica
```bash
./install.sh                 # una sola vez (Ubuntu/Debian/WSL; en macOS usa Homebrew)
python3 -m studio serve      # abre http://127.0.0.1:8765
```
1. Escribe qué quieres crear (o pulsa un ejemplo).
2. Elige estilo (14 estilos) y formato (YouTube, TikTok, Instagram).
3. Opcional: añade personajes, escenario, efectos y música.
4. Pulsa **Ver guion** para revisar/editar diálogos o **Crear animación**.
5. Mira el video, descarga MP4/GIF/storyboard/subtítulos/ZIP y exporta para cada red.

Pestañas extra: **Personajes** (hojas de modelo y versión 3D), **Imagen → Video**, **Texto y logos**,
**3D y Web** (Three.js, GSAP, Lottie, SVG/CSS), **Mis proyectos** y **Estado** (herramientas y claves).

### Opción C — Línea de comandos
```bash
python3 -m studio make "Haz una historia con frutas animadas"
python3 -m studio make "Crea una animación para TikTok de un plátano que baila"          # 9:16 automático
python3 -m studio make "Un gato baila en el escenario" --3d                               # Blender
python3 -m studio img2video foto.jpg --move parallax --effects sparkles
python3 -m studio character manzana --name Rojita --accessory bow                        # hoja de personaje
python3 -m studio logo "Mi Marca" --tagline "Animación con IA"
python3 -m studio export projects/<carpeta>/final.mp4 --preset tiktok
python3 -m studio doctor                                                                  # qué está instalado
```
Referencia completa: [`docs/CLI.md`](docs/CLI.md).

---

## ✨ Qué puede hacer

| Área | Capacidades |
|---|---|
| **Guion** | Planificador en español/inglés (historias, bailes, peleas, magia, terror, clases…); con `--ai` usa Claude |
| **Personajes** | 27 especies (11 frutas, 8 animales, robot, niño/niña/persona, mago, mascota, fantasma, monstruo, estrella), 8 accesorios, 3 tipos de ojos, fichas JSON para consistencia total, hojas de modelo |
| **Animación** | 15 acciones (caminar, correr, saltar, bailar al BPM, hablar, saludar, golpear, patear, celebrar, flotar, temblar, girar, pensar…), 11 emociones, cambios en el tiempo, transformaciones, lip-sync con visemas |
| **Escenarios** | 15 fondos con paralaje × día/atardecer/noche, nubes animadas, cámara (pan, zoom, dolly, temblor, órbita 3D) |
| **Efectos** | 19 VFX deterministas: fuego, humo, lluvia, olas, salpicaduras, nieve, rayos, explosiones, magia, aura y rayo de energía, confeti, corazones, burbujas, niebla, luciérnagas, hojas, speedlines |
| **Estilos** | caricatura, anime, pixel art, minimalista, tierno, cinematográfico, terror, fantasía, papel, plastilina, stop-motion, realista, cómic, retro VHS |
| **3D** | Blender headless: personajes 3D procedurales, 15 escenarios, luces de 3 puntos, EEVEE/Cycles, exporta `.blend` y GLB |
| **Audio** | Voces TTS por personaje (espeak-ng español), música procedural libre de derechos (9 estados de ánimo), 17 efectos sincronizados, ducking, -14 LUFS |
| **Motion design** | Tipografía cinética, logos animados, infografías, fondos en bucle, Lottie, plantillas GSAP/CSS/SVG/Three.js, Remotion |
| **Post** | Transiciones, concat, presets YouTube/Shorts/TikTok/Instagram/web/WhatsApp, WebM, GIF, upscale, 60 fps, bucles, ZIP |
| **Calidad** | QC automático (códec, duración, audio, negros, congelados, LUFS, picos), storyboard, miniatura, SRT |

---

## 🧠 Las 80 Skills

Cada Skill vive en `.claude/skills/<nombre>/SKILL.md` con instrucciones profesionales, principios, procedimiento,
comandos reales, ejemplo completo, herramientas, checklist de calidad y errores comunes. Todas comparten el mismo
`project.json`, y **`animation-workflow`** las orquesta automáticamente.

| Categoría | Skills |
|---|---|
| Animación 2D | 2d-animation, cartoon-animation, anime-animation, character-animation, frame-by-frame-animation, cutout-animation, motion-comics, pixel-art-animation, sprite-animation, story-animation |
| Animación 3D | 3d-animation, 3d-character-animation, 3d-modeling, 3d-rigging, 3d-walk-cycles, 3d-facial-animation, 3d-camera-animation, 3d-environment-animation, blender-animation, threejs-animation |
| Personajes | character-design, character-expressions, character-movement, character-lip-sync, character-dialogue, character-dancing, character-fighting, character-emotions, character-transformations, mascot-animation |
| Efectos visuales | visual-effects, particle-effects, fire-animation, smoke-animation, water-animation, magic-effects, lightning-effects, explosions, energy-effects, cinematic-effects |
| Videos y contenido | ai-video-generation, cinematic-video, short-video-animation, youtube-animation, tiktok-animation, animated-storytelling, music-video-animation, video-transitions, video-editing, seamless-loop-animation |
| Estilos especiales | stop-motion, clay-animation, paper-animation, realistic-animation, fantasy-animation, horror-animation, cute-animation, minimalist-animation, educational-animation, infographic-animation |
| Diseño y movimiento | motion-graphics, animated-logos, typography-animation, kinetic-typography, animated-backgrounds, svg-animation, lottie-animation, css-animation, gsap-animation, interactive-animation |
| Producción profesional | animation-storyboarding, scene-composition, animation-lighting, animation-rendering, animation-sound-design, animation-scripting, animation-quality-control, animation-optimization, animation-upscaling, animation-workflow |

Verificación: `python3 -m studio check-skills`. Para editarlas en bloque: `scripts/skills/data_*.py` → `python3 scripts/skills/build.py`.

---

## 🔌 Herramientas y servicios

| Herramienta | Estado |
|---|---|
| FFmpeg 6.1, Blender 4.0.2 (EEVEE/Workbench/Cycles), espeak-ng, sox | ✅ instalados y probados |
| Three.js 0.170, GSAP 3.15, lottie-web 5.13 (locales, sin CDN) | ✅ probados con captura Chromium |
| Remotion 4.0.290 | ✅ probado |
| Pollinations, Hugging Face, OpenAI, Stability (imágenes) | ⚠️ implementados, requieren red/clave — ver [`docs/APIS.md`](docs/APIS.md) |
| Replicate (video IA), ElevenLabs / OpenAI (voces), Claude (guiones) | ⚠️ implementados, requieren clave |

Las claves se ponen en `.env` (copia de `.env.example`). `.env` está en `.gitignore`: **nunca se sube a GitHub**.

---

## 🧪 Pruebas

```bash
python3 tests/smoke_test.py          # prueba todos los comandos (~10 min) → tests/resultados/REPORTE.md
python3 tests/smoke_test.py --slow   # + 3D completo en Blender y Remotion
python3 -m studio serve & node tests/ui_test.mjs   # prueba la interfaz de punta a punta con un navegador
```

## 📁 Estructura

```
studio/          motor del estudio (Python)        web/             interfaz gráfica
templates/web/   plantillas GSAP/CSS/SVG/Lottie/3D  scripts/         captura web, generador de Skills y docs
remotion/        proyecto Remotion (React)          .claude/skills/  80 Skills
docs/            CLI, APIs, arquitectura            projects/        tus videos (no se suben a git)
tests/           pruebas automáticas                CLAUDE.md        instrucciones para Claude
```

Más detalles: [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md).

## 📜 Licencias

Código del estudio: tuyo. Fuente DejaVu (incluida en `studio/assets/fonts/`, licencia libre en `LICENSE-DejaVu.txt`).
La música y los efectos se sintetizan (sin samples de terceros). Remotion tiene su propia licencia (gratis para
personas y empresas de hasta 3 empleados). Respeta los términos de cada API externa y crea personajes originales.
