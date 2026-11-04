OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
EXT = "💻 programa externo recomendado"

SKILLS = {
"stop-motion": dict(
    title="Stop-motion",
    description="Simula stop-motion: 12 fps con poses mantenidas (on twos), micro-temblor de posición y rotación entre fotogramas, textura y viñeta; también guía para stop-motion real con cámara. Úsala para 'stop motion', 'cuadro a cuadro con objetos', 'animación con juguetes'.",
    intro="`style: stopmotion` cuantiza el tiempo a 1/12 s (las poses se mantienen 2 frames a 24 fps) y aplica un jitter determinista por pose (±1.5 px, ±0.6°) que imita la manipulación manual, más textura y viñeta suave. Para stop-motion real: fotos numeradas → FFmpeg.",
    when=["Look artesanal, juguetes, objetos animados.", "Ensamblar fotos de stop-motion reales del usuario."],
    principles=["12 fps (o 8 para más carácter).", "El temblor es parte del encanto, pero sutil.", "Iluminación constante (evitar parpadeo de luz en fotos reales).",
                "Movimientos con easing marcados en poses clave."],
    steps=["Digital: `make … --style stopmotion`.", "Real: fotos con trípode y exposición manual → `foto_0001.jpg…`.",
           "Ensamblar: `ffmpeg -framerate 12 -i foto_%04d.jpg -vf scale=1920:-2 -r 24 -pix_fmt yuv420p stop.mp4`.", "Deflicker si hay parpadeo: `-vf deflicker`."],
    commands="""python -m studio make "Unos juguetes robot bailan en la mesa" --style stopmotion
ffmpeg -framerate 12 -i fotos/foto_%04d.jpg -vf "scale=1920:-2,deflicker" -r 24 -pix_fmt yuv420p stopmotion_real.mp4""",
    example="""Stop-motion real del usuario con 96 fotos → 8 s a 12 fps, deflicker, música `cute` del estudio con `add_audio`.""",
    tools=[("style stopmotion", "simulación", ENG), ("FFmpeg (deflicker)", "ensamblado real", OK), ("Stop Motion Studio / qStopMotion", "captura con papel cebolla", EXT)],
    qc=["Ritmo 12 fps estable.", "Sin parpadeo de exposición.", "Jitter apreciable pero no mareante."],
    pitfalls=["Exposición automática de la cámara provoca parpadeo.", "Mezclar 24 fps fluido con stop-motion rompe el estilo."],
    related=["clay-animation", "paper-animation", "frame-by-frame-animation"]),

"clay-animation": dict(
    title="Animación de plastilina (claymation)",
    description="Look de plastilina: sombreado suave, textura de arcilla con huellas, colores mate, 12 fps con temblor y viñeta; en 3D con materiales mate y subsurface. Úsala para 'plastilina', 'arcilla', 'claymation', 'estilo Aardman', 'muñecos de plasti'.",
    intro="`style: clay` usa sombreado degradado (no cel), sin contorno, textura de ruido multiplicada (huellas) y la cadencia stop-motion. En 3D, materiales con roughness 0.6–0.8 y subsurface ligero dan aspecto de arcilla.",
    when=["Estética artesanal infantil, publicidad cálida."],
    principles=["Formas redondeadas y gruesas.", "Colores mate saturados, sin brillos especulares fuertes.", "Movimiento a 12 fps con imperfección.", "Iluminación suave de estudio."],
    steps=["`make … --style clay`.", "Para 3D: `--3d` y ajustar roughness en scene3d (`mat(…, rough=0.7, sss=0.1)`).", "Escenarios simples (kitchen, studio, park)."],
    commands="""python -m studio make "Un oso y un conejo de plastilina hacen un pastel en la cocina" --style clay""",
    example="""Anuncio cálido: mascota de plastilina en la cocina, música `cute`, 12 fps, textura visible en primer plano.""",
    tools=[("style clay", "claymation digital", ENG), ("Blender (materiales mate + displacement)", "clay 3D realista", OK)],
    qc=["Textura visible pero no ruidosa.", "Sin contornos de cartoon.", "Movimiento con cadencia de 12 fps."],
    pitfalls=["Brillos especulares fuertes delatan lo digital.", "Escenas muy largas en clay cansan: cortas y expresivas."],
    related=["stop-motion", "cute-animation", "3d-animation"]),

"paper-animation": dict(
    title="Animación de papel (papercraft)",
    description="Estética de papel: textura de papel con fibras, tonos cálidos, sin contornos, sombras proyectadas, capas recortadas y movimiento a saltos (12 fps). Úsala para 'papel', 'papercraft', 'origami', 'recortes de papel', 'collage'.",
    intro="`style: paper` añade textura de papel (ruido de fibras) con tinte cálido, quita contornos y cel shading, y aplica cadencia de 12 fps con jitter de recorte. Complementa con escenarios de capas (paralaje) que simulan teatro de papel.",
    when=["Cuentos, educación, explicativos artesanales."],
    principles=["Capas planas a distintas profundidades.", "Sombra corta bajo cada capa.", "Paleta limitada de cartulinas.", "Imperfecciones intencionales."],
    steps=["`make … --style paper`.", "Prefiere cámara `pan` para lucir el paralaje.", "Música `calm` o `cute`."],
    commands="""python -m studio make "Un zorro y una rana cuentan un cuento en el bosque" --style paper""",
    example="""Cuento de papel de 30 s: 4 escenas en forest/park con paneos, narración por personajes y subtítulos.""",
    tools=[("style paper", "papel digital", ENG), ("Blender (planos con grosor + textura)", "papercraft 3D", OK)],
    qc=["Textura de papel visible en zonas planas.", "Sin contornos negros.", "Paralaje perceptible."],
    pitfalls=["Combinar papel con efectos de partículas brillantes rompe el estilo (usa leaves, confetti).", "Fondos con degradados fuertes no parecen papel."],
    related=["cutout-animation", "stop-motion", "educational-animation"]),

"realistic-animation": dict(
    title="Animación realista",
    description="Busca realismo: sombreado suave, profundidad de campo, iluminación física, Cycles en 3D, y para fotorrealismo real, generación de video/imagen IA. Úsala para 'realista', 'fotorrealista', 'que parezca real', 'hiperrealista'.",
    intro="Honestidad técnica: el motor 2D ofrece `style: realistic` (sombreado suave con desenfoque, contraste y grano leve) y el 3D puede usar Cycles (path tracing). El **fotorrealismo** de personas/animales reales requiere modelos generativos (Skill `ai-video-generation`, claves de Replicate/OpenAI/Stability o conector ElevenLabs) o assets escaneados.",
    when=["El usuario pide realismo; explicar opciones y coste."],
    principles=["La luz hace el realismo: GI, sombras suaves, rim light.", "Materiales físicos (roughness/metallic correctos).", "Movimiento con peso e inercia.",
                "Imperfección: grano, motion blur, DOF."],
    steps=["Pregunta implícita: ¿estilizado-realista (local) o foto-real (IA)?", "Local 3D: `--3d --engine cycles` y `samples` 128+ (lento en CPU).",
           "Foto-real: genera imagen con `image --provider openai|stability|huggingface` y anímala con `img2video --provider replicate`.", "Une y pasa QC."],
    commands="""python -m studio make "Un robot camina por la ciudad de noche" --3d --engine cycles --quality preview
python -m studio image "photorealistic red fox in a snowy forest, golden hour, 85mm" --provider auto -o zorro.png
python -m studio img2video zorro.png --provider replicate --prompt "the fox turns its head, snow falling, slow push in" """,
    spec="""{"engine": "3d", "render_engine": "cycles", "samples": 128}""",
    example="""«Un león realista caminando»: sin claves → explicar que el motor produce estilizado; ofrecer 3D Cycles o `img2video --move parallax` sobre una foto del usuario; con clave → Replicate imagen→video.""",
    tools=[("Blender Cycles", "path tracing", OK), ("style realistic", "aproximación 2D", ENG), ("Replicate / OpenAI / Stability", "fotorrealismo generativo", KEY), ("Poly Haven", "HDRI y texturas reales", NET)],
    qc=["Iluminación coherente con el entorno.", "Sin artefactos de IA (manos, ojos).", "Coste/tiempo comunicado."],
    pitfalls=["Cycles sin denoiser en CPU necesita muchas muestras: tiempos largos.", "Prometer fotorrealismo sin proveedor IA."],
    related=["ai-video-generation", "animation-lighting", "cinematic-effects"]),

"fantasy-animation": dict(
    title="Animación de fantasía",
    description="Mundos de fantasía: castillos, bosques encantados, magos, hadas, criaturas, luces mágicas, gradación violeta-dorada y bloom, música orquestal de fantasía. Úsala para 'fantasía', 'mágico', 'reino', 'hadas', 'dragones', 'cuento de hadas'.",
    intro="`style: fantasy` aplica tinte violeta-dorado, bloom fuerte en altas luces y viñeta; el planificador elige `castle`, magia, luciérnagas y música `fantasy` (Eb mayor, campanas). Especies útiles: mago, estrella, monstruo, conejo, zorro.",
    when=["Cuentos de hadas, aventuras mágicas, videojuegos de fantasía."],
    principles=["Luz como magia: fuentes cálidas en entornos fríos.", "Escala: castillos grandes, personajes pequeños.", "Criaturas con siluetas originales.", "Música con campanas y cuerdas."],
    steps=["`make … --style fantasy`.", "Añade `magic`, `fireflies`, `sparkles`.", "Usa transformaciones para momentos mágicos.", "Cierra con `zoom_out` al castillo."],
    commands="""python -m studio make "Un mago y un conejo buscan una estrella mágica en el castillo" --style fantasy""",
    example="""Aventura mágica de 20 s: llegada al castillo (pan), hechizo (magic + transform), celebración con sparkles, música fantasy.""",
    tools=[("style fantasy + efectos mágicos", "look de fantasía", ENG), ("Blender EEVEE (bloom)", "fantasía 3D", OK), ("FLUX/SDXL (IA)", "fondos pintados", KEY)],
    qc=["Bloom sin quemar caras.", "Paleta coherente violeta/dorado.", "Música acorde."],
    pitfalls=["Abusar del bloom → imagen lechosa.", "Criaturas de franquicias existentes: diseña originales."],
    related=["magic-effects", "character-transformations", "anime-animation"]),

"horror-animation": dict(
    title="Animación de terror (apta para todo público o suave)",
    description="Terror y suspenso: desaturación, viñeta fuerte, parpadeo de luz, grano, niebla, rayos, fantasmas, sustos con cámara y drones sonoros disonantes. Úsala para 'terror', 'miedo', 'Halloween', 'suspenso', 'casa embrujada', 'fantasma'.",
    intro="`style: horror` desatura al 35 %, tiñe hacia rojo-verdoso, aplica viñeta intensa, parpadeo irregular de luz y grano fuerte. El planificador usa `haunted` (bosque muerto + niebla + luna), música `spooky` (drone + viento + campanas disonantes), personajes niño + fantasma.",
    when=["Halloween, historias de miedo, suspenso."],
    principles=["El miedo está en lo que no se ve: oscuridad y sonido.", "Construir tensión (lento) → susto (rápido + sonido) → alivio.",
                "Planos cerrados y cámara inestable.", "Mantener un nivel apto para el público objetivo."],
    steps=["`make … --style horror` (o palabras terror/miedo/embrujado).", "Escena 1 tensión (walk scared + fog), 2 susto (lightning + shake + fantasma), 3 huida (run).",
           "Revisa que el susto no sea excesivo si es para niños."],
    commands="""python -m studio make "Un fantasma asusta a un niño en un bosque embrujado" --style horror""",
    example="""Corto de Halloween de 11 s con 3 escenas, truenos, niebla, 'Continuará…' y música spooky.""",
    tools=[("style horror", "look de terror", ENG), ("effects fog/lightning/smoke", "atmósfera", ENG), ("sox", "efectos de audio extra (reverb, pitch)", OK)],
    qc=["Imagen oscura pero legible.", "Flashes con periodo ≥ 1.5 s (fotosensibilidad).", "Apto para la edad indicada."],
    pitfalls=["Todo negro = no se ve nada: subir ligeramente la luz de personajes.", "Sustos constantes dejan de asustar."],
    related=["smoke-animation", "lightning-effects", "animation-sound-design"]),

"cute-animation": dict(
    title="Animación tierna (kawaii)",
    description="Animación kawaii/tierna: proporciones chibi, ojos grandes, mejillas sonrosadas, paleta pastel, movimientos rebotones, corazones y destellos, música de caja de música. Úsala para 'tierno', 'kawaii', 'cute', 'adorable', 'para niños pequeños'.",
    intro="`style: cute` agranda los ojos 12 %, añade rubor permanente, aclara la paleta (pastel) y usa contorno fino; música `cute` (F mayor, campanas). Efectos recomendados: hearts, sparkles, bubbles.",
    when=["Contenido infantil, stickers, saludos, mascotas tiernas."],
    principles=["Formas redondas, sin esquinas.", "Rebote suave en todo (squash ligero).", "Paleta pastel con alto valor.", "Expresiones felices y sorpresas suaves."],
    steps=["`make … --style cute`.", "Elige conejo, gato, panda, fresa, estrella.", "Añade `hearts` o `sparkles`.", "Exporta GIF/Lottie para stickers."],
    commands="""python -m studio make "Un conejo tierno camina en la nieve" --style cute
python -m studio lottie --color "#f8bbd0" -o sticker_kawaii.json""",
    example="""Tarjeta de cumpleaños: panda y fresa kawaii celebran con confeti y corazones, 8 s, cuadrado 1:1.""",
    tools=[("style cute", "kawaii", ENG), ("Lottie generator", "stickers", ENG)],
    qc=["Colores pastel sin perder contraste del personaje.", "Ritmo alegre.", "Sin expresiones agresivas."],
    pitfalls=["Fondos pastel + personaje pastel = sin contraste: usa contorno o fondo más saturado.", "Música demasiado rápida para lo tierno."],
    related=["cartoon-animation", "mascot-animation", "character-expressions"]),

"minimalist-animation": dict(
    title="Animación minimalista",
    description="Animación minimalista y plana: formas simples, sin contornos, ojos de punto, fondos lisos, paleta reducida, mucho espacio negativo y movimientos precisos con easing. Úsala para 'minimalista', 'flat design', 'limpio', 'simple', 'corporativo moderno'.",
    intro="`style: minimalist` usa ojos de punto, sin contorno ni sombreado y fuerza el fondo `studio` (degradado liso con suelo). Ideal con motion graphics (texto, logos, infografías) para videos corporativos o explicativos.",
    when=["Explainers corporativos, apps, presentaciones, branding moderno."],
    principles=["Menos es más: un elemento protagonista por plano.", "Espacio negativo generoso.", "Easing preciso (in_out, out_back).", "Paleta de 2–3 colores + neutro."],
    steps=["`make … --style minimalist`.", "Combina con `text`, `logo`, `infographic` (paleta corporativo).", "Transiciones `slide`/`wipe` limpias."],
    commands="""python -m studio make "Un robot presenta una nueva app" --style minimalist
python -m studio infographic "2023=40,2024=65,2025=90" --title "Crecimiento" --unit "%\"""",
    example="""Explainer de 30 s: robot minimalista explica 3 ventajas, cada una con infografía o texto animado, música `calm`.""",
    tools=[("style minimalist", "flat", ENG), ("motiongraphics", "texto/logos/infografías", ENG), ("GSAP templates", "animaciones web limpias", OK)],
    qc=["Nada superfluo en pantalla.", "Alineaciones precisas.", "Tipografía consistente."],
    pitfalls=["Minimalista ≠ vacío: mantener una acción clara.", "Demasiados colores rompen el estilo."],
    related=["motion-graphics", "infographic-animation", "educational-animation"]),

"educational-animation": dict(
    title="Animación educativa",
    description="Videos educativos claros: presentador animado, pizarra/aula, explicación paso a paso, ejemplos visuales, infografías, subtítulos, repaso final y ritmo adaptado a la edad. Úsala para 'educativo', 'explica', 'clase', 'lección', 'tutorial animado', 'para enseñar'.",
    intro="El planificador reconoce 'clase/aula/explica' → escenario `classroom` (pizarra), personaje presentador que `talk`, subtítulos y música `calm`. Las infografías (`infographic`) y textos animados (`text`) ilustran datos y conceptos.",
    when=["Lecciones, divulgación, onboarding, formación."],
    principles=["Un concepto por escena; máximo 3 conceptos por video corto.", "Ejemplo concreto después de cada idea.", "Repetición final (resumen).",
                "Lenguaje y ritmo según la edad (niños: frases ≤ 8 palabras)."],
    steps=["Define objetivo de aprendizaje.", "Guion: gancho (pregunta) → explicación → ejemplo → resumen.", "Escenas en `classroom` con `talk`; inserta infografías.",
           "Une con `concat` y añade SRT."],
    commands="""python -m studio make "Clase educativa: un robot explica en el aula por qué llueve" --style minimalist
python -m studio infographic "Mercurio=0.38,Tierra=1,Júpiter=11.2" --title "Tamaño de los planetas (Tierra=1)\"""",
    example="""Lección de 40 s sobre el ciclo del agua: robot en el aula (talk) → escena con lluvia → infografía de etapas → resumen y 'Fin'.""",
    tools=[("Motor 2D (classroom + talk)", "presentador", ENG), ("infographic/kinetic text", "datos y conceptos", ENG), ("Claude (opcional)", "guion didáctico", KEY)],
    qc=["Información correcta (revisar datos).", "Subtítulos completos.", "Ritmo que permite leer."],
    pitfalls=["Datos inventados: verifica cifras antes de animarlas.", "Pizarra con texto fijo irrelevante: personaliza si es necesario."],
    related=["infographic-animation", "kinetic-typography", "animation-scripting"]),

"infographic-animation": dict(
    title="Infografías animadas",
    description="Visualización de datos animada: barras que crecen con rebote, contadores numéricos, títulos, etiquetas, unidades, paletas y formatos para redes; gráficos claros y honestos. Úsala para 'infografía', 'gráfico animado', 'datos animados', 'estadísticas', 'chart animado'.",
    intro="`motiongraphics.infographic(data, …)` anima un gráfico de barras: título con fundido, barras escalonadas con `ease_out_back`, contadores que suben hasta el valor, etiquetas y sonido 'pop' por barra. Paletas: vibrante, pastel, oscuro, neon, corporativo.",
    when=["Mostrar cifras, comparaciones, rankings, resultados."],
    principles=["Eje en cero (honestidad visual).", "Ordenar barras con intención (ranking o tiempo).", "Máximo 7 categorías.", "Etiquetas directas, sin leyenda."],
    steps=["Prepara datos `Etiqueta=valor,…` (verifica la fuente).", "`python -m studio infographic \"…\" --title … --unit …`.", "Formato según destino (9:16 para redes).", "Úsala como escena insertada con `concat`."],
    commands="""python -m studio infographic "Manzana=32,Plátano=24,Fresa=40,Uva=18" --title "Frutas favoritas" --unit " votos"
python -m studio infographic "Ene=12,Feb=18,Mar=27" --title "Ventas (miles)" --format 9:16""",
    example="""Resultados de encuesta para Instagram: 4 barras, paleta pastel, formato 1:1 (añadir `--format 1:1`), 6 s.""",
    tools=[("motiongraphics.infographic", "barras animadas", ENG), ("GSAP/D3 (web)", "gráficos interactivos", OK), ("Remotion", "gráficos con React", OK)],
    qc=["Valores y unidades correctos.", "Texto legible en móvil.", "Escala honesta."],
    pitfalls=["Ejes truncados exageran diferencias.", "Demasiadas categorías en 9:16."],
    related=["educational-animation", "motion-graphics", "kinetic-typography"]),
}
