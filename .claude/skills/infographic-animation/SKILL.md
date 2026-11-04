---
name: infographic-animation
description: Visualización de datos animada: barras que crecen con rebote, contadores numéricos, títulos, etiquetas, unidades, paletas y formatos para redes; gráficos claros y honestos. Úsala para 'infografía', 'gráfico animado', 'datos animados', 'estadísticas', 'chart animado'.
---

# Infografías animadas

**Categoría:** Estilos especiales · **Skills relacionadas:** `educational-animation`, `motion-graphics`, `kinetic-typography`

`motiongraphics.infographic(data, …)` anima un gráfico de barras: título con fundido, barras escalonadas con `ease_out_back`, contadores que suben hasta el valor, etiquetas y sonido 'pop' por barra. Paletas: vibrante, pastel, oscuro, neon, corporativo.

## Cuándo usar esta Skill

- Mostrar cifras, comparaciones, rankings, resultados.

## Principios profesionales

- Eje en cero (honestidad visual).
- Ordenar barras con intención (ranking o tiempo).
- Máximo 7 categorías.
- Etiquetas directas, sin leyenda.

## Procedimiento paso a paso

1. Prepara datos `Etiqueta=valor,…` (verifica la fuente).
2. `python -m studio infographic "…" --title … --unit …`.
3. Formato según destino (9:16 para redes).
4. Úsala como escena insertada con `concat`.

## Comandos del estudio

```bash
python -m studio infographic "Manzana=32,Plátano=24,Fresa=40,Uva=18" --title "Frutas favoritas" --unit " votos"
python -m studio infographic "Ene=12,Feb=18,Mar=27" --title "Ventas (miles)" --format 9:16
```

## Ejemplo completo

Resultados de encuesta para Instagram: 4 barras, paleta pastel, formato 1:1 (añadir `--format 1:1`), 6 s.

## Herramientas recomendadas

| Herramienta | Uso | Estado en el estudio |
|---|---|---|
| motiongraphics.infographic | barras animadas | ✅ motor propio del estudio |
| GSAP/D3 (web) | gráficos interactivos | ✅ instalado y probado |
| Remotion | gráficos con React | ✅ instalado y probado |

## Control de calidad

- [ ] Valores y unidades correctos.
- [ ] Texto legible en móvil.
- [ ] Escala honesta.

## Errores comunes y cómo evitarlos

- Ejes truncados exageran diferencias.
- Demasiadas categorías en 9:16.

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
