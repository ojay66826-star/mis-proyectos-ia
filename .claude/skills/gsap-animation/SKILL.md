---
name: gsap-animation
description: Animaciones web profesionales con GSAP 3: timelines, posiciones relativas, stagger, eases (back, elastic, expo), ScrollTrigger, control determinista (seek) y captura a video. Úsala para 'GSAP', 'timeline web', 'animación web profesional', 'scroll animation', 'animar una landing'.
---

# Animación con GSAP

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `css-animation`, `motion-graphics`, `interactive-animation`

GSAP 3.15 está instalado localmente (`node_modules/gsap`, sin CDN). Las plantillas `gsap-logo.html` y `kinetic-type.html` crean timelines **pausadas** y exponen `window.__seek = t => { tl.seek(t, false) }` (sin devolver el timeline: GSAP es 'thenable' y bloquearía el `await` de la captura).

## Cuándo usar esta Skill

- Animaciones web complejas, intros, landings, banners.

## Principios profesionales

- Construir una timeline maestra con etiquetas y posiciones (`'<'`, `'+=0.2'`).
- Stagger para grupos.
- Eases con carácter (back.out(2), elastic.out(1,0.4)).
- Separar construcción de reproducción (paused: true) para poder capturar.

## Procedimiento paso a paso

1. Copia una plantilla y modifica la timeline.
2. Previsualiza en el servidor del estudio.
3. Captura: `python -m studio web mi_plantilla.html`.
4. Para scroll, usa ScrollTrigger (incluido en el paquete gsap).

## Comandos del estudio

```bash
python -m studio web gsap-logo --query "text=Nuevo Lanzamiento&color=%2310b981" --duration 4.5
python -m studio web kinetic-type --query "text=Hola desde GSAP&bpm=100"
```

## Fragmento de proyecto (project.json)

```json
// patrón de plantilla capturable
const tl = gsap.timeline({ paused: true });
tl.from(".titulo", { y: 80, opacity: 0, duration: 0.6, ease: "back.out(2)" })
  .from(".item", { scale: 0, stagger: 0.08, ease: "elastic.out(1,0.5)" }, "-=0.2");
window.__duration = tl.duration();
window.__seek = (t) => { tl.seek(t, false); };
window.__ready = true;
```

## Ejemplo completo

Banner animado de 6 s para web: título, 3 iconos con stagger y CTA con pulso; capturado en 1200×628 para anuncios.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| GSAP 3.15 (local) | timelines | ✅ instalado y probado |
| capture.mjs | GSAP → MP4 | ✅ instalado y probado |
| ScrollTrigger / SplitText | plugins incluidos en el paquete gsap (no probados aquí) | 📦 incluido, sin probar |

## Control de calidad

- [ ] La captura coincide con la reproducción en vivo.
- [ ] Sin errores de consola.
- [ ] Duración = `tl.duration()`.

## Errores comunes y cómo evitarlos

- Devolver el timeline desde `__seek` cuelga la captura (thenable).
- Usar `gsap.to` sueltos sin timeline impide el seek global.

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
