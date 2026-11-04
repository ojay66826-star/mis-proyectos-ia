OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
EXT = "💻 programa externo recomendado"

SPECIES_LIST = ("frutas: manzana, platano, naranja, fresa, uva, sandia, pina, limon, pera, cereza, aguacate; "
                "animales: gato, perro, conejo, oso, rana, pinguino, zorro, panda; otros: robot, nino, nina, persona, mago, "
                "mascota, fantasma, monstruo, estrella")

SKILLS = {
"character-design": dict(
    title="Diseño de personajes (consistente)",
    description="Diseña personajes originales y mantiene su apariencia idéntica en todas las escenas mediante fichas JSON (character sheet) y hojas de modelo con poses, expresiones y visemas. Úsala para 'crea un personaje', 'diseña una mascota', 'hoja de personaje', 'que el personaje se vea igual siempre'.",
    intro=f"La **ficha** (`id, name, species, kind, shape, color, accent, eyes, accessory, hair, hair_color, skin, voice, personality, height`) es la única fuente de verdad: el renderizador procedural dibuja siempre igual a partir de ella. Especies disponibles: {SPECIES_LIST}. Accesorios: none, hat, bow, glasses, crown, cap, wizard, scarf.",
    when=["Crear o personalizar un personaje.", "Garantizar consistencia en una serie de videos.", "Generar referencias para IA de imagen (prompt fijo)."],
    principles=["Silueta reconocible en negro.", "Paleta de 2–3 colores principales + acento.", "Forma = personalidad: redondo amable, anguloso agresivo, alargado torpe/elegante.",
                "Una característica memorable (accesorio, color de ojos).", "Documentar todo en la ficha y reutilizarla."],
    steps=["Define personalidad y rol (protagonista, amigo, rival).", "Elige especie y color: `python -m studio character <especie> --name … --color … --accessory …`.",
           "Revisa la hoja generada (`*_hoja.png`): 8 poses, 10 emociones, 6 visemas.", "Guarda la ficha `.json` junto al proyecto y pásala en `characters` del project.json.",
           "Para IA de imagen usa `character_prompt(spec)` + semilla fija para reproducir el mismo diseño."],
    commands="""python -m studio character manzana --name "Rojita" --color "#d32f2f" --accessory bow --style cute
python -m studio character robot --name "Bolt" --color "#26a69a" --eyes anime --style anime
python -c "from studio.characters import make_character, character_prompt; print(character_prompt(make_character('gato','Michi'), 'anime'))\"""",
    spec="""{"characters": [{"id": "rojita", "name": "Rojita", "species": "manzana", "color": "#d32f2f",
  "accessory": "bow", "eyes": "round", "personality": "curiosa y valiente"}]}""",
    example="""«Crea una mascota para mi panadería»: especie `estrella` color `#ffb300` con `cap`, estilo `cute`; entregar hoja PNG, ficha JSON, versión 3D (`character3d estrella`) y logo animado con su nombre.""",
    tools=[("Renderizador procedural", "hojas de modelo", ENG), ("Blender", "versión 3D del personaje", OK), ("FLUX/SDXL (HF, Replicate) + IP-Adapter", "diseños IA con referencia", KEY),
           ("Krita", "bocetos y retoques", EXT)],
    qc=["La hoja muestra todas las expresiones correctamente.", "Mismo `id` en todas las escenas.", "Contraste suficiente con los fondos elegidos."],
    pitfalls=["Cambiar el color entre escenas rompe la continuidad: edita la ficha, no la escena.", "Dos personajes del mismo color se confunden: el planificador varía el color si repites especie."],
    related=["character-expressions", "mascot-animation", "animation-workflow", "3d-modeling"]),

"character-expressions": dict(
    title="Expresiones faciales de personajes",
    description="Controla expresiones faciales: neutral, feliz, alegría, triste, enojado, sorprendido, asustado, enamorado, dormido, emocionado y confundido, con cejas, párpados, pupilas, boca, rubor, lágrimas, sudor y venas. Úsala para 'expresión', 'cara de…', 'que ponga cara triste/feliz'.",
    intro="Cada emoción modifica 6 rasgos: tamaño de ojos y pupilas, párpados (sleepy, angry), ángulo de cejas, forma de boca, extras (rubor, lágrima, gota de sudor, vena de enfado) y, en `excited`/`love`, pupilas en forma de estrella o corazón.",
    when=["Reacciones de personajes.", "Primeros planos emotivos.", "Hojas de expresiones para referencia."],
    principles=["La expresión empieza en las cejas y los ojos, la boca confirma.", "Transición de emoción con un pequeño 'take' (sorpresa) intermedio.",
                "Contraste emocional entre personajes en la misma escena.", "Exagerar en estilo cartoon, sutilizar en realista."],
    steps=["Asigna `emotion` al actor o una lista `emotions` con tiempos.", "Combina con una acción coherente (sad + idle, joy + celebrate).",
           "Para ver todas: `python -m studio character <especie>` (fila 2 y 3 de la hoja)."],
    commands="""python -m studio make "Un oso feliz, luego sorprendido y después enamorado" --quality preview""",
    spec="""{"character": "oso", "action": "idle", "emotion": "happy",
 "emotions": [{"t": 0, "emotion": "happy"}, {"t": 1.6, "emotion": "surprised"}, {"t": 3.2, "emotion": "love"}]}""",
    example="""El planificador detecta varias emociones en el texto («feliz, luego sorprendido y enamorado») y crea una escena con fondo de estudio y cambios cada 1.6 s.""",
    tools=[("Rig facial procedural", "11 emociones", ENG), ("Blender shape keys", "expresiones 3D", OK), ("Live2D", "rig facial 2D avanzado", EXT)],
    qc=["La emoción se reconoce en miniatura.", "Sin cambios de emoción en mitad de una palabra.", "Extras (lágrima/sudor) no tapan los ojos."],
    pitfalls=["Cambiar emoción cada <0.5 s parece glitch.", "`joy` cierra los ojos: no la uses en planos donde deba mirar a algo."],
    related=["character-emotions", "character-lip-sync", "character-design"]),

"character-movement": dict(
    title="Movimiento y desplazamiento de personajes",
    description="Planifica trayectorias y desplazamientos: entrar/salir de cuadro, cruzarse, perseguir, posiciones en profundidad, dirección (facing) y velocidad sin patinaje. Úsala para 'que entre por la izquierda', 'que corra hacia…', 'persecución', 'que se mueva por la escena'.",
    intro="Cada actor tiene `from`/`to` normalizados (x 0–1, y 0.82 = suelo), `move_start`/`move_end` para el tramo de movimiento, y `facing`. El orden de dibujo se calcula por la y (más abajo = delante) para simular profundidad.",
    when=["Composición dinámica con desplazamientos.", "Persecuciones, entradas y salidas."],
    principles=["Velocidad coherente con el ciclo: caminar ~0.12 ancho/s, correr ~0.25 ancho/s.", "Entrar desde fuera del cuadro (x<0 o x>1).",
                "Dejar 'aire' delante del personaje en la dirección de mirada.", "Cruces en distintas profundidades (y 0.78 vs 0.86)."],
    steps=["Dibuja en papel el recorrido de cada actor por escena.", "Asigna from/to y el tramo de movimiento.", "Ajusta `facing` en acciones estáticas.",
           "Revisa el storyboard (2 fotogramas por escena muestran posición inicial y media)."],
    commands="""python -m studio make "Un perro persigue a un gato por la ciudad" --quality preview""",
    spec="""{"actors": [
  {"character": "gato", "action": "run", "emotion": "scared", "from": [0.35, 0.84], "to": [1.15, 0.84]},
  {"character": "perro", "action": "run", "emotion": "excited", "from": [-0.15, 0.80], "to": [0.85, 0.80]}]}""",
    example="""Persecución: gato delante (y=0.84) huyendo, perro detrás (y=0.80) con 0.5 de desfase; cámara `pan`; música `action`.""",
    tools=[("Motor 2D (actor_position)", "trayectorias con easing", ENG), ("Blender", "mismas trayectorias en 3D (x×3.2 m)", OK)],
    qc=["Sin patinaje de pies.", "Entradas/salidas completas.", "Orden de profundidad correcto."],
    pitfalls=["y muy distintas cambian el tamaño aparente solo por orden, no por escala: usa `scale` para profundidad real.", "Personajes solapados en la misma x y y."],
    related=["character-animation", "scene-composition", "3d-walk-cycles"]),

"character-lip-sync": dict(
    title="Sincronización labial (lip-sync)",
    description="Sincroniza la boca de los personajes con la voz: TTS por personaje, extracción de envolvente de amplitud, mapeo de letras a visemas (A, E, O, U, M, F, X) y suavizado. Úsala para 'que hable', 'lip sync', 'sincronizar boca', 'doblaje'.",
    intro="`audio.lipsync_track(text, wav, fps)` combina el texto (vocales y labiales del español) con la energía real del audio: si el RMS cae por debajo del umbral la boca se cierra. Funciona con voces de espeak-ng y también con archivos de voz propios o de ElevenLabs.",
    when=["Cualquier diálogo.", "Doblar un audio grabado por el usuario."],
    principles=["La boca se cierra en M/B/P y en silencios.", "Vocales abiertas (A, O) en sílabas acentuadas.",
                "Evitar cambios de 1 frame (el estudio los filtra).", "Voces distintas por personaje (tono y timbre)."],
    steps=["Escribe el diálogo en `dialogue` (máx. ~12 palabras por línea).", "Render: el estudio genera la voz, calcula visemas y anima.",
           "Voz propia (grabada o de ElevenLabs): añade a la línea `\"audio_file\": \"ruta/voz.mp3\"`; el estudio la usa en lugar del TTS y calcula los visemas con ese audio.",
           "Para visemas de máxima precisión instala Rhubarb Lip Sync y usa su salida."],
    commands="""python -m studio make "Un robot explica en el aula cómo funciona el sol" --quality preview
python -c "from studio.audio import tts, lipsync_track; tts('Hola, ¿cómo estás?', 'v.wav'); print(lipsync_track('Hola, ¿cómo estás?', 'v.wav', 24))"
# voz propia en project.json: {"character": "manzana", "text": "Hola a todos", "audio_file": "mi_voz.mp3"}""",
    example="""«Haz que la manzana diga mi texto»: añadir `{"character":"manzana","text":"<texto>"}` a la escena; el visema por frame queda en el proyecto y el video incluye subtítulos.""",
    tools=[("espeak-ng", "TTS local en español (es-419)", OK), ("lipsync_track", "visemas desde texto + audio", ENG), ("Rhubarb Lip Sync", "visemas profesionales", EXT),
           ("ElevenLabs / OpenAI TTS", "voces naturales (STUDIO_TTS=elevenlabs)", KEY), ("Wav2Lip / SadTalker", "lip-sync sobre caras reales", EXT)],
    qc=["Boca cerrada cuando no hay voz.", "Desfase audio-boca ≤ 2 frames.", "Subtítulos coinciden con lo dicho."],
    pitfalls=["Textos con números o siglas se leen raro: escríbelos con letras.", "Frases sin puntuación suenan monótonas en espeak."],
    related=["character-dialogue", "3d-facial-animation", "animation-sound-design"]),

"character-dialogue": dict(
    title="Diálogos de personajes",
    description="Escribe y escenifica diálogos: turnos de palabra, voces distintas, reacciones de quien escucha, subtítulos y ritmo de escena. Úsala para 'conversación', 'que hablen entre ellos', 'diálogo', 'entrevista animada'.",
    intro="Cada línea de `dialogue` genera su voz, se coloca secuencialmente con 0.3 s de pausa y la escena se alarga automáticamente para que quepa. El personaje que habla pasa a `talk` si estaba en `idle`; quien escucha conserva su acción (usa `think` o emociones para reaccionar).",
    when=["Conversaciones entre 2+ personajes.", "Videos explicativos con presentador."],
    principles=["Líneas cortas y con subtexto; una idea por línea.", "Alternar plano/encuadre o posición cada 2–3 líneas.",
                "El oyente reacciona (asiente, sorpresa) — no estatua.", "Voz = personaje: tono agudo para frutas pequeñas, grave para monstruos."],
    steps=["Escribe el intercambio (o usa `--ai`).", "Coloca a los personajes enfrentados (`facing` 1 y -1).", "Añade reacciones con `emotions` en quien escucha.",
           "Edita textos en la interfaz (Ver guion) y renderiza."],
    commands="""python -m studio plan "Una naranja y un limón discuten quién es más ácido" -o dialogo.json
python -m studio render dialogo.json""",
    spec="""{"actors": [{"character": "naranja", "action": "idle", "emotion": "happy", "from": [0.3, 0.82], "facing": 1},
            {"character": "limon", "action": "idle", "emotion": "angry", "from": [0.7, 0.82], "facing": -1}],
 "dialogue": [{"character": "naranja", "text": "¡Yo soy la más dulce del frutero!"},
              {"character": "limon", "text": "Pero yo soy el más fuerte."}]}""",
    example="""Entrevista: presentador `persona` y entrevistado `robot`, 3 escenas con 2 líneas cada una, subtítulos grandes para Shorts (`--format 9:16`).""",
    tools=[("TTS espeak-ng (voces por tipo)", "voces locales", OK), ("Claude (opcional)", "diálogos creativos", KEY), ("ElevenLabs", "voces actorales", KEY)],
    qc=["Ninguna línea queda cortada al final de escena.", "Turnos claros (subtítulo con nombre).", "Volumen de voces homogéneo."],
    pitfalls=["Más de 4 líneas por escena saturan: divide en escenas.", "Dos voces iguales: el estudio varía el tono por id; para más contraste define `voice`."],
    related=["character-lip-sync", "animation-scripting", "story-animation"]),

"character-dancing": dict(
    title="Personajes que bailan",
    description="Coreografías de baile sincronizadas con el tempo de la música: rebote en el pulso, brazos alternos, balanceo, saltos, confeti y focos. Úsala para 'que baile', 'baile', 'fiesta', 'coreografía', 'TikTok dance'.",
    intro="La acción `dance` sincroniza el rebote con el BPM de la música del proyecto (dance = 124 BPM): el cuerpo cae en cada pulso con squash, los brazos alternan arriba/abajo cada compás y la mirada sigue el movimiento. El planificador crea escenas en `stage` con confeti y música `dance`.",
    when=["Baile, fiesta, celebración musical.", "Contenido para TikTok/Reels."],
    principles=["El impacto del movimiento cae en el beat.", "Variación cada 2–4 compases (dance → jump → celebrate).",
                "Formación: grupo en línea con el protagonista al centro.", "Luces de colores y confeti refuerzan la energía."],
    steps=["Pide baile: `make \"… baila …\"`.", "Ajusta `mood` (dance, happy, cute) o `bpm` en el JSON de música.",
           "Alterna acciones por personaje para que no bailen idéntico.", "Exporta vertical para redes."],
    commands="""python -m studio make "Crea una animación para TikTok de un plátano que baila" --format 9:16
python -m studio make "Las frutas hacen una fiesta de baile" --mood dance""",
    example="""TikTok de plátano bailando: 9:16, 3 escenas en escenario (dance+confeti, dance/jump, celebrate), subtítulos grandes amarillos y música dance 124 BPM.""",
    tools=[("Motor 2D (dance sincronizado)", "baile procedural", ENG), ("Blender (dance 3D)", "baile 3D", OK), ("Mixamo dances", "mocap de baile para humanoides", NET)],
    qc=["Los rebotes coinciden con el bombo.", "Nadie se sale de cuadro en 9:16.", "Confeti no tapa caras."],
    pitfalls=["Cambiar el mood sin cambiar bpm descoordina: el baile toma el BPM del mood.", "Muchos bailarines en 9:16: máximo 3."],
    related=["music-video-animation", "tiktok-animation", "character-animation"]),

"character-fighting": dict(
    title="Peleas y acción",
    description="Escenas de pelea: guardia, golpes alternos, patadas, impactos con temblor de cámara, auras de energía, líneas de velocidad y explosiones, con efectos de sonido. Úsala para 'pelea', 'batalla', 'combate', 'lucha', 'escena de acción'.",
    intro="Acciones `punch` (golpes alternos con anticipación y retroceso) y `kick`, emoción `angry` por defecto, y plantillas del planificador: enfrentamiento en el dojo → intercambio con speedlines y aura → explosión final y celebración del ganador. Audio: golpes sincronizados cada 0.7 s.",
    when=["Peleas, duelos, artes marciales, superhéroes.", "Contenido de acción para niños (sin violencia gráfica)."],
    principles=["Claridad: un golpe = anticipación, impacto, recuperación.", "Eje de acción horizontal, rivales enfrentados.",
                "Impacto: shake + flash + sonido en el mismo frame.", "Mantenerlo apto para todo público: sin sangre."],
    steps=["Define rivales y escenario (`dojo`, `city`, `space`).", "Plan: `make \"X y Y pelean …\"`.", "Ajusta `energy` con `on` en el personaje con poder, `explosion` con `start`.",
           "Render y revisa que los golpes se lean."],
    commands="""python -m studio make "Un perro y un gato pelean en el dojo con explosiones" --style anime
python -m studio make "Un robot pelea contra un monstruo en la ciudad de noche" --style cinematic""",
    spec="""{"camera": {"type": "shake"}, "effects": [{"type": "speedlines", "intensity": 0.6}, {"type": "energy", "on": "perro"},
  {"type": "explosion", "x": 0.5, "y": 0.62, "start": 1.2}],
 "actors": [{"character": "perro", "action": "punch", "from": [0.35, 0.82], "to": [0.42, 0.82], "facing": 1},
            {"character": "gato", "action": "kick", "from": [0.66, 0.82], "to": [0.6, 0.82], "facing": -1}]}""",
    example="""Duelo anime: 3 escenas (tensión, intercambio, explosión), música `action` 140 BPM, golpes con SFX sintetizados.""",
    tools=[("Motor 2D (punch/kick)", "coreografía", ENG), ("Efectos energy/explosion/speedlines", "impacto", ENG), ("Blender (punch/kick 3D)", "pelea 3D", OK)],
    qc=["Los personajes miran al rival.", "Cada impacto tiene sonido.", "Apto para todas las edades."],
    pitfalls=["Rivales demasiado separados: los golpes no 'llegan' (dist ≤ 0.3).", "Shake permanente cansa: úsalo solo en la escena de impacto."],
    related=["energy-effects", "explosions", "anime-animation", "cinematic-effects"]),

"character-emotions": dict(
    title="Arcos emocionales de personajes",
    description="Diseña el viaje emocional del personaje a lo largo de la historia (de triste a feliz, de miedo a valentía) combinando expresión, postura, ritmo, color, música y cámara. Úsala para 'que exprese emociones', 'emotivo', 'que pase de triste a feliz', 'escena conmovedora'.",
    intro="Mientras `character-expressions` controla la cara, esta Skill orquesta la emoción completa: acción corporal (sad → idle lento; joy → celebrate), música (`sad`, `calm`, `happy`), hora del día (sunset para nostalgia), cámara (dolly_in en el momento clave) y efectos (hearts, sparkles, rain).",
    when=["Historias con giro emocional.", "Videos de mensajes (cumpleaños, ánimo, despedida)."],
    principles=["Mostrar, no decir: la emoción en la acción antes que en el diálogo.", "Contraste: la alegría pega más tras la tristeza.",
                "Color y luz acompañan: fríos/oscuros → cálidos/brillantes.", "Música cambia con la emoción dominante."],
    steps=["Escribe el arco en 3 estados (inicio → giro → final).", "Asigna emoción + acción + entorno a cada escena.",
           "Usa `emotions` dentro de una escena para el giro.", "Elige `mood` de música acorde (o por escena con proyectos separados unidos con `concat`)."],
    commands="""python -m studio make "Un pingüino triste en la nieve encuentra un amigo y se pone feliz" --quality preview""",
    spec="""{"scenes": [
 {"background": "snow", "time_of_day": "sunset", "effects": [{"type": "snow"}], "actors": [{"character": "pinguino", "action": "idle", "emotion": "sad"}]},
 {"background": "snow", "camera": {"type": "dolly_in"}, "actors": [{"character": "pinguino", "action": "idle", "emotion": "surprised",
   "emotions": [{"t": 1.5, "emotion": "happy"}]}]},
 {"background": "snow", "effects": [{"type": "hearts"}], "actors": [{"character": "pinguino", "action": "celebrate", "emotion": "joy"}]}]}""",
    example="""Mensaje de ánimo: personaje triste bajo la lluvia → aparece el sol (escena 2 sin lluvia, sunset) → celebra con corazones; música `calm`.""",
    tools=[("Motor 2D", "emoción + acción + entorno", ENG), ("Música procedural por mood", "acompañamiento", ENG)],
    qc=["El cambio emocional es claro en el storyboard.", "La música no contradice la emoción.", "Ritmo más lento en momentos tristes."],
    pitfalls=["Cambios emocionales sin causa visible confunden.", "Música alegre en escena triste."],
    related=["character-expressions", "animated-storytelling", "animation-sound-design"]),

"character-transformations": dict(
    title="Transformaciones de personajes",
    description="Transforma un personaje en otro (o cambia de forma) con anticipación, destello, partículas mágicas, escalado elástico y sonido de transformación. Úsala para 'se transforma en', 'se convierte en', 'metamorfosis', 'cambio de forma', 'transformación mágica'.",
    intro="Un actor con `transform_to: <especie>` y `transform_at: <segundos>` cambia de ficha en ese instante: el render escala el personaje (+25 % elástico) durante ±0.3 s, añade un destello blanco difuminado y el audio inserta el arpegio `transform`. Combínalo con `magic`/`sparkles` anclados al personaje.",
    when=["Magia, superhéroes, evoluciones, gags de cambio.", "Revelaciones (de oruga a mariposa conceptual)."],
    principles=["Anticipación: concentrar energía 0.5–1 s antes.", "Ocultar el cambio en el pico del destello.",
                "Mantener el nombre y la posición para continuidad.", "Celebración o reacción después."],
    steps=["Elige personaje origen y especie destino.", "Añade `transform_to` y `transform_at` al actor.", "Añade efecto `magic` con `on` = id del actor.",
           "Render y verifica el destello en el instante correcto."],
    commands="""python -m studio make "Un mago se transforma en estrella con magia" --style fantasy""",
    spec="""{"actors": [{"character": "mago", "action": "wave", "emotion": "excited", "from": [0.5, 0.82],
  "transform_to": "estrella", "transform_at": 2.0}],
 "effects": [{"type": "magic", "on": "mago"}, {"type": "sparkles", "on": "mago", "start": 1.0}]}""",
    example="""«Que la rana se convierta en príncipe»: `transform_to: "persona"` + accesorio corona en la nueva ficha (editar `make_character('persona', accessory='crown')`).""",
    tools=[("Motor 2D (transform_to)", "cambio de ficha + destello", ENG), ("Blender shape keys / Geometry Nodes", "morph 3D", OK)],
    qc=["El destello cubre el cambio.", "Sonido coincide con el destello.", "El personaje transformado conserva la posición."],
    pitfalls=["Transformar en el primer segundo: no da tiempo a reconocer al personaje original.", "Olvidar el efecto mágico: el cambio parece un corte."],
    related=["magic-effects", "fantasy-animation", "particle-effects"]),

"mascot-animation": dict(
    title="Animación de mascotas de marca",
    description="Crea y anima mascotas para marcas, canales o negocios: diseño memorable, saludo, logo animado, intro/outro, stickers Lottie y versión 3D. Úsala para 'mascota', 'personaje para mi marca', 'intro de canal con mascota', 'stickers animados'.",
    intro="Combina `character-design` (ficha con colores de marca), `animated-logos`, `lottie-animation` (stickers) y `3d-modeling`. Entregable típico: hoja de personaje, intro de 4–6 s (saludo + logo), outro (celebrate + 'suscríbete'), Lottie JSON y GLB.",
    when=["Branding con personaje.", "Intro/outro de YouTube o Twitch.", "Stickers para WhatsApp/Telegram."],
    principles=["Colores de marca en la ficha (HEX exacto).", "Pose firma (wave o celebrate) siempre igual.",
                "Duración de intro ≤ 5 s.", "Versiones: horizontal, vertical, cuadrada y transparente."],
    steps=["Ficha: `python -m studio character mascota --name <Marca> --color <HEX> --accessory cap`.",
           "Intro: `plan \"una mascota saluda feliz\" --background studio --duration 5 -o intro.json`, sustituye la ficha del reparto por la de tu mascota (mismo `id` en actores) y `render intro.json`.",
           "Logo: `python -m studio logo \"<Marca>\" --color <HEX> --tagline …`.", "Sticker Lottie: `python -m studio lottie --color <HEX>`.",
           "3D: `python -m studio character3d mascota --color <HEX>`."],
    commands="""python -m studio character mascota --name "Pixi" --color "#00b4d8" --accessory cap --style cute
python -m studio plan "una mascota saluda feliz y celebra" --background studio --duration 5 --style cute -o intro.json
# editar intro.json: characters[0] = ficha de Pixi (pixi_hoja.json)
python -m studio render intro.json
python -m studio logo "Pixi Studio" --color "#00b4d8" --tagline "Animación con IA"
python -m studio lottie --color "#00b4d8" -o pixi_sticker.json""",
    example="""Kit de mascota completo en una carpeta: hoja PNG/JSON, intro MP4, logo MP4, sticker Lottie y GLB 3D.""",
    tools=[("Motor 2D/3D", "mascota", ENG), ("Lottie generator", "stickers vectoriales", ENG), ("LottieFiles", "previsualizar/publicar Lottie", NET)],
    qc=["Colores exactos de marca.", "Lottie abre en lottie-web.", "Intro ≤ 5 s y con sonido corto."],
    pitfalls=["Mascotas con demasiados detalles no escalan a sticker.", "Usar personajes o marcas registradas de terceros (prohibido): crea diseños originales."],
    related=["character-design", "animated-logos", "lottie-animation", "youtube-animation"]),
}
