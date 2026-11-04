---
name: interactive-animation
description: Animaciones que responden al usuario: personajes que siguen el ratón con la mirada, saltan al hacer clic, bailan con una tecla, física simple (gravedad, squash), partículas; Canvas 2D, Three.js y sprites para juegos. Úsala para 'interactiva', 'que reaccione al ratón', 'mini juego', 'animación para mi web que responda'.
---

# Animación interactiva

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `threejs-animation`, `gsap-animation`, `sprite-animation`

`templates/web/interactive.html` implementa un personaje en Canvas 2D con mirada que sigue al cursor, salto con gravedad y squash al aterrizar, modo baile con barra espaciadora y ráfaga de partículas. Incluye modo de captura determinista (simula clics) para generar un video de demostración.

## Cuándo usar esta Skill

- Webs, landings, juegos sencillos, kioscos, demos.

## Principios profesionales

- Respuesta inmediata (<100 ms) a la entrada.
- Física creíble y estable (dt acotado).
- Feedback visual y sonoro en cada interacción.
- Accesible por teclado.

## Procedimiento paso a paso

1. Abre la plantilla en vivo (pestaña 3D y Web).
2. Cambia color con `?color=%23…`; adapta física y dibujo.
3. Para 3D interactivo usa `three-scene.html` (OrbitControls).
4. Para juegos usa sprites de la Skill `sprite-animation` con Phaser/Godot.

## Comandos del estudio

```bash
python -m studio serve      # abrir http://127.0.0.1:8765 → 3D y Web → interactive → Ver en vivo
python -m studio web interactive --duration 6 -o demo_interactiva.mp4
```

## Ejemplo completo

Mascota interactiva para una web: incrustar `interactive.html` en un iframe; la mascota mira al cursor y salta al hacer clic con confeti.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| Canvas 2D | interacción ligera | ✅ instalado y probado |
| Three.js + OrbitControls | 3D interactivo | ✅ instalado y probado |
| Phaser / Godot | juegos 2D | 💻 programa externo recomendado |
| Rive | animación interactiva con state machines | 💻 programa externo recomendado |

## Control de calidad

- [ ] Funciona con ratón y táctil.
- [ ] 60 fps en móviles medios.
- [ ] Sin fugas de memoria (partículas limpiadas).

## Errores comunes y cómo evitarlos

- dt sin límite tras cambiar de pestaña provoca saltos: acotar a 0.05 s.
- Olvidar `resize`.

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
