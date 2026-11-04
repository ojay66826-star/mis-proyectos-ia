OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
EXT = "💻 programa externo recomendado"
MCP = "🔌 conector MCP (si está conectado en Claude)"

SKILLS = {
"ai-video-generation": dict(
    title="Generación de video con IA",
    description="Genera video con modelos de IA (texto→video, imagen→video) usando proveedores reales (Replicate: MiniMax, Wan, Kling, Luma…; conector ElevenLabs en Claude) o el motor local cuando no hay clave. Úsala para 'video con IA', 'genera un video realista', 'texto a video', 'Sora/Kling/Runway', 'convierte esta imagen en video con IA'.",
    intro="El estudio ofrece tres caminos: (1) **local y gratis**: motor 2D/3D e `img2video` (Ken Burns, paralaje 2.5D, efectos); (2) **Replicate** (`REPLICATE_API_TOKEN`, modelo en `REPLICATE_VIDEO_MODEL`, por defecto `minimax/video-01`) vía `providers.generate_video_replicate`; (3) si Claude tiene el **conector ElevenLabs** activo, sus herramientas `creative_generate_video`/`creative_generate_image` generan clips en la cuenta del usuario (gastan créditos: confirmar antes de videos largos). Las integraciones cloud siguen la documentación oficial pero solo se consideran verificadas tras `python -m studio doctor --online` en el equipo del usuario.",
    when=["Se pide realismo fotográfico o movimiento que el motor procedural no logra.", "El usuario tiene clave/créditos y acepta el coste."],
    principles=["Prompt estructurado: sujeto + acción + entorno + cámara + luz + estilo + duración.", "Para consistencia, partir de un primer frame (imagen→video) generado o renderizado por el estudio.",
                "Clips cortos (4–6 s) unidos en edición > un clip largo.", "Revisar derechos y políticas de cada proveedor; no usar personas reales sin permiso."],
    steps=["Comprueba proveedores: `python -m studio doctor` (claves) y `--online` (conectividad).",
           "Sin clave → camino local: `python -m studio make …` o `img2video`.",
           "Con Replicate: `python -m studio img2video frame.png --provider replicate --prompt \"…\"`.",
           "Con el conector ElevenLabs en Claude: crear un flow, generar imagen de referencia, luego video desde ella; descargar y pasar por `qc`.",
           "Unir clips con `video-editing` y añadir audio del estudio."],
    commands="""python -m studio doctor --online
python -m studio image "un dragón tierno volando sobre un castillo al atardecer" --provider auto -o ref.png
python -m studio img2video ref.png --provider replicate --prompt "the dragon flaps its wings, slow cinematic push in" -o dragon_ai.mp4
python -m studio img2video ref.png --move parallax --effects sparkles -o dragon_local.mp4   # alternativa gratuita""",
    example="""«Convierte esta imagen en un video realista»: si hay `REPLICATE_API_TOKEN` → imagen→video con prompt de cámara; si no → `img2video --move parallax --style cinematic` y explicar al usuario qué clave haría falta para movimiento generativo.""",
    tools=[("img2video local", "Ken Burns / paralaje 2.5D", ENG), ("Replicate API", "MiniMax, Wan, Kling, Luma, etc.", KEY), ("ElevenLabs (conector)", "imagen/video/voz generativos", MCP),
           ("Wan 2.x / LTX-Video / CogVideoX (open source)", "texto→video local con GPU NVIDIA ≥ 12 GB", EXT), ("ComfyUI", "flujos de video IA locales", EXT)],
    qc=["Sin deformaciones graves (manos, caras).", "Duración/resolución como se pidió.", "Coste comunicado al usuario.", "QC del estudio aprobado tras añadir audio."],
    pitfalls=["Nombres de modelos cambian con frecuencia: el modelo de Replicate es configurable por variable de entorno.", "Prometer resultados de un proveedor sin haberlo ejecutado."],
    related=["video-editing", "animation-upscaling", "realistic-animation", "animation-workflow"]),

"cinematic-video": dict(
    title="Video cinematográfico",
    description="Dirige videos con lenguaje de cine: planos (general, medio, primer plano), movimientos de cámara, ritmo de montaje, grading, música épica y títulos. Úsala para 'video cinematográfico', 'tráiler', 'corto de cine', 'que parezca una película'.",
    intro="Une `cinematic-effects` (look) con dirección: cada escena es un plano con intención; la duración y la cámara siguen la tensión dramática; la música `epic` crece; transiciones `dip` a negro en cambios de acto.",
    when=["Tráileres, presentaciones dramáticas, cortos narrativos."],
    principles=["Planos: establecimiento (general) → acción (medio) → emoción (primer plano/dolly_in).", "Ritmo: planos largos al principio, cortos en el clímax.",
                "Regla de tercios y aire en la dirección de mirada.", "Un clímax visual y sonoro claro."],
    steps=["Escribe un beat sheet de 4–6 planos.", "Plan con `--style cinematic --transition dip`.", "Asigna cámara por plano (pan, dolly_in, shake, zoom_out final).",
           "Render `fullhd` y exporta preset `youtube`."],
    commands="""python -m studio make "Crea una animación cinematográfica de un robot en la ciudad de noche" --style cinematic --transition dip
python -m studio export projects/<…>/final.mp4 --preset youtube""",
    example="""Tráiler: plano general de ciudad (pan, 4 s) → robot camina (dolly_in) → amenaza (lightning + shake) → clímax (explosion) → título final con logo animado.""",
    tools=[("Motor 2D/3D + style cinematic", "look de cine", ENG), ("Blender EEVEE/Cycles", "planos 3D", OK), ("DaVinci Resolve", "montaje/grading profesional", EXT)],
    qc=["Cada plano tiene propósito.", "Audio con dinámica (silencio antes del clímax).", "Letterbox y grading consistentes."],
    pitfalls=["Todos los planos iguales en duración = monótono.", "Música a todo volumen tapando efectos."],
    related=["cinematic-effects", "3d-camera-animation", "video-editing"]),

"short-video-animation": dict(
    title="Animaciones cortas para redes",
    description="Videos animados de 5–60 s optimizados para retención: gancho en el primer segundo, ritmo rápido, subtítulos grandes, bucle y formatos verticales/cuadrados. Úsala para 'video corto', 'clip para redes', 'reel', 'short', 'video viral'.",
    intro="El planificador detecta 'short/reel/vertical' → formato 9:16 y subtítulos grandes amarillos con contorno. Esta Skill añade reglas de retención y exportación multi-plataforma.",
    when=["Contenido para redes sociales en general (ver también youtube/tiktok)."],
    principles=["Gancho visual en 0–1 s (acción, no título lento).", "Cambio visual cada 1.5–3 s.", "Subtítulos siempre (80 % se ve sin sonido).",
                "Final que enlaza con el inicio (loop)."],
    steps=["Plan con `--format 9:16 --duration 15`.", "Desactiva el título inicial si roba el gancho (`show_title: false`).", "Render, luego `loop` si aplica.",
           "Exporta: `--preset tiktok`, `youtube_shorts`, `instagram`."],
    commands="""python -m studio make "Un plátano baila y hace un truco increíble" --format 9:16 --duration 15
python -m studio export projects/<…>/final.mp4 --preset youtube_shorts""",
    spec="""{"format": "9:16", "subtitles": "big", "show_title": false, "transition": "cut"}""",
    example="""Reel de 12 s: gancho con salto (jump) en el segundo 0, baile con confeti, remate con celebrate; corte seco entre escenas; loop.""",
    tools=[("Motor 2D (9:16)", "render vertical", ENG), ("exporter presets", "tiktok/shorts/instagram", ENG), ("CapCut", "ajustes finales manuales", EXT)],
    qc=["Gancho en el primer segundo.", "Texto dentro de zonas seguras (no bajo la UI de la app).", "Duración ≤ 60 s."],
    pitfalls=["Texto en el 15 % inferior queda tapado por la interfaz de TikTok/Reels.", "Intros largas matan la retención."],
    related=["tiktok-animation", "youtube-animation", "seamless-loop-animation"]),

"youtube-animation": dict(
    title="Animación para YouTube (videos y Shorts)",
    description="Produce animaciones para YouTube: horizontales 16:9 1080p, Shorts 9:16, intro/outro con mascota, miniatura llamativa, capítulos y subtítulos SRT. Úsala para 'para YouTube', 'video de YouTube', 'YouTube Shorts', 'intro para mi canal', 'miniatura'.",
    intro="Entregables: `final.mp4` → preset `youtube` (1920×1080, CRF 18, AAC 192k, faststart) o `youtube_shorts` (1080×1920), `miniatura.jpg` (extraída del momento clave; se puede regenerar), `subtitulos.srt` para subir como CC y sonoridad ≈ -14 LUFS verificada por QC.",
    when=["El destino es YouTube."],
    principles=["Miniatura: personaje con emoción fuerte + 3–4 palabras grandes.", "Intro ≤ 5 s; valor en los primeros 15 s.",
                "Subtítulos SRT (mejoran alcance).", "Audio normalizado ≈ -14 LUFS."],
    steps=["Render en `fullhd` 16:9 (o 9:16 para Shorts).", "Exporta preset y sube con el `.srt`.",
           "Miniatura personalizada: `python -m studio image \"<personaje> sorprendido, fondo colorido\" --provider local` y añade texto.",
           "Intro/outro: Skill `mascot-animation` + `animated-logos`."],
    commands="""python -m studio make "Clase educativa: un robot explica en el aula los planetas" --quality fullhd
python -m studio export projects/<…>/final.mp4 --preset youtube
python -m studio make "Un gato hace un truco de magia" --format 9:16 && python -m studio export <final.mp4> --preset youtube_shorts""",
    example="""Episodio de 45 s para canal infantil: historia de 4 escenas en fullhd, SRT, miniatura, intro de mascota de 4 s concatenada (`exporter.concat`).""",
    tools=[("exporter presets youtube/youtube_shorts", "codificación recomendada", ENG), ("qc (ebur128)", "sonoridad", OK), ("YouTube Studio", "publicación", NET)],
    qc=["1080p, 24/30 fps, H.264 + AAC.", "SRT sincronizado.", "Miniatura 1280×720 legible en pequeño."],
    pitfalls=["Subir el MP4 'hd' 720p en vez de exportar 1080p.", "Música con copyright de terceros: usa la del estudio (procedural, libre)."],
    related=["short-video-animation", "mascot-animation", "animation-optimization"]),

"tiktok-animation": dict(
    title="Animación para TikTok / Reels",
    description="Animaciones verticales 9:16 para TikTok, Instagram Reels y Facebook: gancho inmediato, tendencias de baile, subtítulos grandes en zona segura, ritmo con la música y bucle. Úsala para 'para TikTok', 'Reels', 'video vertical', 'trend', 'baile de TikTok'.",
    intro="El planificador cambia a 9:16 con palabras como tiktok/reels/shorts, usa subtítulos grandes centrados en la zona media-baja (y≈70 %), personajes al 42 % del ancho y música con tempo marcado.",
    when=["El destino es TikTok, Reels o Stories."],
    principles=["0.5 s de gancho; nada de logos al inicio.", "Ritmo sincronizado al beat (cortes y saltos en el pulso).", "Zona segura: margen superior 10 %, inferior 20 %, derecho 15 %.",
                "Duración 7–20 s para máxima retención."],
    steps=["`make \"… para TikTok …\"` o `--format 9:16`.", "Revisa el storyboard vertical.", "Exporta `--preset tiktok` (1080×1920).", "Opcional: `loop` para enganchar."],
    commands="""python -m studio make "Crea una animación para TikTok de un plátano que baila"
python -m studio export projects/<…>/final.mp4 --preset tiktok
python -m studio text "¿Sabías esto? Las fresas no son bayas" --format 9:16 --mode pop     # texto viral""",
    example="""Trend de baile: plátano y fresa bailan en escenario (dance + confeti), 12 s, subtítulos amarillos, preset tiktok y GIF para previsualizar.""",
    tools=[("Motor 2D 9:16", "render vertical", ENG), ("kinetic_typography", "textos virales", ENG), ("Preset tiktok", "1080×1920 CRF 20", ENG)],
    qc=["Nada importante en la franja inferior 20 %.", "Primer frame atractivo (es la portada).", "Audio no satura en móvil."],
    pitfalls=["Usar 16:9 con barras negras: penaliza alcance.", "Subtítulos pequeños ilegibles en móvil."],
    related=["short-video-animation", "character-dancing", "kinetic-typography"]),

"animated-storytelling": dict(
    title="Narrativa animada (storytelling)",
    description="Aplica técnicas narrativas a videos animados: estructura en actos, viaje del héroe, ganchos, ritmo, subtexto, payoff y moraleja; adapta la historia al formato y duración. Úsala para 'cuenta una historia', 'narrativa', 'guion con moraleja', 'storytelling para mi marca'.",
    intro="Capa de dirección narrativa por encima de `story-animation` y `animation-scripting`: decide qué contar, en qué orden y con qué emoción, y lo traduce a escenas del proyecto (duración, cámara, música, efectos).",
    when=["Historias con propósito (educativo, marca, emocional).", "Adaptar un texto/cuento a video."],
    principles=["Personaje con deseo + obstáculo + cambio = historia.", "Setup/payoff: lo que se presenta en la escena 1 se paga al final.",
                "Mostrar en vez de narrar; voz en off solo si aporta.", "Duración: 15 s = 3 beats, 60 s = 6–8 beats."],
    steps=["Resume en logline.", "Divide en beats (escenas) con emoción objetivo.", "Asigna recursos visuales (cámara, música, efectos) a cada beat.",
           "Genera con `plan` (o `--ai`), edita y renderiza.", "Valida: ¿se entiende sin sonido? ¿el final paga el inicio?"],
    commands="""python -m studio plan "Una naranja tímida quiere cantar en el escenario pero tiene miedo; sus amigos la animan y triunfa" --ai -o historia.json
python -m studio render historia.json""",
    example="""Storytelling de marca (panadería): mascota estrella busca el pan perfecto (park) → se le quema (fire + smoke) → aprende con un amigo (idea) → celebra con clientes (confetti) → logo final.""",
    tools=[("Planificador + Claude (opcional)", "estructura y diálogos", KEY), ("Motor 2D/3D", "escenificación", ENG)],
    qc=["Logline clara.", "Cada escena avanza la historia.", "Final emocional o con moraleja."],
    pitfalls=["Demasiados personajes para la duración.", "Final abrupto sin cierre."],
    related=["story-animation", "animation-scripting", "animation-storyboarding", "character-emotions"]),

"music-video-animation": dict(
    title="Videoclips animados",
    description="Videoclips animados sincronizados con música: BPM, cortes en el beat, baile, efectos al ritmo, letras animadas y visualización; con música procedural del estudio o una canción del usuario. Úsala para 'videoclip', 'video musical', 'animación para mi canción', 'lyric video'.",
    intro="La música procedural (9 moods con BPM) sincroniza el baile automáticamente. Para una canción del usuario: detecta BPM (`sox`/`librosa` si se instala), fija `mood`/BPM, renderiza sin música (`music: false`) y mezcla la canción con `exporter.add_audio`.",
    when=["Canciones propias, lyric videos, visualizadores."],
    principles=["Cortes y acentos en el beat (múltiplos de 60/BPM s).", "Secciones: intro, estrofa, estribillo (más energía), puente, final.",
                "Letras sincronizadas y legibles.", "Paleta y efectos según el género musical."],
    steps=["Determina BPM y estructura.", "Duración de escenas = n compases × (4 × 60/BPM).", "Render con `music: false` si usarás audio propio.",
           "Une audio: `python -c \"from studio.exporter import add_audio; add_audio('final.mp4','cancion.mp3','clip.mp4')\"`.", "Lyric video: `python -m studio text \"<letra>\" --mode pop` por frase."],
    commands="""python -m studio make "Las frutas bailan en una fiesta en el escenario" --mood dance --duration 30
python -c "from studio.exporter import add_audio; add_audio('projects/<…>/final.mp4', 'mi_cancion.mp3', 'videoclip.mp4')\"""",
    spec="""{"mood": "dance", "music": false, "scenes": [{"duration": 7.74}, {"duration": 7.74}, {"duration": 7.74}]}""",
    example="""Canción a 124 BPM: compás = 1.935 s; escenas de 4 compases (7.74 s); render sin música; añadir la canción; cortes caen en el beat.""",
    tools=[("Música procedural (audio.synth_music)", "pistas libres de derechos", ENG), ("sox", "análisis/edición de audio", OK), ("librosa / aubio", "detección de BPM", EXT)],
    qc=["Cortes alineados al beat (±1 frame).", "Letras sincronizadas.", "Sin clipping al mezclar la canción."],
    pitfalls=["Canciones con copyright sin licencia.", "Escenas que no son múltiplo del compás desincronizan."],
    related=["character-dancing", "kinetic-typography", "animation-sound-design"]),

"video-transitions": dict(
    title="Transiciones de video",
    description="Transiciones entre escenas y clips: fundido, a negro (dip), barrido, deslizamiento, iris circular, corte, y las 40+ transiciones xfade de FFmpeg; con whoosh sincronizado. Úsala para 'transición', 'pasar de una escena a otra', 'fundido', 'efecto de cambio de escena'.",
    intro="En el motor 2D las escenas se solapan 0.45 s y se mezclan con `transition`: `fade`, `dip`, `wipe`, `slide`, `circle` o `cut` (global o por escena). Para clips externos, `exporter.concat(videos, out, transition, dur)` usa `xfade` de FFmpeg (fade, wipeleft, slideup, circleopen, pixelize, radial, …).",
    when=["Cambiar de escena o unir clips."],
    principles=["La transición comunica: corte = continuidad; fundido = paso de tiempo; dip = cambio de acto; barrido/slide = energía.",
                "Duración 0.3–0.8 s.", "Un mismo tipo predominante por video.", "Sonido de transición sutil."],
    steps=["Elige `transition` global (`--transition`) o por escena (`\"transition\": \"circle\"`).", "Para clips: `concat([...], 'out.mp4', 'wipeleft', 0.5)`.", "Revisa que la transición no corte diálogos."],
    commands="""python -m studio make "Un conejo viaja del bosque a la playa" --transition circle
python -c "from studio.exporter import concat; concat(['a.mp4','b.mp4','c.mp4'], 'unido.mp4', 'slideleft', 0.5)\"""",
    example="""Viaje en 3 lugares con `slide` (energía), y `dip` al final antes de 'Fin'.""",
    tools=[("render.transition", "6 transiciones nativas", ENG), ("FFmpeg xfade", "40+ transiciones", OK), ("GSAP/Remotion", "transiciones a medida", OK)],
    qc=["Sin frames negros inesperados.", "El diálogo no se corta en la transición."],
    pitfalls=["xfade requiere mismo tamaño, fps y formato de píxel en todos los clips.", "Mezclar muchos tipos distintos parece amateur."],
    related=["video-editing", "scene-composition", "animation-workflow"]),

"video-editing": dict(
    title="Edición y montaje de video",
    description="Monta, corta, une, recorta, cambia velocidad, añade audio, subtítulos, texto y logos a videos con FFmpeg y las utilidades del estudio. Úsala para 'edita el video', 'une estos videos', 'corta', 'recorta', 'acelera', 'añade música/subtítulos/marca de agua'.",
    intro="Recetas FFmpeg verificadas + funciones `exporter` (concat con xfade, add_audio, export_preset, loop, upscale, interpolate) y `probe` para inspeccionar. Todo se valida al final con `python -m studio qc`.",
    when=["Post-producción de cualquier video del estudio o del usuario."],
    principles=["Editar sobre copias; nunca sobrescribir el original.", "Mantener fps, resolución y formato de píxel homogéneos.",
                "Recodificar lo mínimo (`-c copy` cuando se pueda).", "Comprobar sincronía audio/video tras cada paso."],
    steps=["Inspecciona: `python -c \"from studio.exporter import probe; print(probe('v.mp4'))\"`.", "Aplica la receta necesaria (abajo).", "Ejecuta `qc` sobre el resultado."],
    commands="""ffmpeg -ss 2 -to 8 -i in.mp4 -c copy recorte.mp4                                  # cortar sin recodificar
ffmpeg -i in.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" rapido.mp4       # x2 velocidad
ffmpeg -i in.mp4 -i logo.png -filter_complex "overlay=W-w-24:24" marca.mp4          # marca de agua
ffmpeg -i in.mp4 -vf subtitles=subtitulos.srt subtitulado.mp4                        # quemar SRT
ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih" vertical.mp4                                  # 16:9 → 9:16 (recorte)
python -c "from studio.exporter import concat; concat(['intro.mp4','ep.mp4'], 'final.mp4', 'fade', 0.4)\"""",
    example="""«Une mi intro con el episodio y pon mi logo»: `concat` intro+episodio con fade → overlay del logo PNG → `qc` → export youtube.""",
    tools=[("FFmpeg 6.1", "edición por comandos", OK), ("exporter.py", "utilidades del estudio", ENG), ("Kdenlive / Shotcut / DaVinci Resolve", "edición visual", EXT)],
    qc=["Sin desincronía audio/video.", "Duración final esperada.", "QC aprobado."],
    pitfalls=["`-c copy` con cortes fuera de keyframe puede dar frames congelados al inicio: recodifica si pasa.", "Concat de clips con distinto sample rate de audio."],
    related=["video-transitions", "animation-rendering", "animation-optimization"]),

"seamless-loop-animation": dict(
    title="Animaciones en bucle perfecto",
    description="Crea loops perfectos sin salto visible: periodos que dividen la duración, partículas cíclicas, fondos periódicos y crossfade final; para GIFs, fondos de stream y redes. Úsala para 'bucle', 'loop infinito', 'GIF en bucle', 'fondo que se repite'.",
    intro="Tres técnicas: (1) **matemática**: todo movimiento con periodo que divide la duración (fondos de `motiongraphics.animated_background` son periódicos por diseño); (2) **ciclos** de acción (walk 0.625 s, dance según BPM, jump 1.2 s); (3) **crossfade** final con `exporter.make_loop` (xfade del final con el inicio).",
    when=["GIFs, fondos animados, stickers, pantallas de espera, clips de redes en loop."],
    principles=["Duración = múltiplo común de los periodos usados.", "Cámara estática o periódica.", "Sin elementos que aparecen una sola vez.", "Verificar el punto de unión frame a frame."],
    steps=["Para fondos: `python -m studio background blobs --duration 6`.", "Para personajes: acción cíclica, `from == to`, duración múltiplo del ciclo.",
           "Para cualquier video: `python -m studio loop video.mp4 --crossfade 0.5`.", "Exporta GIF: `python -m studio export loop.mp4 --preset gif`."],
    commands="""python -m studio background particles --duration 8 --palette neon -o fondo_loop.mp4
python -m studio loop projects/<…>/final.mp4 --crossfade 0.6
python -m studio export fondo_loop.mp4 --preset gif""",
    example="""Sticker de fruta saltando en bucle: `lottie` (ya es cíclico) o `character3d manzana --action jump --duration 2.4` (2 saltos exactos).""",
    tools=[("animated_background", "fondos periódicos", ENG), ("exporter.make_loop", "crossfade de cierre", ENG), ("FFmpeg palettegen", "GIF", OK)],
    qc=["El último frame enlaza con el primero.", "Sin parpadeo en la unión.", "Tamaño de GIF razonable."],
    pitfalls=["Música en loop corta: quítala o usa audio en bucle.", "Partículas con vidas aleatorias que no cierran: usa la versión determinista del estudio."],
    related=["animated-backgrounds", "lottie-animation", "animation-optimization"]),
}
