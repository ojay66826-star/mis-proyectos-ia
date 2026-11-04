---
name: minimalist-animation
description: Animación minimalista y plana: formas simples, sin contornos, ojos de punto, fondos lisos, paleta reducida, mucho espacio negativo y movimientos precisos con easing. Úsala para 'minimalista', 'flat design', 'limpio', 'simple', 'corporativo moderno'.
---

# Animación minimalista

**Categoría:** Estilos especiales · **Skills relacionadas:** `motion-graphics`, `infographic-animation`, `educational-animation`

`style: minimalist` usa ojos de punto, sin contorno ni sombreado y fuerza el fondo `studio` (degradado liso con suelo). Ideal con motion graphics (texto, logos, infografías) para videos corporativos o explicativos.

## Cuándo usar esta Skill

- Explainers corporativos, apps, presentaciones, branding moderno.

## Principios profesionales

- Menos es más: un elemento protagonista por plano.
- Espacio negativo generoso.
- Easing preciso (in_out, out_back).
- Paleta de 2–3 colores + neutro.

## Procedimiento paso a paso

1. `make … --style minimalist`.
2. Combina con `text`, `logo`, `infographic` (paleta corporativo).
3. Transiciones `slide`/`wipe` limpias.

## Comandos del estudio

```bash
python -m studio make "Un robot presenta una nueva app" --style minimalist
python -m studio infographic "2023=40,2024=65,2025=90" --title "Crecimiento" --unit "%"
```

## Ejemplo completo

Explainer de 30 s: robot minimalista explica 3 ventajas, cada una con infografía o texto animado, música `calm`.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| style minimalist | flat | ✅ motor propio del estudio |
| motiongraphics | texto/logos/infografías | ✅ motor propio del estudio |
| GSAP templates | animaciones web limpias | ✅ instalado y probado |

## Control de calidad

- [ ] Nada superfluo en pantalla.
- [ ] Alineaciones precisas.
- [ ] Tipografía consistente.

## Errores comunes y cómo evitarlos

- Minimalista ≠ vacío: mantener una acción clara.
- Demasiados colores rompen el estilo.

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
