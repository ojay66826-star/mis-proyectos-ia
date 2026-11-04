---
name: 2d-animation
description: Crea animaciones 2D completas (personajes, escenarios, cámara, efectos, voces y música) con el motor procedural del estudio. Úsala para 'haz una animación', 'crea un dibujo animado', 'animación 2D', 'cartoon', o cualquier video animado plano sin requisito de 3D.
---

# Animación 2D

**Categoría:** Animación 2D · **Skills relacionadas:** `animation-workflow`, `character-animation`, `scene-composition`, `animation-rendering`, `cartoon-animation`

Skill base de la animación 2D del estudio. Convierte una idea en un video MP4 terminado usando el motor propio `studio` (Pillow + numpy + FFmpeg): personajes vectoriales procedurales con rig de extremidades, escenarios con paralaje, cámara virtual, partículas, lip-sync y mezcla de audio. Todo funciona sin conexión ni claves.

## Cuándo usar esta Skill

- El usuario pide una animación, caricatura o video animado sin especificar 3D.
- Se necesita un resultado rápido, consistente y 100 % gratuito.
- Como base sobre la que otras Skills (estilos, efectos, personajes) añaden capas.

## Principios profesionales

- Aplica los 12 principios de Disney: squash & stretch, anticipación, puesta en escena, arcos, acción secundaria, timing, exageración, sólido, atractivo.
- Composición legible: personaje principal en tercios, siluetas claras, fondo con menos contraste que los personajes.
- Timing a 24 fps (12 fps para estilos stop-motion/papel); las acciones clave duran 0.3–1.2 s.
- Cada escena debe tener una intención (presentar, conflicto, resolución) y durar 3–6 s.
- Movimiento de cámara sutil (pan/zoom ≤15 %) para dar vida sin marear.

## Procedimiento paso a paso

1. Entiende la petición: personajes, acción, emoción, escenario, formato (16:9 / 9:16 / 1:1) y duración.
2. Genera el plan: `python -m studio plan "<idea>" -o proyecto.json` y revísalo (escenas, diálogos, acciones).
3. Ajusta el JSON si hace falta (acciones `walk/run/jump/dance/talk/wave/punch/kick/celebrate/float/spin/think`, emociones, cámara, efectos).
4. Haz un borrador rápido: `python -m studio render proyecto.json --quality preview` y abre `storyboard.jpg`.
5. Corrige timing/composición y renderiza final en `--quality hd` o `fullhd`.
6. Ejecuta `python -m studio qc projects/<…>/final.mp4` y entrega rutas de video, GIF, miniatura y SRT.

## Comandos del estudio

```bash
# De una frase a video terminado
python -m studio make "Una manzana y un plátano juegan en el parque" --style cartoon

# Flujo con revisión del guion
python -m studio plan "Una manzana y un plátano juegan en el parque" -o proyecto.json
python -m studio render proyecto.json --quality preview   # borrador
python -m studio render proyecto.json --quality hd        # final 720p
```

## Fragmento de proyecto (project.json)

```json
{
  "style": "cartoon", "format": "16:9", "mood": "happy",
  "scenes": [{
    "background": "park", "time_of_day": "day", "duration": 4,
    "camera": {"type": "pan"},
    "actors": [{"character": "manzana", "action": "walk", "emotion": "happy", "from": [0.1, 0.82], "to": [0.45, 0.82]}],
    "dialogue": [{"character": "manzana", "text": "¡Hola, amigos!"}],
    "effects": [{"type": "sparkles", "y": 0.5}]
  }]
}
```

## Ejemplo completo

**Petición:** «Crea una animación de un gato que camina por la ciudad de noche».

1. `python -m studio make "Un gato camina por la ciudad de noche" --quality preview` → revisar `storyboard.jpg`.
2. Si el gato debe ir de derecha a izquierda, editar `from/to` en `project.json` (`[0.9,0.82]→[0.1,0.82]`).
3. `python -m studio render projects/<…>/project.json --quality hd` → `final.mp4` con pasos sincronizados, música y QC.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D `studio` | personajes, fondos, cámara, partículas | ✅ motor propio del estudio |
| FFmpeg 6.1 | codificación H.264/AAC | ✅ instalado y probado |
| espeak-ng | voces locales en español | ✅ instalado y probado |
| Krita / OpenToonz | dibujo frame a frame manual | 💻 programa externo recomendado |
| ElevenLabs / OpenAI TTS | voces realistas | 🔑 requiere clave API |

## Control de calidad

- [ ] El storyboard muestra cada escena con intención clara.
- [ ] Los personajes no salen del cuadro ni flotan sobre el suelo.
- [ ] No hay saltos bruscos entre escenas (transición de 0.45 s).
- [ ] Audio presente, voces entendibles, música por debajo (ducking).
- [ ] `qc_report.json` aprobado.

## Errores comunes y cómo evitarlos

- Demasiados personajes en 16:9 (más de 4) → se reducen; repartir en escenas.
- Diálogos largos alargan escenas: máximo ~12 palabras por línea.
- Usar `walk` sin `from/to` distintos deja al personaje caminando en el sitio (moonwalk): define desplazamiento.

## Cómo encaja en el estudio (trabajo en equipo entre Skills)

El estudio sigue un único pipeline y **todas las Skills comparten el mismo proyecto JSON** (`project.json`), así que se combinan sin conversiones:

```
idea → animation-scripting → character-design → animation-storyboarding → scene-composition
     → (animación 2D/3D + personajes + efectos) → animation-sound-design → video-editing
     → animation-rendering → animation-quality-control → animation-optimization / exportación
```

- Orquestador general: Skill `animation-workflow` (decide qué Skills intervienen y en qué orden).
- Motor: `python -m studio …` (ver `docs/CLI.md`). Interfaz: `python -m studio serve` → http://127.0.0.1:8765
- Salida estándar de un proyecto: `projects/<fecha>-<titulo>/` con `final.mp4`, `storyboard.jpg`, `miniatura.jpg`,
  `vista_previa.gif`, `subtitulos.srt`, `characters/*_sheet.png`, `audio/*.wav`, `project.json`, `qc_report.json`.

## Reglas del estudio

1. **Primero lo local y gratuito** (motor 2D, Blender, FFmpeg, espeak-ng, Three.js, GSAP, Lottie, Remotion). Usa APIs de pago
   solo si el usuario lo pide o si la calidad exigida lo requiere, y avisa antes de gastar créditos.
2. **Nunca inventes resultados**: ejecuta el comando, revisa el archivo generado (abre un frame o el storyboard) y reporta
   rutas reales. Si algo requiere una clave que no existe (`python -m studio doctor`), dilo y ofrece la alternativa local.
3. **Consistencia de personajes**: reutiliza siempre la ficha JSON del personaje (mismo `id`, `color`, `species`, `accessory`).
4. **No subas secretos**: las claves viven en `.env` (ignorado por git).
5. Termina con `python -m studio qc <video>` y comunica qué pasó y qué no.
