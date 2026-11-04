---
name: motion-graphics
description: Diseño gráfico en movimiento: títulos, lower thirds, formas, transiciones gráficas, fondos, infografías y logos con easing profesional, en Python (Pillow+FFmpeg), GSAP, CSS o Remotion. Úsala para 'motion graphics', 'gráficos animados', 'grafismo', 'títulos animados', 'animación de marca'.
---

# Motion graphics

**Categoría:** Diseño y movimiento · **Skills relacionadas:** `animated-logos`, `kinetic-typography`, `gsap-animation`, `infographic-animation`

Cuatro motores disponibles: `motiongraphics.py` (Python, rápido, sin navegador), plantillas web GSAP/CSS/SVG capturadas a MP4 (`scripts/capture.mjs`), Remotion (React) y el motor 2D para personajes. Las curvas de easing del estudio: linear, in_out, out_back, elastic, bounce.

## Cuándo usar esta Skill

- Grafismo para videos, presentaciones, redes, marcas.

## Principios profesionales

- Easing siempre (nunca lineal salvo loops).
- Staggering (escalonar) para jerarquía.
- Grid y alineación estrictos.
- Ritmo con la música.

## Procedimiento paso a paso

1. Elige motor: Python (texto/logo/infografía/fondo), web (GSAP para precisión de diseño), Remotion (composiciones React con datos).
2. Define paleta y tipografía (DejaVu incluida; o web fonts en plantillas).
3. Genera y revisa frames clave.
4. Exporta al formato del destino.

## Comandos del estudio

```bash
python -m studio text "Nuevo episodio cada viernes" --mode slide --format 16:9
python -m studio logo "Estudio IA" --tagline "Animación con IA" --color "#6d28d9"
python -m studio web gsap-logo --query "text=Mi Marca&color=%23ff006e" --duration 4
python -m studio remotion "Un zorro presenta las noticias de la semana"
```

## Ejemplo completo

Paquete de grafismo para canal: logo animado (GSAP), lower third con kinetic-type, fondo en bucle (`background blobs`), todo en la paleta de la marca.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| motiongraphics.py | texto/logo/infografía/fondos | ✅ motor propio del estudio |
| GSAP 3.15 | timelines web | ✅ instalado y probado |
| Remotion 4.0.290 | video con React | ✅ instalado y probado |
| After Effects / Cavalry | motion profesional | 💻 programa externo recomendado |

## Control de calidad

- [ ] Easing suave sin saltos.
- [ ] Textos dentro de márgenes seguros.
- [ ] Paleta coherente.

## Errores comunes y cómo evitarlos

- Demasiadas animaciones simultáneas.
- Fuentes no instaladas en la captura web: usar las del sistema o incluirlas.

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
