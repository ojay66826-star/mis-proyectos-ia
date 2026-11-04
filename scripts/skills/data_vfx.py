OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
EXT = "💻 programa externo recomendado"

FX_FIELDS = "Campos comunes de un efecto: `type`, `x`/`y` (0–1) o `on: <id_personaje>`, `start`, `end`, `intensity`, `scale`, `color` [r,g,b], `seed`."

SKILLS = {
"visual-effects": dict(
    title="Efectos visuales (VFX) — visión general",
    description="Selecciona, combina y ajusta efectos visuales para animaciones: partículas, clima, magia, energía, explosiones, niebla, bloom y grading. Úsala cuando la petición pida 'efectos', 'VFX', 'que se vea espectacular', o no esté claro qué efecto concreto usar.",
    intro=f"El sistema de efectos (`studio/effects.py`) dibuja partículas **deterministas**: cada partícula se calcula analíticamente por su semilla y edad, por lo que cualquier frame se puede renderizar aislado (render paralelo, bucles perfectos). Hay 19 efectos con capa de brillo (bloom) automática. {FX_FIELDS}",
    when=["Dar espectacularidad a una escena.", "Elegir combinación de efectos coherente con el estilo y la historia."],
    principles=["Los efectos sirven a la historia: cada uno debe tener motivo (clima, poder, emoción).", "Jerarquía: un efecto protagonista + uno ambiental como máximo.",
                "Coherencia de luz: efectos brillantes en escenas oscuras lucen más.", "Sonido para cada efecto (automático en el estudio)."],
    steps=["Identifica la intención: ambiente (rain, snow, fog, fireflies, leaves, bubbles), poder (magic, energy, energy_beam, lightning), impacto (explosion, water_splash, speedlines), celebración (confetti, sparkles, hearts).",
           "Añade los efectos en `effects` de la escena (o en la interfaz, paso 5).", "Ancla al personaje con `on` cuando el efecto sale de él.",
           "Controla tiempos con `start`/`end` e intensidad con `intensity` (0.5–1.5).", "Revisa frames clave y el sonido."],
    commands="""python -m studio make "Un mago lanza magia bajo la lluvia con rayos" --style fantasy
python -c "from studio.effects import EFFECTS; print(EFFECTS)\"""",
    spec="""{"effects": [{"type": "rain", "intensity": 0.8}, {"type": "lightning", "period": 2.2},
  {"type": "magic", "on": "mago", "start": 1.0, "color": [186, 104, 255]}]}""",
    example="""Escena épica: `fog` (ambiente) + `energy` en el héroe (protagonista) + `lightning` cada 2 s; estilo `cinematic` añade grading y viñeta.""",
    tools=[("effects.py", "19 efectos con bloom", ENG), ("Blender (partículas, Mantaflow)", "fuego/humo/agua simulados 3D", OK), ("ActionVFX / ProductionCrate", "stock VFX (licencias)", NET)],
    qc=["Ningún efecto tapa la cara del protagonista.", "Efectos sincronizados con su sonido.", "Rendimiento: ≤ 3 efectos por escena."],
    pitfalls=["Lluvia + nieve + niebla + confeti = ruido visual.", "Efectos con `on` a un personaje que no está en la escena se descartan (normalize)."],
    related=["particle-effects", "cinematic-effects", "magic-effects", "animation-sound-design"]),

"particle-effects": dict(
    title="Sistemas de partículas",
    description="Diseña sistemas de partículas personalizados (emisión, vida, velocidad, gravedad, color por edad, tamaño, alfa, rotación, bloom) en 2D determinista, en Three.js o en Blender. Úsala para 'partículas', 'chispas', 'polvo', 'confeti', 'brillitos', 'crear un efecto nuevo'.",
    intro="Patrón del estudio: para la partícula i, `r = rng(seed+i)`; `life = r.uniform(a,b)`; `age = (t + r.uniform(0,life)) % life`; `k = age/life`. Posición, tamaño, color y alfa son funciones de k → sin estado, reproducible y en bucle. Para crear un efecto nuevo añade una rama `elif kind == ...` en `draw_effect`.",
    when=["Crear un efecto que no existe.", "Ajustar densidad, color o física de uno existente."],
    principles=["Variación aleatoria acotada (tamaño ±40 %, vida ±30 %).", "Color por edad (caliente→frío, opaco→transparente).",
                "Más partículas pequeñas > pocas grandes.", "Bloom solo en partículas emisivas."],
    steps=["Copia la rama de un efecto similar en `studio/effects.py`.", "Define emisor (punto, línea, área, personaje).", "Define trayectoria analítica (lineal, parabólica con gravedad, espiral).",
           "Registra el nombre en `EFFECTS` (y en `GLOWY` si brilla) y su sonido en `audio.EFFECT_SFX`.", "Prueba con un render corto en preview."],
    commands="""python - <<'PY'
from PIL import Image
from studio.effects import render_effects
im = Image.new('RGBA', (640, 360), (20, 20, 40, 255))
im.alpha_composite(render_effects((640, 360), [{"type": "fireflies"}, {"type": "sparkles", "x": 0.5, "y": 0.6}], t=1.0))
im.save('particulas.png')
PY""",
    example="""Efecto 'polvo mágico dorado': partir de `sparkles`, cambiar trayectoria a espiral (`ang += lt*3`), color base (255,215,64), registrar como `golden_dust`.""",
    tools=[("effects.py", "partículas deterministas", ENG), ("Three.js Points", "partículas web", OK), ("Blender Particle System", "partículas 3D", OK)],
    qc=["El efecto se ve igual en render paralelo.", "Bucle sin saltos (usa periodos que dividan la duración).", "Sin partículas congeladas."],
    pitfalls=["Usar `random` sin semilla rompe el determinismo.", "Demasiadas partículas con blur grande ralentizan."],
    related=["visual-effects", "fire-animation", "magic-effects"]),

"fire-animation": dict(
    title="Animación de fuego",
    description="Fuego animado: llamas ascendentes con color por temperatura (amarillo→naranja→rojo), parpadeo, brillo y crepitar sonoro; hogueras, antorchas, volcanes, personajes en llamas. Úsala para 'fuego', 'llamas', 'hoguera', 'incendio', 'antorcha'.",
    intro="El efecto `fire` emite 70 partículas por intensidad desde una base de ancho `width` (60 px por defecto a 720p), que suben 120–220 px, se estrechan, cambian de color por edad y llevan glow. El audio añade crepitar en bucle.",
    when=["Fuego en escena, poderes de fuego, ambiente cálido nocturno."],
    principles=["Forma de lágrima: base ancha, punta estrecha.", "Movimiento turbulento (oscilación lateral) y rápido (vida 0.5–1 s).",
                "Ilumina el entorno: escena nocturna o atardecer.", "Humo encima para realismo (`smoke` desplazado arriba)."],
    steps=["Coloca la base con `x`,`y` (suelo ≈ 0.82).", "Ajusta `intensity` (altura) y `width`.", "Combina con `smoke` (y más alto) y escena `night`.", "Render y revisa el bloom."],
    commands="""python -m studio make "Unos amigos cuentan historias junto al fuego en el bosque de noche" --quality preview""",
    spec="""{"time_of_day": "night", "effects": [{"type": "fire", "x": 0.5, "y": 0.84, "intensity": 1.2, "width": 50},
  {"type": "smoke", "x": 0.5, "y": 0.62, "intensity": 0.5}, {"type": "fireflies"}]}""",
    example="""Personaje con poder de fuego: `{"type":"fire","on":"dragon","intensity":0.8}` sigue al personaje.""",
    tools=[("effects.py fire", "fuego 2D", ENG), ("Blender Mantaflow", "fuego volumétrico 3D", OK), ("EmberGen", "simulación en tiempo real", EXT)],
    qc=["Colores cálidos sin saturar a blanco.", "Crepitar audible y no molesto.", "Base del fuego apoyada."],
    pitfalls=["Fuego de día pierde impacto.", "Intensidad > 2 cubre la escena."],
    related=["smoke-animation", "particle-effects", "animation-lighting"]),

"smoke-animation": dict(
    title="Animación de humo y vapor",
    description="Humo, vapor, polvo y nubes de impacto: partículas grandes que ascienden, se expanden y se desvanecen con deriva lateral. Úsala para 'humo', 'vapor', 'polvo', 'nube de polvo', 'chimenea', 'niebla densa'.",
    intro="`smoke` usa 26 partículas grises de vida 2–3.5 s que suben 200–340 px expandiéndose de 20 a 100 px de radio y perdiendo alfa; `fog` crea bandas difuminadas horizontales para ambiente. La explosión encadena humo automáticamente tras 0.4 s.",
    when=["Chimeneas, tazas calientes, incendios, aterrizajes, explosiones, ambientes misteriosos."],
    principles=["Movimiento lento y orgánico.", "Mayor tamaño y transparencia con la edad.", "Color según fuente: gris (fuego), blanco (vapor), marrón (polvo)."],
    steps=["Elige `smoke` (columna) o `fog` (ambiente).", "Coloca la fuente; usa `intensity` 0.5–1.5.", "En terror combina `fog` + `horror`."],
    commands="""python -m studio make "Un fantasma aparece entre la niebla en el bosque embrujado" --style horror""",
    spec="""{"effects": [{"type": "smoke", "x": 0.3, "y": 0.8, "intensity": 0.8}, {"type": "fog", "intensity": 1.2}]}""",
    example="""Aterrizaje con polvo: `smoke` con `start` en el momento del contacto, `x` en los pies, intensidad 0.6, `end` a +1.5 s.""",
    tools=[("effects.py smoke/fog", "humo 2D", ENG), ("Blender Mantaflow (smoke)", "humo 3D", OK)],
    qc=["El humo no oscurece al protagonista.", "Movimiento continuo sin reinicios visibles."],
    pitfalls=["Humo opaco = mancha gris: mantener alfa bajo.", "Niebla intensa en 9:16 cubre todo."],
    related=["fire-animation", "explosions", "horror-animation"]),

"water-animation": dict(
    title="Animación de agua",
    description="Agua animada: lluvia con salpicaduras, olas con espuma, salpicaduras parabólicas con ondas, burbujas submarinas y rayos de luz bajo el agua. Úsala para 'agua', 'lluvia', 'mar', 'olas', 'chapuzón', 'bajo el agua', 'burbujas'.",
    intro="Efectos: `rain` (220 gotas inclinadas + salpicaduras en el suelo), `waves` (4 capas de olas sinusoidales con espuma), `water_splash` (gotas parabólicas con gravedad + anillo de onda), `bubbles` (burbujas con brillo). Escenario `underwater` y `beach` complementan.",
    when=["Clima lluvioso, playa, piscina, océano, peces/submarinos."],
    principles=["Gravedad real en salpicaduras (parábola).", "Paralaje en olas (capas a distinta velocidad).",
                "Lluvia inclinada indica viento; gotas rápidas y finas.", "Sonido continuo (rain/splash)."],
    steps=["Ambiente: `rain` o `waves`; acción: `water_splash` anclado.", "Bajo el agua: `background: underwater` + `bubbles`.", "Ajusta intensidad y periodo del splash (`period`)."],
    commands="""python -m studio make "Una rana salta al agua en el fondo del mar con burbujas" --quality preview""",
    spec="""{"background": "beach", "effects": [{"type": "waves"}, {"type": "water_splash", "x": 0.6, "y": 0.86, "period": 1.6}]}""",
    example="""Día de lluvia triste: `rain` intensidad 1.0, `time_of_day: sunset`, personaje `sad`; música `sad`; sonido de lluvia automático.""",
    tools=[("effects.py rain/waves/water_splash/bubbles", "agua 2D", ENG), ("Blender Ocean modifier / FLIP fluids", "agua 3D", OK)],
    qc=["Salpicaduras nacen del punto correcto.", "Olas no cubren a los personajes.", "Audio de lluvia sin clipping."],
    pitfalls=["Lluvia muy densa reduce legibilidad.", "Olas en escenario no costero."],
    related=["particle-effects", "visual-effects", "3d-environment-animation"]),

"magic-effects": dict(
    title="Efectos mágicos",
    description="Magia animada: estrellas de 8 puntas que orbitan y suben, aura brillante pulsante, destellos, polvo de hada, hechizos y transformaciones. Úsala para 'magia', 'hechizo', 'varita', 'hada', 'brillos mágicos', 'poderes mágicos'.",
    intro="`magic` dibuja estrellas que orbitan con rotación temporal y suben mientras aparecen/desaparecen (vida 0.6–1.4 s) más un aura elíptica pulsante; `sparkles` es la versión dorada sin órbita. Color configurable (`color`). Audio: arpegio de campanas.",
    when=["Fantasía, magos, hadas, transformaciones, momentos 'wow'."],
    principles=["Color simbólico: violeta misterio, dorado bondad, verde naturaleza, rojo peligro.", "La magia sale de una fuente (mano/varita/personaje).",
                "Crescendo: empieza sutil, culmina con destello.", "Combinar con estilo `fantasy` (bloom violeta-dorado)."],
    steps=["Ancla `magic` al personaje con `on`.", "Añade `sparkles` con `start` posterior para el clímax.", "Si hay transformación, usa `transform_to` (Skill character-transformations)."],
    commands="""python -m studio make "Haz una animación estilo anime de una niña con magia en un castillo" --style anime""",
    spec="""{"effects": [{"type": "magic", "on": "nina", "color": [255, 128, 220]}, {"type": "sparkles", "on": "nina", "start": 1.2, "intensity": 1.4}]}""",
    example="""Hada que ilumina el bosque: `fireflies` + `magic` verde (`color:[120,255,160]`) en el hada, escena `forest` de noche.""",
    tools=[("effects.py magic/sparkles", "magia 2D", ENG), ("Three.js / GSAP", "magia web interactiva", OK)],
    qc=["La fuente de la magia es clara.", "El color de la magia es coherente en toda la historia."],
    pitfalls=["Magia en cada escena pierde valor.", "Colores mágicos similares al fondo (castillo violeta + magia violeta)."],
    related=["fantasy-animation", "character-transformations", "particle-effects"]),

"lightning-effects": dict(
    title="Rayos y relámpagos",
    description="Rayos procedurales con desplazamiento de punto medio, ramificación, parpadeo, flash de pantalla y truenos sincronizados; también arcos eléctricos. Úsala para 'rayo', 'relámpago', 'tormenta eléctrica', 'electricidad', 'trueno'.",
    intro="`lightning` genera un rayo nuevo cada `period` s con el algoritmo de desplazamiento de punto medio (6 niveles), lo dibuja nítido + glow azulado, parpadea a 30 Hz durante 0.35 s y hace un flash blanco de 0.08 s. El audio pone un trueno en cada descarga.",
    when=["Tormentas, terror, superpoderes eléctricos, momentos dramáticos."],
    principles=["Flash corto y fuerte, luego oscuridad.", "Trueno con ligero retraso respecto al flash (realismo).",
                "Escena nocturna u oscura.", "Combinar con lluvia y temblor de cámara."],
    steps=["Añade `lightning` con `period` 1.8–3 s.", "Usa `on` para que el rayo caiga sobre un personaje.", "Cámara `shake` y estilo `horror` o `cinematic`."],
    commands="""python -m studio make "Un fantasma asusta a un niño en un bosque embrujado" --style horror""",
    spec="""{"time_of_day": "night", "camera": {"type": "shake"}, "effects": [{"type": "rain"}, {"type": "lightning", "period": 2.0}]}""",
    example="""Poder eléctrico del robot: `energy` en el robot (`color:[120,200,255]`) + `lightning` con `on: robot`.""",
    tools=[("effects.py lightning", "rayos procedurales", ENG), ("Blender (curvas + emisión)", "rayos 3D", OK)],
    qc=["No más de 3 flashes por segundo (seguridad para fotosensibles).", "Trueno audible tras cada rayo."],
    pitfalls=["Flashes muy frecuentes pueden afectar a personas fotosensibles: periodo ≥ 1.5 s.", "Rayos de día pierden contraste."],
    related=["energy-effects", "horror-animation", "cinematic-effects"]),

"explosions": dict(
    title="Explosiones",
    description="Explosiones estilizadas: flash, bola de fuego expansiva, onda de choque, escombros con gravedad y humo posterior, con sonido de boom y temblor. Úsala para 'explosión', 'explota', 'boom', 'bomba', 'impacto', 'estallido'.",
    intro="`explosion` dura `length` (1.6 s): flash de 0.08 s, 26 bolas de fuego que se expanden con easing cúbico y cambian de amarillo a naranja-rojo, anillo de onda de choque elíptico, 30 escombros parabólicos y humo encadenado. Audio: ruido filtrado + boom grave.",
    when=["Finales de pelea, gags cartoon, acción, reveal de título."],
    principles=["Anticipación (silencio o zoom) antes del boom.", "Temblor de cámara en el impacto.", "Humo residual para que no desaparezca de golpe.",
                "Apto para todo público: sin daño visible a personajes."],
    steps=["Añade `explosion` con `x`,`y` y `start`.", "Escena con `camera: shake` o `zoom_in`.", "Reacción de personajes (`scared_shake` o `surprised`)."],
    commands="""python -m studio make "Un perro y un gato pelean en el dojo con explosiones" --quality preview""",
    spec="""{"camera": {"type": "shake"}, "effects": [{"type": "explosion", "x": 0.5, "y": 0.6, "start": 0.4, "scale": 1.2}]}""",
    example="""Explosión cartoon de confeti: `explosion` con `intensity:0.6` + `confetti` con `start` 0.3 s después.""",
    tools=[("effects.py explosion", "explosión 2D", ENG), ("Blender Mantaflow", "explosión 3D", OK), ("JangaFX EmberGen", "VFX en tiempo real", EXT)],
    qc=["Flash no supera 2 frames.", "Boom sincronizado.", "Humo posterior visible."],
    pitfalls=["Explosión pegada al personaje sin reacción parece error.", "Varias explosiones simultáneas saturan."],
    related=["fire-animation", "smoke-animation", "character-fighting"]),

"energy-effects": dict(
    title="Efectos de energía y poder",
    description="Auras de poder pulsantes, chispas ascendentes, arcos eléctricos alrededor del personaje y rayos de energía (beams) estilo anime. Úsala para 'aura', 'poder', 'energía', 'super saiyajin', 'rayo de energía', 'kamehameha', 'superpoder'.",
    intro="`energy` (aura de 3 capas pulsando a 10 rad/s + chispas que suben + 2 arcos eléctricos por frame) y `energy_beam` (rayo horizontal que se extiende en 0.3 s con núcleo blanco y glow de color, dirección `dir`). Anclar con `on`.",
    when=["Superhéroes, peleas anime, power-ups, momentos de transformación."],
    principles=["Carga → disparo → impacto.", "Núcleo blanco + borde de color = sensación de intensidad.",
                "Aura sincronizada con la respiración/tensión del personaje.", "Sonido zumbido (energy) + whoosh."],
    steps=["Carga: `energy` con `on: héroe` durante 1–2 s.", "Disparo: `energy_beam` con `start` y `dir` (1 derecha, -1 izquierda).", "Impacto: `explosion` en el rival."],
    commands="""python -m studio make "Un robot carga energía y dispara un rayo contra un monstruo" --style anime""",
    spec="""{"effects": [{"type": "energy", "on": "robot", "end": 1.8, "color": [79, 195, 247]},
  {"type": "energy_beam", "on": "robot", "start": 1.8, "dir": 1}, {"type": "explosion", "x": 0.8, "y": 0.62, "start": 2.1}]}""",
    example="""Power-up de la fresa: aura rosa (`color:[255,64,129]`) + `sparkles` + cambio de emoción a `excited`.""",
    tools=[("effects.py energy/energy_beam", "poderes 2D", ENG), ("Blender (emisión + bloom EEVEE)", "auras 3D", OK)],
    qc=["El beam sale del personaje y en la dirección correcta.", "Aura no oculta la cara."],
    pitfalls=["`dir` incorrecto dispara hacia atrás.", "Beam permanente: limita con `end`."],
    related=["character-fighting", "anime-animation", "lightning-effects"]),

"cinematic-effects": dict(
    title="Efectos cinematográficos",
    description="Look de cine: bandas negras (letterbox 2.39:1), gradación teal & orange, viñeta, grano de película, bloom, profundidad de campo, temblor de cámara, transiciones a negro y títulos. Úsala para 'cinematográfico', 'look de película', 'épico', 'tráiler'.",
    intro="El estilo `cinematic` aplica post-procesado por frame (numpy): grading teal en sombras y naranja en altas luces, contraste +10 %, viñeta, grano animado y letterbox; `letterbox: true/false` se puede forzar en el proyecto. Combínalo con cámara dolly/orbit, transición `dip` y música `epic`.",
    when=["Tráileres, intros épicas, escenas dramáticas, cortos con ambición visual."],
    principles=["Grading consistente en todo el video.", "Movimiento de cámara lento y motivado.", "Silencio antes del clímax.",
                "Títulos sobrios, centrados, con fundido."],
    steps=["Planifica con `--style cinematic` y `--transition dip`.", "Usa cámaras `dolly_in`/`pan`; evita `shake` salvo impactos.",
           "Música `epic`; al final título con `python -m studio logo` o `text --mode typewriter`.", "Exporta en `fullhd`."],
    commands="""python -m studio make "Crea una animación cinematográfica de un robot en la ciudad de noche" --style cinematic --transition dip --quality fullhd""",
    spec="""{"style": "cinematic", "letterbox": true, "transition": "dip", "mood": "epic"}""",
    example="""Tráiler de 20 s: 4 escenas (ciudad noche dolly_in, pelea shake, explosión, título final) + música épica + grading cine.""",
    tools=[("styles.post_process cinematic", "grading + grano + letterbox", ENG), ("DaVinci Resolve (gratis)", "grading profesional", EXT), ("LUTs .cube + FFmpeg lut3d", "grading con LUT", OK)],
    qc=["Negros no aplastados (detalle en sombras).", "Letterbox simétrico.", "Grano sutil (no ruido)."],
    pitfalls=["Letterbox en 9:16 resta espacio: el estudio usa barras finas en vertical.", "Grading exagerado da piel/colores irreales."],
    related=["cinematic-video", "animation-lighting", "3d-camera-animation"]),
}
