OK = "✅ instalado y probado"
ENG = "✅ motor propio del estudio"
KEY = "🔑 requiere clave API"
NET = "🌐 gratis, requiere internet"
EXT = "💻 programa externo recomendado"

BLENDER_NOTE = "Blender 4.0.2 (headless) con EEVEE por software; Cycles sin denoiser en la build de Ubuntu"

SKILLS = {
"3d-animation": dict(
    title="Animación 3D",
    description="Produce animaciones 3D completas con Blender en modo headless: personajes procedurales, escenario, iluminación de tres puntos, cámara animada, lip-sync, render EEVEE/Cycles y montaje con audio. Úsala para 'animación 3D', 'en 3D', 'tridimensional', 'render 3D'.",
    intro=f"El estudio traduce el mismo `project.json` del 2D a una escena de Blender (`studio/blender/scene3d.py`): construye personajes con primitivas suavizadas y materiales PBR, anima con keyframes por frame, coloca luces key/fill/rim y cámara con Track-To, renderiza PNG por escena y los monta con FFmpeg + audio del estudio. {BLENDER_NOTE}.",
    when=["La petición menciona 3D, Blender, render 3D o 'personaje 3D'.", "Se necesita un modelo reutilizable (GLB) además del video."],
    principles=["Iluminación de tres puntos: key cálida, fill suave opuesta, rim fría para separar del fondo.",
                "Cámara a altura de ojos del personaje (0.8–1.1 m) con lente 35 mm para cercanía.",
                "Materiales con roughness 0.3–0.5 para look 'juguete'/estilizado.",
                "Mantener polígonos bajos y subdivisión suave para renders rápidos."],
    steps=["Planifica igual que en 2D (`plan`) y añade `\"engine\": \"3d\"` o usa `--3d`.",
           "Elige motor: `rapido` (Workbench, previsualizar), `eevee` (calidad, por defecto), `cycles` (fotorrealista, lento).",
           "Haz primero `--quality preview` (640×360) para validar cámara y acciones.",
           "Render final en `hd`. Se generan `final.mp4`, `personaje.glb` y `escena_N.blend` editable.",
           "Abre el `.blend` en Blender de escritorio para retoques manuales si el usuario lo desea."],
    commands="""python -m studio make "Crea un personaje 3D: un gato que baila en el escenario" --3d --quality preview
python -m studio make "Un robot camina por la ciudad" --3d --engine eevee --quality hd
blender projects/<…>/frames3d/escena_1.blend          # abrir para edición manual""",
    spec="""{"engine": "3d", "render_engine": "eevee", "samples": 8, "save_blend": true,
 "scenes": [{"background": "stage", "time_of_day": "night", "duration": 5, "camera": {"type": "orbit"},
   "actors": [{"character": "gato", "action": "dance", "emotion": "joy", "from": [0.5, 0.82]}]}]}""",
    example="""«Crea un personaje 3D que baile»: `python -m studio make "Un gato baila en el escenario" --3d` →
render EEVEE con focos de colores, cámara orbital, música dance, GLB exportado y QC aprobado (~4 min en CPU para 6 s a 640×360).""",
    tools=[("Blender 4.0 (bpy)", "modelado/rig/render", OK), ("EEVEE", "render rápido de calidad", OK), ("Cycles", "path tracing", OK),
           ("FFmpeg", "montaje", OK), ("Mixamo", "animaciones humanoides para personajes riggeados", NET)],
    qc=["Personaje apoyado en el suelo, sin intersecciones con el piso.", "Sin frames negros (EGL/GPU).", "Iluminación sin quemados (AgX).", "GLB abre en el visor Three.js."],
    pitfalls=["En servidores sin GPU EEVEE usa software (lento): usa `preview` para iterar.",
              "Cycles sin denoiser produce ruido: sube `samples` a 128+ o instala Blender oficial con OIDN.",
              "Blender usa su propio Python: numpy debe estar instalado para el exportador glTF (python3-numpy)."],
    related=["blender-animation", "3d-character-animation", "3d-camera-animation", "animation-lighting", "animation-rendering"]),

"3d-character-animation": dict(
    title="Animación de personajes 3D",
    description="Anima personajes 3D (caminar, correr, bailar, saltar, saludar, golpear, flotar) con jerarquías de pivotes, squash & stretch volumétrico, parpadeo y boca sincronizada. Úsala para 'personaje 3D que camina/baila/habla'.",
    intro="Cada personaje 3D tiene un empty raíz (posición/rumbo), un empty de cuerpo (bote, squash, inclinación) y pivotes de hombro/cadera para las extremidades. `animate()` en scene3d.py escribe keyframes por frame para que el resultado sea idéntico al motor 2D.",
    when=["Acciones de personaje en 3D.", "Exportar personaje animado a GLB para web/juegos."],
    principles=["Conservar volumen en el squash: escala XY = √s y Z = 1/s.",
                "Rumbo hacia la dirección de marcha (root rotación Z).",
                "Contrapeso: inclinación del cuerpo hacia delante al correr (≈10°).",
                "Parpadeo cada ~3 s y movimiento de boca por visemas."],
    steps=["Define acciones en el JSON (mismas que en 2D).",
           "Para un personaje aislado: `python -m studio character3d <especie> --action dance`.",
           "Revisa el turntable y el GLB (`templates/web/three-scene.html?glb=/projects/.../x.glb`).",
           "Para rigs humanoides reales, importa el GLB en Blender, añade Rigify o sube a Mixamo."],
    commands="""python -m studio character3d gato --action dance --duration 4 --engine eevee
python -m studio character3d robot --action walk --engine rapido -o projects/robot3d""",
    example="""«Haz un perro 3D que salude»: `python -m studio character3d perro --action wave --duration 3` → `perro_3d.mp4` (órbita de cámara) + `perro.glb` con la animación embebida.""",
    tools=[("Blender bpy", "keyframes procedurales", OK), ("glTF 2.0 exporter", "GLB animado", OK), ("Rigify", "rig humanoide avanzado", OK), ("Mixamo", "auto-rig + mocap", NET)],
    qc=["Sin deslizamiento de pies al caminar.", "Brazos no atraviesan el cuerpo.", "La animación del GLB se reproduce en Three.js."],
    pitfalls=["Rotaciones Euler grandes en Y pueden voltear brazos: limitar a ±2.8 rad.", "Escalar el cuerpo con squash afecta a hijos (ojos): es intencional."],
    related=["3d-rigging", "3d-walk-cycles", "3d-facial-animation", "character-animation"]),

"3d-modeling": dict(
    title="Modelado 3D",
    description="Modela personajes, props y escenarios 3D estilizados de forma procedural con Blender (primitivas, modificadores Bevel/Subdivision/SimpleDeform, materiales PBR) y exporta GLB/FBX/OBJ. Úsala para 'modela', 'crea un modelo 3D', 'objeto 3D', 'asset para juego'.",
    intro="El constructor `build_character()` modela 27 tipos de personaje con primitivas suavizadas (esferas UV de 48 segmentos, cilindros, conos), modificadores (Bevel para robots, SimpleDeform Bend para plátano) y materiales Principled BSDF con subsurface. El mismo patrón sirve para props y escenarios.",
    when=["Crear un modelo 3D nuevo o un asset.", "Exportar personajes del estudio a otros programas."],
    principles=["Formas primarias primero (silueta), secundarias después (orejas, hojas), terciarias al final (brillos, mejillas).",
                "Topología ligera y shading suave; usar modificadores no destructivos.",
                "Escala real: personaje ≈1 m de alto, origen en los pies.",
                "Materiales con nombre descriptivo para editarlos luego."],
    steps=["Para personajes del catálogo: `python -m studio character3d <especie>` → GLB.",
           "Para un modelo nuevo, crea una función en un script bpy siguiendo `build_character` (obj_add + mat).",
           "Ejecuta: `blender -b --factory-startup -P mi_modelo.py`.",
           "Exporta: `bpy.ops.export_scene.gltf(filepath='x.glb', export_format='GLB')` o FBX/OBJ.",
           "Verifica en el visor Three.js."],
    commands="""python -m studio character3d aguacate --action idle --duration 1 -o projects/aguacate3d
blender -b --factory-startup --python-expr "import bpy; bpy.ops.mesh.primitive_monkey_add(); bpy.ops.export_scene.gltf(filepath='mono.glb')"
""",
    example="""«Modela una piña 3D para mi juego»: `python -m studio character3d pina --action idle -o projects/pina` → `pina.glb` listo para Godot/Unity/Three.js.""",
    tools=[("Blender 4.0", "modelado procedural", OK), ("glTF/GLB", "intercambio web y juegos", OK), ("Meshy / Tripo / Rodin (texto→3D)", "modelos 3D con IA", KEY),
           ("Hunyuan3D / TripoSR (open source, GPU)", "imagen→3D local", EXT)],
    qc=["Normales correctas (sin caras negras).", "Origen en la base del modelo.", "Archivo GLB < 10 MB."],
    pitfalls=["Aplicar escala antes de exportar (Ctrl+A) si se edita a mano.", "Draco no disponible en la build de Ubuntu: exporta sin compresión."],
    related=["3d-rigging", "blender-animation", "threejs-animation"]),

"3d-rigging": dict(
    title="Rigging 3D",
    description="Prepara personajes 3D para animación: jerarquías de pivotes, armaduras (Armature), pesos automáticos, controles IK/FK y shape keys faciales en Blender. Úsala para 'rig', 'esqueleto', 'huesos', 'preparar para animar', 'skinning'.",
    intro="El estudio usa rigs de pivotes (empties) para personajes estilizados — robustos y rápidos — y documenta cómo pasar a Armature con pesos automáticos o Rigify cuando se necesita deformación orgánica.",
    when=["El modelo debe deformarse (codos, rodillas, cara).", "Se van a usar animaciones de Mixamo o mocap."],
    principles=["Nombres consistentes con sufijos .L/.R para simetría.", "Huesos de control separados de huesos de deformación.",
                "IK en piernas para pies fijos; FK en brazos para arcos naturales.", "Shape keys para visemas (A, E, O, U, M, F)."],
    steps=["Rig de pivotes (rápido): cada extremidad hija de un empty en la articulación (ver `build_character`).",
           "Armature: añade huesos, `Ctrl+P → With Automatic Weights`, prueba poses extremas.",
           "Rigify: añade metarig humano, ajusta, `Generate Rig`.",
           "Facial: crea shape keys por visema y conéctalas a la pista de lip-sync.",
           "Exporta GLB con `export_animations=True` y verifica."],
    commands="""blender -b --factory-startup --python-expr "
import bpy
bpy.ops.object.armature_add(location=(0,0,0))
arm = bpy.context.object; bpy.ops.object.mode_set(mode='EDIT')
b = arm.data.edit_bones[0]; b.name='cuerpo'; b.tail=(0,0,0.6)
bpy.ops.object.mode_set(mode='OBJECT'); bpy.ops.wm.save_as_mainfile(filepath='rig_base.blend')\"""",
    example="""«Riggea mi personaje para usar animaciones de Mixamo»: exportar el modelo a FBX, subirlo a mixamo.com (cuenta gratis de Adobe), descargar con esqueleto y reimportar en Blender.""",
    tools=[("Blender Armature / Rigify", "rig profesional", OK), ("Mixamo", "auto-rig humanoide", NET), ("AccuRIG (ActorCore)", "auto-rig gratuito", EXT)],
    qc=["Poses extremas sin roturas de malla.", "Simetría correcta L/R.", "Animación exportada en el GLB."],
    pitfalls=["Pesos automáticos fallan con mallas no cerradas: unir y limpiar primero.", "Escala no aplicada distorsiona el rig."],
    related=["3d-character-animation", "3d-facial-animation", "3d-modeling"]),

"3d-walk-cycles": dict(
    title="Ciclos de caminar 3D",
    description="Crea ciclos de caminar y correr 3D en bucle: contacto, bajada, paso y subida, contrabalanceo de brazos, bote y rumbo. Úsala para 'ciclo de caminar', 'walk cycle', 'que camine en 3D', 'run cycle'.",
    intro="La acción `walk` usa frecuencia 1.6 Hz (paso cada 0.31 s): piernas ±0.55 rad, brazos opuestos, bote |cos| de 3 cm e inclinación 0.05 rad. `run` sube a 2.6 Hz con mayor amplitud e inclinación. El desplazamiento del root está sincronizado con la duración.",
    when=["Personaje 3D que se desplaza.", "Ciclos en bucle para juegos o fondos."],
    principles=["Las 4 poses clave: contacto, bajada (peso), paso (pierna cruzando), subida.",
                "Velocidad de traslación = longitud de zancada × frecuencia (evita patinaje).",
                "Cadera y hombros giran en oposición.", "Para bucle: duración múltiplo del periodo (0.625 s caminando)."],
    steps=["Define `from`/`to` distintos y acción `walk` o `run`.", "Ajusta la duración para que la distancia cuadre con la zancada (~0.5 unidades/s caminando).",
           "Render `--3d --quality preview` y revisa pies.", "Para ciclo en el sitio (juegos) deja `from == to` y exporta GLB."],
    commands="""python -m studio make "Un pingüino camina en la nieve" --3d --quality preview
python -m studio character3d pinguino --action walk --duration 1.25   # 2 ciclos exactos""",
    example="""Ciclo de caminar en bucle para web: `character3d robot --action walk --duration 1.25` y cargar el GLB en `three-scene.html?glb=…`.""",
    tools=[("Blender keyframes", "ciclo procedural", OK), ("Graph Editor (Cycles modifier)", "bucles manuales", OK), ("Mixamo walk", "mocap", NET)],
    qc=["Pies sin deslizar.", "Bucle sin salto al reiniciar.", "Ritmo de pasos coincide con el audio (footsteps)."],
    pitfalls=["Duración no múltiplo del periodo → salto en el bucle.", "Inclinación excesiva parece que cae."],
    related=["3d-character-animation", "character-movement", "seamless-loop-animation"]),

"3d-facial-animation": dict(
    title="Animación facial 3D",
    description="Anima caras 3D: parpadeo, apertura de boca por visemas sincronizada con la voz, mirada y expresiones mediante escalas o shape keys. Úsala para 'que hable en 3D', 'expresiones 3D', 'lip sync 3D', 'cara 3D'.",
    intro="En 3D la boca escala según visemas (`VIS_OPEN`: A=1.6, O=1.4, E=1.0, U=0.9, F=0.6, M=0.15) calculados de la voz real (`audio.lipsync_track`), y los ojos/pupilas se escalan en Z para parpadear. Para caras orgánicas se recomiendan shape keys.",
    when=["Diálogos en escenas 3D.", "Primeros planos de personaje 3D."],
    principles=["Boca anticipa 1–2 frames al sonido.", "Parpadeo cada 3–4 s, más en nervios.", "Mirada guía la atención: el personaje mira a quien habla.",
                "Exagerar ligeramente la apertura en estilizado."],
    steps=["Añade diálogo al actor en el JSON; el render 3D usa automáticamente sus visemas.",
           "Para shape keys: crea claves 'A','E','O','U','M','F' y conecta con un driver al valor del visema.",
           "Revisa un primer plano con cámara `zoom_in`."],
    commands="""python -m studio make "Un robot 3D saluda y dice hola a sus amigos" --3d --quality preview""",
    spec="""{"actors": [{"character": "robot", "action": "talk", "emotion": "happy", "from": [0.5, 0.82]}],
 "dialogue": [{"character": "robot", "text": "¡Hola! Soy un robot muy simpático."}], "camera": {"type": "zoom_in"}}""",
    example="""Primer plano 3D hablando: escena con `camera: zoom_in`, actor `talk` y una línea; el render keyframea la boca por frame.""",
    tools=[("Blender shape keys / drivers", "caras orgánicas", OK), ("Rhubarb Lip Sync (open source)", "visemas precisos desde audio", EXT),
           ("NVIDIA Audio2Face", "facial realista", EXT)],
    qc=["Boca cerrada en silencios.", "Sin parpadeo durante gritos.", "Sincronía audio-boca ±2 frames."],
    pitfalls=["Visemas cambiando cada frame parecen tics: el estudio elimina cambios de 1 frame.", "Voces cloud (ElevenLabs) cambian la duración: re-planificar tras generar voces."],
    related=["character-lip-sync", "character-expressions", "3d-rigging"]),

"3d-camera-animation": dict(
    title="Animación de cámara 3D",
    description="Diseña movimientos de cámara 3D cinematográficos: órbita, dolly in/out, paneo, travelling, temblor, con Track-To y easing. Úsala para 'cámara que gira', 'plano cinematográfico 3D', 'órbita', 'dolly', 'travelling'.",
    intro="`camera()` en scene3d.py crea una cámara con restricción Track-To a un objetivo a la altura del personaje y keyframes por frame con easing smoothstep. Tipos: `static`, `orbit`, `pan`, `zoom_in`/`dolly_in`, `zoom_out`, `shake`. La distancia se adapta al número de personajes.",
    when=["Planos 3D dinámicos.", "Turntables de producto/personaje."],
    principles=["Mover la cámara con motivación (revelar, seguir, enfatizar).", "Easing in/out siempre; nunca velocidad constante salvo travelling.",
                "Regla de 180° entre personajes que dialogan.", "Lentes: 24–35 mm acción, 50–85 mm retratos."],
    steps=["Elige `camera.type` por escena en el JSON.", "Orbit para presentar personajes; dolly_in para momentos emotivos; shake para impactos.",
           "Previsualiza con `--engine rapido`.", "Ajusta en el `.blend` si se requiere un movimiento a medida (Graph Editor)."],
    commands="""python -m studio make "Una fresa 3D presenta su nuevo baile" --3d --engine rapido --quality preview""",
    spec="""{"scenes": [{"camera": {"type": "orbit"}}, {"camera": {"type": "dolly_in"}}, {"camera": {"type": "shake"}}]}""",
    example="""Turntable de personaje: `character3d estrella --action idle --duration 6` usa órbita completa suave alrededor del personaje.""",
    tools=[("Blender camera + Track To", "movimientos procedurales", OK), ("Camera Shakify (addon)", "temblor realista", EXT), ("Three.js OrbitControls", "cámara interactiva web", OK)],
    qc=["El sujeto nunca sale de cuadro.", "Sin cambios bruscos de velocidad.", "Horizonte nivelado salvo intención."],
    pitfalls=["Órbitas rápidas marean: ≤ 70° en 5 s.", "Cámara dentro de objetos del escenario."],
    related=["cinematic-video", "scene-composition", "3d-environment-animation"]),

"3d-environment-animation": dict(
    title="Escenarios 3D animados",
    description="Crea y anima entornos 3D: suelo, cielo (world), árboles, edificios, escenario con focos, mar, planetas; niebla y luz por hora del día. Úsala para 'escenario 3D', 'mundo 3D', 'fondo 3D', 'ambiente 3D'.",
    intro="`build_set()` genera 15 escenarios 3D coherentes con los 2D (park, forest, city, beach, space, stage con focos RGB, kitchen, classroom, dojo, studio…) y `lights()` adapta energía y color al momento del día (day/sunset/night).",
    when=["Escenas 3D con contexto.", "Fondos 3D para personajes o productos."],
    principles=["Profundidad: elementos en primer plano, medio y fondo.", "El fondo menos saturado y con más niebla.",
                "Color de la luz cuenta la hora: día neutro, atardecer naranja, noche azul.", "Variedad controlada (semilla fija por escenario)."],
    steps=["Elige `background` y `time_of_day` por escena.", "Para entornos a medida, añade props en `build_set` (obj_add con materiales).",
           "Para HDRI realistas: descarga de Poly Haven (CC0) y asígnalo al World.", "Render y revisa la exposición."],
    commands="""python -m studio make "Un astronauta rana explora el espacio" --3d --quality preview""",
    example="""«Escena 3D en la playa al atardecer»: `background: beach`, `time_of_day: sunset` → luz key naranja, mar y arena.""",
    tools=[("Blender", "props procedurales", OK), ("Poly Haven", "HDRI, texturas y modelos CC0", NET), ("Geometry Nodes", "dispersión de vegetación", OK)],
    qc=["Horizonte sin cortes del plano de suelo.", "Exposición correcta de cielo y suelo.", "Escala coherente de props."],
    pitfalls=["Plano de suelo pequeño se ve el borde en órbitas: usa 40×40 m.", "Demasiados objetos ralentizan EEVEE por software."],
    related=["animation-lighting", "3d-animation", "animated-backgrounds"]),

"blender-animation": dict(
    title="Animación con Blender (automatización bpy)",
    description="Automatiza Blender desde línea de comandos: scripts bpy, render headless, Grease Pencil, keyframes, modificadores, exportación GLB/FBX, y depuración de errores típicos (EGL, OIDN, numpy). Úsala para 'usa Blender', 'script de Blender', 'render en Blender', '.blend'.",
    intro=f"Blender está instalado y probado en el estudio ({BLENDER_NOTE}). `studio/blender_bridge.py` lanza `blender -b --factory-startup -noaudio -P scene3d.py -- job.json`, registra `blender.log` y convierte frames a video.",
    when=["Cualquier tarea que requiera Blender.", "Diagnosticar fallos de render 3D."],
    principles=["Siempre `--factory-startup` para resultados reproducibles.", "Pasar parámetros por JSON tras `--`.",
                "Guardar `.blend` de cada escena para edición manual posterior.", "Revisar `blender.log` ante cualquier fallo."],
    steps=["Escribe el script bpy (ver `studio/blender/scene3d.py` como referencia).", "Ejecuta `blender -b --factory-startup -P script.py -- args`.",
           "Si falla EGL: instala `libegl1 libgl1-mesa-dri` (render por software).", "Si falla glTF por numpy: `apt install python3-numpy`.",
           "Si falla Cycles por OIDN: desactiva denoising (por defecto en el estudio)."],
    commands="""blender --version
blender -b --factory-startup -noaudio -P studio/blender/scene3d.py -- projects/<…>/frames3d/job3d.json
blender -b archivo.blend -E BLENDER_EEVEE -s 1 -e 48 -a              # render de un .blend existente""",
    example="""Re-renderizar una escena editada a mano: abrir `escena_1.blend`, ajustar, guardar, y `blender -b escena_1.blend -a`; luego `ffmpeg -framerate 24 -i s01_%04d.png …`.""",
    tools=[("Blender 4.0.2", "3D completo", OK), ("Grease Pencil", "2D dentro de Blender", OK), ("Blender oficial (blender.org)", "OIDN, GPU, versión más reciente", EXT)],
    qc=["`blender.log` sin 'Error:'.", "Número de PNG = duración × fps.", "Colores correctos (AgX)."],
    pitfalls=["Python de Blender ≠ Python del estudio: no importes PIL/numpy del proyecto dentro de bpy.", "Rutas relativas en Blender usan `//`."],
    related=["3d-animation", "animation-rendering", "3d-modeling"]),

"threejs-animation": dict(
    title="Animación 3D web con Three.js",
    description="Crea escenas 3D interactivas en el navegador con Three.js (WebGL): personajes procedurales o GLB de Blender, luces, sombras, OrbitControls, y captura determinista a MP4. Úsala para 'Three.js', 'WebGL', '3D en la web', 'visor 3D', 'escena 3D interactiva'.",
    intro="`templates/web/three-scene.html` (Three.js 0.170 local, sin CDN) crea una escena con iluminación de tres puntos, sombras suaves, árboles low-poly y un personaje animado (dance/walk/jump) o carga un GLB exportado por Blender con su animación. `window.__seek(t)` permite capturar frames exactos con `scripts/capture.mjs` (Chromium + SwiftShader).",
    when=["3D en páginas web o visor de modelos.", "Video 3D rápido sin Blender."],
    principles=["Render determinista: separar estado de animación (`pose(t)`) del bucle de render.", "Tone mapping ACES + sombras PCFSoft para look profesional.",
                "Pixel ratio 1 en captura; `preserveDrawingBuffer` para screenshots.", "Cargar dependencias locales (importmap a node_modules)."],
    steps=["Abre en vivo: `python -m studio serve` → pestaña 3D y Web → three-scene → Ver en vivo.",
           "Parámetros por URL: `color`, `action` (dance/walk/jump), `sky`, `ground`, `glb`, `duration`.",
           "Captura: `python -m studio web three-scene --duration 4 --query \"action=walk&color=%23fb8c00\"`.",
           "Para un GLB: `--query \"glb=/projects/<…>/personaje.glb\"` (servido por el estudio)."],
    commands="""python -m studio web three-scene --duration 4 --query "action=dance&color=%23e53935"
python -m studio web three-scene --query "glb=/projects/<carpeta>/manzana.glb" -o manzana_web.mp4""",
    example="""«Quiero un visor 3D de mi personaje para mi web»: `character3d manzana` → copiar `three-scene.html` + GLB a la web y abrir `three-scene.html?glb=manzana.glb`.""",
    tools=[("Three.js 0.170", "WebGL", OK), ("Playwright + Chromium (SwiftShader)", "captura a video", OK), ("React Three Fiber", "Three.js en React", EXT)],
    qc=["Sin errores en consola.", "Frames idénticos entre capturas (determinismo).", "GLB con animación reproduciéndose."],
    pitfalls=["Abrir el HTML con file:// bloquea módulos ES: usar el servidor del estudio.", "WebGL sin GPU es lento a 1080p: capturar a 720p."],
    related=["interactive-animation", "3d-modeling", "gsap-animation"]),
}
