---
name: character-fighting
description: Escenas de pelea: guardia, golpes alternos, patadas, impactos con temblor de cámara, auras de energía, líneas de velocidad y explosiones, con efectos de sonido. Úsala para 'pelea', 'batalla', 'combate', 'lucha', 'escena de acción'.
---

# Peleas y acción

**Categoría:** Personajes · **Skills relacionadas:** `energy-effects`, `explosions`, `anime-animation`, `cinematic-effects`

Acciones `punch` (golpes alternos con anticipación y retroceso) y `kick`, emoción `angry` por defecto, y plantillas del planificador: enfrentamiento en el dojo → intercambio con speedlines y aura → explosión final y celebración del ganador. Audio: golpes sincronizados cada 0.7 s.

## Cuándo usar esta Skill

- Peleas, duelos, artes marciales, superhéroes.
- Contenido de acción para niños (sin violencia gráfica).

## Principios profesionales

- Claridad: un golpe = anticipación, impacto, recuperación.
- Eje de acción horizontal, rivales enfrentados.
- Impacto: shake + flash + sonido en el mismo frame.
- Mantenerlo apto para todo público: sin sangre.

## Procedimiento paso a paso

1. Define rivales y escenario (`dojo`, `city`, `space`).
2. Plan: `make "X y Y pelean …"`.
3. Ajusta `energy` con `on` en el personaje con poder, `explosion` con `start`.
4. Render y revisa que los golpes se lean.

## Comandos del estudio

```bash
python -m studio make "Un perro y un gato pelean en el dojo con explosiones" --style anime
python -m studio make "Un robot pelea contra un monstruo en la ciudad de noche" --style cinematic
```

## Fragmento de proyecto (project.json)

```json
{"camera": {"type": "shake"}, "effects": [{"type": "speedlines", "intensity": 0.6}, {"type": "energy", "on": "perro"},
  {"type": "explosion", "x": 0.5, "y": 0.62, "start": 1.2}],
 "actors": [{"character": "perro", "action": "punch", "from": [0.35, 0.82], "to": [0.42, 0.82], "facing": 1},
            {"character": "gato", "action": "kick", "from": [0.66, 0.82], "to": [0.6, 0.82], "facing": -1}]}
```

## Ejemplo completo

Duelo anime: 3 escenas (tensión, intercambio, explosión), música `action` 140 BPM, golpes con SFX sintetizados.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Motor 2D (punch/kick) | coreografía | ✅ motor propio del estudio |
| Efectos energy/explosion/speedlines | impacto | ✅ motor propio del estudio |
| Blender (punch/kick 3D) | pelea 3D | ✅ instalado y probado |

## Control de calidad

- [ ] Los personajes miran al rival.
- [ ] Cada impacto tiene sonido.
- [ ] Apto para todas las edades.

## Errores comunes y cómo evitarlos

- Rivales demasiado separados: los golpes no 'llegan' (dist ≤ 0.3).
- Shake permanente cansa: úsalo solo en la escena de impacto.

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
