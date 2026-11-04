OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
EXT = "💻 programa externo recomendado"

SKILLS = {
"motion-graphics": dict(
    title="Motion graphics",
    description="Diseño gráfico en movimiento: títulos, lower thirds, formas, transiciones gráficas, fondos, infografías y logos con easing profesional, en Python (Pillow+FFmpeg), GSAP, CSS o Remotion. Úsala para 'motion graphics', 'gráficos animados', 'grafismo', 'títulos animados', 'animación de marca'.",
    intro="Cuatro motores disponibles: `motiongraphics.py` (Python, rápido, sin navegador), plantillas web GSAP/CSS/SVG capturadas a MP4 (`scripts/capture.mjs`), Remotion (React) y el motor 2D para personajes. Las curvas de easing del estudio: linear, in_out, out_back, elastic, bounce.",
    when=["Grafismo para videos, presentaciones, redes, marcas."],
    principles=["Easing siempre (nunca lineal salvo loops).", "Staggering (escalonar) para jerarquía.", "Grid y alineación estrictos.", "Ritmo con la música."],
    steps=["Elige motor: Python (texto/logo/infografía/fondo), web (GSAP para precisión de diseño), Remotion (composiciones React con datos).",
           "Define paleta y tipografía (DejaVu incluida; o web fonts en plantillas).", "Genera y revisa frames clave.", "Exporta al formato del destino."],
    commands="""python -m studio text "Nuevo episodio cada viernes" --mode slide --format 16:9
python -m studio logo "Estudio IA" --tagline "Animación con IA" --color "#6d28d9"
python -m studio web gsap-logo --query "text=Mi Marca&color=%23ff006e" --duration 4
python -m studio remotion "Un zorro presenta las noticias de la semana\"""",
    example="""Paquete de grafismo para canal: logo animado (GSAP), lower third con kinetic-type, fondo en bucle (`background blobs`), todo en la paleta de la marca.""",
    tools=[("motiongraphics.py", "texto/logo/infografía/fondos", ENG), ("GSAP 3.15", "timelines web", OK), ("Remotion 4.0.290", "video con React", OK), ("After Effects / Cavalry", "motion profesional", EXT)],
    qc=["Easing suave sin saltos.", "Textos dentro de márgenes seguros.", "Paleta coherente."],
    pitfalls=["Demasiadas animaciones simultáneas.", "Fuentes no instaladas en la captura web: usar las del sistema o incluirlas."],
    related=["animated-logos", "kinetic-typography", "gsap-animation", "infographic-animation"]),

"animated-logos": dict(
    title="Logos animados",
    description="Anima logotipos: trazo del contorno, monograma con rebote elástico, letras escalonadas, eslogan, destello de brillo y sonido de marca; versiones Python, GSAP y Lottie. Úsala para 'logo animado', 'animar mi logo', 'intro de marca', 'logo reveal'.",
    intro="`python -m studio logo` genera: anillo que se dibuja (0–0.9 s), disco con monograma y rebote elástico, nombre letra a letra con `out_back`, eslogan con fundido y barrido de brillo, + whoosh/ding/sparkle. La plantilla `gsap-logo.html` hace lo mismo en web (SVG + GSAP) y acepta `text`, `tag`, `color`.",
    when=["Intros de marca, firmas al final de videos, presentaciones."],
    principles=["Duración 2.5–5 s.", "El logo final queda estático ≥ 1 s.", "Movimiento que refleje la personalidad de la marca.", "Sonido corto y reconocible."],
    steps=["Reúne nombre, eslogan y color HEX.", "Versión rápida: `python -m studio logo …`.", "Versión web/vectorial: `python -m studio web gsap-logo --query …`.",
           "Si hay un logo SVG propio, sustituir el SVG de la plantilla gsap-logo y animar sus paths con stroke-dashoffset."],
    commands="""python -m studio logo "Panadería Sol" --tagline "Pan con amor desde 1990" --color "#f59e0b"
python -m studio web gsap-logo --query "text=Panadería Sol&tag=Pan con amor&color=%23f59e0b" -o logo_web.mp4""",
    example="""Logo para cierre de YouTube en 16:9 y 9:16; concatenado al final de cada episodio con `concat(..., 'fade', 0.4)`.""",
    tools=[("motiongraphics.animated_logo", "logo reveal", ENG), ("gsap-logo.html", "logo web/SVG", OK), ("Lottie", "logo vectorial para apps", ENG)],
    qc=["Logo legible y centrado.", "Colores exactos.", "Termina en reposo."],
    pitfalls=["Monograma de iniciales poco legible con nombres de una sola palabra larga.", "Animar logos de terceros sin permiso."],
    related=["motion-graphics", "mascot-animation", "lottie-animation"]),

"typography-animation": dict(
    title="Animación tipográfica",
    description="Anima textos con criterio tipográfico: jerarquía, tracking, entrada/salida por letra, palabra o línea, máscaras, máquina de escribir, subtítulos estilizados y rótulos. Úsala para 'texto animado', 'título animado', 'subtítulos bonitos', 'rótulo', 'efecto máquina de escribir'.",
    intro="Modos de `kinetic_typography`: `pop` (escala con rebote), `slide` (entrada lateral alternada), `wave` (ondulación), `typewriter` (letra a letra). Subtítulos del motor 2D: estándar (caja negra) o `big` (amarillos con contorno, centrados). Rótulos de escena con `caption`.",
    when=["Títulos, citas, subtítulos estilizados, rótulos de capítulo."],
    principles=["Legibilidad primero: contraste ≥ 4.5:1, contorno en fondos complejos.", "Tiempo de lectura: ~3 palabras/segundo.", "Una familia tipográfica, 2 pesos.",
                "Animar con sentido de lectura (izquierda→derecha)."],
    steps=["Elige modo según tono (pop alegre, slide dinámico, typewriter narrativo).", "Ajusta paleta y formato.", "Para subtítulos grandes en el motor: `\"subtitles\": \"big\"`."],
    commands="""python -m studio text "Había una vez un pequeño robot" --mode typewriter --format 16:9 --palette oscuro --music calm
python -m studio make "Un robot cuenta un secreto" --format 9:16     # subtítulos grandes automáticos""",
    example="""Cita inspiradora para redes: `text "El mejor momento para empezar es ahora" --mode pop --palette pastel --format 1:1`.""",
    tools=[("kinetic_typography", "texto animado", ENG), ("kinetic-type.html (GSAP)", "texto web", OK), ("Remotion TituloCinetico", "texto con springs", OK)],
    qc=["Cada palabra visible el tiempo suficiente.", "Sin cortes de palabras por ancho.", "Acentos y ñ correctos (fuente DejaVu)."],
    pitfalls=["Textos largos en modo pop (una pantalla por 3 palabras) se alargan mucho.", "Fuentes sin soporte de acentos."],
    related=["kinetic-typography", "motion-graphics", "video-editing"]),

"kinetic-typography": dict(
    title="Tipografía cinética",
    description="Tipografía cinética sincronizada con música o voz: palabras en el beat, escalas y rotaciones expresivas, cambios de color, fondo dinámico y barra de progreso; estilo lyric video y reels virales. Úsala para 'tipografía cinética', 'kinetic typography', 'lyric video', 'texto al ritmo'.",
    intro="`kinetic_typography` coloca una palabra por pulso según el BPM del mood (dance=124), agrupa en pantallas de hasta 3 palabras y añade pop/whoosh por palabra; `kinetic-type.html` (GSAP) alterna 4 efectos (escala+rotación, subida, entrada lateral con skew, elástico vertical) sobre un degradado animado con barra de progreso.",
    when=["Reels de texto, letras de canciones, frases motivacionales, anuncios."],
    principles=["Sincronía exacta con el pulso.", "Énfasis en palabras clave (tamaño/color).", "Variedad de movimientos con coherencia.", "Contraste fuerte con el fondo."],
    steps=["Escribe el texto en frases cortas.", "Python: `python -m studio text \"…\" --music dance`.", "Web/GSAP: `python -m studio web kinetic-type --query \"text=…&bpm=120\"`.", "Exporta vertical para redes."],
    commands="""python -m studio text "Crea animaciones increíbles con inteligencia artificial" --mode pop --format 9:16
python -m studio web kinetic-type --query "text=Tu historia merece moverse&bpm=110" --width 1080 --height 1920""",
    example="""Lyric video: dividir la letra por compases; `text` por frase con el mismo `music` y BPM de la canción; unir y añadir la canción con `add_audio`.""",
    tools=[("kinetic_typography (Python)", "rápido, sin navegador", ENG), ("kinetic-type.html (GSAP)", "efectos web", OK), ("Remotion", "kinetic con springs", OK)],
    qc=["Palabras en el beat.", "Texto completo y sin erratas.", "Legible en móvil."],
    pitfalls=["BPM de la plantilla distinto al de la canción.", "Palabras muy largas reducen el tamaño: el motor ajusta pero conviene partirlas."],
    related=["typography-animation", "music-video-animation", "tiktok-animation"]),

"animated-backgrounds": dict(
    title="Fondos animados",
    description="Fondos animados en bucle perfecto (manchas fluidas, degradados, partículas, rejilla retro) y escenarios con paralaje y nubes en movimiento para personajes, streams, webs y presentaciones. Úsala para 'fondo animado', 'background', 'fondo en movimiento', 'fondo para stream'.",
    intro="`animated_background` produce loops matemáticamente perfectos (todas las funciones con periodo = duración): `blobs`, `gradient`, `particles`, `grid`. Los escenarios del motor 2D (15 tipos × 3 horas del día) tienen capas de paralaje y nubes animadas.",
    when=["Fondos de stream/presentación/web.", "Escenarios para animaciones."],
    principles=["Fondo subordinado al contenido: menos contraste y saturación.", "Movimiento lento (periodos ≥ 6 s).", "Bucle invisible.", "Paleta coherente con la marca."],
    steps=["Elige tipo y paleta: `python -m studio background blobs --palette pastel --duration 8`.", "Para escenarios: `background` en el project.json + cámara `pan` para paralaje.",
           "Exporta MP4 o GIF/WebM según destino."],
    commands="""python -m studio background blobs --palette pastel --duration 8 -o fondo.mp4
python -m studio background grid --palette neon --format 9:16
python -m studio export fondo.mp4 --preset webm""",
    example="""Fondo para OBS: `background particles --palette oscuro --duration 10` → WebM VP9 ligero en bucle.""",
    tools=[("animated_background", "loops perfectos", ENG), ("backgrounds.py", "15 escenarios con paralaje", ENG), ("CSS/GSAP", "fondos web nativos", OK)],
    qc=["Bucle sin salto.", "No distrae del contenido.", "Peso de archivo adecuado."],
    pitfalls=["Fondos muy saturados detrás de texto.", "Duraciones no enteras en GIF pueden saltar."],
    related=["seamless-loop-animation", "motion-graphics", "3d-environment-animation"]),

"svg-animation": dict(
    title="Animación SVG",
    description="Animaciones vectoriales SVG para web: dibujado de trazos (stroke-dashoffset), morphing, transformaciones con transform-origin, CSS keyframes, SMIL o GSAP, y captura a video. Úsala para 'SVG animado', 'icono animado', 'ilustración vectorial animada', 'animación ligera para web'.",
    intro="`templates/web/svg-css-character.html` muestra un personaje SVG (manzana) animado solo con CSS: rebote con squash & stretch, parpadeo con `steps`, brazos con `transform-origin`, sombra sincronizada y nube a la deriva. `gsap-logo.html` dibuja un anillo con `stroke-dashoffset`. Ambos se capturan determinísticamente vía Web Animations API.",
    when=["Animaciones web ligeras, iconos, ilustraciones, landing pages."],
    principles=["`transform-box: fill-box` y `transform-origin` correctos para rotar piezas.", "Usar `pathLength=1` para animar trazos fácilmente.",
                "Preferir transform/opacity (GPU) frente a propiedades de layout.", "Accesibilidad: respetar `prefers-reduced-motion`."],
    steps=["Parte de la plantilla y reemplaza los paths por tu ilustración (exportada de Inkscape/Figma).", "Anima con CSS keyframes o GSAP.",
           "Previsualiza: `python -m studio serve` → 3D y Web → svg-css-character → Ver en vivo.", "Captura: `python -m studio web svg-css-character --duration 4 --query color=%2343a047`."],
    commands="""python -m studio web svg-css-character --duration 4 --query "color=%23fb8c00" -o naranja_svg.mp4""",
    example="""Icono de 'me gusta' animado para una web: SVG del corazón con `stroke-dashoffset` + `scale` con rebote en hover, y versión MP4 para redes.""",
    tools=[("svg-css-character.html", "plantilla SVG+CSS", OK), ("GSAP DrawSVG/MorphSVG", "SVG avanzado (plugins incluidos en gsap, sin probar)", "📦 incluido, sin probar"), ("Inkscape (gratis)", "edición SVG", EXT)],
    qc=["Pivotes correctos (sin piezas que 'vuelan').", "Funciona en Chrome, Firefox y Safari.", "Peso < 50 KB."],
    pitfalls=["transform-origin en SVG sin fill-box rota respecto al lienzo.", "Animar `d` sin el mismo número de puntos (morph) falla sin plugin."],
    related=["css-animation", "gsap-animation", "lottie-animation"]),

"lottie-animation": dict(
    title="Animación Lottie",
    description="Genera animaciones Lottie (JSON Bodymovin v5) sin After Effects: capas de forma, keyframes con easing, squash & stretch, parpadeo y sombra; reproducción con lottie-web y captura a MP4/GIF; stickers para apps. Úsala para 'Lottie', 'animación JSON', 'sticker animado', 'animación para app'.",
    intro="`studio/lottie.py` escribe JSON Lottie válido (probado con lottie-web 5.13): personaje con cuerpo, hoja, brillo, ojos con parpadeo, pupilas, mejillas y boca, rebote con squash & stretch y sombra que escala. `lottie-player.html` lo reproduce y `__seek` permite capturarlo. Recuerda: en Lottie el primer elemento de la lista se dibuja encima.",
    when=["Animaciones para apps (Android/iOS/Flutter/React Native), webs y stickers."],
    principles=["Vectores = nitidez a cualquier tamaño y archivos pequeños.", "Keyframes con easing (`i`/`o` bezier).", "Loops cerrados (primer y último keyframe iguales).",
                "Evitar efectos no soportados por lottie-web (blur, expresiones)."],
    steps=["`python -m studio lottie --color \"#e53935\" -o personaje.json`.", "Previsualiza: `templates/web/lottie-player.html?src=lottie/personaje.json`.",
           "Captura a video: `python -m studio web lottie-player --query \"src=lottie/personaje.json&loops=3\"`.", "Publica en LottieFiles o integra con lottie-web/lottie-android."],
    commands="""python -m studio lottie --color "#7e57c2" -o templates/web/lottie/uva.json
python -m studio web lottie-player --query "src=lottie/uva.json&loops=3&bg=%23ffffff" --width 512 --height 512 -o uva.mp4""",
    example="""Sticker de mascota para Telegram: generar Lottie, convertir a `.tgs` (gzip del JSON a 512×512, 60 fps, ≤3 s) con herramientas de Telegram.""",
    tools=[("studio/lottie.py", "generador Lottie", ENG), ("lottie-web 5.13", "reproducción y captura", OK), ("LottieFiles", "editor/preview online", NET), ("After Effects + Bodymovin", "Lottie complejo", EXT)],
    qc=["Abre sin errores en lottie-web.", "Bucle limpio.", "Tamaño < 100 KB."],
    pitfalls=["Orden de capas invertido (pupilas tapadas): el estudio ya invierte el orden.", "Keyframes con distinta dimensión (2D vs 3D) rompen la animación."],
    related=["svg-animation", "mascot-animation", "seamless-loop-animation"]),

"css-animation": dict(
    title="Animación CSS",
    description="Animaciones con CSS puro: @keyframes, transiciones, timing functions (cubic-bezier, steps), transform/opacity, animación de variables y control con Web Animations API; ideal para UI y webs ligeras. Úsala para 'animación CSS', 'keyframes', 'animar un botón', 'loader', 'microinteracciones'.",
    intro="La plantilla SVG+CSS demuestra squash & stretch, parpadeo con `steps(1)` y deriva infinita, todo en CSS. Para capturar, `window.__seek(t)` pausa cada animación (`document.getAnimations()`) y fija `currentTime` — técnica válida para cualquier página con CSS animations.",
    when=["Microinteracciones, loaders, banners web, animaciones de UI."],
    principles=["Animar solo `transform` y `opacity` para 60 fps.", "Duraciones de UI 150–400 ms; ilustraciones 0.6–3 s.",
                "`cubic-bezier(.34,1.56,.64,1)` para overshoot.", "`@media (prefers-reduced-motion)` para accesibilidad."],
    steps=["Escribe @keyframes y aplica `animation`.", "Ajusta timing con cubic-bezier.", "Para video: añade el `__seek` de la plantilla y captura con `python -m studio web <archivo.html>`."],
    commands="""python -m studio web svg-css-character --duration 3
python -m studio web ruta/a/mi_animacion.html --duration 5 --width 1080 --height 1080""",
    example="""Loader de marca: tres frutas que botan con `animation-delay` escalonado (0, .15s, .3s), `ease-in-out infinite`; capturado a GIF para redes.""",
    tools=[("CSS + Web Animations API", "animación nativa", OK), ("capture.mjs", "CSS → MP4", OK), ("Animista / cubic-bezier.com", "generadores de keyframes y curvas", NET)],
    qc=["Fluido a 60 fps (DevTools Performance).", "Respeta reduced-motion.", "Sin saltos de layout."],
    pitfalls=["Animar `top/left/width` provoca reflow.", "`transform` sobrescribe otros transforms del mismo elemento: anida elementos."],
    related=["svg-animation", "gsap-animation", "interactive-animation"]),

"gsap-animation": dict(
    title="Animación con GSAP",
    description="Animaciones web profesionales con GSAP 3: timelines, posiciones relativas, stagger, eases (back, elastic, expo), ScrollTrigger, control determinista (seek) y captura a video. Úsala para 'GSAP', 'timeline web', 'animación web profesional', 'scroll animation', 'animar una landing'.",
    intro="GSAP 3.15 está instalado localmente (`node_modules/gsap`, sin CDN). Las plantillas `gsap-logo.html` y `kinetic-type.html` crean timelines **pausadas** y exponen `window.__seek = t => { tl.seek(t, false) }` (sin devolver el timeline: GSAP es 'thenable' y bloquearía el `await` de la captura).",
    when=["Animaciones web complejas, intros, landings, banners."],
    principles=["Construir una timeline maestra con etiquetas y posiciones (`'<'`, `'+=0.2'`).", "Stagger para grupos.", "Eases con carácter (back.out(2), elastic.out(1,0.4)).",
                "Separar construcción de reproducción (paused: true) para poder capturar."],
    steps=["Copia una plantilla y modifica la timeline.", "Previsualiza en el servidor del estudio.", "Captura: `python -m studio web mi_plantilla.html`.", "Para scroll, usa ScrollTrigger (incluido en el paquete gsap)."],
    commands="""python -m studio web gsap-logo --query "text=Nuevo Lanzamiento&color=%2310b981" --duration 4.5
python -m studio web kinetic-type --query "text=Hola desde GSAP&bpm=100\"""",
    spec="""// patrón de plantilla capturable
const tl = gsap.timeline({ paused: true });
tl.from(".titulo", { y: 80, opacity: 0, duration: 0.6, ease: "back.out(2)" })
  .from(".item", { scale: 0, stagger: 0.08, ease: "elastic.out(1,0.5)" }, "-=0.2");
window.__duration = tl.duration();
window.__seek = (t) => { tl.seek(t, false); };
window.__ready = true;""",
    example="""Banner animado de 6 s para web: título, 3 iconos con stagger y CTA con pulso; capturado en 1200×628 para anuncios.""",
    tools=[("GSAP 3.15 (local)", "timelines", OK), ("capture.mjs", "GSAP → MP4", OK), ("ScrollTrigger / SplitText", "plugins incluidos en el paquete gsap (no probados aquí)", "📦 incluido, sin probar")],
    qc=["La captura coincide con la reproducción en vivo.", "Sin errores de consola.", "Duración = `tl.duration()`."],
    pitfalls=["Devolver el timeline desde `__seek` cuelga la captura (thenable).", "Usar `gsap.to` sueltos sin timeline impide el seek global."],
    related=["css-animation", "motion-graphics", "interactive-animation"]),

"interactive-animation": dict(
    title="Animación interactiva",
    description="Animaciones que responden al usuario: personajes que siguen el ratón con la mirada, saltan al hacer clic, bailan con una tecla, física simple (gravedad, squash), partículas; Canvas 2D, Three.js y sprites para juegos. Úsala para 'interactiva', 'que reaccione al ratón', 'mini juego', 'animación para mi web que responda'.",
    intro="`templates/web/interactive.html` implementa un personaje en Canvas 2D con mirada que sigue al cursor, salto con gravedad y squash al aterrizar, modo baile con barra espaciadora y ráfaga de partículas. Incluye modo de captura determinista (simula clics) para generar un video de demostración.",
    when=["Webs, landings, juegos sencillos, kioscos, demos."],
    principles=["Respuesta inmediata (<100 ms) a la entrada.", "Física creíble y estable (dt acotado).", "Feedback visual y sonoro en cada interacción.", "Accesible por teclado."],
    steps=["Abre la plantilla en vivo (pestaña 3D y Web).", "Cambia color con `?color=%23…`; adapta física y dibujo.", "Para 3D interactivo usa `three-scene.html` (OrbitControls).",
           "Para juegos usa sprites de la Skill `sprite-animation` con Phaser/Godot."],
    commands="""python -m studio serve      # abrir http://127.0.0.1:8765 → 3D y Web → interactive → Ver en vivo
python -m studio web interactive --duration 6 -o demo_interactiva.mp4""",
    example="""Mascota interactiva para una web: incrustar `interactive.html` en un iframe; la mascota mira al cursor y salta al hacer clic con confeti.""",
    tools=[("Canvas 2D", "interacción ligera", OK), ("Three.js + OrbitControls", "3D interactivo", OK), ("Phaser / Godot", "juegos 2D", EXT), ("Rive", "animación interactiva con state machines", EXT)],
    qc=["Funciona con ratón y táctil.", "60 fps en móviles medios.", "Sin fugas de memoria (partículas limpiadas)."],
    pitfalls=["dt sin límite tras cambiar de pestaña provoca saltos: acotar a 0.05 s.", "Olvidar `resize`."],
    related=["threejs-animation", "gsap-animation", "sprite-animation"]),
}
