OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
EXT = "💻 programa externo recomendado"
MCP = "🔌 conector MCP (si está conectado en Claude)"

ROUTING = """| Petición del usuario | Skills que se combinan | Comando base |
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
| «Animación para web / Lottie / GSAP / Three.js» | svg/css/gsap/lottie/threejs/interactive-animation | `web <plantilla>`, `lottie` |"""

SKILLS = {
"animation-workflow": dict(
    title="Flujo de trabajo del estudio (orquestador)",
    description="Orquesta TODO el estudio: interpreta cualquier petición de animación o video, decide qué Skills combinar y en qué orden (guion, personajes, escenarios, imágenes, video, movimiento, expresiones, 2D/3D, audio, edición, render, QC, exportación) y ejecuta el pipeline de punta a punta. Úsala SIEMPRE que el usuario pida crear una animación o video, o cuando no esté claro qué Skill usar.",
    intro=f"Esta es la Skill directora. Recibe instrucciones en lenguaje natural («Crea una caricatura animada», «Haz que un personaje baile», «Convierte esta imagen en video»…) y produce el resultado completo combinando Skills especializadas sobre un único `project.json`.\n\n### Tabla de enrutado\n\n{ROUTING}",
    when=["Cualquier petición de producción audiovisual animada.", "Peticiones compuestas que requieren varias Skills.", "Cuando hay que decidir entre 2D, 3D, web o IA externa."],
    principles=["Un proyecto, una fuente de verdad (`project.json`); todas las Skills leen y escriben ahí.", "Iterar barato: plan → storyboard → borrador (`preview`) → final.",
                "Local primero; IA de pago solo si aporta y el usuario lo acepta.", "Verificar cada entrega con QC y mirando frames reales.",
                "Comunicar al final qué se hizo, dónde están los archivos y qué requiere claves."],
    steps=["**Diagnóstico**: `python -m studio doctor` (herramientas/claves disponibles).",
           "**Interpretar** la petición: formato, estilo, personajes, acciones, emociones, escenario, efectos, duración, destino (YouTube/TikTok…), 2D/3D.",
           "**Guion** (`animation-scripting`): `python -m studio plan \"<petición>\" -o projects/<nombre>.json` (con `--ai` si hay ANTHROPIC_API_KEY).",
           "**Personajes** (`character-design`): revisar/ajustar fichas; hoja de modelo para consistencia.",
           "**Storyboard** (`animation-storyboarding`): `python -m studio make … --storyboard-only` y revisar `storyboard.jpg`.",
           "**Animación** 2D (`2d-animation`) o 3D (`3d-animation`), con estilos, movimiento, expresiones y efectos de las Skills correspondientes.",
           "**Audio** (`animation-sound-design`): voces + lip-sync + música + SFX (automático en el render).",
           "**Render** (`animation-rendering`): `python -m studio render <json> --quality hd|fullhd`.",
           "**Edición/exportación** (`video-editing`, `animation-optimization`): concat, logos, presets de plataforma.",
           "**QC** (`animation-quality-control`): `python -m studio qc final.mp4` + inspección visual de 2–3 frames.",
           "**Entrega**: rutas de `final.mp4`, `storyboard.jpg`, `vista_previa.gif`, `subtitulos.srt`, ZIP; lista de lo que necesitaría claves externas."],
    commands="""python -m studio doctor
python -m studio make "Haz una historia con frutas animadas" --quality preview     # borrador rápido
python -m studio render projects/<carpeta>/project.json --quality hd               # final
python -m studio qc projects/<carpeta>/final.mp4
python -m studio export projects/<carpeta>/final.mp4 --preset tiktok
python -m studio serve                                                             # interfaz gráfica""",
    spec="""{
  "title": "…", "style": "cartoon", "format": "16:9", "fps": 24, "mood": "happy", "engine": "2d",
  "music": true, "voices": true, "subtitles": true, "transition": "fade",
  "characters": [ {"id": "…", "species": "…", "color": "#…", "accessory": "none"} ],
  "scenes": [ {"background": "…", "time_of_day": "day", "duration": 4, "camera": {"type": "pan"},
               "actors": [ … ], "dialogue": [ … ], "effects": [ … ], "caption": "…"} ]
}""",
    example="""**«Crea una animación para YouTube Shorts de un gato y un perro que bailan en la playa al atardecer, estilo tierno»**

1. `doctor` → todo local disponible.  2. `plan "… " --style cute --format 9:16 -o projects/baile.json` → 3 escenas en `beach` (sunset), dance/jump/celebrate, música dance.
3. Ajustar: añadir `hearts` en la escena final.  4. `render projects/baile.json --quality preview` → revisar storyboard y GIF.
5. `render … --quality fullhd` → `qc` aprobado.  6. `export … --preset youtube_shorts`.  7. Entregar rutas y mencionar que voces realistas requerirían ELEVENLABS_API_KEY (opcional).""",
    tools=[("CLI `python -m studio`", "pipeline completo", ENG), ("Interfaz web (FastAPI)", "uso sin programar", ENG), ("Blender, FFmpeg, espeak-ng, Chromium, Remotion", "motores", OK),
           ("Claude API / Replicate / ElevenLabs / OpenAI / Stability / HF", "capacidades IA opcionales", KEY)],
    qc=["Se usaron las Skills adecuadas para cada parte de la petición.", "El resultado coincide con formato, estilo y duración pedidos.", "QC aprobado y frames revisados.",
        "Informe final honesto (qué funcionó, qué necesita claves)."],
    pitfalls=["Saltarse el borrador y renderizar en fullhd a la primera (tiempo perdido).", "Mezclar estilos sin intención.", "Decir que algo funcionó sin abrir el archivo."],
    related=["animation-scripting", "animation-storyboarding", "2d-animation", "3d-animation", "animation-quality-control"]),

"animation-storyboarding": dict(
    title="Storyboard de animación",
    description="Crea storyboards y animatics: viñetas por escena con fondo, acciones y cámara, hoja de contacto automática, timing por plano y animatic de baja resolución para validar antes del render final. Úsala para 'storyboard', 'guion gráfico', 'animatic', 'planificar las escenas visualmente'.",
    intro="`render.storyboard()` genera `storyboard.jpg`: dos fotogramas por escena (15 % y 60 % de su duración) con etiqueta de escena, fondo, cámara y acciones. `--storyboard-only` lo crea sin renderizar el video; `--quality preview` produce un animatic rápido (media resolución).",
    when=["Antes de cualquier render largo.", "Para aprobar una historia con el usuario."],
    principles=["Un panel por cambio de idea/plano.", "Indicar movimiento (cámara y personajes).", "Timing anotado por panel.", "Validar legibilidad: ¿se entiende la historia solo con los paneles?"],
    steps=["`python -m studio make \"<idea>\" --storyboard-only` (o `plan` + `render --quality preview`).", "Abre `storyboard.jpg` y revisa composición y continuidad.",
           "Ajusta `project.json` (posiciones, cámaras, duraciones).", "Animatic: `render --quality preview` y revisa `vista_previa.gif`."],
    commands="""python -m studio make "Un robot y una niña exploran el espacio" --storyboard-only
python -m studio render projects/<…>/project.json --quality preview""",
    example="""Aprobación con cliente: entregar `storyboard.jpg` + animatic preview; tras feedback, render final.""",
    tools=[("render.storyboard", "hoja de contacto", ENG), ("Storyboarder (Wonder Unit, gratis)", "storyboard dibujado", EXT), ("Krita", "paneles a mano", EXT)],
    qc=["Todas las escenas presentes.", "Continuidad de personajes y dirección de mirada.", "Duraciones razonables."],
    pitfalls=["Aprobar solo con texto: siempre mostrar el storyboard.", "Ignorar la regla de 180° entre paneles."],
    related=["animation-scripting", "scene-composition", "animation-workflow"]),

"scene-composition": dict(
    title="Composición de escena",
    description="Compone planos legibles y atractivos: regla de tercios, profundidad, aire en la mirada, jerarquía visual, escala, contraste figura-fondo, posiciones de personajes y encuadre por formato (16:9, 9:16, 1:1). Úsala para 'composición', 'encuadre', 'dónde poner a los personajes', 'que se vea mejor la escena'.",
    intro="Coordenadas normalizadas del estudio: x 0–1, y del suelo 0.82 (`GROUND_Y`). Personajes a 46 % de la altura (1–2 personajes) o 38 % (3+); en vertical, 42 % del ancho. El orden de dibujo por y simula profundidad. La cámara `focus` define el centro de zoom.",
    when=["Ajustar posiciones y cámaras.", "Adaptar una escena de 16:9 a 9:16."],
    principles=["Tercios: protagonistas en x≈0.33/0.66.", "Aire delante de la mirada.", "Primer plano más oscuro/grande, fondo más claro/pequeño.",
                "En 9:16 apilar verticalmente o usar 1–2 personajes."],
    steps=["Revisa el storyboard.", "Ajusta `from/to`, `scale`, `facing` y `camera.focus`.", "Para profundidad, distintos `y` (0.78–0.88) y `scale` (0.8–1.1).", "Re-renderiza en preview."],
    commands="""python -m studio render projects/<…>/project.json --quality preview""",
    spec="""{"camera": {"type": "zoom_in", "focus": [0.33, 0.6]},
 "actors": [{"character": "heroe", "from": [0.33, 0.85], "scale": 1.1, "facing": 1},
            {"character": "amigo", "from": [0.7, 0.79], "scale": 0.85, "facing": -1}]}""",
    example="""Diálogo en 9:16: dos personajes a x 0.3 y 0.7, cámara static, subtítulos grandes a y≈70 % — sin superponer caras.""",
    tools=[("Motor 2D (coordenadas normalizadas)", "composición", ENG), ("Blender camera", "composición 3D (guías de tercios)", OK)],
    qc=["Protagonista identificable en 1 s.", "Nada importante en los bordes.", "Subtítulos sin tapar caras."],
    pitfalls=["Centrar todo siempre: estático y aburrido.", "Personajes cortados por los bordes en 9:16."],
    related=["animation-storyboarding", "3d-camera-animation", "character-movement"]),

"animation-lighting": dict(
    title="Iluminación para animación",
    description="Diseña la iluminación: tres puntos (key, fill, rim), hora del día (día, atardecer, noche), color de la luz con intención emocional, focos de escenario, exposición y tone mapping (AgX/Filmic/ACES) en 2D, Blender y Three.js. Úsala para 'iluminación', 'luces', 'que se vea más bonito', 'ambiente nocturno', 'luz dramática'.",
    intro="2D: `time_of_day` cambia paleta (sunset tinta naranja, night oscurece al 45 %), sol con halo, luna y estrellas; los estilos añaden grading/bloom. 3D: `lights()` crea sun key + area fill + area rim con energía por hora, focos RGB en `stage`, transform AgX. Three.js: hemisferio + key con sombras + rim y ACES.",
    when=["Ajustar ambiente y emoción.", "Escenas 3D que se ven planas o quemadas."],
    principles=["Key define la forma; fill controla el contraste; rim separa del fondo.", "Ratio key:fill 2:1 (amable) a 8:1 (dramático).",
                "Temperatura con significado: cálido = seguridad, frío = misterio.", "Exposición sin quemar blancos (tone mapping)."],
    steps=["Elige hora del día por escena.", "En 3D ajusta energías en `lights()` o en el `.blend`.", "Revisa histograma/frame y corrige.", "Aplica estilo (cinematic/fantasy) para grading final."],
    commands="""python -m studio make "Un oso acampa en el bosque al atardecer" --quality preview
python -m studio make "Un gato baila en el escenario" --3d --quality preview     # focos de colores""",
    example="""Escena de terror más legible: mantener `night` pero añadir `fireflies`/`fire` como fuentes de luz motivadas cerca del personaje.""",
    tools=[("backgrounds (time_of_day)", "luz 2D", ENG), ("Blender lights + AgX", "luz 3D", OK), ("Three.js lights + ACES", "luz web", OK), ("Poly Haven HDRI", "iluminación realista", NET)],
    qc=["Personajes bien iluminados (cara legible).", "Sin zonas quemadas.", "Coherencia de dirección de luz entre planos."],
    pitfalls=["Energías de luz en Blender demasiado altas (colores lavados).", "Noche totalmente negra."],
    related=["cinematic-effects", "3d-environment-animation", "animation-rendering"]),

"animation-rendering": dict(
    title="Renderizado de animación",
    description="Renderiza con calidad y eficiencia: niveles de calidad (preview/hd/fullhd), render paralelo multinúcleo, motores 3D (Workbench/EEVEE/Cycles), codificación H.264/AAC, frames PNG, tiempos estimados y recuperación de errores. Úsala para 'renderizar', 'render final', 'exportar en 1080p', 'el render tarda/falla'.",
    intro="El motor 2D renderiza frames en paralelo (`multiprocessing`, hasta 8 procesos) y los envía por tubería a FFmpeg (libx264 CRF 19, yuv420p) sin escribir PNGs; luego mezcla audio y hace mux con faststart. Referencia medida: ~15 s de video 720p en ~80 s con 4 núcleos; preview ~4× más rápido. 3D en CPU sin GPU: EEVEE ≈ 3–6 s/frame a 640×360.",
    when=["Render final, cambios de calidad, problemas de rendimiento."],
    principles=["Iterar en preview, entregar en hd/fullhd.", "No recodificar varias veces (pérdida).", "yuv420p y dimensiones pares para compatibilidad.",
                "Registrar tiempos para estimar."],
    steps=["Elige calidad: `--quality preview|hd|fullhd`.", "2D: `python -m studio render project.json --quality hd`.", "3D: elige `--engine rapido|eevee|cycles`; usa preview para iterar.",
           "Si falla: revisa el mensaje; en 3D mira `frames3d/blender.log`.", "Verifica con `qc`."],
    commands="""python -m studio render projects/<…>/project.json --quality fullhd
python -m studio make "<idea>" --3d --engine eevee --quality preview
tail -50 projects/<…>/frames3d/blender.log""",
    example="""Entrega 1080p de una historia de 30 s: preview (≈40 s) → correcciones → fullhd (≈4–5 min en 4 núcleos) → QC → export youtube.""",
    tools=[("render.py (multiproceso)", "render 2D", ENG), ("FFmpeg libx264/libvpx-vp9", "codificación", OK), ("Blender EEVEE/Cycles", "render 3D", OK),
           ("GPU NVIDIA + Blender oficial", "render 3D 10–50× más rápido", EXT)],
    qc=["Duración y fps correctos.", "Sin frames corruptos ni negros.", "Audio sincronizado."],
    pitfalls=["fullhd en borradores (lento).", "Disco lleno con frames 3D: borra `frames3d/*.png` tras montar si no se necesitan."],
    related=["animation-optimization", "animation-quality-control", "blender-animation"]),

"animation-sound-design": dict(
    title="Diseño de sonido para animación",
    description="Diseña y mezcla el audio: voces TTS por personaje, música procedural por estado de ánimo (9 moods con BPM), efectos sincronizados (pasos, saltos, golpes, magia, truenos, explosiones, lluvia, fuego), ducking bajo diálogos, normalización y stems. Úsala para 'música', 'efectos de sonido', 'voces', 'audio', 'sonido', 'mezcla'.",
    intro="`audio.py` sintetiza todo sin samples externos (libre de derechos): música con progresiones de acordes, bajo, melodía y batería por mood (happy, cute, sad, epic, spooky, dance, action, calm, fantasy); 17 SFX (whoosh, pop, boing, footstep, explosion, magic, thunder, fire, punch, splash, sparkle, rain, jump, ding, transform, energy, wind); `mix_timeline` con ducking de música bajo las voces. `build_audio` coloca SFX automáticamente según acciones y efectos.",
    when=["Cualquier video (el audio se genera automáticamente).", "Cambiar música, añadir una canción propia o voces profesionales."],
    principles=["Jerarquía: voz > SFX > música (ducking 55 %).", "Sincronía SFX-acción al frame.", "Música que refuerza la emoción, no la contradice.",
                "Sonoridad final ≈ -14 LUFS para redes, picos ≤ -1 dBFS."],
    steps=["Elige `mood` (o deja que el planificador lo deduzca).", "Voces: espeak local; para naturales define `STUDIO_TTS=elevenlabs|openai` + clave.",
           "Renderiza; stems en `audio/` (mezcla.wav, musica.wav, voces por línea).", "Canción propia: `music: false` + `add_audio`.", "QC revisa LUFS y picos."],
    commands="""python -m studio make "Un monstruo tierno baila" --mood dance
python -c "from studio.audio import synth_music, write_wav; write_wav('epica.wav', synth_music('epic', 20))"
python -c "from studio.audio import synth_sfx, write_wav; write_wav('magia.wav', synth_sfx('magic'))\"""",
    example="""Escena de tormenta: lluvia en bucle + trueno sincronizado con cada rayo + música `spooky` con drone + voz con ducking. Todo automático a partir de los efectos del JSON.""",
    tools=[("audio.py (síntesis)", "música/SFX/mezcla", ENG), ("espeak-ng", "voces locales", OK), ("sox", "procesado (reverb, pitch, normalize)", OK),
           ("ElevenLabs / OpenAI TTS", "voces naturales", KEY), ("ElevenLabs (conector)", "voces/música generativas", MCP), ("Freesound / Pixabay Music", "bancos CC", NET)],
    qc=["Voces inteligibles sobre la música.", "Sin clipping.", "LUFS en rango (-24 a -8; ideal -14)."],
    pitfalls=["Música con copyright de terceros.", "SFX en bucle que no paran al acabar el efecto: usa `end`."],
    related=["character-lip-sync", "music-video-animation", "animation-quality-control"]),

"animation-scripting": dict(
    title="Guion de animación",
    description="Escribe guiones para animación: logline, estructura, escenas con acción y diálogo, duración por escena, tono y público; los convierte al project.json; con planificador local o Claude (salida estructurada). Úsala para 'guion', 'escribe la historia', 'diálogos', 'script', 'idea para un video'.",
    intro="`planner.plan()` analiza la petición (español/inglés) detectando personajes (27 especies y grupos como 'frutas'), estilo, formato, escenario, acciones, emociones y efectos, y construye la estructura según el género (historia, baile, pelea, magia, terror, acción simple). Con `--ai` y ANTHROPIC_API_KEY, Claude escribe el guion con JSON Schema estricto y el estudio lo normaliza.",
    when=["Antes de producir cualquier animación con narrativa.", "Para convertir un texto/cuento del usuario en escenas."],
    principles=["Formato de guion de animación: acción visual primero, diálogo breve.", "Duración: ~2.5 palabras de diálogo por segundo.",
                "Cada escena con objetivo y cambio.", "Escribir para el oído (TTS): frases simples y puntuadas."],
    steps=["Logline + público + duración.", "`python -m studio plan \"<petición>\" -o guion.json` (añade `--ai` si hay clave).", "Edita textos/acciones en el JSON o en la interfaz.",
           "Valida duración total y legibilidad; pasa a storyboard."],
    commands="""python -m studio plan "Una manzana valiente rescata a un gatito en la ciudad" -o guion.json
python -m studio plan "Una manzana valiente rescata a un gatito en la ciudad" --ai -o guion_ai.json   # con Claude
python -c "import json; d=json.load(open('guion.json')); [print(s['id'], [x['text'] for x in s['dialogue']]) for s in d['scenes']]\"""",
    example="""Del cuento del usuario (texto largo) → resumirlo en 4–6 beats → `plan` con ese resumen y `--ai` → revisar diálogos para TTS (sin abreviaturas).""",
    tools=[("planner.py", "guion local por reglas", ENG), ("Claude API (claude-opus-5-5, structured outputs)", "guion creativo", KEY), ("Fountain / WriterSolo", "guion en formato profesional", EXT)],
    qc=["Personajes de los diálogos existen en el reparto.", "Duración total como se pidió.", "Diálogos naturales al oírlos."],
    pitfalls=["Diálogos largos para TTS.", "Acciones imposibles para el catálogo: usar las disponibles (ver `planner.catalog()`)."],
    related=["animation-storyboarding", "story-animation", "character-dialogue"]),

"animation-quality-control": dict(
    title="Control de calidad (QC)",
    description="Verifica entregas: validez del archivo, códec, dimensiones, duración, pista de audio, tramos negros, congelamientos, sonoridad (LUFS), picos, más revisión visual de frames y checklist artística. Úsala para 'revisa el video', 'control de calidad', 'QC', 'comprueba que esté bien', o al terminar cualquier render.",
    intro="`python -m studio qc` usa ffprobe + filtros de FFmpeg (`blackdetect`, `freezedetect`, `ebur128`) y emite `qc_report.json` (también automático tras cada render). Complementa con inspección visual: extraer 3 frames y mirarlos.",
    when=["Siempre al final de un render.", "Antes de publicar o entregar."],
    principles=["Automatizar lo técnico, mirar lo artístico.", "Errores bloquean; avisos se comunican.", "Verificar contra lo pedido (formato, duración, estilo).", "Nunca afirmar que algo está bien sin comprobarlo."],
    steps=["`python -m studio qc final.mp4 --duration <esperada>`.", "Extrae frames: `ffmpeg -ss 1 -i final.mp4 -frames:v 1 f1.png` (y a mitad/final) y revísalos.",
           "Checklist artístico: personajes consistentes, sin cortes, subtítulos legibles, audio claro.", "Corrige y repite hasta aprobar."],
    commands="""python -m studio qc projects/<…>/final.mp4
ffmpeg -loglevel error -ss 3 -i projects/<…>/final.mp4 -frames:v 1 frame_3s.png
cat projects/<…>/qc_report.json""",
    example="""QC de un Short: aprobado técnicamente pero subtítulo tapado por la UI de TikTok → subir subtítulos (`big` ya los coloca al 70 %) → re-render → QC final.""",
    tools=[("qc.py (ffprobe/ebur128/blackdetect/freezedetect)", "QC técnico", ENG), ("FFmpeg", "extracción de frames", OK), ("tests/ui_test.mjs", "prueba end-to-end de la interfaz", OK)],
    qc=["qc_report `passed: true`.", "Frames revisados visualmente.", "Requisitos del usuario cumplidos."],
    pitfalls=["freezedetect avisa en escenas estáticas intencionales (logos): es aviso, no error.", "LUFS bajo en videos sin música (normal)."],
    related=["animation-rendering", "animation-optimization", "animation-workflow"]),

"animation-optimization": dict(
    title="Optimización y exportación",
    description="Optimiza para cada plataforma: presets (YouTube, Shorts, TikTok, Instagram, web, WhatsApp), WebM VP9, GIF con paleta, tamaño de archivo, faststart, velocidad de render y peso de assets web (Lottie, SVG). Úsala para 'exportar', 'comprimir', 'que pese menos', 'formato para Instagram/WhatsApp', 'GIF'.",
    intro="`exporter.PRESETS`: youtube (1920×1080 CRF 18), youtube_shorts y tiktok (1080×1920), instagram (1080×1080), web (720p CRF 28), whatsapp (480p CRF 30) con pad negro si la proporción no coincide; además `to_webm`, `gif_preview` (palettegen+paletteuse) y `zip_project`.",
    when=["Antes de publicar.", "Archivos demasiado grandes o incompatibles."],
    principles=["Exportar desde el master de mayor calidad.", "Elegir la proporción nativa de la plataforma (evitar barras).", "faststart para streaming web.",
                "GIF solo para clips cortos (≤ 8 s); preferir MP4/WebM."],
    steps=["Elige preset por destino.", "`python -m studio export final.mp4 --preset <preset>`.", "Comprueba peso/duración con `qc`.", "Para web, también WebM: `--preset webm`."],
    commands="""python -m studio export projects/<…>/final.mp4 --preset tiktok
python -m studio export projects/<…>/final.mp4 --preset whatsapp
python -m studio export projects/<…>/final.mp4 --preset webm
python -m studio export projects/<…>/final.mp4 --preset gif
python -m studio export projects/<…> --preset zip""",
    example="""Mismo video para 4 redes: render 16:9 fullhd para YouTube; render 9:16 aparte (recomposición) para TikTok/Shorts; preset instagram 1:1 para el feed; whatsapp para compartir.""",
    tools=[("exporter.py presets", "codificación por plataforma", ENG), ("FFmpeg (x264, VP9, Opus, palettegen)", "códecs", OK), ("HandBrake", "compresión manual", EXT)],
    qc=["Reproducción correcta en móvil.", "Peso dentro de límites (WhatsApp ≤ 16 MB).", "Audio presente tras exportar."],
    pitfalls=["Convertir 16:9 a 9:16 con pad deja barras enormes: mejor re-renderizar en 9:16.", "Recomprimir un archivo ya comprimido varias veces."],
    related=["animation-rendering", "animation-upscaling", "youtube-animation"]),

"animation-upscaling": dict(
    title="Upscaling e interpolación",
    description="Aumenta resolución y fluidez: upscaling Lanczos + nitidez, Real-ESRGAN (anime/video) si está instalado, interpolación de frames a 60 fps (minterpolate) y restauración de clips IA de baja resolución. Úsala para 'mejorar calidad', 'subir resolución', 'upscale', '4K', '60 fps', 'más fluido'.",
    intro="`exporter.upscale(factor, method)` con `lanczos` (siempre disponible) o `realesrgan` (requiere el binario `realesrgan-ncnn-vulkan` y GPU Vulkan, modelo realesr-animevideov3 ideal para animación); `exporter.interpolate(fps)` usa `minterpolate` con compensación de movimiento (MCI, AOBMC).",
    when=["Clips IA a 480–720p que hay que llevar a 1080p/4K.", "Animaciones a 12–24 fps que se quieren a 60 fps."],
    principles=["Mejor renderizar a la resolución final si el contenido es del estudio (fullhd).", "Upscale IA para contenido externo o generado por IA.",
                "Interpolación no conviene en estilos de 12 fps intencionales (stop-motion, anime on twos).", "Revisar artefactos en bordes y texto."],
    steps=["Contenido propio: re-render en `fullhd`.", "Externo: `python -m studio upscale clip.mp4 --factor 2 --method lanczos` (o `realesrgan`).",
           "Fluidez: `python -m studio interpolate clip.mp4 --fps 60`.", "QC y comparación lado a lado."],
    commands="""python -m studio upscale clip_ia.mp4 --factor 2
python -m studio upscale clip_ia.mp4 --factor 4 --method realesrgan       # si está instalado
python -m studio interpolate projects/<…>/final.mp4 --fps 60""",
    example="""Clip de IA de 720p → `upscale --factor 2` (1440p) → `export --preset youtube` (1080p con más detalle) → `interpolate` opcional.""",
    tools=[("FFmpeg Lanczos + unsharp", "upscale clásico", OK), ("minterpolate", "interpolación", OK), ("Real-ESRGAN ncnn (open source)", "upscale IA", EXT), ("RIFE / FILM", "interpolación IA", EXT)],
    qc=["Sin halos ni sobre-nitidez.", "Interpolación sin 'morphing' en movimientos rápidos.", "Audio intacto."],
    pitfalls=["minterpolate es lento y produce artefactos en cortes de escena.", "Upscale ×4 de material muy comprimido amplifica artefactos."],
    related=["animation-optimization", "ai-video-generation", "animation-rendering"]),
}
