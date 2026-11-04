OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
OPT = "⬇️ opcional (instalar aparte)"
EXT = "💻 programa externo recomendado"

SKILLS = {
"2d-animation": dict(
    title="Animación 2D",
    description="Crea animaciones 2D completas (personajes, escenarios, cámara, efectos, voces y música) con el motor procedural del estudio. Úsala para 'haz una animación', 'crea un dibujo animado', 'animación 2D', 'cartoon', o cualquier video animado plano sin requisito de 3D.",
    intro="Skill base de la animación 2D del estudio. Convierte una idea en un video MP4 terminado usando el motor propio `studio` (Pillow + numpy + FFmpeg): personajes vectoriales procedurales con rig de extremidades, escenarios con paralaje, cámara virtual, partículas, lip-sync y mezcla de audio. Todo funciona sin conexión ni claves.",
    when=["El usuario pide una animación, caricatura o video animado sin especificar 3D.",
          "Se necesita un resultado rápido, consistente y 100 % gratuito.",
          "Como base sobre la que otras Skills (estilos, efectos, personajes) añaden capas."],
    principles=["Aplica los 12 principios de Disney: squash & stretch, anticipación, puesta en escena, arcos, acción secundaria, timing, exageración, sólido, atractivo.",
                "Composición legible: personaje principal en tercios, siluetas claras, fondo con menos contraste que los personajes.",
                "Timing a 24 fps (12 fps para estilos stop-motion/papel); las acciones clave duran 0.3–1.2 s.",
                "Cada escena debe tener una intención (presentar, conflicto, resolución) y durar 3–6 s.",
                "Movimiento de cámara sutil (pan/zoom ≤15 %) para dar vida sin marear."],
    steps=["Entiende la petición: personajes, acción, emoción, escenario, formato (16:9 / 9:16 / 1:1) y duración.",
           "Genera el plan: `python -m studio plan \"<idea>\" -o proyecto.json` y revísalo (escenas, diálogos, acciones).",
           "Ajusta el JSON si hace falta (acciones `walk/run/jump/dance/talk/wave/punch/kick/celebrate/float/spin/think`, emociones, cámara, efectos).",
           "Haz un borrador rápido: `python -m studio render proyecto.json --quality preview` y abre `storyboard.jpg`.",
           "Corrige timing/composición y renderiza final en `--quality hd` o `fullhd`.",
           "Ejecuta `python -m studio qc projects/<…>/final.mp4` y entrega rutas de video, GIF, miniatura y SRT."],
    commands="""# De una frase a video terminado
python -m studio make "Una manzana y un plátano juegan en el parque" --style cartoon

# Flujo con revisión del guion
python -m studio plan "Una manzana y un plátano juegan en el parque" -o proyecto.json
python -m studio render proyecto.json --quality preview   # borrador
python -m studio render proyecto.json --quality hd        # final 720p""",
    spec="""{
  "style": "cartoon", "format": "16:9", "mood": "happy",
  "scenes": [{
    "background": "park", "time_of_day": "day", "duration": 4,
    "camera": {"type": "pan"},
    "actors": [{"character": "manzana", "action": "walk", "emotion": "happy", "from": [0.1, 0.82], "to": [0.45, 0.82]}],
    "dialogue": [{"character": "manzana", "text": "¡Hola, amigos!"}],
    "effects": [{"type": "sparkles", "y": 0.5}]
  }]
}""",
    example="""**Petición:** «Crea una animación de un gato que camina por la ciudad de noche».

1. `python -m studio make "Un gato camina por la ciudad de noche" --quality preview` → revisar `storyboard.jpg`.
2. Si el gato debe ir de derecha a izquierda, editar `from/to` en `project.json` (`[0.9,0.82]→[0.1,0.82]`).
3. `python -m studio render projects/<…>/project.json --quality hd` → `final.mp4` con pasos sincronizados, música y QC.""",
    tools=[("Motor 2D `studio`", "personajes, fondos, cámara, partículas", ENG), ("FFmpeg 6.1", "codificación H.264/AAC", OK),
           ("espeak-ng", "voces locales en español", OK), ("Krita / OpenToonz", "dibujo frame a frame manual", EXT),
           ("ElevenLabs / OpenAI TTS", "voces realistas", KEY)],
    qc=["El storyboard muestra cada escena con intención clara.", "Los personajes no salen del cuadro ni flotan sobre el suelo.",
        "No hay saltos bruscos entre escenas (transición de 0.45 s).", "Audio presente, voces entendibles, música por debajo (ducking).",
        "`qc_report.json` aprobado."],
    pitfalls=["Demasiados personajes en 16:9 (más de 4) → se reducen; repartir en escenas.",
              "Diálogos largos alargan escenas: máximo ~12 palabras por línea.",
              "Usar `walk` sin `from/to` distintos deja al personaje caminando en el sitio (moonwalk): define desplazamiento."],
    related=["animation-workflow", "character-animation", "scene-composition", "animation-rendering", "cartoon-animation"]),

"cartoon-animation": dict(
    title="Animación de caricaturas (cartoon)",
    description="Produce caricaturas animadas clásicas: contornos gruesos, colores saturados, brazos de 'manguera' con guantes blancos, squash & stretch exagerado y gags. Úsala para 'caricatura', 'dibujo animado', 'cartoon', 'estilo Cartoon Network/rubber hose'.",
    intro="Estilo cartoon del estudio (`style: cartoon`): silueta con contorno oscuro automático, sombreado cel de una sola banda, brillo especular, extremidades tipo rubber-hose con guantes y zapatos, y física exagerada en saltos y celebraciones.",
    when=["El usuario pide 'caricatura', 'cartoon', 'dibujo animado' o un tono humorístico infantil.",
          "Contenido para niños, mascotas de marca, sketches cómicos."],
    principles=["Exageración: anticipación marcada antes de cada salto (squash 25 %), stretch en el aire.",
                "Poses claras y legibles en silueta; una idea por pose.",
                "Timing cómico: pausa (hold) de 0.3 s antes del remate del gag.",
                "Paleta saturada con fondo más claro y menos contrastado que los personajes.",
                "Sonido cartoon: boing en celebraciones, pops y whoosh en transiciones (automático)."],
    steps=["Define el gag o la historia en 3 golpes: presentación → problema → remate.",
           "Elige personajes con siluetas distintas (p. ej. manzana redonda + plátano alargado).",
           "Planifica con `--style cartoon` y revisa que cada escena tenga una acción exagerada (jump, celebrate, scared_shake).",
           "Añade efectos de apoyo: `confetti`, `sparkles`, `speedlines` para gags rápidos.",
           "Renderiza y revisa el timing en `vista_previa.gif`; ajusta duraciones de escena."],
    commands="""python -m studio make "Una fresa intenta saltar un charco y cae, luego celebra" --style cartoon
python -m studio character fresa --style cartoon --name Fresita     # hoja de personaje
python -m studio export projects/<…>/final.mp4 --preset youtube""",
    example="""**Petición:** «Haz una caricatura de un perro y un gato que se asustan con un rayo».
`python -m studio make "Un perro y un gato en el parque se asustan con un rayo" --style cartoon` → el planificador crea
presentación (wave), problema (scared_shake + lightning + truenos) y resolución (celebrate + confetti).""",
    tools=[("Motor 2D `studio` (style cartoon)", "render completo", ENG), ("Blender Grease Pencil", "cartoon dibujado a mano 2D/3D", OK),
           ("OpenToonz", "producción cartoon tradicional", EXT), ("Freesound.org", "efectos cartoon reales (CC)", NET)],
    qc=["Contornos continuos sin huecos.", "Cada salto tiene anticipación y aterrizaje con squash.", "El gag se entiende sin audio."],
    pitfalls=["Gags sin pausa previa pierden gracia: deja 0.3–0.5 s de hold.", "Demasiados efectos a la vez tapan la acción."],
    related=["2d-animation", "character-expressions", "cute-animation", "animation-sound-design"]),

"anime-animation": dict(
    title="Animación estilo anime",
    description="Crea animaciones con estética anime/manga: ojos grandes brillantes con doble reflejo, cel-shading, bloom suave, líneas de velocidad, animación 'on twos' y planos dramáticos. Úsala para 'estilo anime', 'manga', 'chibi', 'estilo japonés'.",
    intro="El estilo `anime` cambia los ojos de todos los personajes al tipo anime (iris degradado + dos brillos), usa contorno fino, cel-shading, saturación +15 % y bloom en altas luces. Combínalo con `speedlines`, `energy` y cámara `zoom_in`/`dolly_in` para momentos dramáticos.",
    when=["Peticiones 'anime', 'manga', 'chibi', 'opening de anime', 'escena de transformación'.",
          "Historias de magia, peleas o drama juvenil."],
    principles=["Limited animation: poses fuertes y holds; movimiento en capas (pelo, efectos) sobre poses estáticas.",
                "Planos de impacto: zoom rápido + speedlines + flash blanco de 1–2 frames.",
                "Paleta: cielos saturados, sombras con tinte frío, highlights cálidos.",
                "Expresiones icónicas: sudor (scared/confused), venas de enfado (angry), brillo en ojos (excited)."],
    steps=["Define el momento clave (transformación, golpe, confesión) y construye 2 escenas previas que lo preparen.",
           "Planifica con `--style anime`; para niñas/niños usa `nina`/`nino`, para magia `mago` o efecto `magic`.",
           "Añade `speedlines` en acciones rápidas y `energy` con `on: <id>` para auras.",
           "Usa cámara `dolly_in` en el plano clave y `shake` en impactos.",
           "Renderiza; revisa que los ojos anime se vean en el storyboard."],
    commands="""python -m studio make "Haz una animación estilo anime de una niña con magia en un castillo" --style anime
python -m studio character nina --eyes anime --style anime --name Sakura""",
    spec="""{"style": "anime", "scenes": [{"background": "castle", "camera": {"type": "dolly_in"},
  "actors": [{"character": "sakura", "action": "wave", "emotion": "excited", "transform_to": "estrella", "transform_at": 2.0}],
  "effects": [{"type": "magic", "on": "sakura"}, {"type": "speedlines", "intensity": 0.6}]}]}""",
    example="""«Haz un opening de anime con un robot y un zorro peleando» → `python -m studio make "Un robot y un zorro pelean en el dojo" --style anime --format 16:9`.
Resultado: escena de tensión (idle angry), pelea con speedlines + aura de energía, explosión final y música `action`.""",
    tools=[("Motor 2D (style anime)", "ojos anime, cel-shading, bloom", ENG), ("Stable Diffusion + LoRA anime (vía HF/Replicate)", "fondos ilustrados", KEY),
           ("Krita + OpenToonz", "anime dibujado a mano", EXT)],
    qc=["Ojos con iris y dos brillos visibles.", "Speedlines no tapan la cara.", "Momento clave con zoom o flash."],
    pitfalls=["Abusar de speedlines en todas las escenas resta impacto.", "Fondos demasiado detallados compiten con los personajes."],
    related=["character-design", "magic-effects", "energy-effects", "character-fighting"]),

"character-animation": dict(
    title="Animación de personajes",
    description="Anima personajes con acciones creíbles (caminar, correr, saltar, saludar, hablar, bailar, pelear, celebrar) y transiciones entre acciones y emociones en una misma escena. Úsala cuando la petición se centre en lo que HACE un personaje: 'haz que camine/baile/hable/salte'.",
    intro="El rig 2D del estudio tiene cuerpo con squash & stretch, brazos y piernas de dos segmentos (hombro/codo, cadera/rodilla), cara con ojos, cejas, párpados y boca con visemas. `motion.py` genera las poses procedurales y el render admite cambios de acción y emoción en el tiempo (`actions`, `emotions`).",
    when=["'Haz que el personaje camine / baile / hable / salte / salude / pelee'.",
          "Secuencias donde un personaje encadena acciones (camina → se detiene → saluda)."],
    principles=["Ciclos de caminar a ~1.6 Hz (paso cada 0.31 s) con bote vertical y brazos opuestos.",
                "Peso: el cuerpo baja en el contacto y sube en el paso (body_dy).",
                "Encadenar acciones con 0.2–0.3 s de transición; nunca cambiar de pose sin anticipación.",
                "La emoción guía la acción: triste = hombros caídos y ritmo lento; feliz = saltos y brazos arriba."],
    steps=["Lista las acciones en orden con su tiempo aproximado.",
           "En `project.json`, dentro del actor usa `actions: [{t:0, action:'walk'}, {t:2.5, action:'wave'}]`.",
           "Define desplazamiento con `from`/`to` y `move_start`/`move_end` para que solo se mueva mientras camina.",
           "Añade cambios de emoción con `emotions: [{t:0,'emotion':'happy'},{t:3,'emotion':'surprised'}]`.",
           "Revisa la hoja de personaje (`characters/<id>_sheet.png`) para ver todas las poses disponibles."],
    commands="""python -m studio character gato --name Michi          # ver todas las poses y expresiones
python -m studio make "Un gato camina y luego saluda feliz" --quality preview""",
    spec="""{"character": "michi", "from": [0.1, 0.82], "to": [0.55, 0.82], "move_start": 0, "move_end": 2.4,
 "actions": [{"t": 0, "action": "walk"}, {"t": 2.4, "action": "wave"}, {"t": 4.0, "action": "celebrate"}],
 "emotions": [{"t": 0, "emotion": "happy"}, {"t": 4.0, "emotion": "joy"}]}""",
    example="""«Haz que el plátano camine, se asuste y huya»: actor con acciones walk (0–2 s) → scared_shake (2–3 s) → run (3–5 s)
con `to` fuera de cuadro (x=1.15) y emoción scared desde t=2.""",
    tools=[("Motor 2D (motion.py)", "ciclos procedurales", ENG), ("Blender (scene3d.py)", "las mismas acciones en 3D", OK),
           ("Spine / DragonBones", "rig 2D por huesos para juegos", EXT), ("Mixamo", "animaciones 3D humanoides", NET)],
    qc=["Pies apoyados en el suelo en el contacto (sin patinar).", "Cambio de acción sin saltos visibles.", "La emoción se lee en la cara."],
    pitfalls=["Velocidad de desplazamiento incoherente con el ciclo → patinaje: para caminar ≈0.3 del ancho por 2.5 s.",
              "Olvidar `facing`: se calcula solo para walk/run; para otras acciones fíjalo (1 derecha, -1 izquierda)."],
    related=["character-movement", "character-emotions", "character-lip-sync", "character-dancing", "character-fighting"]),

"frame-by-frame-animation": dict(
    title="Animación frame a frame",
    description="Animación tradicional dibujo por dibujo: poses clave, intercalados, hojas de exposición y exportación de secuencias PNG. Úsala para 'frame a frame', 'animación tradicional', 'dibujado a mano', 'flipbook', o cuando haya que intervenir frames individuales.",
    intro="El estudio puede trabajar frame a frame de dos formas: (1) exportando cada frame del motor a PNG para retocarlo en Krita/Photoshop y re-ensamblarlo con FFmpeg, y (2) componiendo secuencias PNG propias (dibujos del usuario) en un video con timing controlado (on ones/twos).",
    when=["El usuario aporta dibujos propios o quiere retocar frames.", "Se pide estética 'hecha a mano', boiling lines o flipbook."],
    principles=["Primero keys (poses extremas), luego breakdowns, luego intercalados.",
                "Animar 'on twos' (12 dibujos/s) da el look tradicional; 'on ones' para acciones rápidas.",
                "Hoja de exposición: lista de qué dibujo va en cada frame y cuánto dura.",
                "Line boil (ligero temblor) da vida a holds largos."],
    steps=["Extrae frames: `ffmpeg -i final.mp4 frames/%04d.png`.",
           "Retoca/dibuja en Krita (Animación → Importar secuencia) u OpenToonz.",
           "Re-ensambla a 12 fps duplicando frames para 24 fps: `ffmpeg -framerate 12 -i frames/%04d.png -r 24 -pix_fmt yuv420p out.mp4`.",
           "Añade el audio original: `python -m studio export … ` o `ffmpeg -i out.mp4 -i audio/mezcla.wav -c:v copy -c:a aac final.mp4`.",
           "Para line boil en el motor, usa `style: paper` o `stopmotion` (temblor por frame)."],
    commands="""ffmpeg -i projects/<…>/final.mp4 -vf fps=12 frames/%04d.png          # exportar a 12 fps
ffmpeg -framerate 12 -i frames/%04d.png -r 24 -c:v libx264 -pix_fmt yuv420p dibujado.mp4
python -m studio loop dibujado.mp4                                          # flipbook en bucle""",
    example="""«Tengo 8 dibujos de un pájaro volando, anímalos»: renombrar `pajaro_0001.png…0008.png`,
`ffmpeg -framerate 8 -stream_loop 3 -i pajaro_%04d.png -c:v libx264 -pix_fmt yuv420p vuelo.mp4`, y `python -m studio qc vuelo.mp4 --no-audio`.""",
    tools=[("FFmpeg", "ensamblar secuencias PNG", OK), ("Krita (gratis)", "dibujo frame a frame con papel cebolla", EXT),
           ("OpenToonz (gratis)", "hojas de exposición profesionales", EXT), ("Blender Grease Pencil", "dibujo 2D en Blender", OK)],
    qc=["Numeración continua de frames sin huecos.", "Mismo tamaño en todos los frames (dimensiones pares).", "Timing coherente (on twos estable)."],
    pitfalls=["Frames de distinto tamaño rompen FFmpeg: normaliza con `-vf scale=1280:720`.", "Mezclar ones y twos sin intención produce tirones."],
    related=["2d-animation", "sprite-animation", "stop-motion", "animation-workflow"]),

"cutout-animation": dict(
    title="Animación cutout (recortes / marionetas)",
    description="Animación por piezas articuladas (marioneta digital): cabeza, torso, brazos y piernas como piezas que rotan sobre pivotes. Úsala para 'cutout', 'recortes', 'marioneta', 'estilo South Park', 'rig 2D por piezas'.",
    intro="Los personajes del estudio ya son marionetas cutout: cada extremidad es una pieza con pivote (hombro, codo, cadera, rodilla) y el cuerpo es una pieza con squash. Con `style: paper` se obtiene el look de papel recortado con textura y animación a 12 fps.",
    when=["Estilo de papel recortado, marionetas, collage.", "Producción rápida de muchos episodios con el mismo rig."],
    principles=["Pivotes bien colocados (hombros dentro del cuerpo) evitan huecos al rotar.",
                "Pocas piezas y bien diseñadas > muchas piezas.",
                "Movimiento a 12 fps con ligeros saltos refuerza el estilo.",
                "Sombra proyectada corta para separar capas."],
    steps=["Elige `style: paper` (o `cartoon` para cutout limpio).",
           "Planifica escenas cortas con acciones claras (talk, wave, walk).",
           "Si el usuario trae piezas propias (PNG), crea un rig en Blender (planos con pivotes) o en OpenToonz/Moho.",
           "Renderiza y comprueba que no haya huecos en articulaciones."],
    commands="""python -m studio make "Dos amigos conversan en el parque" --style paper
python -m studio character persona --style paper""",
    example="""«Haz un episodio corto estilo recortes de papel»: `python -m studio make "Un niño y su perro buscan un tesoro en la playa" --style paper --duration 20`.""",
    tools=[("Motor 2D (style paper)", "cutout con textura de papel", ENG), ("Moho / Cartoon Animator", "cutout profesional", EXT),
           ("Blender (planos + huesos)", "cutout con piezas propias", OK)],
    qc=["Sin huecos en las articulaciones.", "Textura de papel visible pero sutil.", "Ritmo a 12 fps intencional."],
    pitfalls=["Rotaciones extremas (>150°) delatan la pieza: limita ángulos.", "Sombras largas ensucian el plano."],
    related=["paper-animation", "2d-animation", "character-animation"]),

"motion-comics": dict(
    title="Motion comics (cómic animado)",
    description="Convierte historias en cómic animado: viñetas, tramas de semitono, globos/rótulos, paneos sobre ilustraciones y animación limitada. Úsala para 'motion comic', 'cómic animado', 'historieta animada', 'manga animado'.",
    intro="El estilo `comic` aplica trama de puntos (halftone) dependiente de la luminancia, contornos marcados y 12 fps. Se combina con rótulos (`caption`), subtítulos y movimientos de cámara (pan/zoom) para recorrer la 'viñeta'. Para ilustraciones propias usa `img2video` con `--move pan_*`.",
    when=["Narrativas con texto, cómics existentes o ilustraciones fijas que hay que animar.", "Trailers estilo novela gráfica."],
    principles=["Cada viñeta = un plano; la cámara guía la lectura (izquierda→derecha, arriba→abajo).",
                "Animación limitada: solo se mueve lo esencial (ojos, boca, partículas).",
                "Rótulos breves con tipografía bold y contorno.",
                "Ritmo: 2.5–4 s por viñeta."],
    steps=["Divide la historia en viñetas (escenas) con un `caption` cada una.",
           "Renderiza con `--style comic`.",
           "Para páginas de cómic reales: corta cada viñeta como imagen y usa `python -m studio img2video viñeta.png --move pan_right --style none`.",
           "Une los clips con `exporter.concat` (xfade) o la Skill `video-editing`."],
    commands="""python -m studio make "Un superhéroe robot salva la ciudad" --style comic
python -m studio img2video vineta1.png --move pan_right --style none --duration 4 -o v1.mp4""",
    example="""«Anima mi cómic de 4 viñetas»: un `img2video` por viñeta (pan/zoom alternados) + `concat` con transición `fade` + música `epic`.""",
    tools=[("Motor 2D (style comic)", "halftone + contornos", ENG), ("img2video", "paneos sobre viñetas", ENG), ("Remotion", "rótulos/globos programáticos", OK)],
    qc=["La trama no oculta las caras.", "Rótulos legibles en móvil.", "Orden de lectura correcto."],
    pitfalls=["Trama demasiado densa en 9:16 pequeño.", "Paneos rápidos impiden leer."],
    related=["animated-storytelling", "typography-animation", "video-editing"]),

"pixel-art-animation": dict(
    title="Animación pixel art",
    description="Animaciones retro en pixel art: baja resolución, paleta limitada, escalado sin suavizado (nearest neighbor), 8–12 fps y ciclos cortos. Úsala para 'pixel art', '8 bits', '16 bits', 'estilo videojuego retro'.",
    intro="El estilo `pixel` renderiza la escena normal, la reduce a ~240 px de ancho, cuantiza a 40 colores (median cut) y la reescala con vecino más cercano: píxeles nítidos y paleta coherente. Ideal para intros de juegos, streams y redes.",
    when=["'Pixel art', '8-bit', 'retro gaming', 'sprite', 'arcade'.", "Contenido gamer o nostálgico."],
    principles=["Resolución base baja y fija; nunca escalar por factores no enteros en el resultado final.",
                "Paleta limitada (16–40 colores) con rampas de sombreado.",
                "Animación a 8–12 fps con ciclos de 4–8 frames.",
                "Evitar antialiasing y degradados suaves."],
    steps=["Planifica con `--style pixel` (fps 12 automático).",
           "Prefiere escenarios simples (park, space, desert) y personajes con siluetas fuertes.",
           "Exporta GIF para redes: `python -m studio export final.mp4 --preset gif`.",
           "Para sprites de juego, ver Skill `sprite-animation`."],
    commands="""python -m studio make "Un robot salta en el espacio" --style pixel
python -m studio export projects/<…>/final.mp4 --preset gif""",
    example="""«Intro pixel para mi canal de juegos»: `python -m studio make "Un zorro corre por el bosque y salta" --style pixel --format 16:9 --mood action`, luego logo con `python -m studio logo "MiCanal"`.""",
    tools=[("Motor 2D (style pixel)", "pixelado + paleta", ENG), ("Aseprite / LibreSprite", "pixel art manual", EXT), ("FFmpeg palettegen", "GIF de alta calidad", OK)],
    qc=["Píxeles cuadrados y nítidos (sin blur).", "Paleta consistente entre escenas.", "GIF < 8 MB para redes."],
    pitfalls=["Re-escalar el MP4 con bicúbico arruina los píxeles: usa `flags=neighbor`.", "Texto pequeño ilegible tras pixelar."],
    related=["sprite-animation", "minimalist-animation", "animation-optimization"]),

"sprite-animation": dict(
    title="Animación de sprites (hojas de sprites para juegos)",
    description="Genera sprites y spritesheets animados (idle, walk, run, jump, attack) para videojuegos web o motores (Godot, Unity, Phaser), con fondo transparente y metadatos de frames. Úsala para 'sprite', 'spritesheet', 'personaje para mi juego', 'animación de juego 2D'.",
    intro="El renderizador de personajes devuelve imágenes RGBA con ancla en los pies, perfectas para sprites. Esta Skill crea spritesheets (rejilla de frames) por acción con transparencia y un JSON de metadatos compatible con Phaser/Godot.",
    when=["El usuario quiere usar el personaje en un juego.", "Necesita GIF/PNG transparentes por acción."],
    principles=["Todos los frames con el mismo tamaño y el mismo punto de ancla (pies).",
                "Ciclos de 8–12 frames que cierran en bucle perfecto.",
                "Fondo transparente y márgenes mínimos.",
                "Nombres consistentes: <personaje>_<acción>.png + .json."],
    steps=["Elige personaje y acciones (idle, walk, run, jump, punch, celebrate).",
           "Ejecuta el script de abajo para generar la hoja por acción.",
           "Importa en el motor: Phaser `this.load.spritesheet(key, png, {frameWidth, frameHeight})`; Godot `AnimatedSprite2D` + SpriteFrames.",
           "Para pixel art, reescala con `Image.NEAREST`."],
    commands="""python - <<'PY'
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
PY""",
    example="""«Hazme el personaje de mi juego de plataformas»: generar idle/walk/run/jump del `zorro`, entregar PNG + JSON, y un GIF de muestra por acción con `ffmpeg -i foxy_walk.png …` o directamente en el visor del motor.""",
    tools=[("Motor de personajes (render_character)", "frames RGBA", ENG), ("Aseprite", "edición de sprites", EXT), ("TexturePacker / free-tex-packer", "atlas optimizados", EXT),
           ("Godot / Phaser", "motores de juego destino", EXT)],
    qc=["Ancla estable (los pies no saltan entre frames).", "El último frame enlaza con el primero.", "Transparencia correcta (sin halo)."],
    pitfalls=["Recortar cada frame a su caja individual cambia el ancla: usa tamaño común.", "Premultiplicar alfa en el motor si se ven bordes oscuros."],
    related=["pixel-art-animation", "character-animation", "interactive-animation"]),

"story-animation": dict(
    title="Animación de historias",
    description="Construye historias animadas completas con estructura narrativa (inicio, conflicto, clímax, resolución), varios personajes, diálogos y música. Úsala para 'haz una historia', 'cuento animado', 'episodio', 'fábula', 'historia con frutas/animales'.",
    intro="Combina `animation-scripting` (guion) con el motor 2D. El planificador detecta 'historia/cuento' y crea 4 escenas: presentación (walk + saludo), problema (efecto climático o peligro, miedo), solución (idea + celebración con confeti) y despedida al atardecer con 'Fin'.",
    when=["'Historia', 'cuento', 'episodio', 'fábula', 'aventura'.", "Contenido educativo o infantil con moraleja."],
    principles=["Estructura en 3 actos aunque dure 20 s.", "Un deseo claro del protagonista y un obstáculo visible.",
                "El clímax tiene la mayor energía visual (efectos, cámara, música).", "Cierre emocional (atardecer, despedida, 'Fin')."],
    steps=["Escribe la premisa en una frase: «<personaje> quiere <deseo> pero <obstáculo>».",
           "Genera el plan (`--ai` si hay ANTHROPIC_API_KEY para diálogos más creativos).",
           "Edita diálogos en la interfaz (pestaña Crear → Ver guion) o en el JSON.",
           "Renderiza en borrador, ajusta duraciones, render final."],
    commands="""python -m studio make "Haz una historia con frutas animadas en la cocina"
python -m studio plan "Una fábula de un conejo y un zorro que aprenden a compartir" --ai -o fabula.json   # con Claude
python -m studio render fabula.json""",
    example="""«Historia con frutas animadas»: reparto Manzana, Plátano, Fresa y Naranja en la cocina; escena 2 con lluvia y miedo, escena 3 con
idea y celebración, escena 4 despedida. Video ~15 s con voces distintas por personaje y SRT.""",
    tools=[("Planificador local", "estructura y diálogos por plantillas", ENG), ("Claude API (opcional)", "guiones creativos estructurados", KEY),
           ("Motor 2D/3D", "render", ENG)],
    qc=["Se entiende la historia sin sonido (acciones claras).", "Cada personaje tiene al menos una línea o acción propia.", "Final claro."],
    pitfalls=["Historias de más de 6 escenas sin subtramas se vuelven monótonas.", "Diálogos que explican lo que ya se ve."],
    related=["animated-storytelling", "animation-scripting", "character-dialogue", "animation-storyboarding"]),
}
